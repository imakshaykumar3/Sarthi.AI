from typing import Literal
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# User Input Schema
class UserMessage(BaseModel):
    session_id: str
    message: str
    trip_data: Optional[Dict[str, Any]] = None 

class TransportOption(BaseModel):
    type: str 
    provider_name: str 
    number: str 
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    currency: str = "INR"

class HotelOption(BaseModel):
    name: str
    rating: float
    price_per_night: float
    address: str
    amenities: List[str]

class DailyItinerary(BaseModel):
    day: int
    morning: str
    afternoon: str
    evening: str
    local_tips: str

class FinalBill(BaseModel):
    transport_cost: float
    hotel_cost: float
    rental_cost: float
    total_cost: float
    breakdown: Dict[str, float]

class UserIntent(BaseModel):
    category: Literal[
        "select_option",      
        "modify_search",      
        "ask_question",      
        "general_chitchat",   
        "confirm_proceed"     
    ] = Field(description="The category of the user's latest message.")
    
    reasoning: str = Field(description="Brief reason why this category was chosen.")