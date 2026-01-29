# app/tools/flights.py
import os
import json
import re
from amadeus import Client
from typing import Optional
from langchain_core.tools import tool
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

from app.core.llms import data_cleaner_llm

# Initialize local instances
tavily_tool = TavilySearchResults(max_results=3)

amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

AIRLINES = {
    "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet", "UK": "Vistara",
    "QP": "Akasa Air", "IX": "Air India Express", "I5": "AirAsia", "G8": "Go First"
}

# --- Helpers ---
def get_iata_code(place_name: str) -> Optional[str]:
    clean_name = place_name.strip().upper()
    print(f"🔍 Resolving IATA for: {clean_name}...")

    try:
        response = amadeus.reference_data.locations.get(keyword=clean_name, subType="CITY,AIRPORT")
        if response.data:
            code = response.data[0]['iataCode']
            name = response.data[0]['name']
            print(f"✅ Amadeus Direct Hit: {name} ({code})")
            return code
    except Exception:
        pass 

    print(f"🌍 Searching for nearest major airport to {clean_name}...")
    try:
        query = f"What is the nearest major commercial airport to {clean_name}? Return 3-letter IATA code."
        search_result = tavily_tool.invoke(query)
        
        prompt = f"""
        Identify the nearest MAJOR COMMERCIAL AIRPORT IATA code for "{clean_name}".
        SEARCH RESULTS: {str(search_result)[:1000]}
        OUTPUT ONLY THE 3-LETTER CODE (e.g. IXB).
        """
        response_msg = data_cleaner_llm.invoke(prompt)
        content = str(response_msg.content).strip().upper()
        match = re.search(r'\b[A-Z]{3}\b', content)
        if match:
            return match.group(0)
    except Exception as e:
        print(f"⚠️ Dynamic Resolve Failed: {e}")
    return None


# --- Main Tool ---
@tool
def search_flights(source: str, destination: str, date: str):
    """Fetches REAL-TIME flight data using Amadeus."""
    try:
        origin_code = get_iata_code(source)
        dest_code = get_iata_code(destination)

        if not origin_code or not dest_code:
            return json.dumps({"error": "Airports not found."})

        print(f"✈️ Searching Flights: {origin_code} -> {dest_code} on {date}")

        # Resolve Names
        origin_airport_resp = amadeus.reference_data.locations.get(keyword=origin_code, subType="AIRPORT")
        origin_city_code = origin_airport_resp.data[0].get("address", {}).get("cityCode") if origin_airport_resp.data else None
        from_city_label = origin_airport_resp.data[0].get("address", {}).get("cityName")

        dest_airport_resp = amadeus.reference_data.locations.get(keyword=dest_code, subType="AIRPORT")
        dest_city_code = dest_airport_resp.data[0].get("address", {}).get("cityCode") if dest_airport_resp.data else None
        to_city_label = dest_airport_resp.data[0].get("address", {}).get("cityName")

        from_airport_name = origin_airport_resp.data[0].get("name") if origin_airport_resp.data else None
        to_airport_name = dest_airport_resp.data[0].get("name") if dest_airport_resp.data else None

        # Search
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=date,
            adults=1,
            currencyCode="INR",
            max=5
        )

        flights = []
        if response.data:
            for offer in response.data:
                itinerary = offer["itineraries"][0]
                segment = itinerary["segments"][0]
                carrier = segment["carrierCode"]
                
                duration = itinerary["duration"].replace("PT", "").replace("H", "h ").replace("M", "m").lower()
                
                flights.append({
                    "airline": AIRLINES.get(carrier, carrier),
                    "number": f"{carrier}-{segment['number']}",
                    "dep": segment["departure"]["at"].split("T")[1][:5],
                    "arr": segment["arrival"]["at"].split("T")[1][:5],
                    "dur": duration,
                    "price": int(float(offer["price"]["total"])),
                    "stops": len(itinerary["segments"]) - 1,
                    "from_airport_name": from_airport_name,
                    "from_airport_code": origin_code,
                    "to_airport_name": to_airport_name,
                    "to_airport_code": dest_code,
                    "from_city_label": from_city_label,
                    "to_city_label": to_city_label,
                    "user_destination": destination.title()
                })
            return json.dumps(flights)

    except Exception as e:
        print(f"⚠️ Flight Error: {e}")

    # Fallback
    try:
        print("🔄 API Failed. Trying Web Search...")
        res = tavily_tool.invoke(f"flights from {source} to {destination} on {date} price")
        return f"WEB_SEARCH_RESULTS: {str(res)}"
    except Exception:
        return json.dumps([])