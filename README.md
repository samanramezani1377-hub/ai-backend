# AI Backend

Backend-only inference service for AI models.

## Purpose

`ai-backend` is a standalone API environment for serving an interchangeable language model to client applications such as WooGit.

The repository contains the backend, API contract, model/runtime configuration, and automated CPU-safe validation. It does **not** contain model weights and it is not intended to be a user-facing chat application.

## Core decisions

- **Model must be replaceable.** Application code must not be coupled to one model name, one model provider, or one GPU vendor.
- **API only.** This project provides an inference API. UI/chat presentation belongs to the client application.
- **Model weights are external.** Large model files must not be committed to GitHub. The runtime loads the configured model from its model source/storage when deployed on GPU infrastructure.
- **GitHub CI is GPU-independent.** GitHub Actions must never require a GPU to validate or merge the project. CI tests cover API contracts, configuration, request validation, provider behavior with mocks/fakes, and other deterministic checks.
- **GPU inference is a deployment/runtime concern.** Real model loading and inference are integration/deployment checks and run only in an explicitly provisioned GPU environment.
- **First test model:** Qwen 3.5 9B. This is a runtime configuration choice, not a permanent architectural dependency.

## Target architecture

```text
Client (WooGit / other app)
          |
          | HTTPS / JSON
          v
   AI Backend API
          |
          v
   Inference Provider
          |
          +---- configured model
          |
          v
     GPU Runtime
          |
          v
     Model Weights
```

The API layer and inference provider are separated so that changing the model does not require changing the public API.

## Model configuration

The active model is configuration, not hard-coded business logic. A deployment should be able to change the model by changing configuration/environment values and redeploying the runtime.

Example concept:

```text
MODEL_ID=<configured-model>
MODEL_REVISION=<optional-pinned-revision>
MODEL_RUNTIME=<configured-runtime>
```

For the first GPU test, the configured model is Qwen 3.5 9B.

## Testing policy

### GitHub CI

GitHub Actions is responsible for fast, deterministic validation. It must not:

- download multi-gigabyte model weights;
- require a CUDA device;
- start a GPU runtime;
- depend on GPU availability;
- make paid or external GPU calls as a prerequisite for a green CI run.

The CI test suite should instead verify:

- API request/response schemas;
- configuration parsing and validation;
- model-provider selection;
- provider interface behavior using mocks/fakes;
- authentication and error handling where implemented;
- health/readiness behavior that does not require model execution;
- formatting, linting, type checking, and unit tests.

### GPU validation

Real model loading and generation are separate from GitHub CI. A GPU environment is used only for explicit integration/smoke validation of the configured model and runtime.

A GPU failure must not be hidden by changing, skipping, or weakening the normal unit tests. GPU tests must remain clearly identified as GPU integration tests.

## API direction

The first API surface is intentionally small. The backend should expose inference primitives rather than UI-specific behavior.

Planned endpoints:

- `GET /v1/health` — service health
- `POST /v1/chat` — chat/inference request
- `POST /v1/generate` — lower-level text generation when needed

The exact request/response schemas will be documented before implementation and treated as an API contract.

## Non-goals

- No web chat UI in this repository.
- No model weights committed to Git.
- No permanent dependency on Qwen 3.5 9B.
- No GPU requirement for ordinary GitHub CI.
- No provider-specific model API exposed directly to clients when it can be hidden behind the backend contract.

## Initial implementation order

1. Define architecture and API contract.
2. Define a model/provider abstraction.
3. Add configuration for the first test model: Qwen 3.5 9B.
4. Implement API validation and deterministic unit tests.
5. Add the GPU runtime/deployment configuration separately.
6. Run an explicit GPU smoke test against the configured model.
7. Keep model replacement possible without changing the client-facing API.
