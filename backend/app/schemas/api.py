# app/schemas/api.py
from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field

# User Input Schema
class UserMessage(BaseModel):
    session_id: str
    message: str
    trip_data: Optional[Dict[str, Any]] = None 

class UserIntent(BaseModel):
    category: Literal[
        "select_option",      
        "modify_search",      
        "ask_question",      
        "general_chitchat",   
        "confirm_proceed"     
    ] = Field(description="The category of the user's latest message.")
    
    reasoning: str = Field(description="Brief reason why this category was chosen.")

class HotelSchema(BaseModel):
    name: str = Field(description="Name of the hotel or homestay")
    location: str = Field(description="Specific area, e.g., Mall Road, Darjeeling")
    price: int = Field(description="Price in INR. Must be an integer.")
    room_type: Literal["Hostel Bed", "Private Room", "Entire Home", "Luxury Suite"] = Field(
        description="Categorize the stay type based on the price and description."
    )
    rating: str = Field(description="Rating out of 5 stars (e.g., 4.2/5)")
    description: str = Field(description="A 1-sentence catchy description.")
    amenities: List[str] = Field(description="List of amenities like Wifi, AC, etc.")

class HotelListSchema(BaseModel):
    hotels: List[HotelSchema]