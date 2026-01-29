# app/agent/nodes/save_itinerary_node.py
from app.schemas.state import AgentState
from app.utils import safe_dict
from app.core.database import SessionLocal
from app.schemas.models import Trip 
from sqlalchemy.future import select

async def save_itinerary_node(state: AgentState):
    session_id = state.get("session_id")
    details = safe_dict(state.get("trip_details"))
    if not session_id: return {}
    
    async with SessionLocal() as session:
        try:
            result = await session.execute(select(Trip).where(Trip.session_id == session_id))
            existing = result.scalars().first()
            if existing:
                existing.source = details.get("source")
                existing.destination = details.get("destination")
            else:
                new_trip = Trip(session_id=session_id, source=details.get("source"), destination=details.get("destination"))
                session.add(new_trip)
            await session.commit()
        except Exception as e:
            print(f"DB Error: {e}")
    return {}