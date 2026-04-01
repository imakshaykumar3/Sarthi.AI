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
    and current state. Includes Hard Overrides for UI-based selections.
    """
    phase = state.get("current_phase", "gathering_info")
    messages = state.get("messages", [])
    last_msg = get_last_user_message(messages)
    details = safe_dict(state.get("trip_details"))
    
    print(f"🧠 PLANNER (INTENT): Phase='{phase}' | User='{last_msg}'")

    # --- 1. PRIORITY HARD OVERRIDES (Bypass LLM for UI Buttons) ---
    # This prevents the LLM from misinterpreting a structured selection string.
    
    # Check for Hotel Selection -> Itinerary
    selection_keywords = ["selected stay", "finalize my stay", "selected:", "itinerary"]
    if any(k in last_msg.lower() for k in selection_keywords):
        print("🚀 Transitioning to ITINERARY phase (Hard Override)")
        return {"current_phase": "itinerary"}
    
    # Check for Transport Selection
    if "Select option:" in last_msg and phase == "presenting_options":
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

    # Phase: GATHERING -> SEARCH
    if phase == "gathering_info":
        if (details.get("source") and details.get("destination") and details.get("start_date")):
            # If we have the big three, and user isn't just asking a question, search!
            if intent != "ask_question":
                return {"current_phase": "ready_to_search"}

    # Phase: TRANSPORT OPTIONS -> CONFIRMATION
    if phase == "presenting_options":
        if intent == "select_option": 
            return {"current_phase": "confirm_transport"}

    # Phase: CONFIRM TRANSPORT -> SEARCH HOTELS
    if phase == "confirm_transport":
        if intent == "confirm_proceed" or "hotel" in last_msg.lower():
            return {"current_phase": "search_hotels"}

    # Phase: HOTEL OPTIONS -> FINAL ITINERARY
    if phase == "presenting_hotels":
        if intent == "select_option" or "selected" in last_msg.lower():
            print("🚀 Moving to Final Itinerary Generation")
            return {"current_phase": "itinerary"}

    # DEFAULT FALLBACK: Stay in current phase to avoid loops
    return {"current_phase": phase}