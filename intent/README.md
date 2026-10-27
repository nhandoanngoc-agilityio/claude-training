# Intent home

Every feature starts here, before any issue or code. This is Stages 1 and 2 of the
[AI-native SDLC playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook).

```
intent/
  2026-10-27-export-csv/
    intent.md   what is wanted, why, constraints   (Stage 1: Plan)
    spec.md     the contract engineering builds    (Stage 2: Design)
```

Together the two files record what was asked for and what was decided.

## Flow

| Step | Who | How | Ends with |
|---|---|---|---|
| Capture | Anyone with an idea | Ask Claude to "write an intent for …" (`write-intent` skill) | PR `intent: …` |
| Review intent | Product owner | Correct the draft, merge the PR | `intent.md` on `main` |
| Spec | Product owner + Claude | Ask Claude to "spec out intent/<folder>" (`intent-to-spec` skill) | PR `spec: …` with concerns listed |
| Decide | Product owner (tech lead for risky changes) | Resolve each concern, merge or close the PR | Issues opened from the spec |
| Build | Developer + Claude | Plan mode first, then test-first commits (CLAUDE.md "Workflow") | PR `Closes #<issue>` |

A human makes every merge decision. Claude drafts, checks and flags.

## Roles

- **Product owner**: watches this folder and merges intents and specs. Today: @nhandoanngoc-agilityio.
- **Originator**: anyone; non-engineers can write intents through claude.ai without Git.

`_example-tasks-sort/` is a worked example, written after the fact from #16.
