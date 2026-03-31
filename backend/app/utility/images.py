# app/utils/images.py
import httpx
from app.core.config import UNSPLASH_ACCESS_KEY

async def get_hotel_image(hotel_name: str, location: str) -> str:
    """Fetches a high-quality hotel image from Unsplash API."""
    if not UNSPLASH_ACCESS_KEY:
        return "https://images.unsplash.com/photo-1566073771259-6a8506099945" # High-quality fallback

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": f"{hotel_name} {location} luxury hotel architecture",
        "per_page": 1,
        "client_id": UNSPLASH_ACCESS_KEY
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"📸 Unsplash Error: {e}")
    
    # Generic high-end travel fallback
    return "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb"