---
name: intent-to-spec
description: Turns a merged intent.md into a spec.md beside it, checked against the repo's rules, with concerns flagged first (Stage 2 of the SDLC in CLAUDE.md). Use when the user asks for a spec, a design, requirements, or to "spec out" an intent, or names an `intent/` folder.
---

# Intent to spec

The spec turns **what** (intent.md) into a contract the team can plan against. A human decides whether it moves to build; your job is to make that decision easy.

## 1. Read

Read in full: the `intent.md`, `CLAUDE.md`, `CONTEXT.md`, `README.md`, `.claude/claude-security-guidance.md`, `.claude/skills/review-checklist/SKILL.md`, and the code the intent touches (`app/models.py`, `app/store.py`, `app/routers/tasks.py` as relevant). Stop and say so if the intent's status is still `draft` and it isn't merged on `main`.

## 2. Write spec.md

Write `spec.md` next to the intent from [`assets/spec-template.md`](assets/spec-template.md).

- **Concerns** go first and are relentless: check the intent against every CLAUDE.md convention and "Never do" rule, every security rule, every review-checklist item, and README's documented behaviour. A behaviour change to something CLAUDE.md says to keep ("unless a ticket says otherwise") is a concern.
- Every open question from the intent appears in the table, either answered with the evidence or carried forward with the reason.
- Behaviour is specific enough to write tests from: exact params, status codes, edge cases.
- Each issue in "Issues" can be built test-first in one PR.

Done when every intent question is in the table, every rule source is checked, and every Behaviour edge case has a matching Test plan case.

## 3. Hand off for decision

Commit `spec.md` on branch `spec/<slug>`, push, and open a PR titled `spec: <short name>`, listing the concerns in the PR description. Stop there. When the product owner merges it, open the issues from "Issues" with `gh issue create`; each issue is built starting in plan mode (CLAUDE.md "Workflow").
