#graph.py
import os
import json
import re
from amadeus import Client, ResponseError
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

from llms import data_cleaner_llm, gpt_llm
from langchain_core.messages import HumanMessage

# Initialize Tools
tavily_tool = TavilySearchResults(max_results=3)

amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

AIRLINES = {
    "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet", "UK": "Vistara",
    "QP": "Akasa Air", "IX": "Air India Express", "I5": "AirAsia", "G8": "Go First"
}

# ==========================================
# 🧠 DYNAMIC IATA RESOLVER
# ==========================================
def get_iata_code(place_name: str) -> Optional[str]:
    clean_name = place_name.strip().upper()
    print(f"🔍 Resolving IATA for: {clean_name}...")

    # 1. Amadeus Direct Lookup
    try:
        response = amadeus.reference_data.locations.get(keyword=clean_name, subType="CITY,AIRPORT")
        if response.data:
            code = response.data[0]['iataCode']
            name = response.data[0]['name']
            print(f"✅ Amadeus Direct Hit: {name} ({code})")
            return code
    except Exception:
        pass 

    # 2. Web Search Fallback
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

def get_airport_name(iata_code: str):
    try:
        response = amadeus.reference_data.locations.get(
            keyword=iata_code,
            subType="AIRPORT"
        )
        if response.data:
            return response.data[0].get("name")
    except Exception:
        pass
    return None


def get_city_name_from_city_code(iata_code: str):
    """
    Resolve proper city name using CITY lookup.
    DEL -> New Delhi
    BOM -> Mumbai
    """
    try:
        airport_resp = amadeus.reference_data.locations.get(
            keyword=iata_code,
            subType="AIRPORT"
        )

        if not airport_resp.data:
            return None

        city_code = airport_resp.data[0].get("address", {}).get("cityCode")

        if not city_code:
            return None

        # 2️⃣ Resolve CITY entity
        city_resp = amadeus.reference_data.locations.get(
            keyword=city_code,
            subType="CITY"
        )

        if city_resp.data:
            return city_resp.data[0].get("name")

    except Exception as e:
        print(f"City resolve failed for {iata_code}: {e}")

    return None

# ==========================================
# ✈️ FLIGHT SEARCH TOOL
# ==========================================
@tool
def search_flights(source: str, destination: str, date: str):
    """
    Fetches REAL-TIME flight data using Amadeus.
    Returns city + airport data (MMT / Ixigo style).
    """
    try:
        origin_code = get_iata_code(source)
        dest_code = get_iata_code(destination)

        if not origin_code or not dest_code:
            return json.dumps({"error": "Airports not found."})

        print(f"✈️ Searching Flights: {origin_code} -> {dest_code} on {date}")

        # =============================
        # 1️⃣ Resolve ORIGIN city properly
        # =============================
        origin_airport_resp = amadeus.reference_data.locations.get(
            keyword=origin_code,
            subType="AIRPORT"
        )

        origin_city_code = None
        if origin_airport_resp.data:
            origin_city_code = origin_airport_resp.data[0].get("address", {}).get("cityCode")

        from_city_label = get_city_name_from_city_code(origin_city_code)

        # =============================
        # 2️⃣ Resolve DESTINATION city properly
        # =============================
        dest_airport_resp = amadeus.reference_data.locations.get(
            keyword=dest_code,
            subType="AIRPORT"
        )

        dest_city_code = None
        if dest_airport_resp.data:
            dest_city_code = dest_airport_resp.data[0].get("address", {}).get("cityCode")

        to_city_label = get_city_name_from_city_code(dest_city_code)

        # =============================
        # 3️⃣ Resolve airport names
        # =============================
        from_airport_name = origin_airport_resp.data[0].get("name") if origin_airport_resp.data else None
        to_airport_name = dest_airport_resp.data[0].get("name") if dest_airport_resp.data else None

        # =============================
        # 4️⃣ Search flights
        # =============================
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

                duration = (
                    itinerary["duration"]
                    .replace("PT", "")
                    .replace("H", "h ")
                    .replace("M", "m")
                    .lower()
                )

                carrier = segment["carrierCode"]

                flights.append({
                    "airline": AIRLINES.get(carrier, carrier),
                    "number": f"{carrier}-{segment['number']}",
                    "dep": segment["departure"]["at"].split("T")[1][:5],
                    "arr": segment["arrival"]["at"].split("T")[1][:5],
                    "dur": duration,
                    "price": int(float(offer["price"]["total"])),
                    "stops": len(itinerary["segments"]) - 1,

                    # ✅ AIRPORT DATA
                    "from_airport_name": from_airport_name,
                    "from_airport_code": origin_code,
                    "to_airport_name": to_airport_name,
                    "to_airport_code": dest_code,

                    # ✅ PROPER CITY LABELS (THIS FIXES EVERYTHING)
                    "from_city_label": from_city_label,
                    "to_city_label": to_city_label,

                    # Context only
                    "user_destination": destination.title()
                })

    


            return json.dumps(flights)

    except Exception as e:
        print(f"⚠️ Flight Error: {e}")

    # 🔄 Fallback
    try:
        print("🔄 API Failed. Trying Web Search...")
        res = tavily_tool.invoke(
            f"flights from {source} to {destination} on {date} price"
        )
        return f"WEB_SEARCH_RESULTS: {str(res)}"
    except Exception:
        return json.dumps([])



# ==========================================
# 🚆 TRAIN SEARCH TOOL (FIXED)
# ==========================================
class TrainClass(BaseModel):
    name: str = Field(description="Class name (SL, 3A, 2A)")
    price: float = Field(description="Price in INR")
    status: str = Field(description="Availability Status")

# ✅ THIS CLASS DEFINITION WAS MISSING IN YOUR PREVIOUS RUN
class TrainInfo(BaseModel):
    name: str = Field(description="Train Name")
    number: str = Field(description="Train Number")
    departure_time: str = Field(description="HH:MM")
    arrival_time: str = Field(description="HH:MM")
    duration: str = Field(description="Duration")
    
    # These fields fix the "DEST" issue
    from_station_name: str = Field(description="Origin Station Name (e.g. New Delhi)")
    from_station_code: str = Field(description="Origin Code (e.g. NDLS)")
    to_station_name: str = Field(description="Destination Station Name (e.g. New Jalpaiguri)")
    to_station_code: str = Field(description="Destination Code (e.g. NJP)")
    
    classes: List[TrainClass]

class TrainList(BaseModel):
    trains: List[TrainInfo]

@tool
def search_trains(source: str, destination: str, date: str):
    """
    Searches for Train Timetables, prices, and availability using IRCTC data via web search.
    """
    print(f"🚂 Searching Trains: {source} -> {destination} on {date}")
    
    query = f"trains from {source} to {destination} on {date} schedule price and availability irctc"
    try:
        raw_results = tavily_tool.invoke(query)
    except Exception as e:
        print(f"Error fetching train data: {e}")
        return json.dumps([])

    parser_llm = gpt_llm.with_structured_output(TrainList)
    
    prompt = f"""
    You are a Data Extractor.
    Extract train details from the search results below.
    
    CONTEXT:
    Source: {source}
    Destination: {destination}
    Date: {date}
    
    SEARCH RESULTS:
    {raw_results}
    
    🚨 CRITICAL INSTRUCTIONS:
    
    1. **STATION NAMES**:
       - Extract the FULL Station Name for "{destination}".
       - If "{destination}" is a hill station (e.g., Darjeeling, Manali), use the **NEAREST RAILHEAD** (e.g., NJP, Kalka).
       - Populate 'to_station_name' with this real name.
       - Populate 'to_station_code' with the code.

    2. **REALISM**:
       - Extract 'SL' class if listed. Estimate price (~₹800) if missing.
       - Generate realistic availability (e.g. "Available 23", "WL 56").
    """
    
    try:
        # ✅ FIX: Convert Pydantic Object -> JSON String immediately
        cleaned_data = parser_llm.invoke([HumanMessage(content=prompt)])
        return json.dumps([t.model_dump() for t in cleaned_data.trains])
        
    except Exception as e:
        print(f"⚠️ Train Parsing Failed: {e}")
        return json.dumps([])


@tool
def search_hotels(location: str, check_in: str):
    """
    Searches for hotels using Tavily.
    """
    query = f"budget hostel PG hotel in {location} price rating stay on {check_in}"
    try:
        results = tavily_tool.invoke(query)
        return str(results)
    except Exception:
        return "No hotels found."

@tool
def search_local_attractions(location: str, interest: str):
    """
    Searches for attractions.
    """
    query = f"must visit {interest} places in {location} with entry fee and timings"
    try:
        results = tavily_tool.invoke(query)
        return str(results)
    except Exception as e:
        return f"Error: {e}"