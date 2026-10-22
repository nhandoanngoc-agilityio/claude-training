# Rollback

Use this when post-release verification fails, or when the user reports that production is broken after a release.

1. Tell the user right away: "Rolling back v<BAD> to v<PREVIOUS>." Don't wait for them to approve this. Speed matters more here.
2. Find the rollback target. It is in `release-plan.md`, or you can get it with `git describe --tags --abbrev=0 v<BAD>^`.
3. Redeploy the previous tag: `<PROD_DEPLOY_COMMAND> --ref v<PREVIOUS>`
4. If v<BAD> ran a migration that v<PREVIOUS> can't handle, **stop and escalate to <ON_CALL>**. Do not run down-migrations unless a human tells you to.
5. Check `/ready`, the error rate, and the prod smoke tests (same as step 7 of the main checklist).
6. Do not delete the bad tag. Mark its GitHub release as broken: `gh release edit v<BAD> --prerelease --notes "ROLLED BACK: <reason>"`
7. Post in <#releases CHANNEL> after the user approves the text, and open an incident issue.
8. The fix ships as a new patch version through the normal checklist or `hotfix.md`. Never re-tag the same version.
