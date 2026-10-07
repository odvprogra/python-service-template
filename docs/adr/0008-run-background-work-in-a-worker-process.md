# 0008. Run background work in a worker process from the same image

- **Status:** Accepted
- **Date:** 2026-10-07

## Context

Services with a database soon need work that no request waits for: draining a transactional outbox,
expiring records whose date has passed, purging rows kept for a while (idempotency keys, delivered
events). The handbook lists `has_worker` among the template's options (§13), and `pricewright-api`
needs one for its milestone M5.

How it is usually done:

- **A process type of its own.** The Twelve-Factor App runs
  [web and worker processes](https://12factor.net/concurrency) from one codebase and scales each
  independently; a Heroku [Procfile](https://devcenter.heroku.com/articles/procfile) declares `web`
  and `worker` for the same build; cookiecutter-django runs its Celery worker and scheduler as
  compose services built from the project's own image.
- **Background tasks inside the web process** (FastAPI's `BackgroundTasks`, tasks started in the
  lifespan): nothing to deploy, but the work runs on every API replica, stops with every deploy of
  the API, and competes with requests for the event loop.
- **A task queue with a broker** (Celery, RQ, Dramatiq): mature retries and scheduling, plus Redis
  or RabbitMQ to run and monitor.
- **Schedules outside the service** (cron, a Kubernetes CronJob, `pg_cron`): fine for periodic jobs,
  but each platform does it differently, and `pg_cron` only runs SQL.
- **Scheduler libraries:** APScheduler's async rewrite (4.0) is still a pre-release that "should NOT
  be used in production" ([docs](https://apscheduler.readthedocs.io/)); periodic tasks at a fixed
  interval need a loop, not cron expressions.

## Decision

- A `has_worker` option, asked when the service has a database. It adds a `<slug>-worker` command
  (`main.worker`, wired in the composition root like the API) and `infrastructure/worker.py`, a loop
  of periodic tasks:
  - each task runs when the worker starts, then every `interval` plus up to 10% jitter, so replicas
    drift apart;
  - a run that raises is logged as `task.failed` and the task runs again at its next turn;
  - every line a run logs carries the task's name;
  - SIGINT or SIGTERM (`docker stop`) let the runs in progress finish, then the worker exits with
    status 0.
- The same image runs both processes: docker compose gets a `worker` service with its own `command`,
  and an image without an HTTP API starts the worker by default. `just worker` runs it locally.
- The generated worker starts with one task, a database check every minute; services add their own
  tasks in `main.worker_tasks`. Tasks must be safe to run on several replicas at once (row locks,
  `SKIP LOCKED`, advisory locks) and catch up by themselves, because a run missed while the worker
  was down is not replayed.
- The template's CI checks both shapes, with and without an API: the worker logs its start, and
  `docker stop` ends it with status 0.

## Alternatives considered

- **Background tasks in the API process:** see above; they also make "how many times did this run"
  depend on the number of API replicas.
- **Celery, RQ or Dramatiq with Redis:** a broker to operate for work that PostgreSQL can hold
  (`SELECT … FOR UPDATE SKIP LOCKED`); a service can still add one when it needs it.
- **Cron or `pg_cron`:** schedules belong to each platform, and they cannot drain an outbox
  continuously.
- **A scheduler library:** a dependency for a loop of a few lines, or a pre-release.

## Consequences

- **Positive:** one build and one configuration for both processes; the worker scales and deploys on
  its own; the loop is tested without waiting on the clock.
- **Negative:** intervals only, no "every day at 02:00"; no health endpoint (the platform watches
  the process and its logs); a service with workers must make its tasks idempotent and safe to run
  concurrently.
