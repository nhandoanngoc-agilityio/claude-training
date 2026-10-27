# Intent: task priority

Author: nhandoanngoc-agilityio · Status: draft · Date: 2026-10-27

## Problem

Tasks have a status and a due date but no way to say how important they are. A client that wants "the most important work first" has no field to set and nothing to sort on. This is also the first feature taken through the intent → spec → issue → build flow, so it doubles as a training exercise for the team.

## Proposed outcome

- Every task has a priority: `low`, `medium` or `high`.
- A client can set it when creating a task. A task created without one gets `medium`.
- A client can change it later with `PATCH /tasks/{id}`, like any other field.
- Tasks returned by the API show their priority.
- `GET /tasks` can be sorted by priority, alongside the existing sort options.

## Affected users and systems

API clients of `POST /tasks`, `PATCH /tasks/{id}`, `GET /tasks/{id}` and `GET /tasks`. Touches the task models, `TaskStore`, the `/tasks` router, and the README API table.

## Constraints

- Requests that don't mention priority keep working exactly as today, including existing sort, filter and paging behaviour.
- An unknown priority value is rejected with 422, not ignored or cleaned up (CLAUDE.md).
- No new dependency or database.

## Open questions

- What should `PATCH` with `{"priority": null}` do: reject it with 422, or leave the priority unchanged (as `{"title": null}` does)?
- With `sort=priority`, does `order=asc` mean low → high or high → low?
- How are tasks with the same priority ordered? (Other sorts break ties by `id`.)
- Filtering by priority (`?priority=high`) is out of scope for now. Should the spec say so explicitly?
