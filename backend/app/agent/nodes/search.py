# app/agent/nodes/search.py
from app.agent.helpers.train_explainer import build_train_context
from app.agent.helpers.train_nlg import generate_train_explanation
from app.tools.flights import search_flights
from app.tools.trains import search_trains
from app.tools.hotels import search_hotels
from app.schemas.state import AgentState
from app.utils import safe_dict, get_trip
from app.agent.helpers.flight_explainer import build_flight_context
from app.agent.helpers.flight_nlg import generate_flight_explanation
import json

async def flight_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))

    source = details.get("source")
    destination = details.get("destination")
    date = details.get("start_date")

    if not source or not destination or not date:
        return {
            "search_results": "FLIGHTS_DONE: " + json.dumps({
                "info": "Please provide source, destination and travel date.",
                "data": []
            })
        }

    try:
        raw = search_flights.invoke({
            "source": source,
            "destination": destination,
            "date": date
        })

        flights = json.loads(raw) if raw else []

        explanation = ""
        if flights:
            context = build_flight_context(
                destination=destination,   
                flight=flights[0]
            )
            explanation = generate_flight_explanation(context)

        payload = {
            "info": explanation,
            "data": flights
        }

        return {
            "search_results": f"FLIGHTS_DONE: {json.dumps(payload)}"
        }

    except Exception as e:
        return {
            "search_results": "FLIGHTS_DONE: " + json.dumps({
                "info": "Flights are available for your route.",
                "data": []
            })
        }


async def train_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))

    source = details.get("source")
    destination = details.get("destination")
    date = details.get("start_date")

    if not destination or not source or not date:
        return {
            "search_results": {
                "type": "trains",
                "info": "Train options are available for your route.",
                "data": []
            },
            "current_phase": "presenting_options"
        }

    try:
        raw = search_trains.invoke({
            "source": source,
            "destination": destination,
            "date": date
        })

        trains = json.loads(raw)

        explanation = ""
        if trains and isinstance(trains, list):
            context = build_train_context(destination, trains[0])
            explanation = generate_train_explanation(context)

        return {
            "search_results": {
                "type": "trains",
                "info": explanation,
                "data": trains
            },
            "current_phase": "presenting_options"
        }

    except Exception as e:
        return {
            "search_results": {
                "type": "trains",
                "info": "I found train options for your journey.",
                "data": []
            },
            "current_phase": "presenting_options"
        }


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