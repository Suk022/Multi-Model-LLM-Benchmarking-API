import requests
from config import settings

def send_prompt(prompt: str, model: str):
    if model not in settings.MODEL_MAP:
        raise ValueError(f"Model '{model}' not supported.")
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": settings.MODEL_MAP[model],
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(settings.OPENROUTER_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
