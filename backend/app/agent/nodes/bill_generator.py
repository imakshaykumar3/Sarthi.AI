# backend/app/agent/nodes/bill_generator.py
from langchain_core.messages import AIMessage, SystemMessage
from datetime import datetime
from app.core.llms import gptIt_llm
from app.schemas.state import AgentState
from app.utils import safe_dict

async def generate_bill_node(state: AgentState):
    messages = state.get("messages", [])
    details = safe_dict(state.get("trip_details"))
    travelers = int(details.get("travelers", 1) or 1)

    # Calculate trip duration to estimate hotel and food costs
    try:
        d1 = datetime.strptime(details.get("start_date"), "%Y-%m-%d")
        d2 = datetime.strptime(details.get("end_date"), "%Y-%m-%d")
        days = (d2 - d1).days + 1
        if days <= 0: days = 1
    except:
        days = 3 # Fallback

    sys_prompt = f"""
        You are TravelGenie's expert travel accountant. 
        Review the conversation history and generate a comprehensive final bill.

        Extract the chosen options and prices for:
        1. Forward Transport (Flight/Train)
        2. Stay/Hotel (Assume the price shown is per night. Multiply by {days} nights)
        3. Local Rental (Assume the price shown is per day. Multiply by {days} days)
        4. Return Transport (Flight/Train)

        MATH RULES:
        - Travelers: {travelers}. (Multiply all transport costs by this number).
        - Food & Extra Activities: Estimate ₹1,500 per person, per day ({travelers} travelers * {days} days * 1500).

        OUTPUT FORMAT:
        - Start with the header: '### 🧾 Your Final Trip Summary & Bill'
        - Use a clean Markdown table with columns: 'Category', 'Details', and 'Total Cost (₹)'
        - Prominently display the **Grand Total** below the table.
        - End with a warm closing message.
        - Do NOT output raw JSON. Output only the beautifully formatted Markdown.
    """

    try:
        print("🧾 Generating Final Bill...")
        # We pass the system prompt and the last 15 messages so it has context of all selections
        response = await gptIt_llm.ainvoke([SystemMessage(content=sys_prompt)] + messages[-15:])
        
        # 👇 UPDATED RETURN BLOCK
        return {
            "messages": [AIMessage(content=response.content + "\n\n---\n**Would you like me to email these dummy tickets and your itinerary to you?** Just reply with your email address!")],
            "current_phase": "asking_email" # 👈 Stops the graph to wait for user input
        }
    except Exception as e:
        print(f"❌ Bill Gen Error: {e}")
        # Ensure the fallback also asks for the email so the flow doesn't break
        fallback_msg = (
            "### 🧾 Your Final Trip Summary\n"
            "I encountered an error calculating the final math, but your trip is completely booked and saved!\n\n"
            "---\n**Would you like me to email these dummy tickets and your itinerary to you?** Just reply with your email address!"
        )
        return {
            "messages": [AIMessage(content=fallback_msg)],
            "current_phase": "asking_email"
        }