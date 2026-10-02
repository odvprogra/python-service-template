# 0005. Run database migrations as a release step

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

Database services need their schema migrated before new code serves traffic. The image can either
migrate on every start or carry the migrations for a separate step.

## Decision

Images ship `migrations/` and the Alembic configuration, and migrations run as an explicit release
step (`docker run <image> alembic upgrade head`, or the platform's pre-deploy job). The application
never migrates on start. CI verifies the step works from the image, and integration tests verify
that migrations are reversible and in sync with the models.

## Alternatives considered

- **Migrate on application start:** simplest to deploy, but several replicas race to migrate, and a
  failed migration crash-loops the app instead of stopping the release.
- **Migrate from a developer machine:** the schema and the code can drift, and the release depends
  on someone's laptop.

## Consequences

- **Positive:** a failed migration blocks the release while the old version keeps serving.
- **Negative:** deployment needs one more step.
