import asyncio
import httpx
from config import settings

class ModelTimeoutError(Exception):
    pass

class ModelCallError(Exception):
    pass

async def call_model(api_name: str, prompt: str, timeout: int) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": api_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 404:
                    raise ModelCallError(f"Model {api_name} not found (404)")
                elif response.status_code == 429:
                    if attempt < max_retries:
                        backoff = (attempt + 1) * 3
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        raise ModelCallError(f"Rate limit exceeded, retries exhausted")
                
                response.raise_for_status()
                result = response.json()
                
                return {
                    "response_text": result["choices"][0]["message"]["content"],
                    "prompt_tokens": result.get("usage", {}).get("prompt_tokens"),
                    "completion_tokens": result.get("usage", {}).get("completion_tokens"),
                    "total_tokens": result.get("usage", {}).get("total_tokens")
                }
        except httpx.TimeoutException:
            raise ModelTimeoutError(f"Model call timed out after {timeout} seconds")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ModelCallError(f"Model {api_name} not found (404)")
            elif e.response.status_code == 429:
                if attempt < max_retries:
                    backoff = (attempt + 1) * 3
                    await asyncio.sleep(backoff)
                    continue
                else:
                    raise ModelCallError(f"Rate limit exceeded, retries exhausted")
            raise ModelCallError(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise ModelCallError(f"Model call failed: {str(e)}")
