from .model_registry import MODEL_REGISTRY

def calculate_cost(model_key: str, prompt_tokens: int, completion_tokens: int) -> float:
    model = MODEL_REGISTRY.get(model_key)
    if not model or prompt_tokens is None or completion_tokens is None:
        return 0.0
    
    prompt_cost = (prompt_tokens / 1000) * model.cost_per_1k_prompt_tokens
    completion_cost = (completion_tokens / 1000) * model.cost_per_1k_completion_tokens
    
    return prompt_cost + completion_cost
