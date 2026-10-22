# Changelog

## [Unreleased]

## [0.3.0] - 2026-10-22

### Added
- Search tasks with `GET /tasks?q=`. Matching is case-insensitive and looks at the title and description (#9).
- List overdue tasks with `GET /tasks/overdue`. Each task includes `days_late` (#10).

### Changed
- `DELETE /tasks/{id}` now returns 404 for a task that doesn't exist, instead of reporting success (#11).
- Titles that are only whitespace are now rejected with 422 (#12).

### Fixed
- `PATCH /tasks/{id}` changes only the fields you send; other fields are no longer cleared (#6).
- The `due_before` filter skips tasks that have no due date (#7).
- `total_pages` counts a partial last page, and is 0 when there are no tasks (#8).
- Search finds text written in different Unicode forms, e.g. "é" typed as one character or as "e" plus an accent (#13).

## [0.2.0]

- Version bump for the training release.
