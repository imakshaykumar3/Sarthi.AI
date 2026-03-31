import json
from langchain_core.messages import AIMessage
from app.core.llms import gemini_llm
from app.schemas.state import AgentState
from app.utils import safe_dict
from app.schemas.api import HotelListSchema 
from app.utility.images import get_hotel_image

# Force the model to follow the Pydantic schema strictly
structured_llm = gemini_llm.with_structured_output(HotelListSchema)

async def response_node(state: AgentState):
    """
    Consolidated Responder Node:
    Handles confirmation, hotel searching with sorting, and image enrichment.
    """
    phase = state.get("current_phase")
    search_data = state.get("search_results", "")
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")

    # --- Phase: Confirming Transport ---
    if phase == "confirm_transport":
        msg = f"Excellent choice! I've noted your selection for {dest}. Shall we look for hotels now?"
        return {"messages": [AIMessage(content=msg)]}

    # --- Phase: Presenting Hotels (Structured + Images) ---
    if phase == "presenting_hotels":
        if not search_data or len(str(search_data)) < 20:
            msg = f"I found some mentions of stays in {dest}, but I couldn't get clear pricing. Should I try another search?"
            return {"messages": [AIMessage(content=msg)]}
            
        prompt = f"""
        Extract the 5 best stay options for {dest} from the search data.
        Convert all prices to INR (1 USD = 86 INR).

        排序 (SORTING ORDER):
        1. List all "Private Room" or "Luxury Suite" options FIRST.
        2. List all "Hostel Bed" options LAST.

        🧠 CLASSIFICATION LOGIC:
        1. If Price < ₹1,000: Classify as "Hostel Bed".
        2. If Price ₹1,000 - ₹5,000: Classify as "Private Room".
        3. If Price > ₹5,000: Classify as "Luxury Suite".
        
        ⚠️ PRICE CORRECTION:
        - Ensure Private Rooms are at least ₹1,200.
        
        SEARCH DATA:
        {search_data}
        """
        
        try:
            # 1. Get structured data from LLM
            structured_data = structured_llm.invoke(prompt)
            raw_hotels = [hotel.model_dump() for hotel in structured_data.hotels]

            # 2. ✅ ENRICHMENT: Fetch real images via Unsplash (Backend-to-Backend)
            enriched_hotels = []
            for hotel in raw_hotels:
                # We use await here because get_hotel_image is an async function
                img_url = await get_hotel_image(hotel['name'], hotel['location'])
                hotel['image_url'] = img_url
                enriched_hotels.append(hotel)

            # 3. Format the final payload for the Frontend
            payload = {
                "hotels_section": {
                    "data": enriched_hotels
                }
            }
            
            return {"messages": [AIMessage(content=json.dumps(payload))]}
            
        except Exception as e:
            print(f"❌ Responder Error: {e}")
            fallback_msg = f"I found some great hotels in {dest}, but I'm having trouble displaying them right now. Would you like me to try again?"
            return {"messages": [AIMessage(content=fallback_msg)]}

    # --- Default Fallback ---
    return {"messages": [AIMessage(content="I'm here to help! What's our next move?")]}