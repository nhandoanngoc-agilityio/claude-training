# Loops and scheduled runs

Recurring Claude Code checks for this repo. There are two tools, and they suit different jobs:

| | `/loop` | `/schedule` |
|---|---|---|
| Where it runs | Inside the Claude Code session that started it | In the cloud, as a routine |
| Runs when | The session is open and idle | On a cron schedule, with or without you |
| Lifetime | Stops when the session closes; recurring loops expire after 7 days | Until you delete it |
| Good for | Watching something you're working on right now: a PR, a CI run | Daily or weekly chores: morning maintenance |

Loop runs can start late: up to half the interval, capped at 30 minutes. A 5-minute loop can
fire anywhere from 5 to 7.5 minutes after the previous run.

None of these may push, merge, re-run CI or change anything. They report; you decide.

## 1. Watch a PR

| | |
|---|---|
| Purpose | Keep an open PR moving: new review comments, check results, conflicts with `main` |
| Interval | 15 minutes |
| Start | `/loop 15m` with the prompt below (`/loop 15m` alone uses the built-in maintenance prompt) |
| Stop | Ask "stop the PR loop", or close the session |

```
/loop 15m Check PR #<number> in nhandoanngoc-agilityio/claude-training with gh:
`gh pr view <number> --json reviewDecision,mergeable,comments,reviews` and
`gh pr checks <number>`. Report only what changed since the last check: new
comments or reviews (who, one-line summary), checks that finished or failed,
merge conflicts. Don't push, merge or re-run anything.
```

## 2. Babysit CI

| | |
|---|---|
| Purpose | Notice a red build soon after a push or merge |
| Interval | 5 minutes |
| Start | see prompt below; use `--branch <branch>` instead of `main` to watch a PR branch |
| Stop | Ask "stop the CI loop", or close the session |

```
/loop 5m Run `gh run list -R nhandoanngoc-agilityio/claude-training --branch main
--limit 1`. Report the run's status, conclusion and commit title. If it failed,
show `gh run view <id> --log-failed | tail -30`, name the failing test, and suggest
a fix in one or two sentences. Don't re-run, push or change anything.
```

There is no deployment for this app (data is in memory), so CI on GitHub Actions
is the closest thing to a deploy status.

## 3. Morning maintenance

| | |
|---|---|
| Purpose | One short summary at the start of the day |
| When | Weekdays 08:30 local time |
| Start | `/schedule` with the prompt below (a loop would die with the session and expire after 7 days) |
| Stop | `/schedule` → list → delete the routine |

```
/schedule weekdays at 8:30 In nhandoanngoc-agilityio/claude-training, report:
1. Open PRs: age, check status, review status. Flag any older than 2 days or with failing checks.
2. The latest CI run on main: status and conclusion.
3. Remote branches whose PR is merged or closed (candidates to delete).
4. Open issues labelled day-* with no linked PR.
Keep it under 20 lines. Don't push, merge, comment, close or delete anything.
```

## Listing and stopping

- Loops: ask Claude "what loops are running?" to see each loop's ID and next run time. Ask "stop the CI loop" (or give the ID) to cancel one. Closing the session stops all of them.
- Routines: `/schedule` lists, updates and deletes them.
