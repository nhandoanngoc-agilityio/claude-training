# Release plan: v<VERSION>

- **Type**: regular | hotfix
- **Release owner**: <NAME>
- **Current production tag (rollback target)**: v<PREVIOUS>
- **Planned date**: <YYYY-MM-DD>

## Changes
- <user-facing summary> (#PR)

## Risk
- **Database migrations**: none | <list, and whether each is backward compatible>
- **Feature flags to toggle**: none | <flag → state>
- **Config or secrets changes**: none | <list>
- **Breaking changes for users**: none | <list>

## Verification
- Staging smoke tests: pending
- Production checks: /ready, error rate, prod smoke tests
