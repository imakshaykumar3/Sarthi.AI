from typing import Optional, Dict

# Indian Airports
AIRPORTS: Dict[str, Dict[str, str]] = {

    # Metro Cities
    "delhi": {
        "iata": "DEL",
        "airport": "Indira Gandhi International Airport",
        "city": "Delhi"
    },

    "new delhi": {
        "iata": "DEL",
        "airport": "Indira Gandhi International Airport",
        "city": "Delhi"
    },

    "mumbai": {
        "iata": "BOM",
        "airport": "Chhatrapati Shivaji Maharaj International Airport",
        "city": "Mumbai"
    },

    "bangalore": {
        "iata": "BLR",
        "airport": "Kempegowda International Airport",
        "city": "Bengaluru"
    },

    "bengaluru": {
        "iata": "BLR",
        "airport": "Kempegowda International Airport",
        "city": "Bengaluru"
    },

    "kolkata": {
        "iata": "CCU",
        "airport": "Netaji Subhas Chandra Bose International Airport",
        "city": "Kolkata"
    },

    "chennai": {
        "iata": "MAA",
        "airport": "Chennai International Airport",
        "city": "Chennai"
    },

    "hyderabad": {
        "iata": "HYD",
        "airport": "Rajiv Gandhi International Airport",
        "city": "Hyderabad"
    },

    "pune": {
        "iata": "PNQ",
        "airport": "Pune Airport",
        "city": "Pune"
    },

    "ahmedabad": {
        "iata": "AMD",
        "airport": "Sardar Vallabhbhai Patel International Airport",
        "city": "Ahmedabad"
    },

    "jaipur": {
        "iata": "JAI",
        "airport": "Jaipur International Airport",
        "city": "Jaipur"
    },

    "lucknow": {
        "iata": "LKO",
        "airport": "Chaudhary Charan Singh Airport",
        "city": "Lucknow"
    },

    "patna": {
        "iata": "PAT",
        "airport": "Jay Prakash Narayan Airport",
        "city": "Patna"
    },

    "ranchi": {
        "iata": "IXR",
        "airport": "Birsa Munda Airport",
        "city": "Ranchi"
    },

    "bhubaneswar": {
        "iata": "BBI",
        "airport": "Biju Patnaik International Airport",
        "city": "Bhubaneswar"
    },

    "goa": {
        "iata": "GOI",
        "airport": "Goa International Airport",
        "city": "Goa"
    },

    "bagdogra": {
        "iata": "IXB",
        "airport": "Bagdogra Airport",
        "city": "Bagdogra"
    },

    "darjeeling": {
        "iata": "IXB",
        "airport": "Bagdogra Airport",
        "city": "Darjeeling"
    },

    "gangtok": {
        "iata": "IXB",
        "airport": "Bagdogra Airport",
        "city": "Gangtok"
    },

    "shimla": {
        "iata": "SLV",
        "airport": "Shimla Airport",
        "city": "Shimla"
    },

    "manali": {
        "iata": "KUU",
        "airport": "Kullu Airport",
        "city": "Kullu"
    },

    "leh": {
        "iata": "IXL",
        "airport": "Kushok Bakula Rimpochee Airport",
        "city": "Leh"
    },

    "srinagar": {
        "iata": "SXR",
        "airport": "Srinagar Airport",
        "city": "Srinagar"
    },

    "kochi": {
        "iata": "COK",
        "airport": "Cochin International Airport",
        "city": "Kochi"
    },

    "kochin": {
        "iata": "COK",
        "airport": "Cochin International Airport",
        "city": "Kochi"
    },

    "trivandrum": {
        "iata": "TRV",
        "airport": "Trivandrum International Airport",
        "city": "Trivandrum"
    },

    "thiruvananthapuram": {
        "iata": "TRV",
        "airport": "Trivandrum International Airport",
        "city": "Trivandrum"
    },

    "coimbatore": {
        "iata": "CJB",
        "airport": "Coimbatore International Airport",
        "city": "Coimbatore"
    },

    "madurai": {
        "iata": "IXM",
        "airport": "Madurai Airport",
        "city": "Madurai"
    },

    "vijayawada": {
        "iata": "VGA",
        "airport": "Vijayawada Airport",
        "city": "Vijayawada"
    },

    "visakhapatnam": {
        "iata": "VTZ",
        "airport": "Visakhapatnam Airport",
        "city": "Visakhapatnam"
    },

    "nagpur": {
        "iata": "NAG",
        "airport": "Dr. Babasaheb Ambedkar International Airport",
        "city": "Nagpur"
    },

    "indore": {
        "iata": "IDR",
        "airport": "Devi Ahilyabai Holkar Airport",
        "city": "Indore"
    },

    "varanasi": {
        "iata": "VNS",
        "airport": "Lal Bahadur Shastri Airport",
        "city": "Varanasi"
    },

    "amritsar": {
        "iata": "ATQ",
        "airport": "Sri Guru Ram Dass Jee International Airport",
        "city": "Amritsar"
    },

    "udaipur": {
        "iata": "UDR",
        "airport": "Maharana Pratap Airport",
        "city": "Udaipur"
    },

    "jodhpur": {
        "iata": "JDH",
        "airport": "Jodhpur Airport",
        "city": "Jodhpur"
    },

    "dehradun": {
        "iata": "DED",
        "airport": "Jolly Grant Airport",
        "city": "Dehradun"
    },

    "agra": {
        "iata": "AGR",
        "airport": "Agra Airport",
        "city": "Agra"
    }
}


def get_airport(city: str) -> Optional[Dict[str, str]]:
    """
    Returns airport details from city name.
    """

    if not city:
        return None

    key = city.strip().lower()

    return AIRPORTS.get(key)