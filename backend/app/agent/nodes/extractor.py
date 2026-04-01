from datetime import datetime
from langchain_core.messages import HumanMessage
from app.schemas.state import AgentState
from app.core.llms import gpt_llm
from app.utils import safe_dict, get_last_user_message, extract_json_from_text

def extraction_node(state: AgentState):
    existing_details = safe_dict(state.get("trip_details"))
    messages = state.get("messages", [])
    last_message_content = get_last_user_message(messages)

    if not last_message_content.strip(): 
        return {}

    # --- 🚨 CRITICAL FIX: SKIP EXTRACTION FOR SELECTIONS ---
    # If the user is selecting an option or asking for the final itinerary,
    # we do NOT want to overwrite the source/destination/dates.
    stop_keywords = ["selected stay", "select option", "finalize my stay", "itinerary"]
    if any(k in last_message_content.lower() for k in stop_keywords):
        print("⏭️ Extractor: Skipping (Selection Message detected)")
        return {}

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
        You are a DATA PARSER. TODAY: {today}
        User Input: "{last_message_content}"
        Current Data: {existing_details}
        
        Task:
        1. Extract travel details (Source, Destination, Start Date, End Date).
        2. If the user is CHANGING a value (e.g. "Actually go to Paris"), OVERWRITE the old value.
        3. Keep existing values if not mentioned.
        4. If the input is just a confirmation (e.g. "Yes", "Proceed") or a selection, return an empty JSON.
        
        RETURN JSON ONLY: {{ "source": "...", "destination": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }}
    """
    
    try:
        response = gpt_llm.invoke([HumanMessage(content=prompt)])
        
        # Clean the response string
        raw_content = str(response.content)
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        
        new_data = extract_json_from_text(clean_json)
        
        # Filter out empty or null values
        valid_new_data = {k: v for k, v in new_data.items() if v and str(v).strip() and v != "..."}
        
        if valid_new_data:
            print(f"✅ Extracted/Updated: {valid_new_data}")
            # Merge new data with existing stable memory
            return {"trip_details": {**existing_details, **valid_new_data}}
            
    except Exception as e:
        print(f"⚠️ Extraction Error: {e}")
        
    return {}