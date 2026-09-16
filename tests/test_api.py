from fastapi.testclient import TestClient

from app import main
from app.provider import GenerationResult


class FakeProvider:
    model_id = "test-model"

    def generate(self, request):
        assert request.messages[0].content == "hello"
        return GenerationResult(content="world", model=self.model_id)


def test_health():
    client = TestClient(main.app)
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_models_exposes_configured_provider():
    original = main.provider
    main.provider = FakeProvider()
    try:
        response = TestClient(main.app).get("/v1/models")
        assert response.status_code == 200
        assert response.json()["data"][0]["id"] == "test-model"
    finally:
        main.provider = original


def test_chat_normalizes_provider_response():
    original = main.provider
    main.provider = FakeProvider()
    try:
        response = TestClient(main.app).post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "hello"}]},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["model"] == "test-model"
        assert body["choices"][0]["message"] == {"role": "assistant", "content": "world"}
        assert body["id"].startswith("req_")
    finally:
        main.provider = original


def test_chat_returns_503_without_runtime():
    original = main.provider
    main.provider = main.UnconfiguredProvider("test-model")
    try:
        response = TestClient(main.app).post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "hello"}]},
        )
        assert response.status_code == 503
    finally:
        main.provider = original
