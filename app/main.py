from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from .config import get_settings
from .provider import GenerationRequest, UnconfiguredProvider, InferenceProvider, ChatMessage
from .schemas import ChatRequest, ChatResponse, ChatResponseMessage, ChatChoice, HealthResponse, ReadyResponse

settings = get_settings()
provider: InferenceProvider = UnconfiguredProvider(settings.model_id)

app = FastAPI(title="AI Backend", version="1.0.0")


@app.get("/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/v1/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    return ReadyResponse(ready=False, model=provider.model_id)


@app.get("/v1/models")
def models() -> dict[str, list[dict[str, str]]]:
    return {"data": [{"id": provider.model_id, "object": "model"}]}


def _authorize(api_key: str | None) -> None:
    if settings.api_key is not None and api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest, x_api_key: str | None = Header(default=None)) -> ChatResponse:
    _authorize(x_api_key)
    try:
        result = provider.generate(
            GenerationRequest(
                messages=[ChatMessage(role=m.role, content=m.content) for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        id=f"req_{uuid4().hex}",
        model=result.model,
        choices=[ChatChoice(message=ChatResponseMessage(content=result.content))],
    )
