# app/agent/nodes/responder.py
from langchain_core.messages import AIMessage
from app.core.llms import gemini_llm
from app.schemas.state import AgentState
from app.utils import safe_dict

def response_node(state: AgentState):
    # This handles non-streaming responses (e.g. Confirmation, Hotels, Errors)
    phase = state.get("current_phase")
    search_data = state.get("search_results", "")
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")
    
    if phase == "confirm_transport":
        msg = f"Excellent choice! I've noted your selection for {dest}. Shall we look for hotels now?"
        return {"messages": [AIMessage(content=msg)]}
    
    if phase == "presenting_hotels":
        # Format hotels nicely
        prompt = f"Format these hotels into a Markdown table: {search_data}"
        response = gemini_llm.invoke(prompt)
        return {"messages": [response]}

    return {"messages": [AIMessage(content="How can I help you further?")]}