from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from .models import BenchmarkRun, ModelResult as ModelResultDB
from schemas.benchmark import BenchmarkRequest, BenchmarkResponse

async def save_benchmark(
    session: AsyncSession,
    request: BenchmarkRequest,
    response: BenchmarkResponse,
    model_keys: list[str]
) -> None:
    try:
        benchmark_run = BenchmarkRun(
            id=uuid4(),
            prompt=request.prompt,
            criteria=request.criteria,
            tier=request.tier,
            total_duration_ms=response.total_duration_ms
        )
        session.add(benchmark_run)
        
        for result in response.results:
            model_result = ModelResultDB(
                id=uuid4(),
                benchmark_id=benchmark_run.id,
                model_key=result.model_key,
                api_name=result.api_name,
                status=result.status,
                response_text=result.response,
                latency_ms=result.latency_ms,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.total_tokens,
                estimated_cost_usd=result.estimated_cost_usd,
                error_message=result.error_message
            )
            session.add(model_result)
        
        await session.commit()
    except Exception:
        await session.rollback()
        raise
