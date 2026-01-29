from app.core.llms import greeting_llm


def generate_flight_explanation(context: dict) -> str:
    """
    Converts structured flight context into a clear, trust-building explanation.
    Safe to use BEFORE the user selects a flight.
    """

    prompt = f"""
You are a friendly, experienced travel companion.

The traveler has NOT selected a specific flight yet.
Explain what landing will be like and how the journey continues.

FACTS (guaranteed accurate — never invent):
{context}

STRICT RULES:
- 2–3 short sentences only
- NEVER mention exact arrival times
- NEVER imply a flight is already chosen
- NEVER skip distance if it exists
- Do NOT sound robotic, scripted, or salesy

MANDATORY LOGIC:
- Always mention the arrival airport clearly
- If "direct_arrival" is true:
  • Reassure that the airport is at the destination itself
- If "distance_km" exists:
  • Mention the distance once (in km)
  • Explain how travelers usually cover it (shared taxi / private cab)

TONE:
- Calm
- Reassuring
- Slightly energetic
- Confidence-building
- Human and natural

AVOID:
- Vague phrases like “gateway” without distance
- Over-poetic language
- Listing facts mechanically
"""

    response = greeting_llm.invoke(prompt)
    return str(response.content).strip()
