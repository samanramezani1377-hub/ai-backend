# AI Backend

Standalone API-only inference backend for clients such as WooGit.

## Current implementation

The repository now contains a CPU-safe FastAPI foundation with a stable `/v1` contract and a replaceable `InferenceProvider` abstraction.

Implemented endpoints:

- `GET /v1/health` — process health; does not require model execution.
- `GET /v1/ready` — readiness state for the configured runtime.
- `GET /v1/models` — exposes the currently configured model identifier.
- `POST /v1/chat` — stable chat/inference contract.

The model is configuration-driven through environment variables. The default first test model is `Qwen/Qwen3.5-9B`, but application code does not depend on that model. Qwen3.5-9B is an open-weight Qwen model with documented support in common inference runtimes. citeturn0search0turn0search2

## Architecture

```text
WooGit / other client
        |
        | HTTPS + JSON
        v
  Stable /v1 API
        |
        v
InferenceProvider
        |
        +---- configured model
        |
        v
 GPU/runtime deployment
        |
        v
 Model weights outside Git
```

Changing the model, GPU host, or inference runtime should not require a client API change.

## Configuration

```text
MODEL_ID=Qwen/Qwen3.5-9B
MODEL_REVISION=<optional pinned revision>
MODEL_RUNTIME=external
ENVIRONMENT=production
AI_API_KEY=<optional API key>
```

The API does not accept a model name from WooGit. The backend owns model selection so the client remains independent from the serving implementation.

## Chat contract

Request:

```json
{
  "messages": [
    {"role": "user", "content": "سلام"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

Response:

```json
{
  "id": "req_xxx",
  "model": "Qwen/Qwen3.5-9B",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "..."
      }
    }
  ]
}
```

## Runtime boundary

The repository intentionally does **not** download or commit model weights. The current provider is an explicit unconfigured runtime placeholder. Until a GPU runtime adapter is attached, `/v1/chat` returns `503` instead of pretending inference succeeded.

This keeps the API and tests real while leaving GPU deployment as a separate integration layer.

## Testing

GitHub Actions runs deterministic Python tests on a normal CPU runner. It does not require CUDA, a GPU, model weights, or a paid external inference service.

The tests verify health behavior, provider substitution, response normalization, and the expected `503` behavior when no inference runtime is attached.

A separate GPU smoke test will be added when the actual runtime is selected. It must load the configured model and perform real inference; it will not replace or weaken the normal CI tests.

## Non-goals

- No web chat UI.
- No model weights in Git.
- No permanent coupling to Qwen3.5-9B.
- No GPU requirement for ordinary GitHub CI.
- No direct exposure of a provider-specific API to WooGit.
