import time
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.benchmark import BenchmarkRequest, BenchmarkResponse
from services.model_registry import get_models_by_tier, get_all_model_keys
from services.executor import run_benchmark
from services.ranker import rank_results
from db.service import save_benchmark
from db.database import get_db
from config import settings

router = APIRouter()

@router.post("/benchmark", response_model=BenchmarkResponse)
async def create_benchmark(
    request: BenchmarkRequest,
    db: AsyncSession = Depends(get_db)
):
    if request.models:
        model_keys = request.models
    elif request.tier == "all":
        model_keys = get_all_model_keys()
    else:
        model_keys = get_models_by_tier(request.tier)
    
    if not model_keys:
        raise HTTPException(status_code=400, detail="No valid models found")
    
    start_time = time.perf_counter()
    results = await run_benchmark(request.prompt, model_keys, settings.DEFAULT_TIMEOUT_SECONDS)
    total_duration_ms = (time.perf_counter() - start_time) * 1000
    
    summary = rank_results(results, request.criteria)
    
    response = BenchmarkResponse(
        benchmark_id=str(uuid.uuid4()),
        prompt=request.prompt,
        criteria=request.criteria,
        results=results,
        summary=summary,
        total_duration_ms=total_duration_ms,
        created_at=datetime.utcnow()
    )
    
    try:
        await save_benchmark(db, request, response, model_keys)
    except Exception as e:
        import logging
        logging.warning(f"Failed to save benchmark to database: {e}")
    
    return response
