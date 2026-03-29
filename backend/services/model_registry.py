from typing import Literal, Dict, List
from pydantic import BaseModel

class ModelInfo(BaseModel):
    api_name: str
    tier: Literal["default", "extended"]
    param_size: int
    cost_per_1k_prompt_tokens: float = 0.0
    cost_per_1k_completion_tokens: float = 0.0

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    "llama-70b": ModelInfo(
        api_name="meta-llama/llama-3.3-70b-instruct:free",
        tier="default",
        param_size=70
    ),
    "mistral-small": ModelInfo(
        api_name="mistralai/mistral-small-3.1-24b-instruct:free",
        tier="default",
        param_size=24
    ),
    "gemma-27b": ModelInfo(
        api_name="google/gemma-3-27b-it:free",
        tier="default",
        param_size=27
    ),
    "gpt-oss-120b": ModelInfo(
        api_name="openai/gpt-oss-120b:free",
        tier="extended",
        param_size=120
    ),
    "qwen3-80b": ModelInfo(
        api_name="qwen/qwen3-next-80b-a3b-instruct:free",
        tier="extended",
        param_size=80
    ),
    "nemotron-120b": ModelInfo(
        api_name="nvidia/nemotron-3-super-120b-a12b:free",
        tier="extended",
        param_size=120
    )
}

def get_models_by_tier(tier: str) -> List[str]:
    return [key for key, model in MODEL_REGISTRY.items() if model.tier == tier]

def get_all_model_keys() -> List[str]:
    return list(MODEL_REGISTRY.keys())
