# backend/app/agent/nodes/search.py
import json
from langchain_core.messages import AIMessage
from app.agent.helpers.train_explainer import build_train_context
from app.agent.helpers.train_nlg import generate_train_explanation
from app.tools.flights import search_flights
from app.tools.trains import search_trains
from app.tools.hotels import search_hotels
from app.schemas.state import AgentState
from app.utils import safe_dict, get_trip
from app.agent.helpers.flight_explainer import build_flight_context
from app.agent.helpers.flight_nlg import generate_flight_explanation


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
# STANDARD NODES (Hotels & Confirmation)
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


# =========================================================
# NEW LOCAL RENTAL & RETURN TRANSPORT NODES
# =========================================================

async def rental_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    dest = details.get("destination", "your destination")
    
    # Mocked structured output for rentals (replace with actual tool call later)
    mock_rentals = {
        "greeting": f"Here are some popular rental options to help you explore {dest} like a local! Once you select one, I'll look up your return transport.",
        "rentals_section": {
            "data": [
                {"id": "r1", "name": "Royal Enfield Classic 350", "type": "Bike", "price": 1200, "provider": "Royal Rides"},
                {"id": "r2", "name": "Honda Activa 6G", "type": "Scooter", "price": 600, "provider": "City Scoots"},
                {"id": "r3", "name": "Hyundai i20", "type": "Car", "price": 2500, "provider": "ZoomCar"}
            ]
        }
    }
    
    return {
        "messages": [AIMessage(content=json.dumps(mock_rentals))],
        "current_phase": "presenting_rentals" 
    }


async def return_transport_search_node(state: AgentState):
    details = safe_dict(state.get("trip_details"))
    
    # 🔄 SWAP SOURCE AND DESTINATION FOR RETURN JOURNEY
    source = details.get("destination") 
    destination = details.get("source")
    date = details.get("end_date")
    
    if not date:
        return {"messages": [AIMessage(content="I need your return date to book the journey back! Can you tell me when you plan to return?")]}

    print(f"✈️ Searching Return Transport: {source} -> {destination} on {date}")

    flights_data = []
    trains_data = []

    # 1. Fetch Return Flights
    try:
        raw_flights = search_flights.invoke({
            "source": source,
            "destination": destination,
            "date": date
        })
        flights_data = json.loads(raw_flights) if raw_flights else []
    except Exception as e:
        print(f"❌ Return Flight Error: {e}")

    # 2. Fetch Return Trains
    try:
        raw_trains = search_trains.invoke({
            "source": source,
            "destination": destination,
            "date": date
        })
        trains_data = json.loads(raw_trains) if raw_trains else []
    except Exception as e:
        print(f"❌ Return Train Error: {e}")

    # 3. Build Combined Payload
    payload = {
        "greeting": f"Time to head home! Here are your return options from {source} back to {destination} on {date}:"
    }

    if flights_data:
        payload["flights_section"] = {
            "info": "Fastest Return Flights",
            "data": flights_data
        }
        
    if trains_data:
        payload["trains_section"] = {
            "info": "Scenic Return Trains",
            "data": trains_data
        }

    # Fallback if both fail
    if not flights_data and not trains_data:
         return {
            "messages": [AIMessage(content=f"I couldn't fetch return transport from {source} right now. Let me know if you want to try again!")],
            "current_phase": "presenting_return_transport" 
        }

    return {
        "messages": [AIMessage(content=json.dumps(payload))],
        "current_phase": "presenting_return_transport" 
    }