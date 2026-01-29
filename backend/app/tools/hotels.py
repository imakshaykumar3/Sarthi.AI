# app/tools/hotels.py
from langchain_core.tools import tool
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(max_results=3)

@tool
def search_hotels(location: str, check_in: str):
    """Searches for hotels using Tavily."""
    query = f"budget hostel PG hotel in {location} price rating stay on {check_in}"
    try:
        results = tavily_tool.invoke(query)
        return str(results)
    except Exception:
        return "No hotels found."