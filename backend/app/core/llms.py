# app/core/llms.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GOOGLE_API_KEY

# --- Logic Brain ---
gpt_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# --- Content Engine ---
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.4
)

greeting_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.4
)

# --- Data Cleaner ---
data_cleaner_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0
)
