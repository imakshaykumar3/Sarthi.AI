#llms.py
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. Setup LLM ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is missing. Please check your .env file.")

# We use a slightly smarter model for extraction to ensure valid JSON
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

# Reasoning & extraction model
# gpt_llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0
# )
gpt_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0
)


# Narrative & itinerary model
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.4
)
