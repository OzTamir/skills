---
name: unvibe
description: >-
  Rework a Pull Request written by a coding agent into production-grade code
  that fits the existing codebase and is easy to review. Runs a pipeline of
  deep-reasoning subagents that first study the pre-change code and its
  conventions, then understand the PR, map where the new code feels out of place
  or over-engineered, plan minimal idiomatic changes, and apply them as atomic
  commits — ending in a change summary and an optional PR review guide. Use when
  the user explicitly asks to unvibe, clean up, productionize, de-slop,
  simplify, or "make reviewable" an agent- or vibe-coded PR. Do not auto-invoke
  from generic PR or code-review discussion.
---
# unvibe

Turn a vibe-coded PR into production code that a human reviewer will trust.

Coding agents ship PRs that *work* but don't *belong*: over-engineered for the
neighborhood they land in, over-tested or tested differently than the
surrounding code, over-commented, written in idioms the codebase doesn't use.
This skill front-loads hard thinking — five read-only reasoning passes — **before
a single line is rewritten**, so the eventual edits are minimal, idiomatic, and
obviously correct. The goal is not to add; it is to make the change *fit* and
shrink the reviewer's job.

The orchestrator (you) coordinates the pipeline. Phases 1–5 are subagents that
**only read and analyze** — they write findings to a workspace, never to the
repo. Phase 6 is where code changes, run by implementation subagents you
dispatch. Phases 7–8 you do directly.

## Core principles (carry these into every phase)

- **Fit over cleverness.** The yardstick is the *surrounding* code, not abstract
  best practice. Match its altitude, idioms, comment density, and test depth.
- **Simpler beats shorter beats clever.** Complex code is worse than longer
  code. A reviewer-legible 20 lines beats a dense 8-line abstraction.
- **Subtraction is the default move.** Most findings should *remove* speculative
  generality, redundant tests, and noise — not add scaffolding.
- **Behavior is sacred.** Refactors must preserve what the PR does. If a change
  alters behavior, that's a separate, flagged decision — not a silent edit.
- **Every commit must read cleanly on its own.** Atomic, single-concern, with a
  message a reviewer understands without the diff.

## Model and effort

Every subagent in phases 1–6 does load-bearing reasoning. Dispatch each with the
**most capable model available** (`model: "opus"`) and, if your harness exposes
a reasoning-effort control, set it to the **maximum**. Tell each subagent
explicitly that its analysis is the foundation downstream work depends on and
that it should think as deeply as it can before answering. Thinking time is not
the bottleneck here; a shallow pass early poisons every later phase.

## 0. Resolve the PR and set up

Resolve which PR you're improving:

- If the user gave an identifier (number, branch, or URL), pass it to `gh pr view`.
- Otherwise detect the PR for the **current branch**:
  ```bash
  gh pr view --json number,url,title,headRefName,baseRefName,headRefOid,state,isDraft,author
  ```

Stop and report (don't invent) if: `gh` is unauthenticated (`gh auth status`),
no PR exists for the branch (ask for an explicit identifier), or the PR is
merged/closed (flag prominently, ask whether to continue).

Capture `{baseRefName, headRefName, headRefOid}`. Confirm the working tree is on
the PR's head branch and is clean (`git status`). **Never** run this pipeline's
commits against `main` or a detached/foreign branch.

Compute the change set you'll reason about:
```bash
git diff <baseRefName>...<headRefName> --stat
git diff <baseRefName>...<headRefName>   # the full PR diff
git diff <baseRefName>...<headRefName> --name-only
```

The pipeline stays on the head branch throughout (the working tree holds the PR's
changes, which phase 6 will edit). Phase 1 therefore reads the **pre-change**
state via `git show <baseRefName>:<path>`, not the working tree — its prompt
already does this.

Create a run workspace **outside the repo tree** (your scratchpad, or
`mktemp -d`). Call it `$WS`. Every analysis phase writes one markdown artifact
there:

| Phase | Artifact |
| --- | --- |
| 1 | `$WS/grounding.md` |
| 2 | `$WS/pr-analysis.md` |
| 3 | `$WS/consistency-gaps.md` |
| 4 | `$WS/simplification.md` |
| 5 | `$WS/plan.md` |

The exact, verbatim subagent prompts live in
[references/subagent-prompts.md](references/subagent-prompts.md). Read that file
and use each prompt as written, substituting the placeholders
(`{BASE}`, `{HEAD}`, `{CHANGED_FILES}`, `{WS}`, prior-artifact paths). Do **not**
paraphrase them — the wording is tuned.

## The pipeline (dependency-aware, parallelized)

```
Wave A (parallel):   [1 grounding]   [2 pr-analysis]
                            \             /
Wave B (parallel):      [3 gaps]     [4 simplification]
                            \             /
                          [5 synthesis → plan.md]
                                  |
                          [6 implement + commit]
                                  |
                          [7 summary table]
                                  |
                          [8 review guide?]  (optional, ask first)
```

### Wave A — dispatch phases 1 and 2 together (single message, parallel)

Both are independent reads of the same PR from opposite ends of time. Phase 1
studies the **pre-change** code on the base branch; phase 2 studies the **new**
code the PR introduces. Launching them concurrently is the efficient default.

- **Phase 1 — Baseline grounding.** Understand the flows the PR touches *as they
  worked before the change*. Beyond functionality, extract the codebase's
  implicit contract: naming, error-handling style, comment density and what
  comments are *for*, module boundaries, how wide and deep tests go. Output is a
  deduced "house style" for the exact area the PR lands in. → `$WS/grounding.md`
- **Phase 2 — PR understanding + atomic-unit decomposition.** Understand what the
  PR does (the goal — bugs fixed, features added) and *how the new code is
  written*, applying the same analytical lens as phase 1 so phase 3 can compare
  like with like. Then decompose the diff into **atomic units of change** —
  independently-reasonable-about slices keyed by file/area — to enable
  parallelism downstream. → `$WS/pr-analysis.md`

Wait for both to complete before Wave B.

### Wave B — dispatch phases 3 and 4 together (single message, parallel)

- **Phase 3 — Consistency-gap mapping.** Reads `grounding.md` + `pr-analysis.md`.
  Measures how *out of place* the new code feels against the house style: is it
  over-engineered relative to its neighbors? Does it test things the rest of the
  code doesn't, or test more heavily? Too many comments? Off idioms, wrong
  module, inconsistent naming? Surfaces every gap with file:line evidence and the
  existing pattern it should match. → `$WS/consistency-gaps.md`
- **Phase 4 — Simplification & over-engineering hunt.** Reads `pr-analysis.md`
  plus any best-practice/convention docs the repo itself ships (e.g. the nearest
  `AGENTS.md` / `CLAUDE.md`, a `CONTRIBUTING.md`, or a project rules directory).
  Challenges the *approach*: where could the same goal be reached with less and
  simpler code? Agents tunnel-vision into elaborate solutions — this phase steps
  back and asks what to cut. → `$WS/simplification.md`

Phases 3 and 4 view the change through different lenses (fit vs. excess) and are
independent; run them concurrently.

### Phase 5 — Synthesis into a plan

One subagent reads `consistency-gaps.md` + `simplification.md` (and may
re-consult the earlier artifacts) and produces `$WS/plan.md`: a deduplicated,
prioritized, **grounded** action plan. Overlapping findings from phases 3 and 4
get merged into single changes. The plan is the contract phase 6 executes — see
the required schema in the prompt reference. Each change carries:

- a stable `id`, the target file(s), and a one-line intent;
- the concrete edit in code terms (enough that an implementer needn't re-derive it);
- a **conventional-commit message** (`type(scope): summary`, no ticket IDs, no AI
  attribution);
- a `risk` note (does it touch behavior? tests? a public API?);
- a `depends_on` list and a `parallel_group` so the orchestrator knows what can
  run concurrently and what must serialize. **Every file is owned by exactly one
  change** — merge all edits to a given path into a single change. This makes each
  change a clean one-commit unit (phase 6 stages whole files) and lets any changes
  that share a group run concurrently without touching the same file. Groups run
  one at a time in `depends_on` order; changes within a group run in parallel.

After phase 5, **show the user the plan** (the ordered change list with commit
messages and the parallel groups) before writing code. This is the natural
checkpoint: a quick scan catches a wrong call before any edit. Proceed once they
confirm.

## 6. Implement (code changes happen here)

You orchestrate; subagents edit. Work `parallel_group` by `parallel_group` in
dependency order. Within a group, dispatch one implementation subagent per
change in a single message (parallel). Use the implementation prompt in the
reference. Constraints passed to every implementer:

- Edit **only** the files named in your change. No "while I'm here" cleanups, no
  edits outside the assigned change.
- **Do not** run any git command, stage, commit, or push. **Do not** run lint,
  format, or tests. The orchestrator verifies and commits.
- Preserve behavior unless the change explicitly says otherwise. If you discover
  the planned edit is wrong or unsafe, stop and return `pushback` with the
  reason rather than improvising.
- Two implementers must never touch the same file (each file is owned by exactly
  one change), so concurrent dispatch is always safe.

After all implementers in all groups return, **verify once** over the union of
changed files with the narrowest reliable command the repo provides — its lint,
type-check, and/or test runner, scoped to the affected projects/packages only,
never the whole workspace. Detect the command from the repo's own tooling
(its task runner, build config, or convention docs); if you can't determine a
reliable scoped command, run the closest project-level check and say so.

Only once verification is **green**, commit each change as its own atomic commit,
in dependency order, staging just that change's files. Because each file belongs
to exactly one change, `git add <files>` stages only that change's edits:

```bash
git add <files-for-change-id>
git commit -m "<planned conventional-commit message>"
```

Invoking this skill with auto-commit is the authorization for these per-change
commits (the user chose this when the run started). Do **not** push or open/edit
PRs unless separately asked. If verification fails, do not commit broken work:
attempt a scoped fix (re-dispatch the relevant implementer), and if it still
fails, stop and surface the failure with the exact command output.

## 7. Change summary

Print one table summarizing what was done:

```
| # | Change | Files | Commit | Risk | Source finding |
|---|--------|-------|--------|------|----------------|
| 1 | <intent> | <paths> | <type(scope): summary> | <behavior/test/api/none> | gaps#/sim# |
```

Follow it with: commits created (count + short SHAs), the verification command
run and its PASS result, anything deferred or pushed back, and the literal note:
`Changes are committed locally on <headRefName>; review the diff and push when ready.`

## 8. Optional — PR review guide (ask first)

Ask the user (via the question tool) whether they want a **Claude Artifact** that
explains the PR for reviewers. If yes, dispatch one subagent (review-guide prompt
in the reference) that reuses the workspace artifacts to produce a guide written
from the *reviewer's* perspective — not a changelog of this skill's edits. It
must cover: the codebase and flows **as they were before** (with real code
samples and `file:line` references from `grounding.md`); the goal and
functionality the PR adds (with samples, explicitly tying "here's how the code
shown above changes"); and a recommended reading order — "how to review this PR".
Render it with the Artifact tool (load the `artifact-design` skill first, per its
own instructions).

## Hard rules

- Phases 1–5 subagents are **read-only on the repo**. They may write only their
  one workspace artifact. If a phase-1–5 agent edits repo source, that's a bug.
- **Never** skip a phase or collapse the thinking phases to save time — the value
  of this skill *is* the front-loaded analysis. A shallow plan produces vibe
  edits, which defeats the purpose.
- **Never** let two subagents edit the same file concurrently.
- **Never** commit to `main` or push without explicit instruction.
- **Never** invent findings. Every gap/simplification must cite real evidence
  (file:line, the existing pattern). "Looks fine" is a valid phase result.
- **Never** change behavior as a side effect of a "cleanup." Behavior changes are
  explicit plan items with a `risk` flag.
- If `gh pr view` can't resolve a single PR, stop and ask — don't guess.
