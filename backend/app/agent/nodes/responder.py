import json
from langchain_core.messages import AIMessage
from app.core.llms import gemini_llm
from app.schemas.state import AgentState
from app.utils import safe_dict
from app.schemas.api import HotelListSchema 

# ✅ Initialize structured LLM once for strict Pydantic compliance
structured_llm = gemini_llm.with_structured_output(HotelListSchema)

def response_node(state: AgentState):
    phase = state.get("current_phase")
    search_data = state.get("search_results", "")
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")

    # --- Phase 1: Confirming Transport ---
    if phase == "confirm_transport":
        msg = f"Excellent choice! I've noted your selection for {dest}. Shall we look for hotels now?"
        return {"messages": [AIMessage(content=msg)]}

    # --- Phase 2: Presenting Hotels (Structured & Sorted) ---
    if phase == "presenting_hotels":
        # Check if search_data exists and isn't a short error message
        if not search_data or len(str(search_data)) < 20:
            msg = f"I found some mentions of stays in {dest}, but I couldn't get clear pricing. Should I try another search?"
            return {"messages": [AIMessage(content=msg)]}
            
        # Unified Prompt with Sorting, Classification, and Price Guardrails
        prompt = f"""
        Extract the 5 best stay options for {dest} from the following search data.
        Convert all prices to INR (1 USD = 86 INR) and provide them as integers.

        排序 (SORTING ORDER - CRITICAL):
        1. List all "Private Room", "Luxury Suite", or "Entire Home" options FIRST.
        2. List all "Hostel Bed" options LAST.
        User experience goal: Show standard hotels before budget hostels.

        🧠 CLASSIFICATION LOGIC:
        1. If Price < ₹1,000: Classify as "Hostel Bed".
        2. If Price ₹1,000 - ₹5,000: Classify as "Private Room".
        3. If Price > ₹5,000: Classify as "Luxury Suite".
        
        ⚠️ PRICE CORRECTION:
        - If a result is a Private Room/Hotel, ensure the price is at least ₹1,200.
        - If it's a Hostel Bed, prices between ₹200-₹800 are acceptable.
        - If a "Luxury Hotel" is listed at ₹300, correct it to a realistic minimum of ₹3,500.

        SEARCH DATA:
        {search_data}
        """
        
        try:
            # Invoke the LLM to get structured Pydantic output
            structured_data = structured_llm.invoke(prompt)
            
            # Convert Pydantic objects to a list of dictionaries for JSON serialization
            hotel_list = [hotel.model_dump() for hotel in structured_data.hotels]

            # Wrap in the payload format the Frontend MessageBubble expects
            payload = {
                "hotels_section": {
                    "data": hotel_list
                }
            }
            
            return {"messages": [AIMessage(content=json.dumps(payload))]}
            
        except Exception as e:
            print(f"❌ Structured Output Error: {e}")
            fallback_msg = f"I found some great hotels in {dest}, but I'm having trouble displaying them right now. Would you like me to try again?"
            return {"messages": [AIMessage(content=fallback_msg)]}

    # --- Default Fallback ---
    return {"messages": [AIMessage(content="I'm here to help! What's our next move?")]}