---
name: release-checklist
description: Runs the team's release process step by step, from version bump through post-release verification, with validation gates and a human approval before production. Use when the user asks to cut, ship, publish, tag, or deploy a release, prepare release notes, do a hotfix, or roll back a release, even if they don't say "checklist".
---

# Release checklist

Every release follows the same gated sequence. Do not skip a step or change its order.
If a gate fails, stop, report what failed, and fix it before you continue. Never "note it and move on".

<!-- TODO(team): still to fill in: <#releases CHANNEL>, <OWNER or CHANNEL> in the announcement, <MILESTONE>, <SECOND_REVIEWER> (hotfix.md), <ON_CALL> (rollback.md). -->

This app has no deployed environments. "Staging" is the app run locally from `main`, and a release is the tag plus its GitLab release. The smoke tests are `scripts/smoke.sh` in the repo.

## Pick the release type first

- **Regular release**: follow the checklist below.
- **Hotfix** (production is broken, fix is already merged): read `references/hotfix.md`. It shortens steps 3–4.
- **Rollback** (a release that just went out is misbehaving): read `references/rollback.md` and do that right away. Do not try a fix-forward first.

## Progress

Copy this into your reply and tick each box as you finish it:

```
Release <VERSION> progress:
- [ ] 1. Preflight passes (scripts/preflight.sh)
- [ ] 2. Version decided and release plan written
- [ ] 3. Version bumped, changelog updated, release MR merged
- [ ] 4. Release candidate deployed to staging, smoke tests pass
- [ ] 5. Human approval received
- [ ] 6. Tagged and deployed to production
- [ ] 7. Post-release verification passes
- [ ] 8. Release notes published and announced
- [ ] 9. Close-out done
```

## Steps

### 1. Preflight

Run exactly, from the repo root:

```bash
bash .claude/skills/release-checklist/scripts/preflight.sh
```

It checks: you are on the default branch, the working tree is clean, the branch is up to date with the remote, and the GitLab pipeline on HEAD is green (via `glab`).
If it exits non-zero, fix what it reports and run it again. Only go on when it prints `PREFLIGHT OK`.

### 2. Decide the version and write the plan

1. List the changes since the last tag: `git log $(git describe --tags --abbrev=0)..HEAD --oneline`
2. Pick the version using semver:
   - any breaking change (`!` or `BREAKING CHANGE:`) → major
   - any `feat:` → minor
   - otherwise → patch
3. Write `release-plan.md` from `assets/release-plan-template.md`. Fill in the version, the change list, any migrations, feature flags to turn on, and the rollback target (the current production tag).
4. Show the plan to the user. If there is a database migration, say so clearly. Migrations change how rollback works (see Gotchas).

### 3. Bump the version and update the changelog

1. Create the branch `release/v<VERSION>`.
2. Bump the version in `pyproject.toml` and in `app/main.py` (`FastAPI(version=...)`, which `GET /version` returns), then run `uv lock` to update `uv.lock`.
3. Add a `## [<VERSION>] - <YYYY-MM-DD>` section to `CHANGELOG.md`, grouped into Added / Changed / Fixed / Removed. Write for users, not as a list of commit hashes.
4. Push with `git push origin release/v<VERSION>` and open an MR with `glab mr create --title "Release v<VERSION>" --target-branch main`. Get it reviewed and merged, then `git switch main && git pull --ff-only origin main`.

### 4. Release candidate on staging (local)

1. On the freshly pulled `main`, start the app and run the smoke tests against it, then stop it:

```bash
uv run uvicorn app.main:app --port 8001 > /dev/null 2>&1 &
bash scripts/smoke.sh http://127.0.0.1:8001 <VERSION>
pkill -f 'uvicorn app.main:app --port 8001'
```

2. Only go on when it prints `SMOKE OK`. It checks `/health`, that `/version` is `<VERSION>`, and a create / get / search / delete round trip.
3. If they fail, do not patch the running app. Fix them on the default branch and go back to step 1.

### 5. Approval gate

Stop and ask the user (or the release owner) for an explicit "yes, ship v<VERSION>".
Include the plan summary, the staging results, and the rollback target.
Never take earlier approval, CI status, or a passing staging deploy as approval for production.

### 6. Tag and deploy to production

```bash
git tag -a v<VERSION> -m "Release v<VERSION>"
git push origin v<VERSION>
```

There is no production deploy: the pushed tag is the release. Note: `.gitlab-ci.yml` only runs on branches (`if: $CI_COMMIT_BRANCH`), so pushing a tag does not start a pipeline (https://gitlab.asoft-python.com/nhan.doanngoc/claude-training/-/pipelines).

### 7. Post-release verification

Check that the tag itself works. Check it out, run the smoke tests on it, then go back to `main`:

```bash
git switch --detach v<VERSION>
uv run uvicorn app.main:app --port 8001 > /dev/null 2>&1 &
bash scripts/smoke.sh http://127.0.0.1:8001 <VERSION>
pkill -f 'uvicorn app.main:app --port 8001'
git switch main
```

Also confirm `git ls-remote --tags origin v<VERSION>` points at the release merge commit.

If any check fails, go to `references/rollback.md` right away.

### 8. Release notes and announcement

1. Create the GitLab release from the tag, with the changelog section as its body: `glab release create v<VERSION> --name "v<VERSION>" --notes-file <(sed -n '/## \[<VERSION>\]/,/## \[/p' CHANGELOG.md | sed '$d')`
2. Write the announcement from `assets/announcement-template.md`. Before posting it to <#releases CHANNEL>, show the draft to the user and post only after they approve it.

### 9. Close-out

- Close the <MILESTONE> milestone and move any open issues to the next one
- Delete the `release/v<VERSION>` branch
- If anything went wrong, add it to the Gotchas section below

## Gotchas

<!-- TODO(team): these are common starting points. Replace them with your own real failure cases. Every time you have to correct the agent during a release, add a line here. -->

- The app has no database or other dependencies, so `/health` is the readiness check (the smoke script calls it first). If a database is ever added, add a `/ready` endpoint that checks it and use that instead, because `/health` stays 200 while the database is down.
- If a release ever has a database migration (there is none today; data is in memory), rolling back the code does **not** roll back the schema. Migrations must be backward compatible with the previous release (expand, then contract). If one isn't, flag it in step 2 and get approval for that specifically.
- Push the tag only after the release MR is merged and you have pulled again. A tag on a stale local commit ships the wrong code.
- CI on the release MR is not CI on the merge commit. Preflight checks HEAD of the default branch for this reason.
- The step 8 notes command stops at the next `## [` heading. Older headings without brackets (e.g. `## 0.2.0`) don't match, so the notes would run to the end of the file. Write every version heading as `## [X.Y.Z]`.
- Push to `origin` (GitLab) only. Local `main` tracks the `github` mirror, so a bare `git push` goes to the wrong remote.
- Don't release on Fridays or before a holiday unless the user explicitly confirms it's a hotfix.
