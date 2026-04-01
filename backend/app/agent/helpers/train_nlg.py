#backend/app/agent/helpers/train_nlg.py
from app.core.llms import greeting_llm


def generate_train_explanation(context: dict) -> str:
    """
    Converts structured train arrival facts into a natural, trustworthy explanation.
    No hardcoding. Fully context-driven.
    """

    prompt = f"""
      You are a confident, well-travelled Indian travel companion.

      Explain what happens after the train journey ends, using the facts below.

      FACTS (always accurate, do not invent anything):
      {context}

      ABSOLUTE RULES:
      - 2–3 short sentences only
      - Sound warm, human, and reassuring
      - NEVER sound robotic or salesy
      - NEVER ignore distance if it is provided

      MANDATORY LOGIC:
      - If direct_arrival is true:
        • Clearly say the traveler arrives directly at the destination station
      - If distance_km exists:
        • Mention the distance once, naturally
        • Explain how the traveler usually covers it
      - If transport_modes include something scenic or iconic:
        • Mention it as an optional experience (not required, not forced)
      - If no special experience exists:
        • Keep the explanation simple and practical

      STYLE:
      - Calm confidence
      - Light excitement
      - Trust-building, not promotional
      """

    response = greeting_llm.invoke(prompt)
    return str(response.content).strip()
