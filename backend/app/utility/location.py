# app/utils/location.py
import re
from typing import Optional, Dict
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults
from app.core.llms import data_cleaner_llm

tavily_tool = TavilySearchResults(max_results=3)

def get_ground_transfer_info(
    destination: str,
    airport_city: str,
    airport_name: str
) -> Optional[Dict[str, str]]:
    """
    Returns distance & road time info if destination != airport city.
    """

    if destination.lower() == airport_city.lower():
        return None

    query = f"Distance from {airport_name} to {destination} in km and travel time by road"

    try:
        results = tavily_tool.invoke(query)

        prompt = f"""
        Extract distance (km) and road travel time from the text below.

        TEXT:
        {results}

        RETURN STRICT JSON:
        {{
          "distance_km": "number",
          "road_time": "X–Y hours"
        }}
        """

        response = data_cleaner_llm.invoke(prompt)
        text = str(response.content)

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return eval(match.group(0))  # safe here because controlled
    except Exception:
        pass

    return None
