# Spec: sort the task list

Intent: [intent.md](intent.md) · Status: shipped (worked example, written after the fact from #16) · Date: 2026-10-22

## Concerns

- **Title sort and Unicode.** `q` matching ignores case and Unicode normalization form (#13). Sorting with plain `casefold` would order "é" (NFC) and "e"+accent (NFD) differently from how search treats them. Recommendation: sort titles with the same normalization as `q`. (Shipped that way; see README.)

Checked with nothing found: CLAUDE.md "Never do", security guidance (`sort`/`order` are enums, so input is bounded), review checklist (static paths unaffected).

## Open questions

| Question (from intent.md) | Answer |
|---|---|
| Undated tasks with `sort=due_date`? | Last, in both `asc` and `desc`. |
| Title sort ignores case? | Yes, and Unicode form too (see Concerns). |
| Ties? | Broken by `id`, ascending. |

## Behaviour

`GET /tasks` gains two optional query params:

| Param | Values | Default | Invalid value |
|---|---|---|---|
| `sort` | `created_at`, `due_date`, `title` | none: insertion order | 422 |
| `order` | `asc`, `desc` | `asc`; ignored without `sort` | 422 |

Sorting runs after `status` / `due_before` / `q` filters and before paging, so `total` and `total_pages` don't change.

## Design

- `app/routers/tasks.py`: `sort` and `order` as enum `Query` params; call a small sort helper before paging. Router stays thin.
- README API table and CHANGELOG `[Unreleased]`.

## Test plan

`tests/test_sorting.py`: each key × order; undated tasks last in both orders; case- and NFD-insensitive titles; ties by id; sort + each filter; sort + paging totals unchanged; 422 for unknown `sort` and `order`; no `sort` keeps insertion order.

## Out of scope

Multi-key sorting; sorting `/tasks/overdue`.

## Issues

- #16 Sort GET /tasks by created_at, due_date or title (branch `feat/16-tasks-sort`, failing tests first).
