import asyncio
import time
from typing import List
from schemas.benchmark import ModelResult
from .model_registry import MODEL_REGISTRY
from .openrouter_client import call_model, ModelTimeoutError, ModelCallError
from .cost_calculator import calculate_cost

async def run_benchmark(prompt: str, model_keys: List[str], timeout: int) -> List[ModelResult]:
    async def call_single_model(model_key: str):
        start_time = time.perf_counter()
        model = MODEL_REGISTRY.get(model_key)
        
        if not model:
            return ModelResult(
                model_key=model_key,
                api_name="",
                status="error",
                error_message=f"Model {model_key} not found in registry"
            )
        
        try:
            result = await call_model(model.api_name, prompt, timeout)
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            cost = calculate_cost(
                model_key,
                result["prompt_tokens"],
                result["completion_tokens"]
            )
            
            return ModelResult(
                model_key=model_key,
                api_name=model.api_name,
                response=result["response_text"],
                latency_ms=latency_ms,
                prompt_tokens=result["prompt_tokens"],
                completion_tokens=result["completion_tokens"],
                total_tokens=result["total_tokens"],
                estimated_cost_usd=cost,
                status="success"
            )
        except ModelTimeoutError:
            return ModelResult(
                model_key=model_key,
                api_name=model.api_name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                status="timeout"
            )
        except (ModelCallError, Exception) as e:
            return ModelResult(
                model_key=model_key,
                api_name=model.api_name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                status="error",
                error_message=str(e)
            )
    
    tasks = [call_single_model(key) for key in model_keys]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if isinstance(r, ModelResult)]
