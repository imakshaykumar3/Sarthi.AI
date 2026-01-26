from dotenv import load_dotenv
load_dotenv()

import uvicorn
import aiosqlite 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver 
from typing import Dict, Any

from database import get_db, init_db
from schemas import UserMessage
from graph import workflow 
from models import Trip

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

agent_with_memory = None
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