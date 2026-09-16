from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class GenerationRequest:
    messages: Sequence[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass(frozen=True)
class GenerationResult:
    content: str
    model: str


class InferenceProvider(Protocol):
    model_id: str

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate a response using the configured model/runtime."""


class UnconfiguredProvider:
    """Explicit provider placeholder used until a GPU runtime is attached."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise RuntimeError("Inference runtime is not configured")
