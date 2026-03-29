from typing import Literal, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class BenchmarkRequest(BaseModel):
    prompt: str
    models: Optional[List[str]] = None
    tier: Literal["default", "extended", "all"] = "default"
    criteria: Literal["fastest", "cheapest", "balanced"] = "balanced"

class ModelResult(BaseModel):
    model_key: str
    api_name: str
    response: Optional[str] = None
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    status: Literal["success", "error", "timeout"]
    error_message: Optional[str] = None

class BenchmarkSummary(BaseModel):
    fastest: Optional[str] = None
    cheapest: Optional[str] = None
    recommended: Optional[str] = None
    criteria_used: str

class BenchmarkResponse(BaseModel):
    benchmark_id: str
    prompt: str
    criteria: str
    results: List[ModelResult]
    summary: BenchmarkSummary
    total_duration_ms: float
    created_at: datetime
