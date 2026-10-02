# python-service-template

> A [Copier](https://copier.readthedocs.io/) template that generates Python services following the
> [engineering handbook](https://github.com/odvprogra/engineering-standards/blob/v1/HANDBOOK.md),
> and keeps them in sync with it as it evolves.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Why

Every service should start from the same production-ready baseline (layout, tooling, CI, docs)
instead of a copy of the last project. Copier also supports `copier update`, so improvements to the
template reach existing services as a reviewable diff instead of being re-applied by hand.

## Generate a service

Requires [uv](https://docs.astral.sh/uv/) (and Docker for services with a database).

```sh
uvx copier copy --trust gh:odvprogra/python-service-template my-service
```

Copier asks for:

| Question         | Default                   | Meaning                                                                 |
| ---------------- | ------------------------- | ----------------------------------------------------------------------- |
| `project_name`   | —                         | Human-readable name                                                     |
| `project_slug`   | from the name             | Repository and distribution name (kebab-case)                           |
| `package_name`   | from the slug             | Python import package (snake_case)                                      |
| `description`    | —                         | One-line pitch                                                          |
| `author_name`    | Oscar David Valle Pereyra | Author in `pyproject.toml` and the license                              |
| `github_owner`   | `odvprogra`               | Owner used in badges and links                                          |
| `has_web_api`    | `true`                    | FastAPI HTTP API with Problem Details, request IDs and health endpoints |
| `has_database`   | `false`                   | PostgreSQL with async SQLAlchemy, Alembic and testcontainers            |
| `license`        | `MIT`                     | `MIT` or `Apache-2.0`                                                   |
| `copyright_year` | current year              | Year in the license                                                     |
| `standards_ref`  | `v1`                      | Release of the shared CI workflows that the generated CI pins           |

## What a generated service includes

- Hexagonal-lite layout: `domain`, `application`, `infrastructure` and a `main.py` composition root,
  with an **architecture test** (import-linter) that fails if a layer imports outward or the domain
  imports frameworks
- Settings from the environment with pydantic-settings (validated at startup) and `.env.example`
- Structured logging with structlog: JSON when deployed, console locally, standard-library records
  in the same format, context such as `request_id` on every line
- `pyproject.toml` for uv with ruff (lint + format), mypy strict, pytest, coverage (80% gate) and
  hypothesis configured; Python 3.14 pinned in `.python-version`
- `justfile` with the uniform commands: `setup`, `lint`, `typecheck`, `test`, `check`, `fmt`
- pre-commit hooks: whitespace and file checks, ruff and mypy (through `uv run`, so the versions
  come from `uv.lock`), gitleaks, and Conventional Commits on the commit message
- `.github/workflows/ci.yml` calling the shared `python-ci` and `security` workflows
- With `has_web_api`: a FastAPI app with
  - RFC 9457 Problem Details for domain, validation, HTTP and unexpected errors (a 500 never leaks
    internals)
  - a pure ASGI request-context middleware: `X-Request-ID` on every response (caller's ID echoed if
    safe, UUIDv7 otherwise), the same ID on every log line, one `request.completed` line per request
  - `/health/live` and `/health/ready` with pluggable readiness checks
  - a committed `openapi.json` with a drift test (`just openapi` regenerates it) and `just dev`
- With `has_database`: PostgreSQL 18 through async SQLAlchemy (asyncpg) and Alembic
  - `DATABASE_URL` as a secret setting; plain `postgres://` URLs from hosting providers are accepted
  - a declarative base with deterministic constraint names, a session factory and a readiness check
  - Alembic configured in `pyproject.toml`; new revisions are run through ruff automatically
  - integration tests on a real PostgreSQL (testcontainers) that prove migrations are reversible and
    that models and migrations are in sync (`alembic check`)
  - `docker-compose.yml` for local development; `just dev`, `just migrate`, `just migration`

After generating: `cd my-service && git init && just setup && just check`.

## Update a generated service

```sh
uvx copier update --trust
```

Answers are stored in the generated `.copier-answers.yml`; Copier re-applies the template and shows
the differences as a normal git diff to review.

## License

[MIT](LICENSE)
