import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def get_llm():
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    temperature = float(os.getenv("TEMPERATURE", 0.2))
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
