# 0003. Verify the template by checking the projects it generates

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

A template's output is code. Rendering without errors proves little: a generated project can render
and still fail its own lint, types, tests, hooks or container build, and options multiply the cases.

## Decision

CI renders **every option combination** (`api-db`, `api`, `db`, `minimal`) and runs the generated
project's **own** commands: `just setup`, `just check` (including integration tests on a real
PostgreSQL) and `pre-commit run --all-files`. It then builds the image, checks that it runs as
non-root and smoke-tests `/health/ready`. `scripts/check_variant.py` implements this once, for CI
and for `just test`.

## Alternatives considered

- **Snapshot tests of the rendered files:** fast, but they assert what the files look like, not that
  they work, and every intentional change rewrites the snapshots.
- **Checking only the default options:** cheaper, but most template bugs live in the combinations.

## Consequences

- **Positive:** a change that breaks any generated service fails here, before anyone generates it.
- **Positive:** the generated CI configuration, hooks and Dockerfile are exercised, not only the
  code.
- **Negative:** the matrix takes several minutes per run and needs Docker. Acceptable for a repo
  that changes rarely.
