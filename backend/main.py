# # backend/main.py

# from dotenv import load_dotenv
# load_dotenv()

# import uvicorn
# import sqlite3  # ✅ Import sqlite3 for persistence
# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.ext.asyncio import AsyncSession
# from langchain_core.messages import HumanMessage
# # from langgraph.checkpoint.memory import MemorySaver  <-- DELETED
# from langgraph.checkpoint.sqlite import SqliteSaver  # ✅ ADDED: Persistent Checkpointer
# from typing import Dict, Any

# from database import get_db, init_db
# from schemas import UserMessage
# from graph import workflow 
# from models import Trip

# # --- App Configuration ---
# app = FastAPI(
#     title="TravelGenie AI API",
#     description="Backend for the Autonomous Travel Agent",
#     version="2.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
# checkpointer = SqliteSaver(conn)

# # Compile graph with PERMANENT memory
# agent_with_memory = workflow.compile(checkpointer=checkpointer)

# @app.on_event("startup")
# async def on_startup():
#     await init_db()

# @app.get("/")
# async def root():
#     return {"message": "TravelGenie AI System is Online 🟢"}

# @app.post("/chat")
# async def chat_endpoint(user_input: UserMessage, db: AsyncSession = Depends(get_db)):
#     session_id = user_input.session_id
#     user_text = user_input.message
#     trip_data = user_input.trip_data  # ✅ Catch the direct form data

#     config = {"configurable": {"thread_id": session_id}}

#     # 1. Base Input: Always include the user message
#     inputs: Dict[str, Any] = {
#         "messages": [HumanMessage(content=user_text)]
#     }

#     # 2. ⚡ DIRECT FILLING LOGIC ⚡
#     if trip_data:
#         # Inject data directly into state
#         inputs["trip_details"] = trip_data
        
#         # 🚀 CRITICAL: Force the graph to skip extraction and go straight to search
#         inputs["current_phase"] = "ready_to_search"

#     try:
#         # Run the Graph
#         final_state = await agent_with_memory.ainvoke(inputs, config=config)
#     except Exception as e:
#         print(f"Error: {e}") 
#         raise HTTPException(status_code=500, detail=str(e))

#     # Extract Response
#     messages = final_state["messages"]
#     ai_response = messages[-1].content if messages else "I encountered an error processing that."
    
#     return {
#         "session_id": session_id,
#         "response": ai_response,
#         "current_phase": final_state.get("current_phase", "unknown")
#     }

# @app.get("/trip/{session_id}")
# async def get_trip_history(session_id: str):
#     config = {"configurable": {"thread_id": session_id}}
#     state = await agent_with_memory.aget_state(config)
#     if not state:
#         # Return empty structure if session doesn't exist yet
#         return {"trip_details": None}
#     return state.values

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# backend/main.py

from dotenv import load_dotenv
load_dotenv()

import uvicorn
import aiosqlite # ✅ Changed from sqlite3 to aiosqlite
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver # ✅ Use Async Saver
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

# Global variables to hold state
agent_with_memory = None
db_connection = None

@app.on_event("startup")
async def on_startup():
    await init_db()
    
    global agent_with_memory, db_connection
    
    # ✅ Initialize Async Persistence
    try:
        db_connection = await aiosqlite.connect("checkpoints.db")
        checkpointer = AsyncSqliteSaver(db_connection)
        
        # Ensure tables are created
        await checkpointer.setup()
        
        # Compile graph with PERMANENT memory
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
async def chat_endpoint(user_input: UserMessage, db: AsyncSession = Depends(get_db)):
    if not agent_with_memory:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    session_id = user_input.session_id
    user_text = user_input.message
    trip_data = user_input.trip_data 

    config = {"configurable": {"thread_id": session_id}}

    inputs: Dict[str, Any] = {
        "messages": [HumanMessage(content=user_text)]
    }

    if trip_data:
        inputs["trip_details"] = trip_data
        inputs["current_phase"] = "ready_to_search"

    try:
        # Run the Graph (Async)
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