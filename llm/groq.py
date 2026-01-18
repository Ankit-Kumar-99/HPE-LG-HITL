from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()  

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set!")
    
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key
    )
