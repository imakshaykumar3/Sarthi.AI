# app/agent/nodes/planner.py
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llms import gpt_llm
from app.schemas.state import AgentState
from app.schemas.api import UserIntent
from app.utils import safe_dict, get_last_user_message

router_llm = gpt_llm.with_structured_output(UserIntent)

def planner_node(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    messages = state.get("messages", [])
    last_msg = get_last_user_message(messages)
    details = safe_dict(state.get("trip_details"))
    
    print(f"🧠 PLANNER (INTENT): Phase='{phase}' | User='{last_msg}'")

    system_instruction = f"""
        You are a Router for a Travel Agent.
        Current Conversation Phase: {phase}
        Definitions:
        - select_option: User is picking a specific flight, train, or hotel.
        - modify_search: User changes dates, location, or budget.
        - confirm_proceed: User agrees to move to the next step (e.g., "Yes, find hotels", "Proceed").
        - ask_question: User asks about baggage, weather, or details.
        """
    
    try:
        intent_result = router_llm.invoke(
            [
                SystemMessage(content=system_instruction),
                HumanMessage(content=last_msg)
            ],
            config={"callbacks": []} 
        )
        intent = intent_result.category
        print(f"🧭 ROUTER DECISION: {intent}")
    except Exception as e:
        print(f"⚠️ Router Error: {e}")
        intent = "general_chitchat"

    # --- TRANSITIONS ---
    if intent == "modify_search":
        return {"current_phase": "ready_to_search"}

    if phase == "presenting_options":
        if intent == "select_option": return {"current_phase": "confirm_transport"}
        if intent == "ask_question": return {"current_phase": "presenting_options"}

    if phase == "confirm_transport":
        if intent == "confirm_proceed" or "hotels" in last_msg.lower():
            return {"current_phase": "search_hotels"}

    if phase == "presenting_hotels":
        if intent == "select_option": return {"current_phase": "itinerary"}

    if phase == "gathering_info":
        if (details.get("source") and details.get("destination") and details.get("start_date")):
            if intent != "ask_question":
                return {"current_phase": "ready_to_search"}

    return {"current_phase": phase}