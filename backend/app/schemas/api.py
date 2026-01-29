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