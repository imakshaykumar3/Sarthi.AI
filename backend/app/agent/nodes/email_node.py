import re
from langchain_core.messages import AIMessage
from app.schemas.state import AgentState
from app.utility.email import send_dummy_tickets

async def send_email_node(state: AgentState):
    messages = state.get("messages", [])
    last_msg = messages[-1].content
    
    # 1. Extract email using regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', last_msg)
    
    if not email_match:
        return {
            "messages": [AIMessage(content="I didn't catch a valid email address. Could you please double-check and send it again?")], 
            "current_phase": "asking_email"
        }
    
    user_email = email_match.group(0)
    
    # 2. Gather data for the email
    itinerary = state.get("final_itinerary", {}).get("plan", "No itinerary found.")
    
    # The bill is the second-to-last message (from the AI)
    bill = messages[-2].content if len(messages) >= 2 else "Bill Details"

    print(f"📧 Sending dummy tickets to {user_email}...")
    
    # 3. Send it
    success = send_dummy_tickets(user_email, itinerary, bill)
    
    if success:
        msg = f"✅ **Whoosh!** 🧞‍♂️ I've successfully emailed your dummy tickets and final itinerary to **{user_email}**. Have a fantastic trip!"
    else:
        msg = "⚠️ I tried to send the email, but my SMTP configuration seems to be missing. Your trip is fully booked in my memory though!"

    return {
        "messages": [AIMessage(content=msg)],
        "current_phase": "completed"
    }