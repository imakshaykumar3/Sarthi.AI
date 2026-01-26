# # backend/graph.py
# import json
# import re
# from typing import Literal, Optional, Dict, Any, List
# from datetime import datetime, timedelta

# from langgraph.graph import StateGraph, END
# from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
# from langchain_core.runnables import RunnableConfig 
# from sqlalchemy.future import select

# # --- Project Imports ---
# from llms import gpt_llm, gemini_llm
# from state import AgentState
# from tools import search_flights, search_trains, search_hotels
# from prompts import MASTER_SYSTEM_PROMPT
# from database import SessionLocal
# from models import Trip

# # =========================================================
# # 🔹 HELPER FUNCTIONS (Keep as is)
# # =========================================================
# def safe_dict(val: Any) -> Dict[str, Any]:
#     if isinstance(val, dict): return val
#     return {}

# def get_trip(details: Any, key: str) -> Optional[str]:
#     d = safe_dict(details)
#     return d.get(key)

# def trim_messages(messages: List[Any], keep: int = 2) -> List[Any]:
#     if not messages: return []
#     return messages[-keep:]

# def get_last_user_message(messages: List[Any]) -> str:
#     if not messages: return ""
#     last_msg = messages[-1]
#     if hasattr(last_msg, "content"): return str(last_msg.content)
#     if isinstance(last_msg, dict): return str(last_msg.get("content", ""))
#     return str(last_msg)

# def extract_json_from_text(text: str) -> Dict[str, Any]:
#     try:
#         return json.loads(text)
#     except:
#         match = re.search(r"\{.*\}", text, re.DOTALL)
#         if match:
#             try: return json.loads(match.group(0))
#             except: pass
#     return {}

# # =========================================================
# # 1️⃣ EXTRACTION NODE 
# # =========================================================
# def extraction_node(state: AgentState):
#     existing_details = safe_dict(state.get("trip_details"))
#     messages = state.get("messages", [])
#     last_message_content = get_last_user_message(messages).lower()

#     if any(k in last_message_content for k in ["select", "choose", "book", "lock", "option selected", "confirm"]):
#         print("⏭️ User is selecting an option. Skipping extraction.")
#         return {} 

#     if (existing_details.get("source") and 
#         existing_details.get("destination") and 
#         existing_details.get("start_date")):
#         return {} 

#     if not last_message_content.strip(): return {}

#     today = datetime.now().strftime("%Y-%m-%d")
#     prompt = f"""
#         You are a DATA PARSER. TODAY: {today}
#         Extract missing travel details from: "{last_message_content}"
#         Current Data: {existing_details}
#         RETURN JSON ONLY: {{ "source": "...", "destination": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }}
#     """
#     try:
#         response = gpt_llm.invoke([HumanMessage(content=prompt)])
#         clean_json = str(response.content).replace("```json", "").replace("```", "").strip()
#         new_data = extract_json_from_text(clean_json)
#         valid_new_data = {k: v for k, v in new_data.items() if v and str(v).strip()}
#         if valid_new_data:
#             print(f"✅ Extracted: {valid_new_data}")
#             return {"trip_details": {**existing_details, **valid_new_data}}
#     except Exception as e:
#         print(f"⚠️ Extraction Error: {e}")
#     return {}

# # =========================================================
# # 2️⃣ PLANNER NODE 
# # =========================================================
# def planner_node(state: AgentState):
#     phase = state.get("current_phase", "gathering_info")
#     last_msg = get_last_user_message(state.get("messages", [])).lower()
#     details = safe_dict(state.get("trip_details"))
    
#     print(f"🧠 PLANNER: Current Phase '{phase}' | User said: '{last_msg}'")

#     is_selection = any(k in last_msg for k in ["select", "book", "lock", "choose", "reserve", "confirm"])

#     if phase == "presenting_options" and is_selection:
#         print("✅ TRANSITION: Options -> Confirm Transport")
#         return {"current_phase": "confirm_transport"}

#     if phase == "confirm_transport":
#         print("✅ TRANSITION: Confirm -> Search Hotels")
#         return {"current_phase": "search_hotels"}

#     if phase == "presenting_hotels" and is_selection:
#         print("✅ TRANSITION: Hotels -> Itinerary")
#         return {"current_phase": "itinerary"}

#     if phase == "gathering_info":
#         if (details.get("source") and details.get("destination") and details.get("start_date")):
#             return {"current_phase": "ready_to_search"}

#     return {"current_phase": phase}

# # =========================================================
# # 3️⃣ TOOL NODE
# # =========================================================
# def tool_execution_node(state: AgentState):
#     phase = state.get("current_phase")
#     details = safe_dict(state.get("trip_details"))

#     if phase == "ready_to_search":
#         src = get_trip(details, "source")
#         dst = get_trip(details, "destination")
#         date = get_trip(details, "start_date")
#         print(f"🔎 Running Search Tools for {src} to {dst} on {date}...")
#         try:
#             flights = search_flights.invoke({"source": src, "destination": dst, "date": date})
#         except Exception as e:
#             flights = f"Flight Search Error: {e}"
#         try:
#             trains = search_trains.invoke({"source": src, "destination": dst, "date": date})
#         except Exception as e:
#             trains = f"Train Search Error: {e}"
#         return {
#             "search_results": f"FLIGHTS_DATA:\n{flights}\n\nTRAINS_DATA:\n{trains}",
#             "current_phase": "presenting_options" 
#         }

#     if phase == "search_hotels":
#         dst = get_trip(details, "destination")
#         date = get_trip(details, "start_date")
#         print(f"🏨 Searching Hotels in {dst}...")
#         raw_hotels = search_hotels.invoke({"location": dst, "check_in": date})
#         return {
#             "search_results": raw_hotels,
#             "current_phase": "presenting_hotels"
#         }
#     return {}

# # =========================================================
# # 4️⃣ CONFIRM NODE
# # =========================================================
# def confirm_transport_node(state: AgentState):
#     return {"current_phase": "confirm_transport"}

# # =========================================================
# # 5️⃣ RESPONSE NODE (🚨 THE FIX)
# # =========================================================
# def response_node(state: AgentState):
#     phase = state.get("current_phase", "gathering_info")
#     search_data = state.get("search_results", "")
#     last_msg = get_last_user_message(state.get("messages", [])).lower()
    
#     # 🚨 SELF-CORRECTION: If user says "select", FORCE confirmation logic
#     if any(k in last_msg for k in ["select", "book", "lock", "choose", "confirm", "option selected"]):
#         if phase == "presenting_options":
#             phase = "confirm_transport" # Override phase locally
    
#     details = safe_dict(state.get("trip_details"))
#     user_trip_date = get_trip(details, "start_date") or "Unknown Date"
#     dest = get_trip(details, "destination") or "your destination"

#     instructions = MASTER_SYSTEM_PROMPT.replace("__PHASE__", phase)
#     instructions += f"\n\n🚨 CONTEXT: User is traveling to {dest} on {user_trip_date}."

#     # --- LOGIC PER PHASE ---
    
#     if phase == "presenting_options":
#         # Strict JSON for Options
#         instructions += f"\n\n🚨 RAW FLIGHT/TRAIN DATA:\n{search_data}"
#         instructions += f"""
#         \n\n⚠️ **STRICT OUTPUT RULES:**
#         1. **JSON ONLY**: You MUST return **ONLY VALID JSON**. No Markdown tables.
#         2. **GREETING**: Include a warm greeting: "Welcome to {dest}! 🏔️ I've found options for {user_trip_date}."
#         3. **STRUCTURE**: {{ "greeting": "...", "flights_section": {{...}}, "trains_section": {{...}} }}
#         """
        
#     elif phase == "confirm_transport":
#         instructions += f"\n\n🚨 RAW FLIGHT/TRAIN DATA (Reference this for confirmation details):\n{search_data}"
        
#         instructions += f"""
#         \n\n🚨 **TASK: CONFIRM SELECTION WITH DETAILS**
#         The user has selected a specific flight or train.
#         1. **IDENTIFY**: Find the selected option in the raw data above based on the user's message.
#         2. **CONFIRM**: Reply with a confirmation that includes:
#            - The Transport Name (e.g. Indigo, Rajdhani Express)
#            - Departure Time & Date
#            - Arrival Time
#            - "Excellent choice! Your [Transport] departs at [Time] on {user_trip_date}..."
#         3. **NEXT STEP**: Ask if they want to proceed to finding hotels in {dest}.
#         """

#     elif phase == "presenting_hotels":
#         instructions += f"\n\n🚨 RAW HOTEL DATA:\n{search_data}"

#     try:
#         user_msg_content = "Generate response."
#         response = gemini_llm.invoke([
#             SystemMessage(content=instructions),
#             HumanMessage(content=user_msg_content)
#         ])
    
#         content = response.content
        
#         if isinstance(content, list):
#             extracted_text = []
#             for item in content:
#                 if isinstance(item, dict): extracted_text.append(item.get("text", ""))
#                 elif hasattr(item, "text"): extracted_text.append(item.text)
#                 elif isinstance(item, str): extracted_text.append(item)
#             content = "".join(extracted_text)
            
#         content = str(content).strip()

#         # Clean up Markdown if JSON
#         if content.startswith("```json"):
#             content = content.replace("```json", "").replace("```", "")
        
#         return {"messages": [AIMessage(content=content)]}
        
#     except Exception as e:
#         print(f"❌ LLM GENERATION ERROR: {e}") 
#         return {"messages": [AIMessage(content="I'm having trouble connecting to the AI brain right now. Please try again.")]}

# # =========================================================
# # 6️⃣ SAVE NODE
# # =========================================================
# async def save_itinerary_node(state: AgentState, config: RunnableConfig):
#     return {}

# # =========================================================
# # 7️⃣ ROUTING
# # =========================================================
# workflow = StateGraph(AgentState)

# workflow.add_node("extractor", extraction_node)
# workflow.add_node("planner", planner_node)
# workflow.add_node("tools", tool_execution_node)
# workflow.add_node("confirm", confirm_transport_node)
# workflow.add_node("responder", response_node)
# workflow.add_node("saver", save_itinerary_node)

# workflow.set_entry_point("extractor")

# workflow.add_edge("extractor", "planner")
# workflow.add_edge("tools", "responder")
# workflow.add_edge("confirm", "responder")

# def route_from_planner(state: AgentState):
#     phase = state.get("current_phase", "gathering_info")
#     if phase == "ready_to_search": return "tools"
#     if phase == "search_hotels": return "tools" 
#     if phase == "confirm_transport": return "confirm"
#     return "responder"

# workflow.add_conditional_edges("planner", route_from_planner)
# workflow.add_edge("responder", END)
# workflow.add_edge("saver", END)

# backend/graph.py

import json
import re
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime, timedelta

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig 
from sqlalchemy.future import select

# --- Project Imports ---
from llms import gpt_llm, gemini_llm
from state import AgentState
from tools import search_flights, search_trains, search_hotels
from prompts import MASTER_SYSTEM_PROMPT
from database import SessionLocal
from models import Trip

# =========================================================
# 🔹 HELPER FUNCTIONS
# =========================================================

def safe_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict): return val
    return {}

def get_trip(details: Any, key: str) -> Optional[str]:
    d = safe_dict(details)
    return d.get(key)

def trim_messages(messages: List[Any], keep: int = 2) -> List[Any]:
    if not messages: return []
    return messages[-keep:]

def get_last_user_message(messages: List[Any]) -> str:
    if not messages: return ""
    last_msg = messages[-1]
    if hasattr(last_msg, "content"): return str(last_msg.content)
    if isinstance(last_msg, dict): return str(last_msg.get("content", ""))
    return str(last_msg)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except: pass
    return {}

# =========================================================
# 1️⃣ EXTRACTION NODE (Guard Clause Logic)
# =========================================================
def extraction_node(state: AgentState):
    """
    Extracts details ONLY if they are missing.
    """
    existing_details = safe_dict(state.get("trip_details"))
    messages = state.get("messages", [])
    last_message_content = get_last_user_message(messages).lower() # Convert to lower for easier matching

    # 🚨 FIX 1: Stronger Guard Clause for Selection
    if any(k in last_message_content for k in ["select", "choose", "book", "lock", "option selected", "confirm", "reserve"]):
        print("⏭️ User is selecting an option. Skipping extraction.")
        return {} 

    if (existing_details.get("source") and 
        existing_details.get("destination") and 
        existing_details.get("start_date")):
        return {} 

    if not last_message_content.strip(): return {}

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
        You are a DATA PARSER. TODAY: {today}
        Extract missing travel details from: "{last_message_content}"
        Current Data: {existing_details}
        RETURN JSON ONLY: {{ "source": "...", "destination": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }}
    """
    
    try:
        response = gpt_llm.invoke([HumanMessage(content=prompt)])
        clean_json = str(response.content).replace("```json", "").replace("```", "").strip()
        new_data = extract_json_from_text(clean_json)
        
        valid_new_data = {k: v for k, v in new_data.items() if v and str(v).strip()}
        
        if valid_new_data:
            print(f"✅ Extracted: {valid_new_data}")
            return {"trip_details": {**existing_details, **valid_new_data}}
            
    except Exception as e:
        print(f"⚠️ Extraction Error: {e}")
        
    return {}

# =========================================================
# 2️⃣ PLANNER NODE (The Decision Maker)
# =========================================================
def planner_node(state: AgentState):
    # Normalize phase to ensure string matching works
    phase = str(state.get("current_phase", "gathering_info")).strip()
    
    last_msg = get_last_user_message(state.get("messages", [])).lower()
    details = safe_dict(state.get("trip_details"))
    
    print(f"🧠 PLANNER: Phase='{phase}' | User='{last_msg}'")

    # 🚨 FIX 3: AGGRESSIVE SELECTION DETECTION
    is_selection = any(k in last_msg for k in ["select", "book", "lock", "choose", "reserve", "confirm"])

    # --- TRANSITION LOGIC ---

    # 1. From Options -> Confirm
    if phase == "presenting_options" and is_selection:
        print("✅ TRANSITION: Options -> Confirm Transport")
        return {"current_phase": "confirm_transport"}

    # 2. From Confirm -> Hotels
    if phase == "confirm_transport":
        print("✅ TRANSITION: Confirm -> Search Hotels")
        return {"current_phase": "search_hotels"}

    # 3. From Hotels -> Itinerary
    if phase == "presenting_hotels" and is_selection:
        print("✅ TRANSITION: Hotels -> Itinerary")
        return {"current_phase": "itinerary"}

    # 4. Auto-Start (Gathering -> Search)
    if phase == "gathering_info":
        if (details.get("source") and details.get("destination") and details.get("start_date")):
            return {"current_phase": "ready_to_search"}

    # Default: No change
    return {"current_phase": phase}


# =========================================================
# 3️⃣ TOOL NODE (Search Execution)
# =========================================================
def tool_execution_node(state: AgentState):
    phase = state.get("current_phase")
    details = safe_dict(state.get("trip_details"))

    # Only run tools if we are in a 'search' phase
    if phase == "ready_to_search":
        src = get_trip(details, "source")
        dst = get_trip(details, "destination")
        date = get_trip(details, "start_date")

        print(f"🔎 Running Search Tools for {src} to {dst} on {date}...")
        try:
            flights = search_flights.invoke({"source": src, "destination": dst, "date": date})
        except Exception as e:
            flights = f"Flight Search Error: {e}"

        try:
            trains = search_trains.invoke({"source": src, "destination": dst, "date": date})
        except Exception as e:
            trains = f"Train Search Error: {e}"

        return {
            "search_results": f"FLIGHTS_DATA:\n{flights}\n\nTRAINS_DATA:\n{trains}",
            "current_phase": "presenting_options" # Force Move to Presentation
        }

    if phase == "search_hotels":
        dst = get_trip(details, "destination")
        date = get_trip(details, "start_date")
        print(f"🏨 Searching Hotels in {dst}...")
        raw_hotels = search_hotels.invoke({"location": dst, "check_in": date})
        return {
            "search_results": raw_hotels,
            "current_phase": "presenting_hotels" # Force Move to Presentation
        }

    return {}

# =========================================================
# 4️⃣ CONFIRM NODE
# =========================================================
def confirm_transport_node(state: AgentState):
    # This node just acts as a passthrough or specific logic holder
    return {"current_phase": "confirm_transport"}


# =========================================================
# 5️⃣ RESPONSE NODE (The Voice)
# =========================================================
def response_node(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    search_data = state.get("search_results", "")
    last_msg = get_last_user_message(state.get("messages", [])).lower()
    
    if phase == "presenting_options" and any(k in last_msg for k in ["select", "book", "choose", "confirm"]):
        print("⚠️ RESPONSE NODE: Forcing 'confirm_transport' logic override.")
        phase = "confirm_transport"

    details = safe_dict(state.get("trip_details"))
    user_trip_date = get_trip(details, "start_date") or "Unknown Date"
    dest = get_trip(details, "destination") or "your destination"

    instructions = MASTER_SYSTEM_PROMPT.replace("__PHASE__", phase)
    instructions += f"\n\n🚨 CONTEXT: User is traveling to {dest} on {user_trip_date}."

    # --- LOGIC PER PHASE ---
    if phase == "presenting_options":
        # Strict JSON for Options
        instructions += f"\n\n🚨 RAW FLIGHT/TRAIN DATA:\n{search_data}"
        instructions += f"""
        \n\n⚠️ **STRICT OUTPUT RULES:**
        1. **JSON ONLY**: You MUST return **ONLY VALID JSON**. No Markdown tables.
        2. **GREETING**: The 'greeting' field MUST be a short, engaging welcome message that **appreciates the specific beauty or vibe of {dest}**.
           - Example: "The misty hills of Darjeeling are calling! 🏔️ I've found some excellent travel options for your journey on {user_trip_date}."
           - Make it sound like a travel consultant, not a robot.
        3. **STRUCTURE**: {{ "greeting": "...", "flights_section": {{...}}, "trains_section": {{...}} }}
        """
        
    elif phase == "confirm_transport":
        # 🚨 CONFIRMATION LOGIC
        instructions += f"\n\n🚨 RAW FLIGHT/TRAIN DATA (Reference this to find details):\n{search_data}"
        instructions += f"""
        \n\n🚨 **TASK: ACKNOWLEDGE SELECTION (NO BOOKING YET)**
        The user has selected a specific flight or train (User said: "{last_msg}").
        
        1. **TONE**: You are a consultant, NOT a booking engine. 
           - **DO NOT** say "I have confirmed your booking" or "Ticket reserved". Payment hasn't happened.
           - **INSTEAD SAY**: "Excellent choice," "That is a great option," or "I've noted that down."

        2. **DETAILS (MANDATORY FORMAT)**:
           You MUST explicitly mention the dates in the Departure/Arrival lines.
           - **Departure**: [Time] from [Station/Airport] on {user_trip_date}
           - **Arrival**: [Time] at [Station/Airport] on [Calculate Date: If raw data says "Next Day" or "Day 2", add 1 day to {user_trip_date}]

        3. **NEXT STEP**: Ask: "Shall I now proceed to find the best budget-friendly hotels in {dest}?"
        4. **NO JSON**: Do NOT output JSON here. Just text.
        """

    elif phase == "presenting_hotels":
        instructions += f"\n\n🚨 RAW HOTEL DATA:\n{search_data}"

    try:
        user_msg_content = "Generate response."
        response = gemini_llm.invoke([
            SystemMessage(content=instructions),
            HumanMessage(content=user_msg_content)
        ])
    
        content = response.content
        
        # Helper to join list responses
        if isinstance(content, list):
            extracted_text = []
            for item in content:
                if isinstance(item, dict): extracted_text.append(item.get("text", ""))
                elif hasattr(item, "text"): extracted_text.append(item.text)
                elif isinstance(item, str): extracted_text.append(item)
            content = "".join(extracted_text)
            
        content = str(content).strip()

        # Clean up Markdown if JSON
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        return {"messages": [AIMessage(content=content)]}
        
    except Exception as e:
        print(f"❌ LLM GENERATION ERROR: {e}") 
        return {"messages": [AIMessage(content="I'm having trouble connecting to the AI brain right now. Please try again.")]}

# =========================================================
# 6️⃣ SAVE NODE
# =========================================================
async def save_itinerary_node(state: AgentState, config: RunnableConfig):
    return {}

# =========================================================
# 7️⃣ ROUTING
# =========================================================
workflow = StateGraph(AgentState)

workflow.add_node("extractor", extraction_node)
workflow.add_node("planner", planner_node)
workflow.add_node("tools", tool_execution_node)
workflow.add_node("confirm", confirm_transport_node)
workflow.add_node("responder", response_node)
workflow.add_node("saver", save_itinerary_node)

workflow.set_entry_point("extractor")

workflow.add_edge("extractor", "planner")
workflow.add_edge("tools", "responder")
workflow.add_edge("confirm", "responder")

def route_from_planner(state: AgentState):
    # Normalize phase string
    phase = str(state.get("current_phase", "gathering_info")).strip()
    
    if phase == "ready_to_search": return "tools"
    if phase == "search_hotels": return "tools" 
    if phase == "confirm_transport": return "confirm"
    return "responder"

workflow.add_conditional_edges("planner", route_from_planner)
workflow.add_edge("responder", END)
workflow.add_edge("saver", END)