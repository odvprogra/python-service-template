# 0002. Use Copier for the service template

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

Every Python service must start from the same baseline, and improvements to that baseline must reach
services that already exist. Generating once and diverging forever is what the template exists to
prevent.

## Decision

We will use [Copier](https://copier.readthedocs.io/):

- Answers are stored in `.copier-answers.yml`, so `copier update` re-renders the template with the
  same options and applies the difference as a reviewable git diff (three-way merge).
- Options are Jinja conditions on file contents and file names (`has_web_api`, `has_database`).
- Files a project owns after generation (README, ADR-0001, architecture doc, `CLAUDE.md`) are listed
  in `_skip_if_exists`, so updates never overwrite them.

## Alternatives considered

- **cookiecutter:** the most widely known, but generation is one-way; keeping services in sync needs
  an extra tool (cruft) layered on top.
- **GitHub template repository:** zero tooling, but no options and no update path at all.
- **A shared library instead of a template:** good for code, but cannot ship tooling configuration,
  CI, Dockerfiles or documentation.

## Consequences

- **Positive:** baseline improvements reach existing services through `copier update`.
- **Positive:** one template covers four service shapes without copies.
- **Negative:** Jinja inside Python, TOML and YAML is harder to read. The CI matrix (ADR-0003)
  compensates by rendering and checking every combination.
