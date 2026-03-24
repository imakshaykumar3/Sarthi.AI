from dotenv import load_dotenv
load_dotenv()

import uvicorn
import aiosqlite 
import json
import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.state import CompiledStateGraph
from typing import Dict, Any, Optional 

from app.core.database import get_db, init_db
from app.schemas.api import UserMessage
from app.agent.graph import workflow 
from app.schemas.models import Trip

# --- App Configuration ---
app = FastAPI(
    title="TravelGenie AI API",
    description="Backend for the Autonomous Travel Agent",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold state
# ✅ FIX: Explicit Type Hint removes the "red line" warning in IDEs
agent_with_memory: Optional[CompiledStateGraph] = None
db_connection = None

@app.on_event("startup")
async def on_startup():
    await init_db()
    
    global agent_with_memory, db_connection
    
    try:
        db_connection = await aiosqlite.connect("checkpoints.db")
        checkpointer = AsyncSqliteSaver(db_connection)
        
        await checkpointer.setup()
        
        agent_with_memory = workflow.compile(checkpointer=checkpointer)
        print("✅ Persistence Layer Initialized (AsyncSqliteSaver)")
        
    except Exception as e:
        print(f"❌ Failed to initialize persistence: {e}")
        raise e

@app.on_event("shutdown")
async def on_shutdown():
    if db_connection:
        await db_connection.close()

@app.get("/")
async def root():
    return {"message": "TravelGenie AI System is Online 🟢"}

# ---------------------------------------------------------
# 🔹 STANDARD CHAT ENDPOINT (For Selections/Confirmations)
# ---------------------------------------------------------
@app.post("/chat")
async def chat_endpoint(user_input: UserMessage):
    if not agent_with_memory:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    session_id = user_input.session_id
    user_text = user_input.message
    trip_data = user_input.trip_data 

    config = {"configurable": {"thread_id": session_id}}

    inputs: Dict[str, Any] = {
        "messages": [HumanMessage(content=user_text)],
        "session_id": session_id 
    }

    if trip_data:
        inputs["trip_details"] = trip_data
        inputs["current_phase"] = "ready_to_search"

    try:
        final_state = await agent_with_memory.ainvoke(inputs, config=config)
    except Exception as e:
        print(f"Error: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

    messages = final_state["messages"]
    ai_response = messages[-1].content if messages else "I encountered an error processing that."
    
    return {
        "session_id": session_id,
        "response": ai_response,
        "current_phase": final_state.get("current_phase", "unknown")
    }

# ---------------------------------------------------------
# 🔹 STREAMING ENDPOINT (For Planning Phase)
# ---------------------------------------------------------
@app.post("/chat/stream")
async def chat_stream_endpoint(user_input: UserMessage):
    """
    Streaming Endpoint: Returns SSE (Server-Sent Events)
    This allows the Greeting -> Flights -> Trains to appear sequentially.
    """
    if not agent_with_memory:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    session_id = user_input.session_id
    config = {"configurable": {"thread_id": session_id}}
    
    inputs = {
        "messages": [HumanMessage(content=user_input.message)],
        "session_id": session_id
    }
    
    if user_input.trip_data:
        inputs["trip_details"] = user_input.trip_data
        inputs["current_phase"] = "ready_to_search"

    async def event_generator():

        async for event in agent_with_memory.astream_events(inputs, config=config, version="v1"): # type: ignore
            
            kind = event["event"]
            name = event.get("name", "")
            
            # 1. Detect Greeting Completion (from greeting_node)
            if kind == "on_chain_end" and name == "greeting_gen":
                try:
                    # Extract the message content from the node output
                    messages = event["data"]["output"]["messages"]
                    output_text = messages[0].content
                    
                    if "GREETING_Start:" in output_text:
                        clean_text = output_text.replace("GREETING_Start: ", "")
                        yield f"data: {json.dumps({'type': 'greeting', 'content': clean_text})}\n\n"
                except Exception as e:
                    print(f"Stream Greeting Error: {e}")

            # 2. Detect Flight Search Completion (from flight_search_node)
            elif kind == "on_chain_end" and name == "flight_search":
                try:
                    raw_data = event["data"]["output"]["search_results"]
                    if "FLIGHTS_DONE:" in raw_data:
                        json_str = raw_data.replace("FLIGHTS_DONE: ", "")
                        payload = json.loads(json_str)

                        event_payload = {
                            "type": "flights",
                            "info": payload.get("info", ""),
                            "data": payload.get("data", [])
                        }

                        yield f"data: {json.dumps(event_payload)}\n\n"

                except Exception as e:
                    print(f"Stream Flight Error: {e}")

            # 3. Detect Train Search Completion (from train_search_node)
            elif kind == "on_chain_end" and name == "train_search":
                try:
                    payload = event["data"]["output"]["search_results"]

                    event_payload = {
                        "type": "trains",
                        "info": payload.get("info", "Train options for your journey"),
                        "data": payload.get("data", [])
                    }

                    yield f"data: {json.dumps(event_payload)}\n\n"

                except Exception as e:
                    print(f"Stream Train Error: {e}")

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/trip/{session_id}")
async def get_trip_history(session_id: str):
    if not agent_with_memory:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    config = {"configurable": {"thread_id": session_id}}
    state = await agent_with_memory.aget_state(config)
    if not state:
        return {"trip_details": None}
    return state.values

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)