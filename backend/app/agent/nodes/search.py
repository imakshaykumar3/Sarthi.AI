# app/agent/nodes/search.py
from app.tools.flights import search_flights
from app.tools.trains import search_trains
from app.tools.hotels import search_hotels
from app.schemas.state import AgentState
from app.utils import safe_dict, get_trip
import json

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