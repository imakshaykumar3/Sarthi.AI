# #tools.py
# import os
# from amadeus import Client, ResponseError
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.tools import tool

# # --- Initialize Tools ---
# tavily_tool = TavilySearchResults(max_results=5)

# amadeus = Client(
#     client_id=os.getenv('AMADEUS_CLIENT_ID'),
#     client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
# )

# # --- Airline Code Mapper ---
# AIRLINES = {
#     "AI": "Air India",
#     "6E": "IndiGo",
#     "SG": "SpiceJet",
#     "UK": "Vistara",
#     "QP": "Akasa Air",
#     "IX": "Air India Express",
#     "I5": "AirAsia India"
# }

# def get_airline_name(code):
#     return AIRLINES.get(code, code) # Returns "Air India" if found, else just "AI"

# # --- Helper for Tavily Fallback ---
# def search_flights_with_tavily(source, destination, date):
#     print(f"⚠️ Switching to Tavily for {source}->{destination}...")
#     query = f"Indigo Akasa Air India SpiceJet flight ticket price {source} to {destination} on {date} list in INR"
#     return tavily_tool.invoke(query)

# # --- Tool Definitions ---

# @tool
# def search_flights(source: str, destination: str, date: str):
#     """
#     Searches for flights. Merges Amadeus (Official) + Tavily (LCCs).
#     """
#     results_pool = []
    
#     # PART 1: AMADEUS
#     try:
#         # Get Codes
#         origin_res = amadeus.reference_data.locations.get(keyword=source, subType="CITY")
#         dest_res = amadeus.reference_data.locations.get(keyword=destination, subType="CITY")
        
#         if origin_res.data and dest_res.data:
#             origin_code = origin_res.data[0]['iataCode']
#             dest_code = dest_res.data[0]['iataCode']
            
#             flight_response = amadeus.shopping.flight_offers_search.get(
#                 originLocationCode=origin_code,
#                 destinationLocationCode=dest_code,
#                 departureDate=date,
#                 adults=1,
#                 currencyCode='INR',
#                 max=10 
#             )
            
#             if flight_response.data:
#                 for offer in flight_response.data:
#                     price = offer['price']['total']
#                     seg = offer['itineraries'][0]['segments'][0]
#                     carrier_code = seg['carrierCode']
#                     carrier_name = get_airline_name(carrier_code) # <--- FIX: Get Full Name
#                     f_num = seg['number']
#                     dep = seg['departure']['at'].split('T')[1][:5]
#                     dur = offer['itineraries'][0]['duration'][2:]
                    
#                     # We format it so the AI can read it easily
#                     results_pool.append(f"Airline: {carrier_name} ({carrier_code}) {f_num} | Departs: {dep} | Duration: {dur} | Price: ₹{price}")
#     except Exception as e:
#         print(f"Amadeus Error: {e}")

#     # PART 2: TAVILY (Backup)
#     try:
#         lcc_query = f"Indigo Akasa SpiceJet flight price {source} to {destination} on {date} list in INR"
#         tavily_res = tavily_tool.invoke(lcc_query)
#         results_pool.append(f"\n--- Web Results ---\n{tavily_res}")
#     except Exception as e:
#         print(f"Tavily Error: {e}")

#     if not results_pool:
#         return "No flights found."
        
#     return "\n".join(results_pool)

# @tool
# def search_trains(source: str, destination: str, date: str):
#     """
#     Searches for Train Schedules. 
#     INCLUDES ESTIMATED FARES FALLBACK to prevent 'N/A' prices.
#     """
#     # We ask for a schedule list specifically
#     query = f"train schedule from {source} to {destination} indian railways list of trains"
    
#     try:
#         results = tavily_tool.invoke(query)
        
#         clean_output = []
#         if isinstance(results, list):
#             for item in results:
#                 content = item.get('content', '')
#                 clean_output.append(f"- {content}")
        
        
#         fare_estimates = f"""
#         \n--- STANDARD FARE REFERENCE (Use these if exact live price is missing in the search results) ---
#         Route: {source} to {destination}
#         Approx Distance: Long Distance (>1500km)
#         - Sleeper (SL): ₹850 - ₹1,100 (Approx)
#         - 3rd AC (3A): ₹2,200 - ₹2,600 (Approx)
#         - 2nd AC (2A): ₹3,200 - ₹3,800 (Approx)
#         - 1st AC (1A): ₹5,500+ (Approx)
        
#         (Note to AI: If exact price is not in search results, use these approximate values and mark them as 'Approx'.)
#         """
        
#         # Combine real schedule data with the price cheat-sheet
#         final_data = "\n\n".join(clean_output) + fare_estimates
#         return final_data
        
#     except Exception as e:
#         return f"Error searching trains: {str(e)}"

    
# # tools.py

# import re
# import random
# from langchain_core.tools import tool

# @tool
# def search_hotels(location: str, check_in: str):
#     """
#     REALISTIC hotel/PG/hostel search.
#     - Names, location, stay type: ALWAYS from real search
#     - Price: extracted if available, else estimated
#     - Estimated prices follow realistic ranges & distribution
#     """

#     # ----------------------------
#     # 1️⃣ SEARCH REAL DATA
#     # ----------------------------
#     query = (
#         f"budget hostel PG hotel in {location} "
#         f"with rating and location details "
#         f"for stay on {check_in}"
#     )

#     try:
#         results = tavily_tool.invoke(query)
#     except Exception:
#         results = []

#     # ----------------------------
#     # 2️⃣ EXTRACT STAY CANDIDATES
#     # ----------------------------
#     stays = []

#     if isinstance(results, list):
#         for item in results:
#             text = item.get("content", "")

#             # crude but effective filters
#             if any(k in text.lower() for k in ["hostel", "pg", "hotel", "guest"]):
#                 stays.append(text)

#     # Limit to avoid overload
#     stays = stays[:5]

#     # ----------------------------
#     # 3️⃣ PRICE EXTRACTION / FALLBACK
#     # ----------------------------
#     used_prices = set()
#     enriched_output = []

#     def extract_price(text):
#         match = re.search(r"₹\s?(\d{3,5})", text)
#         if match:
#             return int(match.group(1))
#         return None

#     def estimate_price(stay_type):
#         ranges = {
#             "Dorm Bed": (700, 1000),
#             "Shared Room": (900, 1400),
#             "Private Room": (1200, 2000),
#             "Budget Hotel": (1800, 3000),
#         }
#         low, high = ranges[stay_type]
#         price = random.randrange(low, high, 100)
#         while price in used_prices:
#             price += 100
#         used_prices.add(price)
#         return price

#     # ----------------------------
#     # 4️⃣ INFER STAY TYPE
#     # ----------------------------
#     for text in stays:
#         text_lower = text.lower()

#         if "dorm" in text_lower or "hostel" in text_lower:
#             stay_type = "Hostel"
#             room_type = "Dorm Bed"
#         elif "pg" in text_lower or "shared" in text_lower:
#             stay_type = "PG"
#             room_type = "Shared Room"
#         else:
#             stay_type = "Hotel"
#             room_type = "Private Room"

#         # Try real price
#         price = extract_price(text)

#         if price is None:
#             price = estimate_price(room_type)
#             price_label = f"₹{price} (Approx)"
#         else:
#             price_label = f"₹{price}"

#         enriched_output.append(
#             f"""
#                 STAY FOUND:
#                 {text}

#                 INFERRED:
#                 - Stay Type: {stay_type}
#                 - Room Type: {room_type}
#                 - Price: {price_label}
#                 """
#         )

#     # ----------------------------
#     # 5️⃣ FINAL RULES FOR LLM
#     # ----------------------------
#     rules = f"""
#         IMPORTANT RULES:
#         - Stay names & locations MUST come from search text only
#         - NEVER invent hotel names
#         - Use estimated price ONLY if price not found
#         - Estimated prices must be marked (Approx)
#         - NEVER repeat the same price
#         - Focus on cheapest + best rated stays
#         """

#     return "\n\n".join(enriched_output) + "\n\n" + rules


# @tool
# def search_local_attractions(location: str, interest: str):
#     """
#     Searches for attractions.
#     """
#     query = f"must visit {interest} places in {location} with entry fee and timings"
#     try:
#         results = tavily_tool.invoke(query)
#         return results
#     except Exception as e:
#         return f"Error searching attractions: {str(e)}"

import os
import json
import re
from amadeus import Client, ResponseError
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

# --- Initialize Tools ---
tavily_tool = TavilySearchResults(max_results=5)

# ✅ REAL-TIME FLIGHT API
amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

AIRLINES = {
    "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet", "UK": "Vistara",
    "QP": "Akasa Air", "IX": "Air India Express", "I5": "AirAsia", "G8": "Go First"
}

# @tool
# def search_flights(source: str, destination: str, date: str):
#     """
#     Fetches REAL-TIME flight data.
#     1. Tries Amadeus API (Official Data).
#     2. Falls back to Web Search (Tavily) if API fails.
#     """
#     flights = []
    
#     # --- STRATEGY 1: Amadeus API (Preferred) ---
#     try:
#         origin_res = amadeus.reference_data.locations.get(keyword=source, subType="CITY")
#         dest_res = amadeus.reference_data.locations.get(keyword=destination, subType="CITY")
        
#         if origin_res.data and dest_res.data:
#             origin_code = origin_res.data[0]['iataCode']
#             dest_code = dest_res.data[0]['iataCode']
            
#             response = amadeus.shopping.flight_offers_search.get(
#                 originLocationCode=origin_code,
#                 destinationLocationCode=dest_code,
#                 departureDate=date,
#                 adults=1,
#                 currencyCode='INR',
#                 max=5
#             )
            
#             if response.data:
#                 for offer in response.data:
#                     itinerary = offer['itineraries'][0]
#                     segment = itinerary['segments'][0]
                    
#                     # Duration
#                     dur_iso = itinerary['duration'] # PT2H30M
#                     dur = dur_iso.replace("PT", "").replace("H", "h ").replace("M", "m").lower()
                    
#                     # Airline
#                     code = segment['carrierCode']
#                     name = AIRLINES.get(code, code)
                    
#                     # Times (Splitting "2024-01-30T10:30:00")
#                     dep = segment['departure']['at'].split("T")[1][:5]
#                     arr = segment['arrival']['at'].split("T")[1][:5]
                    
#                     flights.append({
#                         "airline": name,
#                         "number": f"{code}-{segment['number']}",
#                         "dep": dep,
#                         "arr": arr,
#                         "dur": dur,
#                         "price": int(float(offer['price']['total'])),
#                         "stops": len(itinerary['segments']) - 1
#                     })
                
#                 return json.dumps(flights)

#     except Exception as e:
#         print(f"⚠️ Amadeus failed, switching to Web Search: {e}")

#     # --- STRATEGY 2: Web Search Fallback (If API fails) ---
#     try:
#         query = f"flight schedule {source} to {destination} on {date} indigo spicejet air india departure times and price"
#         results = tavily_tool.invoke(query)
#         return f"WEB_SEARCH_RESULTS: {str(results)}"
#     except Exception as e:
#         return json.dumps({"error": str(e)})
# backend/tools.py

@tool
def search_flights(source: str, destination: str, date: str):
    """
    Fetches REAL-TIME flight data.
    """
    flights = []
    
    try:
        origin_res = amadeus.reference_data.locations.get(keyword=source, subType="CITY")
        dest_res = amadeus.reference_data.locations.get(keyword=destination, subType="CITY")
        
        if origin_res.data and dest_res.data:
            origin_code = origin_res.data[0]['iataCode']
            dest_code = dest_res.data[0]['iataCode']
            
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
                    
                    # Duration
                    dur_iso = itinerary['duration'] 
                    dur = dur_iso.replace("PT", "").replace("H", "h ").replace("M", "m").lower()
                    
                    # Airline
                    code = segment['carrierCode']
                    name = AIRLINES.get(code, code)
                    
                    # Times
                    dep = segment['departure']['at'].split("T")[1][:5]
                    arr = segment['arrival']['at'].split("T")[1][:5]
                    
                    flights.append({
                        "airline": name,
                        "number": f"{code}-{segment['number']}",
                        "dep": dep,
                        "arr": arr,
                        "dur": dur,
                        "price": int(float(offer['price']['total'])),
                        "stops": len(itinerary['segments']) - 1,
                        
                        # 🚨 NEW FIELDS ADDED HERE:
                        "from_city": source.title(),  # e.g. "Delhi"
                        "to_city": destination.title() # e.g. "Darjeeling"
                    })
                
                return json.dumps(flights)

    except Exception as e:
        print(f"⚠️ Amadeus failed: {e}")

    # --- STRATEGY 2: Web Search Fallback ---
    try:
        query = (
            f"flight schedule {source} to {destination} on {date} "
            f"indigo spicejet akasa air india express. "
            f"Show flight numbers (e.g. 6E-123), departure times, and price in INR."
        )
        results = tavily_tool.invoke(query)
        # We include the source/dest in the string so the LLM can extract them if needed
        return f"WEB_SEARCH_RESULTS for flight from {source} to {destination}: {str(results)}"
    except Exception as e:
        return json.dumps({"error": str(e)})

# backend/tools.py

@tool
def search_trains(source: str, destination: str, date: str):
    """
    Searches for Train Timetables using a targeted query that includes the specific date.
    """
    query = f"trains from {source} to {destination} on {date} schedule price and availability"
    
    try:
        results = tavily_tool.invoke(query)
        return str(results)
    except Exception as e:
        return f"Error: {e}"

@tool
def search_hotels(location: str, check_in: str):
    """
    Searches for hotels using Tavily.
    """
    query = f"budget hostel PG hotel in {location} with rating and location details for stay on {check_in}"
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