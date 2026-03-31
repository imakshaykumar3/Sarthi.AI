# app/agent/graph.py
from langgraph.graph import StateGraph, END
from app.schemas.state import AgentState
from app.agent.nodes.extractor import extraction_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.search import (
    flight_search_node,
    train_search_node,
    hotel_search_node
)
from app.agent.nodes.responder import response_node
from app.agent.nodes.greeting import greeting_node
from app.agent.nodes.save_itinerary_node import save_itinerary_node

# --- Define the Router Logic ---
def route_planner(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    
    # Logic: If we are ready to search transport, go to the stream pipeline
    if phase == "ready_to_search":
        return "greeting_gen" 
    
    # Logic: If user said 'Yes' to hotels, go to the hotel search node
    if phase == "search_hotels":
        return "hotel_search"
    
    # Logic: If we are presenting hotels or confirming transport, go to responder
    if phase in ["confirm_transport", "presenting_hotels"]:
        return "responder"
    
    # Default fallback to the responder for chitchat/info gathering
    return "responder"

# --- Initialize Graph ---
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("extractor", extraction_node)
workflow.add_node("planner", planner_node)
workflow.add_node("greeting_gen", greeting_node)
workflow.add_node("flight_search", flight_search_node)
workflow.add_node("train_search", train_search_node)
workflow.add_node("hotel_search", hotel_search_node)
workflow.add_node("responder", response_node)
workflow.add_node("saver", save_itinerary_node)

# --- Define Edges ---

# 1. Start with extraction then plan
workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "planner")

# 2. Conditional routing from Planner
# The keys in the dictionary map the return value of route_planner to the node name
workflow.add_conditional_edges(
    "planner", 
    route_planner,
    {
        "greeting_gen": "greeting_gen",
        "hotel_search": "hotel_search",
        "responder": "responder"
    }
)

# 3. Pipeline for Transport (Streamed)
workflow.add_edge("greeting_gen", "flight_search")
workflow.add_edge("flight_search", "train_search")
workflow.add_edge("train_search", "saver")
workflow.add_edge("saver", END)

# 4. Hotel Path
# After searching hotels, we MUST go to responder to format the Gemini table
workflow.add_edge("hotel_search", "responder")

# 5. End of Conversation turn
workflow.add_edge("responder", END)
