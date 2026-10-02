# 0006. Keep httpx for API tests until httpx2 matures

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

Generated API tests use `httpx.AsyncClient` with `ASGITransport`. Starlette 1.7 deprecates using
`httpx` inside its `TestClient` in favor of [httpx2](https://github.com/pydantic/httpx2), the
successor maintained by the Pydantic organization: same API, first released in May 2026, 18 releases
by the decision date. The generated pytest configuration treats warnings as errors, so the
deprecation surfaced immediately.

## Decision

Keep `httpx` and do not use Starlette's `TestClient`. API tests use `httpx.AsyncClient`, which
raises no warning, and the lifespan test enters `app.router.lifespan_context` directly. No
dependency that is a few months old enters every generated service.

## Alternatives considered

- **Adopt httpx2 now:** aligned with Starlette's direction, but very young for a baseline that every
  service inherits.
- **Silence the warning:** hides the signal that the ecosystem is moving.

## Consequences

- **Positive:** a stable, widely known test client in every service.
- **Negative:** a migration is coming. Revisit when httpx2 has a year of releases or when `httpx`
  stops working with a supported Starlette; a superseding ADR would switch every service through
  `copier update`.
