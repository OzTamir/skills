# Context engineering for Claude 5-generation models

Cross-cutting reference for any Claude 5-generation target (**Opus 5**, **Fable 5**,
**Mythos 5**, **Sonnet 5**). Source:
https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
(Anthropic, July 2026 — they removed **over 80% of Claude Code's system prompt** for Opus 5
and Fable 5 with no measurable loss on coding evals.)

Read this **in addition to** the model-specific reference whenever the thing being optimized
is *durable, reused context* rather than a one-shot prompt:

- a system prompt for an agent or product
- a `CLAUDE.md` / `AGENTS.md`
- a skill (`SKILL.md`)
- tool descriptions
- anything the user will reuse across many different, unpredictable user messages

For a one-shot prompt, skim it — the "rules → judgment" and "don't repeat yourself" points
still apply. Everything below is about *subtraction*: the failure mode for these models is
an over-constrained context, not an under-specified one.

## The core diagnosis: over-constraint

The old guardrails existed to prevent worst-case behavior from weaker models. Carried
forward, they now produce **conflicting instructions** — e.g. a system prompt saying "DO NOT
add comments" while a skill says "leave documentation as appropriate" and the user asks for
something else again. Claude can usually resolve the conflict, but it has to spend reasoning
to do it, and sometimes resolves it wrong.

Ask of every line in a durable context: *does this capable model still need this, or am I
paying tokens and reasoning to constrain judgment it already has?*

## The six shifts (then → now)

### 1. Rules → judgment

**Then** (Claude Code's old system prompt):

> In code: default to writing no comments. Never write multi-paragraph docstrings or
> multi-line comment blocks — one short line max. Don't create planning, decision, or
> analysis documents unless the user asks for them — work from conversation context, not
> intermediate files.

**Now:**

> Write code that reads like the surrounding code: match its comment density, naming, and
> idiom.

Absolute rules are wrong for some subset of requests. State the *principle* and the *why*,
and let the model read the situation. Keep hard rules only where a wrong call is genuinely
costly (destructive actions, security, compliance).

### 2. Examples → interface design

Giving examples used to be the #1 rule for tool usage. Now examples **constrain the model to
the exploration space they demonstrate.** Instead, invest in the design of tools, scripts,
and files: make parameters expressive and self-describing.

Example: a Todo tool whose `status` is an enum of `pending | in_progress | completed` already
hints at correct usage; a single line ("keep exactly one item `in_progress`") defines the
requested behavior. No usage examples needed.

For prompt optimization this means: prefer a well-named, well-typed interface and a crisp
description over a gallery of examples. Examples remain useful for locking *output
format/tone* — just fewer than you're used to.

### 3. Everything upfront → progressive disclosure

Don't build a central repository of every practice you *might* need. Claude 5-gen models are
good at loading the right context at the right time.

- Move detailed, situational guidance into **skills** that get invoked when relevant
  (Anthropic moved code review and verification out of the system prompt into skills).
- Same idea for tools: **deferred loading** — the agent searches for a tool's full definition
  only when it needs it, so a large tool surface costs no context until used.
- For long skills and CLAUDE.md files: split into a **tree of files loaded at the right
  time** rather than one monolith.

### 4. Repetition → single, well-placed descriptions

Older models needed instructions repeated, and weighted the end of the context more heavily.
That's no longer true. Delete duplicated guidance: **put tool instructions in the tool
description, not also in the system prompt.** Each instruction should live in exactly one
place.

### 5. Manual memory in CLAUDE.md → auto-memory

The `#` hotkey workflow (append facts to CLAUDE.md by hand) is superseded: Claude now saves
memories relevant to the work and the user automatically. Don't design a prompt around
manual memory curation.

### 6. Simple specs → rich references

Markdown plan/spec files were the norm. Claude now handles far richer references, and
**code beats prose**:

- HTML artifacts instead of markdown descriptions
- a **detailed test suite** as the spec
- a function in another codebase to port
- **rubrics** (e.g. "what does good API design look like") that verifier agents can check
  work against

For design work specifically: an HTML mockup produces better results than a written
description *or* a screenshot.

## Where each kind of context belongs

- **System prompt** — product context and operations: what product the model is in and what
  it's doing. If you're building your own harness, this is where to spend real effort.
- **CLAUDE.md** — lightweight. A brief line on what the repo is for, then spend most of the
  tokens on **gotchas** (e.g. "all types live in one monolithic file and nowhere else").
  Never state the obvious — anything the model can learn by looking at the file tree is
  wasted tokens. Push situational instructions into skills and reference them.
- **Skills** — lightweight guides that let Claude find information when needed. They're at
  their best encoding opinions, knowledge, and practices **specific to you, your team, or
  your product**. Avoid over-constraining except in genuinely critical areas. Split long
  ones across files.
- **References** — `@`-mentioned files: specs, mockups, whole codebases. Prefer artifacts in
  code, which are high-fidelity instructions in a language the model knows well.

## Applying this in the optimizer

When the user's "prompt" is durable context, the optimized version should usually be
**shorter than what they brought you.** Concretely:

- Strip absolute prohibitions that exist to prevent old-model failure modes; replace with a
  principle plus the reason.
- Hunt for **conflicting instructions** across the layers they showed you and resolve them
  down to one statement in one place.
- Delete duplicated instructions; assign each one a single home.
- Split anything long and situational into "load when relevant" pieces, and say so.
- Replace example galleries with better-designed interfaces/parameters where the examples
  were teaching *usage* rather than *format*.
- Where a spec is being described in prose, suggest a code-shaped reference instead (test
  suite, HTML mockup, existing function, rubric).

Anthropic ships this as guidance inside `claude doctor` — the `/doctor` command in Claude
Code rightsizes skills and CLAUDE.md files automatically. Worth mentioning to the user if
what they're optimizing is a CLAUDE.md or a skill.
