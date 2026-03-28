from langchain_groq import ChatGroq
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import get_config

def get_llm():
    cfg = get_config()
    if not cfg["GROQ_API_KEY"]:
        raise ValueError("GROQ_API_KEY is not set. Add it to .streamlit/secrets.toml or environment variables.")
    return ChatGroq(
        api_key=cfg["GROQ_API_KEY"],
        model=cfg["GROQ_MODEL"],
        temperature=0.3,
    )
