import requests
from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, MODEL_MAP

def send_prompt(prompt: str, model: str):
    if model not in MODEL_MAP:
        raise ValueError(f"Model '{model}' not supported.")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_MAP[model],
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
