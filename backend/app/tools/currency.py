import os
import time
import requests

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Cache validity (1 hour)
CACHE_DURATION = 60 * 60

_rate_cache = {
    "rate": None,
    "timestamp": 0,
}


def get_conversion_rate(
    base_currency: str = "USD",
    target_currency: str = "INR"
):
    """
    Returns the conversion rate.
    Uses an in-memory cache for 1 hour.
    """

    global _rate_cache

    now = time.time()

    # Return cached rate if still valid
    if (
        _rate_cache["rate"] is not None
        and now - _rate_cache["timestamp"] < CACHE_DURATION
    ):
        print("✅ Using cached exchange rate")
        return _rate_cache["rate"]

    print("🌍 Fetching exchange rate from API...")

    url = (
        f"https://v6.exchangerate-api.com/v6/"
        f"{API_KEY}/pair/{base_currency}/{target_currency}"
    )

    response = requests.get(url, timeout=10)

    response.raise_for_status()

    data = response.json()

    if data["result"] != "success":
        raise Exception(data)

    rate = data["conversion_rate"]

    _rate_cache["rate"] = rate
    _rate_cache["timestamp"] = now

    return rate


@tool
def convert_currency(
    amount: float,
    base_currency: str = "USD",
    target_currency: str = "INR",
):
    """
    Convert currency using cached exchange rate.
    """

    rate = get_conversion_rate(
        base_currency,
        target_currency
    )

    return {
        "success": True,
        "original_amount": amount,
        "original_currency": base_currency,
        "converted_amount": round(amount * rate, 2),
        "target_currency": target_currency,
        "conversion_rate": rate
    }