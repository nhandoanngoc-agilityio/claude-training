---
name: release-checklist
description: Runs the team's release process step by step, from version bump through post-release verification, with validation gates and a human approval before production. Use when the user asks to cut, ship, publish, tag, or deploy a release, prepare release notes, do a hotfix, or roll back a release, even if they don't say "checklist".
---

# Release checklist

Every release follows the same gated sequence. Do not skip a step or change its order.
If a gate fails, stop, report what failed, and fix it before you continue. Never "note it and move on".

<!-- TODO(team): replace every <PLACEHOLDER> with your real commands, URLs and channels. -->

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
- [ ] 3. Version bumped, changelog updated, release PR merged
- [ ] 4. Release candidate deployed to staging, smoke tests pass
- [ ] 5. Human approval received
- [ ] 6. Tagged and deployed to production
- [ ] 7. Post-release verification passes
- [ ] 8. Release notes published and announced
- [ ] 9. Close-out done
```

## Steps

### 1. Preflight

Run exactly:

```bash
bash scripts/preflight.sh
```

It checks: you are on the default branch, the working tree is clean, the branch is up to date with the remote, and CI on HEAD is green.
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
2. Bump the version in <VERSION_FILES, e.g. package.json, pyproject.toml>.
3. Add a `## [<VERSION>] - <YYYY-MM-DD>` section to `CHANGELOG.md`, grouped into Added / Changed / Fixed / Removed. Write for users, not as a list of commit hashes.
4. Open a PR titled `Release v<VERSION>`, get it reviewed, and merge it. Then pull the default branch again.

### 4. Release candidate on staging

1. Deploy: `<STAGING_DEPLOY_COMMAND>`
2. Run the smoke tests: `<SMOKE_TEST_COMMAND> --env staging`
3. If they fail, do not try to fix them on staging. Fix them on the default branch and go back to step 1.

### 5. Approval gate

Stop and ask the user (or the release owner) for an explicit "yes, ship v<VERSION>".
Include the plan summary, the staging results, and the rollback target.
Never take earlier approval, CI status, or a passing staging deploy as approval for production.

### 6. Tag and deploy to production

```bash
git tag -a v<VERSION> -m "Release v<VERSION>"
git push origin v<VERSION>
```

Then: `<PROD_DEPLOY_COMMAND>` (or watch the tag-triggered pipeline at <CI_URL>).
Do not run anything after this until the deploy reports success.

### 7. Post-release verification

Over the next <15> minutes, check:
- `<PROD_URL>/ready` returns 200 (not `/health`, see Gotchas)
- The error rate on <DASHBOARD_URL> is no higher than before the release
- The smoke tests pass against production: `<SMOKE_TEST_COMMAND> --env prod`

If any check fails, go to `references/rollback.md` right away.

### 8. Release notes and announcement

1. Create the GitHub release from the tag, with the changelog section as its body: `gh release create v<VERSION> --notes-file <(sed -n '/## \[<VERSION>\]/,/## \[/p' CHANGELOG.md | sed '$d')`
2. Write the announcement from `assets/announcement-template.md`. Before posting it to <#releases CHANNEL>, show the draft to the user and post only after they approve it.

### 9. Close-out

- Close the <MILESTONE> milestone and move any open issues to the next one
- Delete the `release/v<VERSION>` branch
- If anything went wrong, add it to the Gotchas section below

## Gotchas

<!-- TODO(team): these are common starting points. Replace them with your own real failure cases. Every time you have to correct the agent during a release, add a line here. -->

- `/health` returns 200 as long as the web server is up, even when the database is down. Always check `/ready`.
- If the release has a database migration, rolling back the code does **not** roll back the schema. Migrations must be backward compatible with the previous release (expand, then contract). If one isn't, flag it in step 2 and get approval for that specifically.
- Push the tag only after the release PR is merged and you have pulled again. A tag on a stale local commit ships the wrong code.
- CI on the release PR is not CI on the merge commit. Preflight checks HEAD of the default branch for this reason.
- Don't release on Fridays or before a holiday unless the user explicitly confirms it's a hotfix.
