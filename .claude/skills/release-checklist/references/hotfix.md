# Hotfix

Use this when production has an urgent bug and its fix is already merged to the default branch.

The changes from the main checklist:
- **Version**: always a patch bump.
- **Step 3**: the release MR may be self-approved by the release owner if <SECOND_REVIEWER> isn't available. Write that down in the MR.
- **Step 4**: you may run only the smoke tests that cover the broken area. Say which ones you skipped.
- **Step 5 is still required.** A hotfix still needs an explicit human "ship it".
- **Friday and holiday rule**: does not apply.

Every other step is unchanged, including preflight, post-release verification and close-out.

If the fix is **not** merged yet, stop. Ask the user to merge it first or to roll back instead (`rollback.md`).
