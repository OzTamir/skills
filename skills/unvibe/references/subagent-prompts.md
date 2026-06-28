# unvibe — subagent prompt templates

Copy each prompt verbatim into the corresponding `Agent` call, substituting the
`{PLACEHOLDERS}`. Dispatch every one with `model: "opus"` and maximum reasoning
effort. Placeholders:

- `{BASE}` / `{HEAD}` — base and head branch names
- `{CHANGED_FILES}` — newline list from `git diff {BASE}...{HEAD} --name-only`
- `{WS}` — the run workspace directory (outside the repo)
- `{PR_TITLE}`, `{PR_NUMBER}` — from `gh pr view`

A note shared by all analysis agents (1–5): they are **read-only on the
repository**. The only file they may write is their assigned `{WS}/*.md`
artifact. Keep that constraint in every prompt.

---

## Phase 1 — Baseline grounding

```
You are grounding a later code-review pipeline in how this codebase ACTUALLY
works and is ACTUALLY written, in the specific area a PR is about to change —
BEFORE that change. Your output is the "house style" yardstick everything
downstream is measured against, so think as deeply as you can; a shallow read
here weakens every later phase.

## Inputs
- Base branch (pre-change state): {BASE}
- Files the PR touches:
{CHANGED_FILES}

## Reading the PRE-change state (important)
The working tree is checked out on the PR head ({HEAD}), so reading a changed
file directly shows POST-PR code. To see the baseline, read changed files from
the base ref: `git show {BASE}:<path>`. Use `git diff {BASE}...{HEAD}` to know
which files/hunks changed. Surrounding files that the PR does NOT touch are
identical on both refs, so reading the working tree for those is fine. Never
describe post-PR code as the house style.

## What to do
Work entirely against the pre-change code (the {BASE} ref). For the modules,
functions, and flows the PR touches:

1. Functionality & flows. Trace how each affected flow works today, end to end.
   What calls what, what the data is, what the invariants and error paths are.
   You must be able to explain "before this PR, X happened by doing Y".
2. Coding standards actually in force (observed, not aspirational):
   - Naming conventions for functions, types, variables, modules.
   - Error-handling idiom (how errors are represented, raised, propagated, and
     logged in this language and this codebase).
   - Control-flow and abstraction altitude — how much indirection, how many
     helpers, how much generality is typical here vs. inline straight-line code.
   - Comment density and PURPOSE: do comments explain why (invariants, gotchas)
     or are they absent because names carry meaning? Quote 2-3 representative
     examples.
   - Module boundaries and separation of concerns — what lives where and why.
3. Test posture for this area:
   - Where do tests live (colocated, a separate test dir/suite, none)?
   - How DEEP (edge cases, error paths) and how WIDE (how much surface) do they
     go? What is conventionally NOT tested (trivial accessors, framework or
     language facts)?
   - Idioms: parametrization/table tests, fixtures, builders, mocking
     boundaries — whatever this codebase actually uses.
   - Roughly the test-to-code ratio that is normal here.

Ground every claim in evidence: cite file:line and quote short snippets. Read
the actual pre-change files (via `git show {BASE}:<path>` for changed files); do
not generalize from memory. If a convention is inconsistent
in the existing code, say so plainly rather than inventing a rule.

## Output
Write a markdown report to {WS}/grounding.md with these sections:
# Baseline grounding
## Affected flows (how they work pre-change)   — with file:line refs
## Observed coding standards                    — naming, errors, altitude, comments
## Comment conventions                          — with quoted examples
## Test posture                                 — depth, width, idioms, what's skipped
## The house style, distilled                   — a tight bulleted "rules the PR's
   code should obey to fit in", each rule tied to evidence above
Return only a 5-line summary plus the path {WS}/grounding.md. Do not edit any
repository file.
```

---

## Phase 2 — PR understanding + atomic-unit decomposition

```
You are analyzing the NEW code a PR introduces — both what it achieves and how
it is written — and decomposing it into atomic units so later phases can work in
parallel. Apply the SAME analytical lens a reviewer would apply to the existing
codebase, because a later phase will directly compare your read of this code to a
read of the pre-change code. Think deeply; this is foundational.

## Inputs
- PR: #{PR_NUMBER} — {PR_TITLE}
- Diff to study:  git diff {BASE}...{HEAD}
- Changed files:
{CHANGED_FILES}

## What to do
1. Goal (the why). What does this PR accomplish? Bugs fixed, features added,
   behavior changed. State it abstractly first, then concretely per area.
2. How the new code is written (the same dimensions phase 1 extracts from the
   old code, so they're comparable): naming, error handling, abstraction
   altitude, comment density and purpose, module placement, and the testing it
   adds (depth, width, idioms). Cite file:line; quote representative snippets.
3. Atomic-unit decomposition. Break the diff into the smallest INDEPENDENTLY
   reasonable-about units of change. A unit is a coherent slice — typically one
   file or one tightly-coupled file+test pair — that could be understood, and
   later modified, on its own. For each unit give:
   - unit id (u1, u2, …), the file(s) and the hunks/symbols it covers,
   - a one-line description of what that unit does,
   - whether it is production code, test code, config, or docs,
   - obvious coupling to other units (so downstream knows what can parallelize).

Read the real diff and the real files; do not infer from the title.

## Output
Write markdown to {WS}/pr-analysis.md:
# PR analysis
## Goal                              — abstract, then per-area
## How the new code is written       — per dimension, with file:line + snippets
## Atomic units                      — a table: id | files | description | kind | coupled-to
Return only a 5-line summary plus the path {WS}/pr-analysis.md. Do not edit any
repository file.
```

---

## Phase 3 — Consistency-gap mapping

```
You map where the PR's new code does NOT fit the existing codebase. You are not
judging the code against abstract ideals — only against how THIS codebase writes
code, as captured in the grounding report. Be specific and evidence-based; vague
"could be cleaner" notes are useless downstream.

## Inputs (read both fully first)
- House style / baseline: {WS}/grounding.md
- PR analysis + atomic units: {WS}/pr-analysis.md
- The diff for verification: git diff {BASE}...{HEAD}

## What to look for (the "out of place" axes)
For each atomic unit, compare the new code to the house style and flag genuine
gaps:
- Over-engineering relative to neighbors: indirection, abstraction, generality,
  config, wrappers/helpers/layers the surrounding code wouldn't bother with.
- Testing mismatch: tests for things this codebase doesn't test (trivial
  accessors, framework/language facts), heavier/deeper testing than the area's
  norm, or non-idiomatic test style (copy-paste instead of the codebase's
  parametrization idiom, inline fixtures the repo extracts, mocking internals).
- Comment mismatch: more comments than the area uses, what-not-why comments,
  banners/section dividers, restating the code or the types.
- Idiom & style drift: error handling, naming, control flow, module placement
  that diverges from the established pattern.

## Output
Write markdown to {WS}/consistency-gaps.md. For EACH finding:
- id (g1, g2, …), the atomic unit it belongs to,
- file:line,
- axis (over-engineering | testing | comments | idiom | placement | naming),
- what's off (one sentence),
- the existing pattern it should match (quote it, with its file:line from
  grounding or the codebase),
- suggested direction (usually: remove / inline / align to pattern),
- severity (high = a reviewer would definitely flag it; low = nit).
End with a short "looks consistent" list of areas that already fit, so phase 5
doesn't touch them. If the PR is broadly consistent, say so honestly.
Return only a 5-line summary plus the path. Do not edit any repository file.
```

---

## Phase 4 — Simplification & over-engineering hunt

```
You challenge the APPROACH of this PR and find where the same goal could be
achieved with less and simpler code. Coding agents tunnel-vision into elaborate
solutions; your job is to step back and ask what to cut. Remember the principle:
simpler beats shorter beats clever, and complex code is worse than longer code —
do not propose dense one-liners that hurt readability. Think hard about the
problem the PR solves, not just the code it wrote.

## Inputs
- PR analysis + atomic units + the stated goal: {WS}/pr-analysis.md
- The diff: git diff {BASE}...{HEAD}
- The repo's OWN convention/best-practice docs — find and READ the relevant ones
  before judging. Look for whatever this repo ships, e.g.: the nearest AGENTS.md
  or CLAUDE.md to the changed files, a CONTRIBUTING.md or STYLE guide, a project
  rules directory (e.g. a rules/, .cursor/rules, or similar). These typically
  encode the repo's stance on test scope, comments, edit scope, and prose
  density. (Read whichever exist; skip cleanly if none are present and judge by
  the house style from grounding instead.)

## What to find
- Speculative generality: abstractions, wrappers, generics, config, optional
  parameters and default-value scaffolding, extension points with a single
  caller — anything added for a future that isn't here.
- Reinvention: new code that re-implements something the codebase or the
  language's standard library already provides. Search for the existing utility
  before flagging.
- Unnecessary indirection: helpers/layers that don't earn their keep; a thing
  done in 3 hops that the codebase does in 1.
- Redundant or over-broad tests that add maintenance without confidence (the
  test-scope principle: if removing a test wouldn't reduce confidence, delete it).
- Whole-approach alternatives: if a structurally simpler design reaches the same
  goal, describe it concretely (what to keep, what to collapse) — even if it's a
  bigger change, surface it as an option with a clear cost/benefit.

## Output
Write markdown to {WS}/simplification.md. For EACH opportunity:
- id (s1, s2, …), the atomic unit(s) affected, file:line,
- the opportunity (what to simplify/remove and the simpler shape),
- why it's safe (does it preserve behavior? what could break?),
- estimated reduction (rough lines/concepts removed) and reviewer benefit,
- which repo doc/principle backs it (cite the rule if the repo documents one).
Flag behavior-changing suggestions distinctly from pure refactors. If the PR is
already appropriately simple, say so — do not manufacture cuts.
Return only a 5-line summary plus the path. Do not edit any repository file.
```

---

## Phase 5 — Synthesis into a plan

```
You turn two findings reports into ONE grounded, executable plan that
implementation agents will follow. Merge overlap, drop noise, sequence the work,
and write commit messages. Be decisive: the plan is a contract, not a menu.

## Inputs (read all)
- {WS}/consistency-gaps.md
- {WS}/simplification.md
- For context if needed: {WS}/grounding.md, {WS}/pr-analysis.md
- The repo's commit/style conventions, if it documents any (e.g. AGENTS.md /
  CLAUDE.md / CONTRIBUTING.md). Otherwise follow Conventional Commits.

## How to build the plan
1. Merge: a single code change often resolves a gap AND a simplification — make
   it one change citing both source findings. Deduplicate ruthlessly.
2. Filter: drop low-value nits that aren't worth a commit. Prefer high-impact,
   reviewer-visible improvements. Keep the change set tight.
3. File ownership: EVERY file is owned by exactly ONE change — merge all edits to
   a given path into a single change, even if they resolve different findings.
   This guarantees each change is a clean one-commit unit (the orchestrator stages
   whole files) and that no two changes ever touch the same file.
4. Order & group: compute dependencies (a change that deletes a function must
   precede one that edits its caller, etc.) and assign parallel_groups. The
   orchestrator runs one group at a time in dependency order, and all changes
   WITHIN a group concurrently. Since files are already disjoint across changes,
   grouping is purely about `depends_on` ordering — independent changes share a
   group; a change goes in a later group than anything it depends on.
5. Specify each change so an implementer needn't re-derive intent.

## Output — write {WS}/plan.md with a "## Changes" section, one block per change:

### <id>  (e.g. c1)
- files: <exact paths the implementer may touch>
- intent: <one line>
- edit: <concrete instructions in code terms — what to remove/rewrite/align,
  enough that the implementer just executes>
- preserves_behavior: <yes | no — and if no, what changes and why it's intended>
- risk: <none | test | behavior | public-api>
- commit: <type(scope): imperative summary>   (conventional commits; NO ticket
  IDs, NO AI attribution, lower-case summary)
- source: <g#, s# findings this resolves>
- depends_on: [<ids>]
- parallel_group: <integer; ordering only — a change goes in a later group than
  anything in its depends_on. Files are already disjoint across changes, so any
  changes sharing a group run safely in parallel>

End with a "## Execution order" listing the parallel_groups in order and which
change ids run concurrently in each. Then a one-paragraph "## Summary" the
orchestrator can show the user as the pre-implementation checkpoint.
Return only that summary plus the path {WS}/plan.md. Do not edit any repository
file.
```

---

## Phase 6 — Implementation (one per change; dispatch a group in parallel)

```
You implement ONE planned change to this PR's branch. Other agents are
implementing other changes to other files in parallel, so stay strictly inside
your assigned files.

## Your change
{PASTE THE SINGLE CHANGE BLOCK FROM plan.md HERE — id, files, intent, edit,
preserves_behavior, risk}

## Rules
- Modify ONLY these files: <files>. No edits elsewhere. No "while I'm here"
  cleanups, no reformatting untouched lines, no scope creep.
- Make exactly the edit described. Preserve behavior unless the change block
  explicitly says behavior changes.
- Do NOT run git (no add/commit/push). Do NOT run lint, format, or tests. The
  orchestrator verifies and commits across all changes.
- Match the surrounding code's style — the whole point is to fit in. If you're
  removing over-engineering/comments/tests, align to the house style, don't
  introduce a new one.
- If the planned edit turns out to be wrong, unsafe, or behavior-changing in a
  way the block didn't intend, STOP and return pushback instead of improvising.

## Return
- status: done | pushback
- if done: the file:line(s) you changed and a one-line description of the edit.
- if pushback: the reason, and what you'd do instead.
Do not verify, lint, or test.
```

---

## Phase 8 — PR review guide (optional Artifact)

```
You write a PR REVIEW GUIDE for human reviewers of PR #{PR_NUMBER} — {PR_TITLE}.
Write it from the reviewer's perspective (how to understand and review this
change), NOT as a changelog of edits that were made to the PR. Reuse the analysis
already gathered; you have rich material.

## Inputs (read all)
- {WS}/grounding.md       — the codebase & flows BEFORE the change
- {WS}/pr-analysis.md     — the goal and the new code
- {WS}/plan.md            — what was refined (for the "state after" view)
- The current diff:  git diff {BASE}...{HEAD}

## The guide must contain, in this order
1. Context — the codebase before the change. Explain the relevant flows AS THEY
   WERE, with real code samples and file:line references (pull these from
   grounding.md). The reviewer should understand the starting point.
2. What the PR does. The goal and the functionality added, with code samples
   from the new code. Crucially, tie it back: "here is how the before-code shown
   above changes into this" — show the transition, not just the new state.
3. How to review this PR. A recommended reading order (which files/units first
   and why), what to scrutinize (risk areas, behavior changes from plan.md), and
   what is safe to skim. Reference atomic units from pr-analysis.md.

Use concrete code samples throughout; reference file:line so a reviewer can jump
to source. Be accurate — every claim grounded in the artifacts/diff.

## Output
Return the guide as a single self-contained HTML or Markdown document suitable
for rendering as a Claude Artifact. The orchestrator will render it.
```
