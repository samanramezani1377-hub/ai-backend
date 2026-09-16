# Architecture

## 1. Responsibility

`ai-backend` is an inference API service. Its only product responsibility is to accept model requests and return model results through a stable HTTP API.

The client owns UI, conversation presentation, and client-side interaction state.

## 2. Separation of concerns

```text
API Layer
   |
   v
Application / Request Layer
   |
   v
Inference Provider Interface
   |
   +-------------------+
   |                   |
   v                   v
Local/Mock Provider   GPU Model Provider
                         |
                         v
                    Configured Model
```

The API must depend on an abstraction such as an inference provider, not on a specific model implementation.

## 3. Model replacement

A model is selected through deployment configuration.

Changing from the initial Qwen 3.5 9B test model to another compatible model should require configuration/runtime changes, not a rewrite of the API layer.

The provider abstraction should isolate model-specific details such as:

- model identifier;
- tokenizer/model loading;
- generation parameters;
- device selection;
- runtime-specific initialization;
- model-specific output normalization.

The API should expose normalized request and response structures.

## 4. Model storage

Model weights are external to the Git repository. The GPU runtime obtains the configured model from the selected model source/storage and keeps it available for inference according to the runtime's caching strategy.

GitHub stores source code and configuration, not large model checkpoints.

## 5. Runtime boundary

The deployment environment is responsible for:

- GPU allocation;
- CUDA/runtime dependencies when required;
- downloading/loading model weights;
- keeping the model loaded when appropriate;
- exposing the API service;
- restarting/recovering the inference process.

The GitHub repository remains the source of truth for the code and deployment configuration.

## 6. First model

The first model used for GPU smoke testing is **Qwen 3.5 9B**.

This choice is deliberately represented as configuration. It must not become a hard-coded requirement throughout the project.

## 7. API boundary

The client communicates only with the AI Backend API:

```text
Client
  |
  | POST /v1/chat
  v
AI Backend
  |
  v
Provider
  |
  v
Model
```

The client should not need to know whether inference is performed by a local runtime, a hosted GPU runtime, or another compatible provider.

## 8. Health semantics

Health and readiness are separate concepts when the implementation reaches deployment:

- **Health:** the API process is alive and can answer basic health requests.
- **Readiness:** the inference runtime is initialized sufficiently to serve model requests.

A basic health check must not require generating text from the model.

## 9. Failure isolation

The backend should return explicit API errors for configuration, validation, provider, timeout, and model/runtime failures. Internal provider details should not leak unnecessarily into the public contract.

## 10. Future model/runtime changes

The architecture must support all of the following without changing the client-facing API unnecessarily:

- changing model;
- changing model revision;
- changing GPU provider;
- changing inference runtime;
- changing GPU type;
- introducing a model cache;
- adding a second compatible provider for fallback/testing.
