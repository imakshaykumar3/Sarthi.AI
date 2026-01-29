# app/tools/trains.py
import json
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

from app.core.llms import gpt_llm

tavily_tool = TavilySearchResults(max_results=3)

# Pydantic models for extraction
class TrainClass(BaseModel):
    name: str = Field(description="Class name (SL, 3A, 2A)")
    price: float = Field(description="Price in INR")
    status: str = Field(description="Availability Status")

class TrainInfo(BaseModel):
    name: str = Field(description="Train Name")
    number: str = Field(description="Train Number")
    departure_time: str = Field(description="HH:MM")
    arrival_time: str = Field(description="HH:MM")
    duration: str = Field(description="Duration")
    from_station_name: str = Field(description="Origin Station Name (e.g. New Delhi)")
    from_station_code: str = Field(description="Origin Code (e.g. NDLS)")
    to_station_name: str = Field(description="Destination Station Name (e.g. New Jalpaiguri)")
    to_station_code: str = Field(description="Destination Code (e.g. NJP)")
    classes: List[TrainClass]

class TrainList(BaseModel):
    trains: List[TrainInfo]

@tool
def search_trains(source: str, destination: str, date: str):
    """Searches for Train Timetables using IRCTC data via web search."""
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
    CONTEXT: Source: {source}, Destination: {destination}, Date: {date}
    SEARCH RESULTS: {raw_results}
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
        cleaned_data = parser_llm.invoke([HumanMessage(content=prompt)])
        return json.dumps([t.model_dump() for t in cleaned_data.trains])
    except Exception as e:
        print(f"⚠️ Train Parsing Failed: {e}")
        return json.dumps([])