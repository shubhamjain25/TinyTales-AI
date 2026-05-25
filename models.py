from dotenv import load_dotenv
from langchain_groq import ChatGroq
from schema import GROQ_MODEL
from cartesia import Cartesia
import os

load_dotenv()

def get_deterministic_llm():
    return ChatGroq(model=GROQ_MODEL, temperature=0.2)

def get_creative_llm():
    return ChatGroq(model=GROQ_MODEL, temperature=0.7)

def get_cartesia_client() -> Cartesia:
    api_key = os.environ.get("CARTESIA_API_KEY")
    if not api_key:
        raise ValueError("CARTESIA_API_KEY is not set in environment.")
    return Cartesia(api_key=api_key)