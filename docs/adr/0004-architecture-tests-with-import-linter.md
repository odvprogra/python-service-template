# 0004. Enforce the dependency rule with architecture tests

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

The handbook's architecture style (hexagonal-lite) depends on one rule: dependencies point inward
and the domain imports no framework or infrastructure library. Rules that are only written down
erode, usually one convenient import at a time.

## Decision

Generated services declare import contracts with
[import-linter](https://import-linter.readthedocs.io/) in `pyproject.toml`: a layers contract and a
"the domain is pure Python" forbidden contract. `tests/architecture` runs them from pytest, so the
check runs wherever tests run: locally and in CI.

## Alternatives considered

- **Code review only:** depends on the reviewer noticing one import among many changes.
- **A separate CI step:** works, but is easy to skip locally and needs another workflow input.
- **Ruff banned imports:** can ban modules globally, not per layer.

## Consequences

- **Positive:** a layer violation fails the build and names the contract that was broken.
- **Negative:** import-linter reconfigures logging when it runs, which once broke unrelated tests.
  The shared test fixture now restores every logger's state after each test.
