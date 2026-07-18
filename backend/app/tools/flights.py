#backend/app/tool/flights.py
import os
import json
import traceback
from datetime import datetime
import re
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

from app.data.airports import get_airport
from app.tools.currency import get_conversion_rate

load_dotenv()

DUFFEL_TOKEN = os.getenv("DUFFEL_API_TOKEN")

BASE_URL = "https://api.duffel.com"

HEADERS = {
    "Authorization": f"Bearer {DUFFEL_TOKEN}",
    "Duffel-Version": "v2",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

ALLOWED_AIRLINES = {
    "Air India",
    "Air India Express",
    "IndiGo",
    "Akasa Air",
    "SpiceJet",
    "Alliance Air",
    "Star Air",
}

def rank_flights(flights):
    """
    Rank flights by:
    50% Price
    30% Duration
    20% Stops
    """

    if not flights:
        return flights

    prices = [f["price"] for f in flights]
    durations = [
        duration_to_minutes(f["dur"])
        for f in flights
    ]
    stops = [f["stops"] for f in flights]

    min_price = min(prices)
    max_price = max(prices)

    min_duration = min(durations)
    max_duration = max(durations)

    min_stop = min(stops)
    max_stop = max(stops)

    for flight in flights:

        price_score = (
            (flight["price"] - min_price)
            /
            max(max_price - min_price, 1)
        )

        duration_score = (
            (
                duration_to_minutes(flight["dur"])
                - min_duration
            )
            /
            max(max_duration - min_duration, 1)
        )

        stop_score = (
            (flight["stops"] - min_stop)
            /
            max(max_stop - min_stop, 1)
        )

        flight["score"] = (
            price_score * 0.50
            +
            duration_score * 0.30
            +
            stop_score * 0.20
        )

    return sorted(
        flights,
        key=lambda x: x["score"]
    )


def duration_to_minutes(duration: str) -> int:
    """
    Convert:
    '2h 30m'
    '45m'
    '5h'
    into total minutes.
    """

    if not duration:
        return 9999

    hours = 0
    minutes = 0

    h = re.search(r"(\d+)h", duration)
    m = re.search(r"(\d+)m", duration)

    if h:
        hours = int(h.group(1))

    if m:
        minutes = int(m.group(1))

    return hours * 60 + minutes

def safe_get(obj, *keys):

    current = obj

    for key in keys:

        if not isinstance(current, dict):
            return None

        current = current.get(key)

        if current is None:
            return None

    return current


def extract_time(value):

    if not value:
        return "--:--"

    try:

        return datetime.fromisoformat(
            value.replace("Z", "")
        ).strftime("%H:%M")

    except Exception:

        return value[11:16]


def format_duration(duration):

    if not duration:
        return "--"

    return (
        duration
        .replace("PT", "")
        .replace("H", "h ")
        .replace("M", "m")
        .strip()
    )


def format_price(price):

    try:
        return int(float(price))
    except:
        return 0
    
def airport_payload(first_segment, last_segment):

    return {

        "from_airport_name":
            safe_get(first_segment, "origin", "name"),

        "from_airport_code":
            safe_get(first_segment, "origin", "iata_code"),

        "from_city_label":
            safe_get(first_segment, "origin", "city_name"),

        "to_airport_name":
            safe_get(last_segment, "destination", "name"),

        "to_airport_code":
            safe_get(last_segment, "destination", "iata_code"),

        "to_city_label":
            safe_get(last_segment, "destination", "city_name"),
    }

def airline_payload(segment):

    airline = safe_get(
        segment,
        "operating_carrier",
        "name"
    )

    logo = safe_get(
        segment,
        "operating_carrier",
        "logo_symbol_url"
    )

    code = safe_get(
        segment,
        "marketing_carrier",
        "iata_code"
    )

    number = segment.get(
        "marketing_carrier_flight_number",
        ""
    )

    return {

        "airline":
            airline or "Unknown Airline",

        "number":
            f"{code}{number}",

        "logo":
            logo or ""
    }

def build_flight_card(offer):

    slices = offer.get("slices") or []

    if not slices:
        raise Exception("No slices found")

    slice_data = slices[0]

    segments = slice_data.get("segments") or []

    if not segments:
        raise Exception("No segments found")

    first = segments[0]
    last = segments[-1]

    flight = {}

    # Airline Information
    flight.update(
        airline_payload(first)
    )

    # Airport Information
    flight.update(
        airport_payload(first, last)
    )

    # Departure & Arrival
    flight["dep"] = extract_time(
        first.get("departing_at")
    )

    flight["arr"] = extract_time(
        last.get("arriving_at")
    )

    # Journey Duration
    flight["dur"] = format_duration(
        slice_data.get("duration")
    )

    # ⭐ Raw Duffel Price (USD)
    try:
        flight["price"] = float(
            offer.get("total_amount", 0)
        )
    except (ValueError, TypeError):
        flight["price"] = 0.0

    # Original Currency
    flight["currency"] = offer.get(
        "total_currency",
        "USD"
    )

    # Stops
    flight["stops"] = max(
        len(segments) - 1,
        0
    )

    # Duffel Offer ID
    flight["offer_id"] = offer.get("id")

    return flight

@tool
def search_flights(
    source: str,
    destination: str,
    departure_date: str,
):
    """
    Search flights using Duffel and convert prices to INR.
    """

    origin = get_airport(source)
    dest = get_airport(destination)

    if origin is None:
        return json.dumps({
            "error": f"Unknown source city: {source}"
        })

    if dest is None:
        return json.dumps({
            "error": f"Unknown destination city: {destination}"
        })

    payload = {
        "data": {
            "slices": [
                {
                    "origin": origin["iata"],
                    "destination": dest["iata"],
                    "departure_date": departure_date
                }
            ],
            "passengers": [
                {
                    "type": "adult"
                }
            ],
            "cabin_class": "economy"
        }
    }

    try:

        response = httpx.post(
            f"{BASE_URL}/air/offer_requests?return_offers=true",
            headers=HEADERS,
            json=payload,
            timeout=90
        )

        response.raise_for_status()

        result = response.json()

        data = result.get("data") or {}

        offers = data.get("offers") or []

        print(f"Offers Found: {len(offers)}")

        if not offers:
            return json.dumps([])

        # Fetch exchange rate ONCE (cached for 1 hour)
        try:
            conversion_rate = get_conversion_rate(
                "USD",
                "INR"
            )
        except Exception as e:
            print("Currency API Error:", e)
            conversion_rate = 1.0

        flights = []

        for offer in offers:

            try:

                airline = (
                    offer.get("slices", [{}])[0]
                        .get("segments", [{}])[0]
                        .get("operating_carrier", {})
                        .get("name", "")
                )

                if airline not in ALLOWED_AIRLINES:
                    continue

                card = build_flight_card(offer)

                # Duffel returns total_amount as string
                usd_price = float(card["price"])

                # Convert to INR
                card["price"] = round(
                    usd_price * conversion_rate
                )

                card["currency"] = "INR"

                flights.append(card)

            except Exception:
                traceback.print_exc()
                continue

        best_flights = rank_flights(flights)

        return json.dumps(best_flights[:8])

    except httpx.HTTPStatusError as e:

        print("Duffel HTTP Error")
        print(e.response.text)

        return json.dumps([])

    except Exception:
        traceback.print_exc()
        return json.dumps([])