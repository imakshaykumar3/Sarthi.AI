#state.py
from typing import TypedDict, Annotated, List, Dict, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


# -----------------------------
# Trip Details (Stable Memory)
# -----------------------------
class TripData(TypedDict, total=False):
    source: Optional[str]
    destination: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    budget: Optional[str]
    travelers: Optional[str]


# -----------------------------
# Global Agent State
# -----------------------------
class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    current_phase: str
    trip_details: TripData
    search_results: Optional[str]
    selected_transport: Optional[Dict[str, Any]]
    selected_hotel: Optional[Dict[str, Any]]
    user_interests: Optional[List[str]]
    add_ons: Dict[str, Any]
