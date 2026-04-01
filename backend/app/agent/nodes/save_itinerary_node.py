from app.schemas.state import AgentState
from app.utils import safe_dict
from app.core.database import SessionLocal
from app.schemas.models import Trip 
from sqlalchemy.future import select

async def save_itinerary_node(state: AgentState):
    session_id = state.get("session_id")
    details = safe_dict(state.get("trip_details"))
    
    # 1. Grab the generated itinerary and selections from the state
    itinerary_data = state.get("final_itinerary")
    selected_hotel = state.get("selected_hotel")
    selected_transport = state.get("selected_transport")

    if not session_id: 
        print("⚠️ Save Itinerary: No session_id found in state.")
        return {}
    
    async with SessionLocal() as session:
        try:
            # 2. Check if the trip record already exists
            result = await session.execute(select(Trip).where(Trip.session_id == session_id))
            existing = result.scalars().first()
            
            if existing:
                # Update existing record
                existing.source = details.get("source")
                existing.destination = details.get("destination")
                existing.start_date = details.get("start_date")
                existing.end_date = details.get("end_date")
                
                # Save the JSON data
                if itinerary_data:
                    existing.final_itinerary = itinerary_data
                
                # Save transport/hotel as a 'bill' or summary
                existing.final_bill = {
                    "hotel": selected_hotel,
                    "transport": selected_transport
                }
                
                print(f"✅ Updated itinerary for session: {session_id}")
            else:
                # Create new record if for some reason it wasn't created during gathering_info
                new_trip = Trip(
                    session_id=session_id,
                    source=details.get("source"),
                    destination=details.get("destination"),
                    start_date=details.get("start_date"),
                    end_date=details.get("end_date"),
                    final_itinerary=itinerary_data,
                    final_bill={
                        "hotel": selected_hotel,
                        "transport": selected_transport
                    }
                )
                session.add(new_trip)
                print(f"✅ Created new trip record for session: {session_id}")

            await session.commit()
            
        except Exception as e:
            await session.rollback()
            print(f"❌ DB Save Error: {e}")
            
    return {}