#graph.py
import json
import re
import asyncio
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
from schemas import UserIntent

# =========================================================
# 🔹 HELPER FUNCTIONS
# =========================================================

def clean_content(content):
    if isinstance(content, list):
        # Join all text parts if it's a list
        return " ".join([c.get("text", "") for c in content if "text" in c])
    return str(content)

def safe_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict): return val
    return {}

def get_trip(details: Any, key: str) -> Optional[str]:
    d = safe_dict(details)
    return d.get(key)

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
# 1️⃣ EXTRACTION NODE 
# =========================================================
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

# # =========================================================
# # 2️⃣ PLANNER NODE (Semantic Router)
# # =========================================================
# router_llm = gpt_llm.with_structured_output(UserIntent)

# def planner_node(state: AgentState):
#     phase = state.get("current_phase", "gathering_info")
#     messages = state.get("messages", [])
#     last_msg = get_last_user_message(messages)
#     details = safe_dict(state.get("trip_details"))
    
#     print(f"🧠 PLANNER (INTENT): Phase='{phase}' | User='{last_msg}'")

#     system_instruction = f"""
#     You are a Router for a Travel Agent.
#     Current Conversation Phase: {phase}
#     Definitions:
#     - select_option: User is picking a specific flight, train, or hotel.
#     - modify_search: User changes dates, location, or budget.
#     - confirm_proceed: User agrees to move to the next step (e.g., "Yes, find hotels", "Proceed").
#     - ask_question: User asks about baggage, weather, or details.
#     """
    
#     try:
#         intent_result = router_llm.invoke([
#             SystemMessage(content=system_instruction),
#             HumanMessage(content=last_msg)
#         ])
#         intent = intent_result.category
#         print(f"🧭 ROUTER DECISION: {intent}")
#     except Exception:
#         intent = "general_chitchat"

#     # --- TRANSITIONS ---
#     if intent == "modify_search":
#         return {"current_phase": "ready_to_search"}

#     if phase == "presenting_options":
#         if intent == "select_option": return {"current_phase": "confirm_transport"}
#         if intent == "ask_question": return {"current_phase": "presenting_options"}

#     if phase == "confirm_transport":
#         if intent == "confirm_proceed" or "hotels" in last_msg.lower():
#             return {"current_phase": "search_hotels"}

#     if phase == "presenting_hotels":
#         if intent == "select_option": return {"current_phase": "itinerary"}

#     if phase == "gathering_info":
#         if (details.get("source") and details.get("destination") and details.get("start_date")):
#             if intent != "ask_question":
#                 return {"current_phase": "ready_to_search"}

#     return {"current_phase": phase}

# =========================================================
# 2️⃣ PLANNER NODE (Semantic Router)
# =========================================================
router_llm = gpt_llm.with_structured_output(UserIntent)

def planner_node(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    messages = state.get("messages", [])
    last_msg = get_last_user_message(messages)
    details = safe_dict(state.get("trip_details"))
    
    print(f"🧠 PLANNER (INTENT): Phase='{phase}' | User='{last_msg}'")

    system_instruction = f"""
    You are a Router for a Travel Agent.
    Current Conversation Phase: {phase}
    Definitions:
    - select_option: User is picking a specific flight, train, or hotel.
    - modify_search: User changes dates, location, or budget.
    - confirm_proceed: User agrees to move to the next step (e.g., "Yes, find hotels", "Proceed").
    - ask_question: User asks about baggage, weather, or details.
    """
    
    try:
        intent_result = router_llm.invoke(
            [
                SystemMessage(content=system_instruction),
                HumanMessage(content=last_msg)
            ],
            config={"callbacks": []} 
        )
        intent = intent_result.category
        print(f"🧭 ROUTER DECISION: {intent}")
    except Exception as e:
        print(f"⚠️ Router Error: {e}")
        intent = "general_chitchat"

    # --- TRANSITIONS ---
    if intent == "modify_search":
        return {"current_phase": "ready_to_search"}

    if phase == "presenting_options":
        if intent == "select_option": return {"current_phase": "confirm_transport"}
        if intent == "ask_question": return {"current_phase": "presenting_options"}

    if phase == "confirm_transport":
        if intent == "confirm_proceed" or "hotels" in last_msg.lower():
            return {"current_phase": "search_hotels"}

    if phase == "presenting_hotels":
        if intent == "select_option": return {"current_phase": "itinerary"}

    if phase == "gathering_info":
        if (details.get("source") and details.get("destination") and details.get("start_date")):
            if intent != "ask_question":
                return {"current_phase": "ready_to_search"}

    return {"current_phase": phase}

# =========================================================
# 3️⃣ STREAMING PIPELINE NODES (The New Architecture)
# =========================================================

# A. GREETING NODE (Runs first, fast)
# async def greeting_node(state: AgentState):
#     details = safe_dict(state.get("trip_details"))
#     dest = details.get("destination", "your destination")
    
#     prompt = f"""
#     Write a short, high-energy, evocative welcome message about traveling to {dest}.
#     Max 2 sentences. Use emojis. 
#     Example: "The misty hills of Darjeeling are calling! 🏔️"
#     """
#     response = await gemini_llm.ainvoke(prompt)
#     # Prefix "GREETING_Start:" tells the frontend to render this as the greeting bubble
#     return {"messages": [AIMessage(content=f"GREETING_Start: {response.content}")]}
async def greeting_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")
    
    # prompt = f"""
    # Write a short, high-energy, evocative welcome message about traveling to {dest}.
    # Max 2 sentences. Use emojis. 
    # Example: "The misty hills of Darjeeling are calling! 🏔️"
    # """

    prompt = f"""
        Write a highly evocative, confidence-boosting welcome message about {dest}
        that makes the reader feel proud and excited about choosing this destination.
        Limit to 2–3 sentences, high energy, vivid imagery, and emojis.
        """
    response = await gemini_llm.ainvoke(prompt)
    
    clean_text = clean_content(response.content)
    
    return {"messages": [AIMessage(content=f"GREETING_Start: {clean_text}")]}

# B. FLIGHTS NODE (Runs second)
async def flight_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    src = details.get("source")
    dst = details.get("destination")
    date = details.get("start_date")
    
    try:
        # invoke tools (synchronous or async depending on implementation)
        result = search_flights.invoke({"source": src, "destination": dst, "date": date})
    except Exception as e:
        result = json.dumps({"error": str(e)})
        
    return {"search_results": f"FLIGHTS_DONE: {result}"}

# C. TRAINS NODE (Runs third)
async def train_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    src = details.get("source")
    dst = details.get("destination")
    date = details.get("start_date")
    
    try:
        result = search_trains.invoke({"source": src, "destination": dst, "date": date})
    except Exception as e:
        result = json.dumps({"error": str(e)})
        
    # We append this to the existing search_results so the state holds BOTH
    return {"search_results": f"TRAINS_DONE: {result}", "current_phase": "presenting_options"}

# =========================================================
# 4️⃣ STANDARD NODES (Hotels & Confirmation)
# =========================================================

def hotel_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    dst = get_trip(details, "destination")
    date = get_trip(details, "start_date")
    print(f"🏨 Searching Hotels in {dst}...")
    try:
        raw_hotels = search_hotels.invoke({"location": dst, "check_in": date})
    except Exception as e:
        raw_hotels = "Error searching hotels."
    return {"search_results": raw_hotels, "current_phase": "presenting_hotels"}

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

async def save_itinerary_node(state: AgentState):
    # (Same as before - decoupled DB save)
    session_id = state.get("session_id")
    details = safe_dict(state.get("trip_details"))
    if not session_id: return {}
    
    async with SessionLocal() as session:
        try:
            result = await session.execute(select(Trip).where(Trip.session_id == session_id))
            existing = result.scalars().first()
            if existing:
                existing.source = details.get("source")
                existing.destination = details.get("destination")
            else:
                new_trip = Trip(session_id=session_id, source=details.get("source"), destination=details.get("destination"))
                session.add(new_trip)
            await session.commit()
        except Exception as e:
            print(f"DB Error: {e}")
    return {}

# =========================================================
# 🔄 ROUTING & GRAPH SETUP
# =========================================================
workflow = StateGraph(AgentState)

workflow.add_node("extractor", extraction_node)
workflow.add_node("planner", planner_node)

# Stream Pipeline
workflow.add_node("greeting_gen", greeting_node)
workflow.add_node("flight_search", flight_search_node)
workflow.add_node("train_search", train_search_node)

# Standard Nodes
workflow.add_node("hotel_search", hotel_search_node)
workflow.add_node("responder", response_node)
workflow.add_node("saver", save_itinerary_node)

# Entry
workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "planner")

# Conditional Routing
def route_planner(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    
    if phase == "ready_to_search":
        return "greeting_gen" 
    if phase == "search_hotels":
        return "hotel_search"
    if phase == "confirm_transport":
        return "responder"
    
    return "responder" # Default

workflow.add_conditional_edges("planner", route_planner)

# Pipeline Edges
workflow.add_edge("greeting_gen", "flight_search")
workflow.add_edge("flight_search", "train_search")
workflow.add_edge("train_search", "saver")
workflow.add_edge("saver", END)

# Standard Edges
workflow.add_edge("hotel_search", "responder")
workflow.add_edge("responder", END)