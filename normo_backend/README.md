# Normo Backend - Agentic AI Chatbot

## Quickstart

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Start the API with UV:

```bash
uv run normo-backend
# or
uv run uvicorn normo_backend.api.app:app --reload
```

3. Test health:

```bash
curl http://localhost:8000/health
```

4. Chat:

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Structure

- `src/normo_backend/api/`: FastAPI app and routes
- `src/normo_backend/services/`: Chat orchestration
- `src/normo_backend/agents/`: LangGraph agent and tools wiring
- `src/normo_backend/models/`: Pydantic schemas
- `src/normo_backend/utils/`: Utility modules (logging, etc.)
- `src/normo_backend/config.py`: Settings via pydantic-settings

## Notes

- Uses `uv` with `pyproject.toml` for dependencies.
- LLM: `langchain-openai` with LangGraph. Set `OPENAI_API_KEY` in `.env`.


source .env && PYTHONPATH=/Users/mohammadalnajdawi/Desktop/Repository/normo_backend/src uv run python -m normo_backend.main