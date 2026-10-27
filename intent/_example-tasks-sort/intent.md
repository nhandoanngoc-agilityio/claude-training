# Intent: sort the task list

Author: nhandoanngoc-agilityio · Status: shipped (worked example, written after the fact from #16) · Date: 2026-10-22

## Problem

`GET /tasks` returns tasks in insertion order only. A client that wants "what's due next" or an alphabetical list has to fetch every page and sort it locally, which breaks paging.

## Proposed outcome

Clients can ask the API for the list sorted by creation time, due date or title, ascending or descending, and paging still works on the sorted list.

## Affected users and systems

API clients of `GET /tasks`. Touches the `/tasks` router, `TaskStore` listing, and the README API table.

## Constraints

- Requests without a sort parameter keep today's order.
- Filters (`status`, `due_before`, `q`) and paging totals behave exactly as now.
- Invalid input is rejected with 422, not ignored (CLAUDE.md).
- No new dependency.

## Open questions

- Where do tasks without a due date go when sorting by due date?
- Should title sorting ignore case?
- How are ties ordered?
