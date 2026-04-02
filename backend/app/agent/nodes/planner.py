from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llms import gpt_llm
from app.schemas.state import AgentState
from app.schemas.api import UserIntent
from app.utils import safe_dict, get_last_user_message

# Load the structured output model
router_llm = gpt_llm.with_structured_output(UserIntent)

def planner_node(state: AgentState):
    """
    The Brain of the Agent: Determines the next phase based on user intent 
    and current state. Includes Phase-Aware Hard Overrides for UI-based selections.
    """
    phase = state.get("current_phase", "gathering_info")
    messages = state.get("messages", [])
    last_msg = get_last_user_message(messages)
    details = safe_dict(state.get("trip_details"))
    
    print(f"🧠 PLANNER (INTENT): Phase='{phase}' | User='{last_msg}'")

    # --- 1. PRIORITY HARD OVERRIDES (Phase-Aware) ---
    msg_lower = last_msg.lower()

    # Override: Rental Selection -> Return Transport
    if phase == "presenting_rentals" and ("select" in msg_lower or "rental" in msg_lower):
        print("🚀 Transitioning to RETURN_TRANSPORT (Hard Override)")
        return {"current_phase": "search_return_transport"}

    # Override: Hotel Selection -> Itinerary
    if phase == "presenting_hotels" and ("select" in msg_lower or "stay" in msg_lower or "itinerary" in msg_lower):
        print("🚀 Transitioning to ITINERARY phase (Hard Override)")
        return {"current_phase": "itinerary"}
    
    # Override: Transport Selection -> Confirm
    if phase == "presenting_options" and "select" in msg_lower:
        print("🚀 Transitioning to CONFIRM_TRANSPORT (Hard Override)")
        return {"current_phase": "confirm_transport"}

    # --- 2. LLM INTENT CLASSIFICATION (Fallback for Natural Language) ---
    system_instruction = f"""
        You are a Routing Expert for an AI Travel Agent named TravelGenie.
        Current Conversation Phase: {phase}
        
        Analyze the user's latest message and categorize it:
        - select_option: User is picking a specific flight, train, or hotel.
        - modify_search: User wants to change dates, destination, or source city.
        - confirm_proceed: User says 'yes', 'proceed', 'go ahead', or 'find hotels'.
        - ask_question: User asks about weather, baggage, or travel advice.
        - general_chitchat: Greeting or unrelated text.
        """
    
    try:
        intent_result = router_llm.invoke(
            [
                SystemMessage(content=system_instruction),
                HumanMessage(content=last_msg)
            ]
        )
        intent = intent_result.category
        print(f"🧭 ROUTER DECISION: {intent}")
    except Exception as e:
        print(f"⚠️ Router Error: {e}")
        intent = "general_chitchat"

    # --- 3. STATE TRANSITION LOGIC ---

    # GLOBAL OVERRIDE: User wants to change the search parameters
    if intent == "modify_search":
        print("🔄 User requested modification. Resetting to search.")
        return {"current_phase": "ready_to_search"}

    if phase == "gathering_info":
        if (details.get("source") and details.get("destination") and details.get("start_date")):
            if intent != "ask_question":
                return {"current_phase": "ready_to_search"}

    if phase == "presenting_options" and intent == "select_option": 
        return {"current_phase": "confirm_transport"}

    if phase == "confirm_transport" and (intent == "confirm_proceed" or "hotel" in msg_lower):
        return {"current_phase": "search_hotels"}

    if phase == "presenting_hotels" and (intent == "select_option" or "selected" in msg_lower):
        print("🚀 Moving to Final Itinerary Generation")
        return {"current_phase": "itinerary"}

    if phase == "asking_rentals":
        if "yes" in msg_lower or "car" in msg_lower or "bike" in msg_lower or "sure" in msg_lower:
            print("🚀 Moving to Rental Search")
            return {"current_phase": "search_rentals"}
        elif "no" in msg_lower or "skip" in msg_lower:
            print("🚀 Skipping Rentals, Moving to Return Transport")
            return {"current_phase": "search_return_transport"}

    if phase == "presenting_rentals" and (intent == "select_option" or "selected" in msg_lower or "continue" in msg_lower):
        print("🚀 Moving to Return Transport")
        return {"current_phase": "search_return_transport"}

    # DEFAULT FALLBACK
    return {"current_phase": phase}