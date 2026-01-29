from typing import Dict, Any
from app.utility.location import get_ground_transfer_info


def build_train_context(
    destination: str,
    train: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Returns structured arrival + onward travel facts for trains.
    No natural language. No hardcoding.
    """

    arrival_station = train.get("to_station_name") or ""
    arrival_city = train.get("to_station_city") or ""

    direct_arrival = (
        destination.strip().lower() == arrival_city.strip().lower()
        if arrival_city else False
    )

    context: Dict[str, Any] = {
        "destination": destination,
        "arrival_station": arrival_station,
        "arrival_city": arrival_city,
        "direct_arrival": direct_arrival,
    }

    # Only compute onward travel if destination is different
    if not direct_arrival and arrival_city:
        transfer = get_ground_transfer_info(
            destination=destination,
            airport_city=arrival_city,     
            airport_name=arrival_station,  
        )

        if transfer:
            context.update({
                "distance_km": transfer.get("distance_km"),
                "road_time": transfer.get("road_time"),
                "transport_modes": transfer.get("transport_modes", []),
                "experience_tag": transfer.get("experience_tag"),
            })

    return context
