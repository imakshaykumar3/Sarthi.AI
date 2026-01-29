#app/agent/nodes/extractor.py
from datetime import datetime
from langchain_core.messages import HumanMessage
from app.schemas.state import AgentState
from app.core.llms import gpt_llm
from app.utils import safe_dict, get_last_user_message, extract_json_from_text

def extraction_node(state: AgentState):
    existing_details = safe_dict(state.get("trip_details"))
    messages = state.get("messages", [])
    last_message_content = get_last_user_message(messages)

    if not last_message_content.strip(): return {}

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
        You are a DATA PARSER. TODAY: {today}
        User Input: "{last_message_content}"
        Current Data: {existing_details}
        
        Task:
        1. Extract travel details (Source, Destination, Start Date, End Date).
        2. If the user is CHANGING a value (e.g. "Actually go to Paris"), OVERWRITE the old value.
        3. Keep existing values if not mentioned.
        
        RETURN JSON ONLY: {{ "source": "...", "destination": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }}
    """
    
    try:
        response = gpt_llm.invoke([HumanMessage(content=prompt)])
        clean_json = str(response.content).replace("```json", "").replace("```", "").strip()
        new_data = extract_json_from_text(clean_json)
        
        valid_new_data = {k: v for k, v in new_data.items() if v and str(v).strip()}
        
        if valid_new_data:
            print(f"✅ Extracted/Updated: {valid_new_data}")
            return {"trip_details": {**existing_details, **valid_new_data}}
            
    except Exception as e:
        print(f"⚠️ Extraction Error: {e}")
        
    return {}