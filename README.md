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

Requires [uv](https://docs.astral.sh/uv/).

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

## Update a generated service

```sh
uvx copier update --trust
```

Answers are stored in the generated `.copier-answers.yml`; Copier re-applies the template and shows
the differences as a normal git diff to review.

## License

[MIT](LICENSE)
