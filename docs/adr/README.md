# Architecture Decision Records

Decisions this template makes for every service generated from it. Decisions shared by every repo
live in
[engineering-standards](https://github.com/odvprogra/engineering-standards/tree/v1/docs/adr).

| #    | Decision                                                                                                                | Status   |
| ---- | ----------------------------------------------------------------------------------------------------------------------- | -------- |
| 0001 | [Record architecture decisions](0001-record-architecture-decisions.md)                                                  | Accepted |
| 0002 | [Use Copier for the service template](0002-use-copier-for-the-service-template.md)                                      | Accepted |
| 0003 | [Verify the template by checking the projects it generates](0003-verify-the-template-by-checking-generated-projects.md) | Accepted |
| 0004 | [Enforce the dependency rule with architecture tests](0004-architecture-tests-with-import-linter.md)                    | Accepted |
| 0005 | [Run database migrations as a release step](0005-run-migrations-as-a-release-step.md)                                   | Accepted |
| 0006 | [Keep httpx for API tests until httpx2 matures](0006-keep-httpx-for-api-tests.md)                                       | Accepted |
| 0007 | [Name migration files by UTC creation time](0007-name-migrations-by-utc-creation-time.md)                               | Accepted |

New ADRs start from [the template](template.md).
