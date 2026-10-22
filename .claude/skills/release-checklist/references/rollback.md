# Rollback

Use this when post-release verification fails, or when the user reports that production is broken after a release.

1. Tell the user right away: "Rolling back v<BAD> to v<PREVIOUS>." Don't wait for them to approve this. Speed matters more here.
2. Find the rollback target. It is in `release-plan.md`, or you can get it with `git describe --tags --abbrev=0 v<BAD>^`.
3. There is no deployed environment to redeploy. v<PREVIOUS> stays the last good tag. Tell users of the API to run that tag (`git switch --detach v<PREVIOUS>`).
4. If v<BAD> ran a migration that v<PREVIOUS> can't handle, **stop and escalate to <ON_CALL>**. Do not run down-migrations unless a human tells you to.
5. Run the smoke tests on v<PREVIOUS> as in step 7 of the main checklist, but use main's copy of the script, because older tags may not have it: `bash <(git show main:scripts/smoke.sh) http://127.0.0.1:8001 <PREVIOUS>`.
6. Do not delete the bad tag. Mark its GitLab release as broken (`glab release create` updates an existing release): `glab release create v<BAD> --name "v<BAD> (ROLLED BACK)" --notes "ROLLED BACK: <reason>. Original notes: CHANGELOG.md [<BAD>]."`
7. Post in <#releases CHANNEL> after the user approves the text, and open an incident issue.
8. The fix ships as a new patch version through the normal checklist or `hotfix.md`. Never re-tag the same version.
