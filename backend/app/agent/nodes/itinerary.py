import re
from datetime import datetime
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.core.llms import gptIt_llm  # Ensure this matches your logic model in core/llms.py
from app.schemas.state import AgentState
from app.utils import safe_dict

async def itinerary_node(state: AgentState):
    """
    Generates a full-duration, arrival-aware itinerary using GPT-4o-mini.
    Calculates total days dynamically and uses '---' for frontend card splitting.
    """
    # 1. Safely extract state data
    details = safe_dict(state.get("trip_details"))
    transport = state.get("selected_transport") or {}
    
    # 2. Resolve Arrival Time for Day 1 logic
    # Falls back to "Morning" if no transport selection is found in state
    arrival_time = transport.get("arr") or transport.get("arrival_time") or "Morning"
    
    # 3. Resolve Hotel Name
    selected_hotel = state.get("selected_hotel") or details.get("selected_hotel")
    hotel_name = "your selected stay"
    if isinstance(selected_hotel, dict):
        hotel_name = selected_hotel.get("name", "your selected stay")
    
    # 4. Calculate Trip Duration (Full inclusive count)
    dest = details.get("destination", "your destination")
    start_date_str = details.get("start_date")
    end_date_str = details.get("end_date")
    
    total_days = 1 # Default
    try:
        if start_date_str and end_date_str:
            d1 = datetime.strptime(start_date_str, "%Y-%m-%d")
            d2 = datetime.strptime(end_date_str, "%Y-%m-%d")
            total_days = (d2 - d1).days + 1
            if total_days <= 0: total_days = 1
    except Exception as e:
        print(f"⚠️ Date Calculation Error: {e}")
        total_days = 3 # Fallback

    print(f"🧠 GPT-4o-mini: Generating {total_days}-day plan for {dest} (Arrival: {arrival_time})")

    # 5. Build the System Prompt
    system_prompt = f"""
    You are TravelGenie 🧞‍♂️, a premium local travel guide in {dest}. 
    The traveler is staying at: {hotel_name}.
    Arrival Time on Day 1: {arrival_time}.
    Total Trip Duration: {total_days} Days.
    
    TASK: Create a highly personalized day-by-day itinerary for exactly {total_days} days.
    
    CRITICAL INSTRUCTIONS:
    1. DAY 1 LOGIC: Since the traveler arrives at {arrival_time}, adjust Day 1. If arrival is after 12:00 PM, skip breakfast/morning treks and start with check-in and lunch/evening activities.
    2. SEPARATOR: Use '---' (three dashes) on a new line to separate EVERY single day. This is vital for the frontend.
    3. FORMATTING: 
       - Use '### 🗓️ Day X: [Theme Name]' for headers.
       - Use '🌅 **Morning**:', '☀️ **Afternoon**:', '🌙 **Evening**:', and '💡 **Pro Tip**:' for sub-sections.
    4. LOCAL INSIGHT: Mention specific local dish names (e.g., 'Thukpa', 'Recheado Fish'), restaurant names, and specific 'Hidden Gems' not found in standard brochures.
    5. No conversational filler or introductory text. Start immediately with Day 1.
    """

    user_msg = f"Generate my complete {total_days}-day journey for {dest} from {start_date_str} to {end_date_str}."

    try:
        # 6. GPT-4o-mini API Call
        response = await gptIt_llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ])
        
        content = str(response.content).strip()

        # Clean markdown wrappers if returned
        if content.startswith("```"):
            content = re.sub(r"```(markdown|json)?", "", content).strip("`").strip()

        # 7. Update state and return WITH Rental Question Trigger
        # Using an f-string for cleaner formatting
        rental_prompt = f"\n\n---\n### 🚗 Local Travel\nYour adventure is mapped out! Would you like me to find some rental cars or bikes for your local travel in {dest}?"
        
        return {
            "messages": [AIMessage(content=content + rental_prompt)], 
            "current_phase": "asking_rentals", # 👈 NEW PHASE TRIGGER
            "final_itinerary": {"plan": content} 
        }
        
    except Exception as e:
        print(f"❌ Itinerary Generation Error: {e}")
        error_fallback = f"### 🗓️ Day 1: Welcome to {dest}\nI encountered an error generating your full {total_days}-day plan. Please try selecting your stay again or ask for a specific day."
        
        # Kept the phase as 'completed' here so it doesn't ask for rentals if the itinerary failed
        return {
            "messages": [AIMessage(content=error_fallback)],
            "current_phase": "completed",
            "final_itinerary": {"plan": error_fallback}
        }