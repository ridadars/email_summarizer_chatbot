import os
from dotenv import load_dotenv

# absolute path to .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
print("Looking for .env at:", dotenv_path)

load_dotenv(dotenv_path)

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("MODEL_NAME:", os.getenv("MODEL_NAME"))
print("TEMPERATURE:", os.getenv("TEMPERATURE"))
