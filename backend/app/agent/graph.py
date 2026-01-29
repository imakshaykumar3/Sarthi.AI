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

workflow = StateGraph(AgentState)

workflow.add_node("extractor", extraction_node)
workflow.add_node("planner", planner_node)

# Stream Pipeline
workflow.add_node("greeting_gen", greeting_node)
workflow.add_node("flight_search", flight_search_node)
workflow.add_node("train_search", train_search_node)

# Standard Nodes
workflow.add_node("hotel_search", hotel_search_node)
workflow.add_node("responder", response_node)
workflow.add_node("saver", save_itinerary_node)

# Entry
workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "planner")

# Conditional Routing
def route_planner(state: AgentState):
    phase = state.get("current_phase", "gathering_info")
    
    if phase == "ready_to_search":
        return "greeting_gen" 
    if phase == "search_hotels":
        return "hotel_search"
    if phase == "confirm_transport":
        return "responder"
    
    return "responder" # Default

workflow.add_conditional_edges("planner", route_planner)

# Pipeline Edges
workflow.add_edge("greeting_gen", "flight_search")
workflow.add_edge("flight_search", "train_search")
workflow.add_edge("train_search", "saver")
workflow.add_edge("saver", END)

# Standard Edges
workflow.add_edge("hotel_search", "responder")
workflow.add_edge("responder", END)