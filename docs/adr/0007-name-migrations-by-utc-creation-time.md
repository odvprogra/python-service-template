# 0007. Name migration files by UTC creation time

- **Status:** Accepted
- **Date:** 2026-10-03

## Context

Alembic names a migration `<revision>_<slug>.py`, where the revision is a random 12-character hex
id. The order Alembic applies migrations in comes from each file's `down_revision`, not from its
name ([Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)), so a directory
listing shows migrations in random order and nobody can tell which one follows which.

Other tools name migrations so they sort:

- **Rails:** a UTC timestamp, `20261003144800_create_users.rb`; branches never collide.
- **Django:** a sequence, `0002_users.py`; two branches that add a migration collide and need a
  merge migration.
- **Flyway:** versions, `V2__users.sql`; the same collisions as a sequence.

Alembic's own documentation shows a `file_template` that puts the date and time in front of the
revision. The slug is already cut to 40 characters (`truncate_slug_length`), so names stay short.

Constraint names have a related limit: PostgreSQL identifiers stop at 63 characters. SQLAlchemy
shortens longer names produced by a naming convention with a stable 4-character hash suffix
([SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions)),
but the template's convention named unique, foreign key and index constraints after their first
column only: two composite unique constraints on one table that start with `tenant_id`, as a
multi-tenant service has, would get the same name and the migration would fail.

## Decision

- Generated services set
  `file_template = "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s"`
  and `timezone = "UTC"`: files sort by creation time, Rails style, and keep Alembic's random
  revision ids. `alembic[tz]` brings `tzdata`, which Windows needs to resolve `UTC`.
- A unit test fails if the history has more than one head (two PRs that each add a migration on the
  same parent) or if a file does not follow the naming pattern.
- The naming convention lists every column (`column_0_N_name`) for unique, foreign key and index
  constraints.
- The template's CI generates a revision in every database variant and runs that test.

## Alternatives considered

- **Alembic's default names:** correct order, but unreadable listings.
- **Sequential revision ids (`--rev-id 0002`):** readable, but manual, and parallel branches collide
  on the same number.
- **Local time:** names would depend on each developer's time zone.

## Consequences

- **Positive:** `ls migrations/versions` reads as the history; a branched history fails in CI
  instead of at deploy time; composite constraints have descriptive names.
- **Negative:** one more dependency (`tzdata`, data only). Existing services rename their migration
  files once when they update (the naming test requires it); Alembic does not care about names.
