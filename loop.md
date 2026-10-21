# Loops

Recurring Claude Code checks used for this repo. Loops are session-only: they live in
the Claude Code session that started them, run only while that session is idle, and
stop when the session closes. Recurring loops also expire after 7 days.

Runs can start late: up to half the interval, capped at 30 minutes. A 5-minute loop can
fire anywhere from 5 to 7.5 minutes after the previous run.

## 1. MR maintenance

| | |
|---|---|
| Purpose | Keep an open MR moving: new review comments, CI result, conflicts with `main` |
| Interval | 15 minutes |
| Start | `/loop 15m` (no prompt, so Claude Code uses its built-in maintenance prompt) |
| Checks | Whatever the built-in prompt covers; record what the first run reports |
| Stop | Ask "stop the loop", or close the session |

Our MRs are on GitLab, and the built-in prompt may look for GitHub PRs. If the first
run can't find the MR, restart with an explicit prompt:

```
/loop 15m Check GitLab MR !<number> with glab: new comments, pipeline or merge
conflicts since the last check. Report only what changed. Don't push or merge.
```

## 2. CI status

| | |
|---|---|
| Purpose | Notice a red build on `main` soon after a merge |
| Interval | 5 minutes |
| Start | see prompt below |
| Checks | Latest GitHub Actions `CI` run on `main` of `nhandoanngoc-agilityio/claude-training` |
| Stop | Ask "stop the loop", or close the session |

```
/loop 5m Run `gh run list -R nhandoanngoc-agilityio/claude-training --branch main
--limit 1`. Report the run's status, conclusion and commit title. If it failed,
show `gh run view <id> --log-failed | tail -30`. Don't re-run or change anything.
```

There is no deployment for this app (data is in memory), so CI on GitHub Actions
is the closest thing to a deploy status. GitLab CI can't run for this project.

## Listing and stopping

- Ask Claude "what loops are running?" to see each loop's ID and next run time.
- Ask "stop the CI loop" (or give the ID) to cancel one. Closing the session stops all of them.
