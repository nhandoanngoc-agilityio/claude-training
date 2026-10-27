# Spec: <short name>

Intent: [intent.md](intent.md) · Status: draft · Date: <YYYY-MM-DD>

## Concerns

<Conflicts the product owner must resolve before build: with CLAUDE.md conventions or "Never do", `.claude/claude-security-guidance.md`, existing behaviour in README, or between the intent's own constraints. Each one: what conflicts, the options, a recommendation. "None found" after checking each source.>

## Open questions

| Question (from intent.md) | Answer, or "carried forward: <why>" |
|---|---|

## Behaviour

<The contract a client sees: endpoints, params, request/response fields, status codes (422 for invalid input), ordering and edge cases (undated tasks, empty lists, Unicode). A table per endpoint.>

## Design

<Which files change and why, following CLAUDE.md "Layout": models (validation), `TaskStore` (data, under `self._lock`), router (thin), README API table, CHANGELOG.>

## Test plan

<Test file(s) in `tests/`, and the cases: happy path, each edge case in Behaviour, each 422. These become the failing tests committed first.>

## Out of scope

<What this spec deliberately leaves out.>

## Issues

<One or more GitHub issues to open on acceptance, each in the repo's format: title, **Type**, ## What, ## How (branch name, test-first), ## Done when (checklist).>
