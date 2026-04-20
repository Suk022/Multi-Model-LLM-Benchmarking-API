# Multi-Model LLM Benchmarking API

A FastAPI service that benchmarks multiple LLMs concurrently and ranks them 
by speed, cost, or a balanced composite score.

Sends one prompt to multiple models simultaneously via OpenRouter.ai, 
measures latency and token usage per model, and returns a ranked 
recommendation. All runs persist to PostgreSQL.

---

## API

### GET /health
```json
{"status": "ok"}
```

### POST /chat
```json
{
  "prompt": "Explain quantum computing",
  "model": "llama-70b"
}
```
```json
{
  "response": "...",
  "latency": 3.97,
  "prompt_tokens": 4,
  "response_tokens": 47,
  "model": "llama-70b",
  "timestamp": "17:20 March 30, 2026"
}
```

### POST /benchmark
```json
{
  "prompt": "Write a Python function to calculate fibonacci",
  "tier": "default",
  "criteria": "balanced"
}
```
```json
{
  "benchmark_id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt": "Write a Python function to calculate fibonacci",
  "criteria": "balanced",
  "results": [
    {
      "model_key": "llama-70b",
      "api_name": "meta-llama/llama-3.3-70b-instruct:free",
      "response": "def fibonacci(n):...",
      "latency_ms": 3970.5,
      "prompt_tokens": 8,
      "completion_tokens": 156,
      "total_tokens": 164,
      "estimated_cost_usd": 0.0,
      "status": "success"
    }
  ],
  "summary": {
    "fastest": "llama-3b",
    "cheapest": "llama-70b",
    "recommended": "llama-3b",
    "criteria_used": "balanced"
  },
  "total_duration_ms": 4520.1,
  "created_at": "2026-03-30T12:20:47.475859"
}
```

`tier`: `"default"` | `"extended"` | `"all"`  
`criteria`: `"fastest"` | `"cheapest"` | `"balanced"`  
`models`: optional — explicit list of model keys, overrides `tier` 

One model failing does not affect others. `recommended` is `null` 
only if every model fails.

---

## Model Registry

| Key | Model | Tier | Params |
|-----|-------|------|--------|
| llama-70b | meta-llama/llama-3.3-70b-instruct:free | default | 70B |
| gemma-27b | google/gemma-3-27b-it:free | default | 27B |
| gemma-12b | google/gemma-3-12b-it:free | default | 12B |
| llama-3b | meta-llama/llama-3.2-3b-instruct:free | default | 3B |
| qwen3-80b | qwen/qwen3-next-80b-a3b-instruct:free | extended | 80B |
| nemotron-120b | nvidia/nemotron-3-super-120b-a12b:free | extended | 120B |
| arcee-trinity | arcee-ai/trinity-large-preview:free | extended | unknown |

Adding a new model = one dict entry in `model_registry.py`. 
Models with `active: False` are skipped before any HTTP calls fire.

---

## Architecture

```
POST /benchmark
      │
      ▼
  Router          resolve model list from tier or explicit keys
      │
      ▼
  Executor        asyncio.gather() — one coroutine per model
      │           return_exceptions=True for per-model isolation
      ▼
  Normalizer      raw OpenRouter response → ModelResult schema
      │
      ▼
  Ranker          min-max normalize latency + cost, weighted composite
      │
      ▼
  DB + Response   atomic PostgreSQL write, return BenchmarkResponse
```

---

## Tech Stack

FastAPI, SQLAlchemy 2.0, asyncpg, Pydantic v2, httpx, PostgreSQL

---

## Setup

```bash
git clone https://github.com/Suk022/Multi-Model-LLM-Benchmarking-API.git
pip install -r requirements.txt
```

Create `.env`:
```
OPENROUTER_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
```

```bash
uvicorn main:app --reload
```

Docs at `http://127.0.0.1:8000/docs`.

---

## Known Limitations

**Rate limits** — free tier models 429 frequently under parallel load. 
Retry logic: 2 retries on 429, backoff 3s then 6s. Doesn't eliminate 
failures, just reduces them.

**Migrations** — using `create_all()` on startup, not Alembic. 
Schema changes require manual table drops in development.

**Cost data** — all models stubbed at `0.0` (free tier). 
`cost_calculator.py` is wired up; update rates when switching to 
paid models.

**Caching** — not yet implemented. Repeated identical prompts re-hit 
the API. Redis-backed cache is the intended upgrade path.

---

## Deployment

Hosted on Render free tier.  
Cold start: first request after 15 minutes of inactivity takes 30–60s.
