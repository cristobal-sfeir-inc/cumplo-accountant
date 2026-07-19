# cumplo-accountant

## Overview
FastAPI service that tracks users' Cumplo balance and credentials. Deployed on Cloud Run; receives
requests via `not-cumplo-api` (API Gateway). Depends on `cumplo-common` for Firestore, auth deps,
and shared Pydantic models.

## Build & Test
- Install deps: `poetry install`
- Run service locally: `uvicorn cumplo_accountant.main:app --reload`
- Build Docker image: `make build`
- Start container: `make start`
- Stop container: `make down`
- Update common library: `make update-common`

Python 3.13, Poetry 2.4.x.

## Code Quality
- Auto-fix lint + format: `make format`
- Verify code quality (CI gate): `make lint`

`make lint` runs: `ruff check` → `ruff format --check` → `basedpyright` → `docformatter --check`.
`make format` runs: `ruff format` → `ruff check --fix` → `docformatter --in-place`.

## Releasing (CI/CD)
Deployed by Google Cloud Build on push to `master`. Cloud Build builds the Docker image and
deploys to Cloud Run — it does NOT run lint/type/tests. PR-check enforcement lives in the
`.github/workflows/lint.yml` GitHub Actions workflow (`make lint` on every PR).

## Git workflow
- Branch prefixes: `feat/`, `fix/`, `chore/`, `ci/`. Conventional-commit subjects.
- `master` is protected: every change needs a **PR + code-owner review** (`@cnsfeir-reviewer`).
  **Never push to `master` directly.**

## Gotchas
- **Private registry auth.** `cumplo-common` lives in a private Artifact Registry. For local dev,
  set `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account key with read access, or run
  `gcloud auth application-default login` and install `keyrings-google-artifactregistry-auth`.
  CI uses Workload Identity Federation (WIF) via `vars.WIF_PROVIDER` / `vars.PUBLISH_SA`.
- **Dockerfile still targets Python 3.12.** Update the `FROM python:3.12-slim-bookworm` base
  image to `3.13-slim-bookworm` in a follow-up to align with `pyproject.toml`.
- **No test suite.** The service currently has no tests. Treat any new path you touch as
  requiring at least a smoke test.

## Before committing
- [ ] Run `make format`, then `make lint` and ensure it passes.
- [ ] No secrets or credential files committed.
