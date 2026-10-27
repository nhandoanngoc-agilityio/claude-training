---
name: write-intent
description: Captures a feature idea, bug report or metric breach as an intent.md in `intent/` (Stage 1 of the SDLC in CLAUDE.md). Use when the user has an idea, a request or a problem to turn into work, says "write an intent", or wants to start a new feature, even if they don't say "intent".
---

# Write an intent

An intent states **what** is wanted, **why**, and under which **constraints**. It never says how to build it; that is the spec's job (`intent-to-spec` skill).

## 1. Brainstorm

Ask the originator questions, a few at a time, until you can fill every section of [`assets/intent-template.md`](assets/intent-template.md) from their answers. Use the terms in `CONTEXT.md`. Check `CLAUDE.md` ("Conventions", "Never do") and `README.md` for existing behaviour the idea would change, and ask about each conflict you find.

Done when every section has content from the originator, or an explicit "None".

## 2. Write the file

- Path: `intent/<YYYY-MM-DD>-<slug>/intent.md`, with today's date and a 2–4 word kebab-case slug.
- Copy the template; status `draft`; author is the originator.
- Problem and outcome describe user-visible behaviour. Move any implementation idea the originator gave into "Open questions" as "Should we …?".
- An intent fits on one screen. Split an idea with two separate outcomes into two intents.

## 3. Hand off for review

Branch `intent/<slug>` from `main`, commit only the intent file, push, and open a PR titled `intent: <short name>` for the product owner to review. Stop there: the product owner corrects and merges it. The spec comes after the merge.
