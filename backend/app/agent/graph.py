# backend/app/agent/graph.py
from langgraph.graph import StateGraph, END
from app.schemas.state import AgentState

# Import Nodes
from app.agent.nodes.extractor import extraction_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.greeting import greeting_node
from app.agent.nodes.responder import response_node
from app.agent.nodes.save_itinerary_node import save_itinerary_node
from app.agent.nodes.itinerary import itinerary_node 
from app.agent.nodes.search import (
    flight_search_node,
    train_search_node,
    hotel_search_node,
    rental_search_node,
    return_transport_search_node
)
from app.agent.nodes.bill_generator import generate_bill_node
from app.agent.nodes.email_node import send_email_node

# Initialize Graph
workflow = StateGraph(AgentState)

# --- 1. Define Nodes ---
workflow.add_node("extractor", extraction_node)
workflow.add_node("planner", planner_node)
workflow.add_node("greeting_gen", greeting_node)
workflow.add_node("flight_search", flight_search_node)
workflow.add_node("train_search", train_search_node)
workflow.add_node("hotel_search", hotel_search_node)
workflow.add_node("itinerary_gen", itinerary_node)
workflow.add_node("responder", response_node)
workflow.add_node("saver", save_itinerary_node)
workflow.add_node("rental_search", rental_search_node)                
workflow.add_node("return_transport", return_transport_search_node)    
workflow.add_node("bill_generator", generate_bill_node)
workflow.add_node("send_email", send_email_node)

# --- 2. Define Entry & Fixed Edges ---
# The entry point is always the extractor to capture user intent from the latest message.
workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "planner")

# --- 3. Define Conditional Routing ---
def route_planner(state: AgentState):
    """
    Determines which specialized node to run based on the 'current_phase' 
    set by the planner_node.
    """
    phase = state.get("current_phase", "gathering_info")
    
    print(f"🛤️ Graph Router: Routing phase '{phase}'")

    if phase == "ready_to_search":
        return "greeting_gen" 
    
    if phase == "search_hotels":
        return "hotel_search"
    
    if phase == "itinerary":
        return "itinerary_gen"

    if phase == "search_rentals":
        return "rental_search"
        
    if phase == "search_return_transport":
        return "return_transport"

    if phase == "generate_bill":
        return "bill_generator"
        
    if phase == "send_email":
        return "send_email"
    
    # Fallback for gathering_info, confirm_transport, and presenting_hotels
    return "responder" 

# Planner decides the phase, route_planner executes the transition
workflow.add_conditional_edges("planner", route_planner)

# --- 4. Define Pipeline & Terminal Edges ---

# A. Transport Pipeline (Streaming Flow)
# After streaming flights and trains, we must END so the frontend 
# can display the options and wait for a user click.
workflow.add_edge("greeting_gen", "flight_search")
workflow.add_edge("flight_search", "train_search")
workflow.add_edge("train_search", END) 

# B. Hotel Pipeline
# hotel_search finds data -> responder formats it to JSON -> END (wait for selection)
workflow.add_edge("hotel_search", "responder")

# C. Itinerary Pipeline (The Final Act)
# itinerary_gen builds the plan -> saver writes to DB -> END (Success)
workflow.add_edge("itinerary_gen", "saver") 

# D. Local Travel & Return Transport Pipeline (The Encore)
# Both of these must stop at END so the frontend can render the choices for the user
workflow.add_edge("rental_search", END) 
workflow.add_edge("return_transport", END)

# E. Bill Generation & Email Pipeline
# generate_bill builds the final markdown -> saver writes to DB -> END
# send_email triggers the email sending -> saver writes to DB -> END
workflow.add_edge("bill_generator", "saver")
workflow.add_edge("send_email", "saver")
workflow.add_edge("saver", END)

# F. Standard Responder Edge
# Ensures confirmation messages and "gathering info" questions reach the user.
workflow.add_edge("responder", END)