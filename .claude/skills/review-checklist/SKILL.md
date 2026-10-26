---
name: review-checklist
description: Reviews a branch, PR or diff in this repo against the team's checklist (route order, store locking, the title null guard, 422 on bad input, test-first commits, security) and reports pass/fail per check with file:line. Use when the user asks to review a branch, a PR or changes, to "self-review before opening a PR", or to check a diff against team conventions, even if they don't say "checklist".
---

# Review checklist

Checks that `/code-review` and `/security-review` don't know about because they come from this repo's own rules (CLAUDE.md) and from bugs we have already shipped or seeded. Run it on the diff, not the whole codebase.

## 1. Find the diff

```bash
git fetch origin main -q
git diff origin/main...HEAD --stat
git log origin/main..HEAD --oneline
```

For a PR number, use `gh pr diff <n>` and `gh pr view <n>` instead. Read every changed file in full, not just the hunks: several checks below (route order, locking) depend on code around the change.

## 2. Go through every check

Mark each one **pass**, **fail** (with file:line and one sentence on why) or **n/a** (the diff doesn't touch that area). Don't skip a check because it looks unlikely.

### API and models
- [ ] Static paths (`/tasks/overdue`, `/tasks/done`, ...) are declared before `/{task_id}` in `app/routers/tasks.py`.
- [ ] Invalid input gets a 422 from the models or `Query(...)` limits. Nothing is silently trimmed, clamped or "fixed" (titles are stored exactly as sent).
- [ ] Length limits (`title`, `q`) count code points; no NFD normalization before the check.
- [ ] `due_before` stays strict and skips undated tasks; `total_pages` rounds up and is 0 for an empty list, unless the linked issue says otherwise.
- [ ] The router stays thin: validate, call the store, map `None` to 404. No storage logic in the router.
- [ ] New query params and endpoints are in the README API table.

### Store (`app/store.py`)
- [ ] Every write (create, update, delete, clear, any new bulk method) runs inside `with self._lock:`.
- [ ] No dict is changed while it's being looped over (`for k in self._tasks: del ...`). Build a list of keys first.
- [ ] The `title` null guard in `TaskStore.update` is still there: `{"title": null}` must not wipe a title.
- [ ] Reads that are used to compute a write (read-then-write) happen inside the same lock.

### Tests and commits
- [ ] Each bug fix has a failing-test commit before the fix commit (`git log origin/main..HEAD --oneline`).
- [ ] New behaviour has tests in the matching `tests/test_<area>.py` and they use the `client` fixture.
- [ ] Edge cases from the issue's "Done when" list each have a test.
- [ ] `uv run pytest -q` passes.

### Process
- [ ] Branch is `fix/<issue>-<slug>` (or `feat/` / `chore/`) from `main`, not `main` itself.
- [ ] PR description has what / why / how tested / `Closes #<issue>`.
- [ ] No new dependency or database added without the owner asking for it (`pyproject.toml`, `uv.lock`).
- [ ] `.gitlab-ci.yml` not changed unless the issue asks.

### Security
- [ ] No user input reaches a shell (`subprocess`, `os.system`), `eval`/`exec`, a file path or a regex without validation.
- [ ] No secrets, tokens or personal data in code, tests, logs or error messages.
- [ ] Every new input has a size limit (string length, list size, page size), so one request can't make the server do unbounded work.
- [ ] Error responses don't leak stack traces or internal paths.
- [ ] Workflow changes (`.github/workflows/`) don't widen `permissions` or expose secrets to PRs from forks.

## 3. Report

Reply with one table, failures first:

| Check | Result | Where | Why |
|---|---|---|---|

Then a one-line verdict: **ready**, **ready after fixes** (list them), or **needs rework**. Don't fix anything unless asked; a review reports.

## Pre-PR self-review

Before opening a PR, run in this order and fix what's real before pushing:

1. This checklist.
2. `/code-review` on the branch.
3. `/security-review` if the diff touches input handling, the store, hooks or workflows.

If a finding turns out to be a false positive, say why in the PR description so reviewers don't raise it again.
