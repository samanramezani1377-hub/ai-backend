# Testing Policy

## Goal

The project must have reliable GitHub CI without requiring access to a GPU.

GitHub CI validates the software around inference. It does not attempt to prove that a real GPU can load or run the selected model.

## Test layers

### Layer 1 — Static and deterministic CI

Runs on ordinary GitHub-hosted runners.

Includes:

- formatting;
- linting;
- type checking;
- unit tests;
- API schema tests;
- configuration tests;
- provider-selection tests;
- error mapping tests.

These tests must be deterministic and must not require model weights or CUDA.

### Layer 2 — Mock inference tests

The real provider interface is tested with a fake/mock inference implementation.

These tests verify that:

- API requests reach the provider correctly;
- generation parameters are passed correctly;
- provider results are normalized correctly;
- provider failures become correct API errors;
- timeouts and malformed results are handled correctly.

No GPU or real model is required.

### Layer 3 — GPU integration/smoke test

This is intentionally separate from ordinary GitHub CI.

It verifies the real deployment path:

```text
GPU runtime
   |
   +-- load configured model
   |
   +-- initialize inference runtime
   |
   +-- send one small test request
   |
   +-- validate response
   v
pass/fail
```

The first configured model for this test is Qwen 3.5 9B.

## Rules

1. A normal GitHub CI run must never require a GPU.
2. A normal GitHub CI run must never download the full model.
3. Unit tests must not silently switch to a fake implementation merely to hide a production failure; mock tests are explicitly separate and named as such.
4. GPU integration tests must be clearly identified as GPU/integration tests.
5. A GPU test failure must not be converted into a false green unit-test result.
6. API contract tests must remain runnable without any model runtime.
7. Health endpoint tests must not require model generation.

## Suggested CI split

```text
GitHub Actions
│
├── lint
├── typecheck
├── unit-tests
├── api-contract-tests
└── build/package validation

Separate GPU environment
│
└── gpu-smoke-test
       └── Qwen 3.5 9B
```

The exact GPU execution provider can change later. The repository should not make GitHub CI dependent on that provider.

## Why this split exists

The backend is software that happens to execute a model on a GPU. Most regressions in API contracts, configuration, validation, error handling, and application logic can and should be caught without a GPU.

GPU-specific validation is reserved for the small set of checks that genuinely require real model weights and GPU execution.
