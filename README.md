# Multi-Model LLM Benchmarking API

A FastAPI backend that sends a single prompt to multiple LLMs in parallel and returns a structured benchmark — latency, token usage, cost estimates, and a ranked recommendation. Built on OpenRouter.ai.

The original `/chat` endpoint (single-model routing) stays intact. `/benchmark` is the new core.

---

## What It Does

**Current (live)**
- Route a prompt to Mistral or Llama via `POST /chat`
- Returns response, latency, token counts, and timestamp
- Logs every interaction to `chat_logs.csv`

**Incoming**
- `POST /benchmark` — fire one prompt at multiple LLMs simultaneously
- Parallel async execution via `asyncio.gather` — total time ≈ slowest model, not sum
- Per-model metrics: latency, prompt tokens, completion tokens, estimated cost
- Ranked recommendation: `fastest`, `cheapest`, or `balanced` (composite score)
- Partial failure support — one model failing doesn't kill the response
- Tiered model pools: `default` (3 models, fast) and `extended` (6 models, comprehensive)
- In-memory prompt cache with 5-minute TTL
- Benchmark run logging to `benchmark_logs.csv`

---

## Model Pool (Upcoming)

All models are free tier via OpenRouter.

| Key | Model | Tier | Params |
|---|---|---|---|
| `mistral` | mistralai/mistral-small-3.1-24b-instruct | default | 24B |
| `llama` | meta-llama/llama-3.3-70b-instruct | default | 70B |
| `gemma` | google/gemma-3-27b-it | default | 27B |
| `gpt-oss-120b` | openai/gpt-oss-120b | extended | 120B |
| `qwen3` | qwen/qwen3-next-80b-a3b-instruct | extended | 80B |
| `hermes` | nousresearch/hermes-3-llama-3.1-405b | extended | 405B |

Adding a new model = one entry in `MODEL_REGISTRY`. No other changes needed.

---

## API

### Health Check
```http
GET /health
```
Returns `{ "status": "ok" }`.

---

### Chat (existing)
```http
POST /chat
Content-Type: application/json

{
  "prompt": "Your question here",
  "model": "mistral" | "llama"
}
```

---

### Benchmark (upcoming)
```http
POST /benchmark
Content-Type: application/json

{
  "prompt": "Explain how transformers work",
  "tier": "default",
  "criteria": "balanced"
}
```

`tier`: `"default"` (3 models) | `"extended"` (6 models) | `"all"`  
`criteria`: `"fastest"` | `"cheapest"` | `"balanced"`  
`models`: optional list of specific model keys — overrides `tier` if provided

**Response:**
```json
{
  "prompt": "Explain how transformers work",
  "criteria": "balanced",
  "recommendation": "mistral",
  "results": [
    {
      "model_key": "mistral",
      "api_name": "mistralai/mistral-small-3.1-24b-instruct:free",
      "response": "...",
      "latency_ms": 1240,
      "prompt_tokens": 6,
      "completion_tokens": 193,
      "total_tokens": 199,
      "estimated_cost_usd": 0.0,
      "status": "success"
    },
    {
      "model_key": "llama",
      "api_name": "meta-llama/llama-3.3-70b-instruct:free",
      "response": null,
      "latency_ms": null,
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null,
      "estimated_cost_usd": null,
      "status": "error",
      "error": "rate_limited"
    }
  ],
  "summary": {
    "fastest": "gemma",
    "cheapest": "mistral",
    "recommended_balanced": "mistral"
  }
}
```

One model erroring out does not affect the others. `recommendation` is `null` only if every model fails.

---

## Architecture (Upcoming)

```
POST /benchmark
      │
      ▼
  Router Layer         — resolves model list from tier or explicit keys
      │
      ▼
  Executor Layer       — asyncio.gather(), one coroutine per model
      │                  return_exceptions=True for partial failure
      ▼
  Normalizer           — raw OpenRouter response → ModelResult schema
      │
      ▼
  Ranker               — min-max normalized composite scoring
      │
      ▼
  Response + Logger    — BenchmarkResponse + append to benchmark_logs.csv
```

Key files (upcoming):
```
backend/
├── registry.py          # MODEL_REGISTRY dict + get_models_by_tier()
├── pricing.py           # COST_MAP + compute_cost()
├── schemas.py           # ModelResult, BenchmarkRequest, BenchmarkResponse
├── executor.py          # async call_model() + run_benchmark()
├── ranker.py            # rank_results() + build_summary()
├── cache.py             # in-memory prompt cache, 5-min TTL
├── benchmark_logger.py  # append-only CSV logging per benchmark run
└── main.py              # /chat (existing) + /benchmark (new)
```

---

## Requirements

- Python 3.8+
- OpenRouter.ai API key — free at [openrouter.ai](https://openrouter.ai)

---

## Setup

**1. Clone the repo**

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set environment variable**

Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**4. Run**
```bash
uvicorn main:app --reload
```

API at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

---

## Testing

```bash
pytest
```

Benchmark tests mock at the `httpx.AsyncClient` level — no real API calls made. Covers partial failure, all-fail, and ranking correctness.

---

## Deployment

Hosted on Render free tier.

**Public URL:** [https://promptcue-llm-chat-api.onrender.com](https://promptcue-llm-chat-api.onrender.com)  
**Docs:** [/docs](https://promptcue-llm-chat-api.onrender.com/docs)

The server sleeps after 15 minutes of inactivity. First request after sleep takes 30–60 seconds. Subsequent requests are fast.

---

## Tradeoffs

**Parallel calls vs cost:** Benchmarking sends the same prompt to N models per request. At scale this is N× token usage. For now all models are free tier — cost is zero. The architecture is ready for paid models: `pricing.py` has the cost computation, just update the rates.

**In-memory cache:** Simple dict with SHA256 key. Evicts on TTL expiry (5 min) and hard cap (500 entries). The right production upgrade is Redis — the cache interface stays the same, only the backing store changes.

**Free tier rate limits:** OpenRouter free models can 429 under parallel load. The executor retries on 429 up to twice (1s, 2s linear backoff) before marking the model as `rate_limited`. Other errors are not retried.
