from typing import Literal, Dict, List
from pydantic import BaseModel

class ModelInfo(BaseModel):
    api_name: str
    tier: Literal["default", "extended"]
    param_size: int
    cost_per_1k_prompt_tokens: float = 0.0
    cost_per_1k_completion_tokens: float = 0.0
    active: bool = True

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    "llama-70b": ModelInfo(
        api_name="meta-llama/llama-3.3-70b-instruct:free",
        tier="default",
        param_size=70,
        active=True
    ),
    "mistral-small": ModelInfo(
        api_name="mistralai/mistral-small-3.1-24b-instruct:free",
        tier="default",
        param_size=24,
        active=False
    ),
    "gemma-27b": ModelInfo(
        api_name="google/gemma-3-27b-it:free",
        tier="default",
        param_size=27,
        active=True
    ),
    "gpt-oss-120b": ModelInfo(
        api_name="openai/gpt-oss-120b:free",
        tier="extended",
        param_size=120,
        active=False
    ),
    "qwen3-80b": ModelInfo(
        api_name="qwen/qwen3-next-80b-a3b-instruct:free",
        tier="extended",
        param_size=80,
        active=True
    ),
    "nemotron-120b": ModelInfo(
        api_name="nvidia/nemotron-3-super-120b-a12b:free",
        tier="extended",
        param_size=120,
        active=True
    ),
    "gemma-12b": ModelInfo(
        api_name="google/gemma-3-12b-it:free",
        tier="default",
        param_size=12,
        active=True
    ),
    "llama-3b": ModelInfo(
        api_name="meta-llama/llama-3.2-3b-instruct:free",
        tier="default",
        param_size=3,
        active=True
    ),
    "arcee-trinity": ModelInfo(
        api_name="arcee-ai/trinity-large-preview:free",
        tier="extended",
        param_size=0,
        active=True
    )
}

def get_models_by_tier(tier: str) -> List[str]:
    return [key for key, model in MODEL_REGISTRY.items() if model.tier == tier and model.active]

def get_all_model_keys() -> List[str]:
    return [key for key, model in MODEL_REGISTRY.items() if model.active]
