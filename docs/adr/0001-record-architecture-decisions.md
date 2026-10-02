# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

The template makes decisions on behalf of every service generated from it. A service owner who
disagrees with one needs to see why it was made before changing it, here or in their own repo.

## Decision

We will record the template's decisions as ADRs in `docs/adr/`, in the format and with the rules of
[ADR-0001 in engineering-standards](https://github.com/odvprogra/engineering-standards/blob/v1/docs/adr/0001-record-architecture-decisions.md).
Decisions shared by every repo (runtime baseline, type checker, architecture style) live there and
are linked, not repeated.

## Alternatives considered

- **Explaining decisions only in pull requests:** the reasoning exists but is hard to find later.

## Consequences

- **Positive:** generated services can cite the template's ADRs instead of re-arguing them.
- **Negative:** template changes that make a decision need an ADR, not only a PR description.
