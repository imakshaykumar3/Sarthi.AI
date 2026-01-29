# app/agent/nodes/greeting.py
from app.schemas.state import AgentState
from app.utils import safe_dict, get_trip
from graph import clean_content
from langchain_core.messages import AIMessage
from app.core.llms import greeting_llm

async def greeting_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")

    prompt = f"""
        Write a highly evocative, confidence-boosting welcome message about {dest}
        that makes the reader feel proud and excited about choosing this destination.
        Limit to 2–3 sentences, high energy, vivid imagery, and emojis.
        """
    response = await greeting_llm.ainvoke(prompt)
    
    clean_text = clean_content(response.content)
    
    return {"messages": [AIMessage(content=f"GREETING_Start: {clean_text}")]}
