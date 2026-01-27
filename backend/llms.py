#llms.py
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. Setup LLM ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is missing. Please check your .env file.")

# --- 1. THE LOGIC BRAIN (GPT-4o-mini) ---
# Use this for: Extraction, Routing, Decision Making
gpt_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# --- 2. THE CONTENT ENGINE (Gemini 2.5 Flash) ---
# Use this for: Parsing Search Results, Writing Greetings, Itineraries
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.4
)

# --- 3. THE DATA CLEANER (Gemini 2.5 Flash or Lite) ---
# Use this for: Converting messy web text into clean JSON (Train tool)
# Why: Cost-effective for processing lots of text.
data_cleaner_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    temperature=0
)