# import os
# import json
# import re
# from amadeus import Client, ResponseError
# from typing import List, Optional
from pydantic import BaseModel, Field
from typing import List
# try:
#     from langchain_tavily import TavilySearchResults
# except ImportError:
#     from langchain_community.tools.tavily_search import TavilySearchResults

# from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
# from llms import data_cleaner_llm 

# tavily_tool = TavilySearchResults(max_results=3)

# amadeus = Client(
#     client_id=os.getenv('AMADEUS_CLIENT_ID'),
#     client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
# )

# AIRLINES = {
#     "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet", "UK": "Vistara",
#     "QP": "Akasa Air", "IX": "Air India Express", "I5": "AirAsia", "G8": "Go First"
# }

# # ==========================================
# # 🧠 DYNAMIC IATA RESOLVER (No Hardcoding)
# # ==========================================
# def get_iata_code(place_name: str) -> Optional[str]:
#     """
#     Finds the IATA code for a city dynamically.
#     1. Tries Amadeus Direct Lookup (Fastest).
#     2. If Amadeus finds nothing (e.g., hill station), searches Web for 'Nearest airport to X'.
#     3. Uses LLM to extract the code from search results.
#     """
#     clean_name = place_name.strip()
#     print(f"🔍 Dynamic IATA Resolve for: {clean_name}...")

#     try:
#         response = amadeus.reference_data.locations.get(keyword=clean_name, subType="CITY,AIRPORT")
#         if response.data:
#             code = response.data[0]['iataCode']
#             print(f"✅ Amadeus Direct Hit: {clean_name} -> {code}")
#             return code
#     except Exception:
#         pass 

#     print(f"🌍 Amadeus didn't find an airport in {clean_name}. Searching for the NEAREST one...")
    
#     try:
#         query = f"What is the nearest airport to {clean_name}? Return the 3-letter IATA code."
#         search_result = tavily_tool.invoke(query)
        
#         prompt = f"""
#         TASK: Identify the nearest airport IATA code for "{clean_name}" based on the search results below.
        
#         SEARCH RESULTS:
#         {str(search_result)}
        
#         INSTRUCTIONS:
#         1. Find the name of the nearest airport mentioned.
#         2. Extract its 3-letter IATA code (e.g. IXB, KUU, COK).
#         3. Return ONLY the 3-letter code. Nothing else.
#         """
        
#         response_msg = data_cleaner_llm.invoke(prompt)
#         content = response_msg.content
        
#         if isinstance(content, list):
#             content = " ".join([str(c) for c in content])
        
#         code = str(content).strip().upper()
        
#         code = re.sub(r'[^A-Z]', '', code)
        
#         if len(code) == 3:
#             print(f"✅ Web Resolved: Nearest airport to {clean_name} is {code}")
#             return code
#         else:
#             print(f"⚠️ LLM returned invalid code: {code}")
            
#     except Exception as e:
#         print(f"⚠️ Dynamic Resolve Failed: {e}")
    
#     return None
# # ==========================================
# # ✈️ FLIGHT SEARCH TOOL
# # ==========================================
# @tool
# def search_flights(source: str, destination: str, date: str):
#     """
#     Fetches REAL-TIME flight data using Amadeus with Dynamic IATA Resolution.
#     """
#     flights = []
    
#     try:
#         origin_code = get_iata_code(source)
#         dest_code = get_iata_code(destination)

#         if not origin_code or not dest_code:
#             return json.dumps({"error": f"Could not locate airports for {source} or {destination}. Please check spelling."})

#         print(f"✈️ Searching Flights: {origin_code} -> {dest_code} on {date}")

#         response = amadeus.shopping.flight_offers_search.get(
#             originLocationCode=origin_code,
#             destinationLocationCode=dest_code,
#             departureDate=date,
#             adults=1,
#             currencyCode='INR',
#             max=5
#         )
        
#         if response.data:
#             for offer in response.data:
#                 itinerary = offer['itineraries'][0]
#                 segment = itinerary['segments'][0]
                
#                 dur_iso = itinerary['duration'] 
#                 dur = dur_iso.replace("PT", "").replace("H", "h ").replace("M", "m").lower()
                
#                 code = segment['carrierCode']
#                 name = AIRLINES.get(code, code)
                
#                 flights.append({
#                     "airline": name,
#                     "number": f"{code}-{segment['number']}",
#                     "dep": segment['departure']['at'].split("T")[1][:5],
#                     "arr": segment['arrival']['at'].split("T")[1][:5],
#                     "dur": dur,
#                     "price": int(float(offer['price']['total'])),
#                     "stops": len(itinerary['segments']) - 1,
#                     "from_city": source.title(),     
#                     "to_city": destination.title()   
#                 })
            
#             return json.dumps(flights)
#         else:
#             print("⚠️ Amadeus found no flights.")

#     except Exception as e:
#         print(f"⚠️ Flight Search Error: {e}")

#     # --- STRATEGY 3: Web Search Fallback ---
#     print(f"🔄 Amadeus empty/failed. Trying Web Search...")
#     try:
#         query = f"flights from {source} to {destination} on {date} price"
#         raw_results = tavily_tool.invoke(query)
#         return f"WEB_SEARCH_RESULTS: {str(raw_results)}" 
#     except Exception as e:
#         return json.dumps({"error": str(e)})

import os
import json
import re
from amadeus import Client, ResponseError
from typing import List, Optional, Dict, Any
from langchain_core.tools import tool
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

# 🟢 IMPORT CORRECT LLM (Flash/Lite)
from llms import data_cleaner_llm, gpt_llm

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
# 🧠 DYNAMIC IATA RESOLVER (Fixed Logic)
# ==========================================
def get_iata_code(place_name: str) -> Optional[str]:
    """
    Finds the IATA code for a city dynamically.
    1. Tries Amadeus Direct Lookup (Fastest).
    2. If Amadeus finds nothing (e.g., hill station), searches Web for 'Nearest airport to X'.
    3. Uses LLM to extract the code from search results.
    """
    clean_name = place_name.strip()
    print(f"🔍 Dynamic IATA Resolve for: {clean_name}...")

    # 1. Try Amadeus First
    try:
        response = amadeus.reference_data.locations.get(keyword=clean_name, subType="CITY,AIRPORT")
        if response.data:
            code = response.data[0]['iataCode']
            print(f"✅ Amadeus Direct Hit: {clean_name} -> {code}")
            return code
    except Exception:
        pass 

    # 2. Web Search Fallback
    print(f"🌍 Amadeus didn't find an airport in {clean_name}. Searching for the NEAREST one...")
    
    try:
        query = f"What is the nearest airport to {clean_name}? Return the 3-letter IATA code."
        search_result = tavily_tool.invoke(query)
        
        # 🟢 FIX 1: Truncate search results and use stricter prompt
        prompt = f"""
        TASK: Identify the nearest airport IATA code for "{clean_name}".
        
        SEARCH RESULTS:
        {str(search_result)[:1000]}  
        
        INSTRUCTIONS:
        1. Find the 3-letter IATA code (e.g. IXB, DEL, BOM).
        2. OUTPUT ONLY THE CODE. Do not write "The code is...".
        3. If multiple found, pick the nearest one.
        """
        
        response_msg = data_cleaner_llm.invoke(prompt)
        content = str(response_msg.content).strip().upper()
        
        # 🟢 FIX 2: Strict Regex Extraction (Ignores "The code is..." text)
        match = re.search(r'\b[A-Z]{3}\b', content)
        
        if match:
            code = match.group(0)
            print(f"✅ Web Resolved: Nearest airport to {clean_name} is {code}")
            return code
        else:
            print(f"⚠️ Could not find valid 3-letter code in: {content}")
            return None
            
    except Exception as e:
        print(f"⚠️ Dynamic Resolve Failed: {e}")
    
    return None

# ==========================================
# ✈️ FLIGHT SEARCH TOOL
# ==========================================
@tool
def search_flights(source: str, destination: str, date: str):
    """
    Fetches REAL-TIME flight data using Amadeus with Dynamic IATA Resolution.
    """
    flights = []
    
    try:
        # Resolve IATA codes dynamically
        origin_code = get_iata_code(source)
        dest_code = get_iata_code(destination)

        if not origin_code or not dest_code:
            return json.dumps({"error": f"Could not locate airports for {source} or {destination}. Please check spelling."})

        print(f"✈️ Searching Flights: {origin_code} -> {dest_code} on {date}")

        # Call Amadeus API
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=date,
            adults=1,
            currencyCode='INR',
            max=5
        )
        
        if response.data:
            for offer in response.data:
                itinerary = offer['itineraries'][0]
                segment = itinerary['segments'][0]
                
                # Parse Duration
                dur_iso = itinerary['duration'] 
                dur = dur_iso.replace("PT", "").replace("H", "h ").replace("M", "m").lower()
                
                # Parse Airline
                code = segment['carrierCode']
                name = AIRLINES.get(code, code)
                
                flights.append({
                    "airline": name,
                    "number": f"{code}-{segment['number']}",
                    "dep": segment['departure']['at'].split("T")[1][:5],
                    "arr": segment['arrival']['at'].split("T")[1][:5],
                    "dur": dur,
                    "price": int(float(offer['price']['total'])),
                    "stops": len(itinerary['segments']) - 1,
                    "from_city": source.title(),     
                    "to_city": destination.title()   
                })
            
            return json.dumps(flights)
        else:
            print("⚠️ Amadeus found no flights.")

    except Exception as e:
        print(f"⚠️ Flight Search Error: {e}")

    # --- STRATEGY 3: Web Search Fallback ---
    print(f"🔄 Amadeus empty/failed. Trying Web Search...")
    try:
        query = f"flights from {source} to {destination} on {date} price"
        raw_results = tavily_tool.invoke(query)
        # Return special marker for LLM to parse later
        return f"WEB_SEARCH_RESULTS: {str(raw_results)}" 
    except Exception as e:
        return json.dumps({"error": str(e)})
    
# ==========================================
# 🚆 TRAIN SEARCH TOOL
# ==========================================
class TrainClass(BaseModel):
    name: str = Field(description="Class name like 'SL', '3A', '2A', '1A', 'CC'")
    price: float = Field(description="Price in INR")
    status: str = Field(description="REALISTIC Status. e.g. 'Available 12', 'WL 45', 'RAC 10'. NEVER use '(Approx)'.")

class TrainInfo(BaseModel):
    name: str = Field(description="Name of the train")
    number: str = Field(description="Train number")
    departure_time: str = Field(description="HH:MM format")
    arrival_time: str = Field(description="HH:MM format")
    duration: str = Field(description="Duration e.g., '12h 30m'")
    from_station: str = Field(description="Origin station code")
    to_station: str = Field(description="Destination station code")
    classes: List[TrainClass] = Field(description="List of available classes with realistic status")

class TrainList(BaseModel):
    trains: List[TrainInfo]

@tool
def search_trains(source: str, destination: str, date: str):
    """
    Searches for Train Timetables and returns STRICT JSON data.
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
    Extract train details from the following search results.
    
    CONTEXT:
    Source: {source}
    Destination: {destination}
    Date: {date}
    
    SEARCH RESULTS:
    {raw_results}
    
    🚨 IMPORTANT INSTRUCTIONS FOR REALISM:
    1. Sleeper Class (SL)**: You MUST extract 'SL' or 'Sleeper' class if listed. Do NOT ignore it.
       - If SL price is missing, Estimate it at ~₹500-900.
       - If 3A price is missing, Estimate it at ~₹1800-2500.
    2. **Availability**: You MUST extract or generate specific numbers.
       - GOOD: "Available 23", "WL 56", "RAC 12", "Available 104"
       - BAD: "Available (Approx)", "Waitlist", "Available"
       - If the exact number is missing in the text, GENERATE a realistic number based on the train type (e.g. SL usually has high availability or high WL).
    
    3. **Prices**:
       - If missing, ESTIMATE: SL=~800, 3A=~2000, 2A=~3000.

    4. **Classes**:
       - Return a list of classes (SL, 3A, 2A) for each train.
    """
    
    try:
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