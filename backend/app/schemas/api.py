# backend/app/schemas/api.py
from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- User Input Schemas ---
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

# --- Hotel Schemas (THE MISSING PART) ---
class HotelSchema(BaseModel):
    name: str = Field(description="Name of the hotel")
    location: str = Field(description="Specific area in the destination")
    price: int = Field(description="Approximate price per night in INR")
    room_type: Literal["Hostel Bed", "Private Room", "Entire Home", "Luxury Suite"] = Field(
        description="Type of accommodation"
    )
    rating: str = Field(description="Rating out of 5 stars")
    description: str = Field(description="A catchy description")
    amenities: List[str] = Field(description="List of amenities")
    image_url: Optional[str] = Field(None, description="URL of the hotel image")

class HotelListSchema(BaseModel):
    hotels: List[HotelSchema]