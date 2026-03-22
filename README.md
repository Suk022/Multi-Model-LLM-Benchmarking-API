# Multi-Model LLM Chat Service Backend

A minimal FastAPI service that lets you chat with two open-source LLMs — **Mistral-7B** and **Llama-3.1-8B Instruct** — via OpenRouter.ai. Supports model switching, logs latency and token counts, and persists logs to a CSV file.

## Features

- Route prompts to **Mistral-7B** or **Llama-3.1-8B Instruct** via a `model` parameter
- Log round-trip latency, token counts, model used, and timestamp for each request
- Persist logs in a CSV file (`chat_logs.csv`)
- Simple HTTP API (`POST /chat`)
- Health check endpoint (`GET /health`)
- Automated tests via `pytest`

## Requirements

- Python 3.8+
- OpenRouter.ai API key (free to obtain)

## Setup

1. **Clone the repo**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Get your key from [https://openrouter.ai/](https://openrouter.ai/)
   - Create a `.env` file in the project root:
     ```
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     ```

## Running the Service

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

### Health Check

```http
GET /health
```

Returns `{ "status": "ok" }`.

### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "prompt": "Your question here",
  "model": "mistral" | "llama"
}
```

`model` must be either `"mistral"` or `"llama"`. Returns the model response, latency, token counts, model used, and timestamp as JSON.

## Logging

All interactions are logged to `chat_logs.csv` with:

- Timestamp
- Model
- Prompt
- Response
- Latency (seconds)
- Prompt tokens
- Response tokens

## Testing

```bash
pytest
```

## Example Log Analysis

The `chat_logs.csv` file records every interaction with the chat service, capturing key metrics for both supported models.

### Sample Log Entries

| timestamp                  | model   | prompt                                                     | latency (s) | prompt_tokens | response_tokens |
|----------------------------|---------|------------------------------------------------------------|-------------|---------------|-----------------|
| 2025-07-15T17:20:47.475859 | mistral | Hello, who are you?                                        | 3.97        | 4             | 47              |
| 2025-07-15T17:25:03.890301 | llama   | How can LLMs model benefits a Tech Startup                 | 13.79       | 8             | 446             |
| 2025-07-15T17:28:11.275427 | llama   | Tell in three points how you and mistral LLM is different? | 17.32       | 11            | 258             |

### What This Demonstrates

- **Model switching:** Prompts are routed to both `mistral` and `llama`, confirming multi-model support
- **Latency tracking:** Each entry logs the round-trip time for the model to respond
- **Token counts:** Both prompt and response token counts are recorded, enabling usage tracking
- **Prompt variety:** The log demonstrates versatility across different prompt types

## Evaluating the Live API

- **Public URL:** [https://promptcue-llm-chat-api.onrender.com](https://promptcue-llm-chat-api.onrender.com)
- **Supported models:** `"mistral"` and `"llama"`
- **No local setup required**

### Testing with Swagger UI

Visit [`/docs`](https://promptcue-llm-chat-api.onrender.com/docs) in your browser for interactive API testing.

### Testing with Postman

1. Create a new `POST` request to `https://promptcue-llm-chat-api.onrender.com/chat`
2. In the **Body** tab, select **raw → JSON**
3. Enter the following payload (choose either model):
   ```json
   {
     "prompt": "Hello, who are you?",
     "model": "mistral"
   }
   ```
4. Click **Send**. You should receive a JSON response with the model's reply, latency, token counts, and more.

## Deployment Note

This project is hosted on Render's free tier. The server sleeps after 15 minutes of inactivity, so **the first request may take 30–60 seconds** due to cold start. Subsequent requests will respond quickly.