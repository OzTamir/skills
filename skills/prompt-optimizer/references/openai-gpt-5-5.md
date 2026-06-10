# Prompting OpenAI GPT-5.5

Self-contained guide for optimizing a prompt that will run on **OpenAI GPT-5.5**
(`gpt-5.5`). Sources of truth (fetch for the latest):
https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5 and
https://developers.openai.com/api/docs/guides/latest-model

The headline: GPT-5.5 is an **outcome-first** model. Describe the destination, the
constraints, and what "good" looks like, then leave room for the model to choose the path.
Treat it as a new model family to tune for, not a drop-in for an older GPT prompt stack —
start from the smallest prompt that preserves your contract and add only what changes
behavior.

## What makes GPT-5.5 different (tune for these)

- **Outcome-first beats step-by-step.** Define the expected outcome, success criteria,
  allowed side effects, evidence rules, and output shape. Avoid prescriptive
  "first do A, then B, then C" process guidance unless the exact path genuinely matters —
  it adds noise, narrows the search space, and produces mechanical answers.
- **Drop absolute rules for judgment calls.** Reserve `ALWAYS` / `NEVER` / `must` / `only`
  for true invariants (safety, required output fields, forbidden actions). For judgment
  calls (when to search, ask, use a tool, keep iterating) use *decision rules*, not
  absolutes.
- **Add explicit stopping conditions.** GPT-5.5 follows instructions literally and
  thoroughly; tell it when it's done. "After each result, ask: can I answer the core
  request now with sufficient evidence? If yes, answer." For retrieval, give a budget.
- **Default style is concise, direct, task-oriented.** Great for production, but
  customer-facing/conversational products need explicit personality, warmth, and
  formatting guidance. Separate **personality** (how it sounds) from **collaboration
  style** (when it asks vs. assumes, how proactive, how it handles uncertainty) — keep both
  short, and don't let them replace clear goals.
- **More efficient reasoning** — strong results with fewer reasoning tokens, even at the
  same effort. Don't pad the prompt to "force thinking."
- **It already knows the current UTC date** — don't inject it unless you need a specific
  business timezone or effective date.
- **For editing/rewriting/summaries:** tell it what to *preserve* (length, structure,
  genre) before asking it to improve style, or it may expand and embellish.

## API knobs worth setting (only if the user controls the API call)

- **`reasoning.effort`** defaults to `medium` (the recommended balanced starting point).
  Use `low` for efficient reasoning where planning/tool-use still matters; `high`/`xhigh`
  only when evals show a measurable quality gain (higher effort can cause overthinking on
  under-specified tasks); `none` only for latency-critical, no-reasoning tasks
  (classification, fast lookups).
- **`text.verbosity`** defaults to `medium`; set `low` for concise output (it's
  proportionally more concise than older models at `low`).
- **Structured Outputs:** prefer the Structured Outputs feature over describing a JSON
  schema in the prompt — it validates automatically and improves accuracy.
- **Prompt caching:** put stable content first, dynamic/user-specific content last.
- **Tools:** put most tool-specific guidance (what it does, when to use it, inputs, side
  effects, error modes) in the *tool descriptions*, not the system prompt. Use the
  Responses API for reasoning/tool/multi-turn use cases.

## Suggested prompt structure (GPT-5.5's own recommended shape)

Keep each section short; add detail only where it changes behavior.

```
Role: [1-2 sentences: the model's function, context, and job]

# Personality
[tone, demeanor, collaboration style — only for conversational products]

# Goal
[the user-visible outcome]

# Success criteria
[what must be true before the final answer]

# Constraints
[policy, safety, business, evidence, and side-effect limits]

# Output
[sections, length, tone]

# Stop rules
[when to retry, fall back, abstain, ask, or stop]
```

## High-value patterns (lift these in when they fit)

Outcome-first task framing:

```
[Do the task] end to end.

Success means:
- [concrete, checkable condition]
- [concrete, checkable condition]
- if evidence is missing, ask for the smallest missing field
```

Retrieval budget (a stopping rule for search):

```
Start with one broad search using short, discriminative keywords. If the top results
contain enough citable support, answer from them. Search again only when a required fact
is missing, the user asked for exhaustive coverage, or a specific document must be read —
not to improve phrasing or add nonessential detail.
```

Creative-drafting guardrail (slides, copy, summaries):

```
Use retrieved/provided facts for concrete product, metric, date, and capability claims,
and cite them. Don't invent specifics to sound stronger. With little citable support,
write a useful generic draft with clearly labeled placeholders instead of unsupported
specifics.
```

Preamble for perceived responsiveness on tool-heavy tasks:

```
Before any tool calls for a multi-step task, send a short user-visible update (one or two
sentences) that acknowledges the request and states your first step.
```

## Checklist before finalizing a GPT-5.5 prompt

- [ ] The prompt states the outcome and success criteria, not a rigid step list.
- [ ] `ALWAYS`/`NEVER` are reserved for true invariants; judgment calls use decision rules.
- [ ] Explicit stop / "you're done when…" conditions are present for any multi-step task.
- [ ] Personality + collaboration style are defined *only* if it's a conversational product
      (and kept short).
- [ ] No redundant current-date injection; no in-prompt JSON schema if Structured Outputs
      can be used instead.
- [ ] For edits/rewrites: what to preserve is stated before what to improve.
