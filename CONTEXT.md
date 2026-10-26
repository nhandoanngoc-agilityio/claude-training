# Context

Glossary for the Task Tracker training repo. Terms only; how things are built lives in CLAUDE.md and the code.

## Tasks

- **Task**: one item to track, with a title, optional description and due date, and a status.
- **Status**: where a task is: `todo`, `in_progress` or `done`.
- **Overdue task**: a task that isn't `done` and whose due date is before today (UTC).
- **Undated task**: a task with no due date. Date filters skip it.

## Reviews

- **Finding**: one problem a reviewer (a person or a tool) reports at a file:line.
- **True positive (TP)**: a finding that is a real problem.
- **False positive (FP)**: a finding that isn't a real problem. Record why, so it can be tuned out.
- **Seeded branch**: a branch with bugs put in on purpose to measure reviewers. Never merged.
- **Seeded bug**: one bug put in on a seeded branch.
- **Answer key**: the lead's private list of seeded bugs. Shared only after every review has run.
- **Missed seed**: a seeded bug that a reviewer didn't report.
- **Signal**: how useful a reviewer is: precision (TP share of its findings), recall on seeded bugs, and cost.
