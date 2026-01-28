#llms.py
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. Setup LLM ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is missing. Please check your .env file.")

# --- 1. THE LOGIC BRAIN (GPT-4o-mini) ---
gpt_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# --- 2. THE CONTENT ENGINE (Gemini 2.5 Flash) ---
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.4
)

greeting_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.4
)

# --- 3. THE DATA CLEANER (Gemini 2.5 Flash or Lite) ---
data_cleaner_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    temperature=0
)