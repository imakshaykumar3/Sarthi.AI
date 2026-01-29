from typing import Dict, Any
from app.utility.location import get_ground_transfer_info


def build_flight_context(
    destination: str,
    flight: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Returns structured travel facts.
    NO natural language here.
    Safe before user selects a flight.
    """

    airport_name = flight.get("to_airport_name") or ""
    airport_code = flight.get("to_airport_code") or ""
    airport_city = flight.get("to_city_label") or ""
    duration = flight.get("dur") or "around 2–3 hours"


    direct_arrival = (
        destination.strip().lower() == airport_city.strip().lower()
        if airport_city else False
    )

    context: Dict[str, Any] = {
        "destination": destination,
        "airport_name": airport_name,
        "airport_code": airport_code,
        "flight_duration": duration,
        "direct_arrival": direct_arrival,
    }

    if not direct_arrival and airport_name and airport_city:
        transfer = get_ground_transfer_info(
            destination=destination,
            airport_city=airport_city,
            airport_name=airport_name
        )

        if transfer:
            context.update({
                "distance_km": transfer.get("distance_km"),
                "road_time": transfer.get("road_time"),
                "transport_options": ["shared taxi", "private cab"]
            })

    return context
