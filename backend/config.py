import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL_MAP = {
    "mistral": "mistralai/mistral-7b-instruct",
    "llama": "meta-llama/llama-3.1-8b-instruct"
}

LOG_FILE = "chat_logs.csv"
