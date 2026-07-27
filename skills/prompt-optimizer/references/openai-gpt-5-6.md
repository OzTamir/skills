# Prompting OpenAI GPT-5.6

Self-contained guide for optimizing a prompt that will run on **OpenAI GPT-5.6**. Source of
truth (fetch for the latest): https://developers.openai.com/api/docs/guides/latest-model
(the `prompt-guidance?model=gpt-5.6` path redirects to the same page). The GPT-5.5 tab of
that doc is the previous model's page — this file already carries forward the parts of it
that still hold, so you don't need `openai-gpt-5-5.md` unless the target really is 5.5.

The headline: GPT-5.6 is **outcome-first and lean**. It infers the user's underlying goal
and intended level of work from context, so prescribing every step wastes tokens and hurts
quality. OpenAI's own numbers: leaner system prompts scored **~10–15% better on evals while
cutting tokens 41–66% and cost 33–67%** in a sample of internal coding-agent runs. Treat
optimization as subtraction with a few high-value additions.

## Model variants (pick one)

- `gpt-5.6-sol` — flagship capability. The bare `gpt-5.6` alias routes here.
- `gpt-5.6-terra` — strong performance at a lower price.
- `gpt-5.6-luna` — efficient, high-volume workloads.

## What makes GPT-5.6 different (tune for these)

- **Leaner is measurably better.** State each instruction **once**. Remove repeated
  instructions, redundant examples, and irrelevant tools. Expose only task-relevant tools
  and keep their descriptions concise and precise. Keep examples and style guidance only
  where they encode a product requirement or correct a measured gap.
- **It infers intent well — supply context, not steps.** You often don't need to prescribe
  the path. Do still supply: domain context, hard constraints, approval boundaries, success
  criteria, and *when an important ambiguity should trigger a question*.
- **It's already more concise than GPT-5.5.** Broad brevity instructions ("Be concise",
  "Keep it short") may now be unnecessary, and can make responses *too* brief. Re-check
  whether yours still earns its place; if a task needs a short answer, say what the answer
  must **preserve** rather than just that it should be short.
- **It's proactive and persistent on multi-step tasks.** Without explicit autonomy
  boundaries it may pause too often or go further than intended. Define what level of action
  each request authorizes (snippet below).
- **Repeating approval language backfires.** Restating "ask first", "do not mutate", or
  "wait for approval" causes unnecessary approval requests for safe, expected actions. Keep
  the policy in one place, once.
- **Vague tone labels don't work.** "Friendly" / "empathetic" are ambiguous. Describe the
  writing choices instead: how directly to state the answer, when to acknowledge a problem,
  whether reassurance or a sign-off belongs.
- **Frontend design is notably better** — layout, visual hierarchy, design judgment. Fewer
  prompt-side workarounds needed for UI generation.
- **Token-efficient at frontier quality**, so don't pad the prompt to "force thinking."
- **Safety classifiers run in real time** on cyber and biology misuse, mid-generation. They
  can intervene on legitimate dual-use work (code review, vulnerability research, patch
  development, security education, defensive testing) and can pause streaming for seconds.
  Not a prompting lever, but worth flagging to the user. If the app serves individual end
  users, send a stable, privacy-preserving `safety_identifier` per request.
- **Images at `original` or `auto` detail keep their original dimensions** instead of being
  resized to a patch/pixel budget — large images cost more input tokens and latency.

### Carried forward from GPT-5.5 (still true)

- **Outcome-first beats step-by-step.** Define the expected outcome, success criteria,
  allowed side effects, evidence rules, and output shape; leave the path to the model unless
  the exact path genuinely matters.
- **Drop absolute rules for judgment calls.** Reserve `ALWAYS` / `NEVER` / `must` / `only`
  for true invariants (safety, required output fields, forbidden actions). For judgment calls
  (when to search, ask, use a tool, keep iterating) use *decision rules*.
- **Give explicit stopping conditions.** Tell it when it's done; give retrieval a budget.
- **Separate personality from collaboration style** for conversational products — how it
  sounds vs. when it asks rather than assumes. Keep both short.
- **It knows the current UTC date** — don't inject it unless you need a specific business
  timezone or effective date.
- **For editing/rewriting/summaries:** state what to *preserve* (length, structure, genre)
  before asking it to improve style, or it may expand and embellish.

## API knobs worth setting (only if the user controls the API call)

- **`reasoning.effort`** — supports `none`, `low`, `medium`, `high`, `xhigh`, `max`.
  `medium` is a balanced starting point and the default; `low` for latency-sensitive work;
  `high`/`xhigh` when more reasoning shows a *measured* quality gain; `max` reserved for the
  hardest quality-first workloads (benchmark it against `xhigh`). If migrating from GPT-5.5
  or 5.4, keep the current effort as baseline and also test **one level lower** — 5.6 often
  holds or improves quality with fewer tokens. If currently on `none`, keep it as the latency
  baseline and also test `low` when the workflow benefits from reasoning or tool use.
- **`reasoning.mode: "pro"`** — pro mode: more model work before a single final answer.
  Same model slug, no separate Pro slug. Effort is chosen independently (defaults to
  `medium` in both modes). Use it when a marginal quality gain materially changes the
  outcome and the task is hard enough to benefit — complex optimization, high-value coding
  or review, deep analysis with clear evaluation criteria. Prefer standard mode for routine,
  latency-sensitive, or high-volume work, and whenever evals show no meaningful gain.
  **Keep the prompt identical**: don't ask it to "use pro mode", "think harder", or generate
  candidate answers.
- **`reasoning.context`** — persisted reasoning across turns. Omit or `auto` for the model
  default (check the response's `reasoning.context` field for the effective mode);
  `all_turns` when goals, assumptions, and priorities stay stable across turns (continue
  with `previous_response_id` so earlier reasoning is available); `current_turn` when
  earlier reasoning is no longer relevant. Managing history manually means resending prior
  user inputs and every response output item — and replaying the encrypted reasoning items
  under `store: false` or ZDR.
- **`text.verbosity`** — `low` / `medium` / `high` as the default detail level, then use the
  prompt for task-specific length, structure, and required content.
- **Prompt caching** — implicit caching needs no code change. Cache **writes cost 1.25×**
  the uncached input rate on 5.6, so track `cached_tokens` and `cache_write_tokens`. Use
  explicit breakpoints or `prompt_cache_options.mode: "explicit"` to avoid needless writes;
  `prompt_cache_retention` is replaced by `prompt_cache_options.ttl`. Stable content first,
  dynamic/user-specific content last.
- **Structured Outputs** — prefer the feature over describing a JSON schema in the prompt.
- **Responses API** for reasoning, tool-calling, and multi-turn workflows.
- **Multi-agent (beta)** — one 5.6 instance coordinating parallel subagents and synthesizing
  results. Worth it for complex tasks that divide cleanly into independent workstreams.
- **Programmatic Tool Calling** — add the `programmatic_tool_calling` tool and opt eligible
  tools in with `allowed_callers`; see the section below for when it fits.

## Suggested prompt structure

Keep each section short; add detail only where it changes behavior.

```
Role: [1-2 sentences: the model's function, context, and job]

# Personality
[tone as concrete writing choices — only for conversational products]

# Goal
[the user-visible outcome]

# Success criteria
[what must be true before the final answer]

# Constraints
[policy, safety, business, evidence, and side-effect limits]

# Autonomy
[what this request authorizes; what needs confirmation]

# Output
[sections, length, required content]

# Stop rules
[when to retry, fall back, abstain, ask, or stop]
```

## High-value snippets (lift these in when they fit)

Autonomy and approval boundaries — a compact policy is usually enough:

```
For requests to answer, explain, review, diagnose, or plan, inspect the relevant
materials and report the result. Do not implement changes unless the request also
asks for them.

For requests to change, build, or fix, make the requested in-scope local changes
and run relevant non-destructive validation without asking first.

Require confirmation for external writes, destructive actions, purchases, or a
material expansion of scope.
```

Name the safe local actions explicitly (reading files, inspecting logs, editing in-scope
code, running tests). Keep it in one place and state each rule once.

What a short answer must include (better than "be concise"):

```
Lead with the conclusion. Include the evidence needed to support it, any material
caveat, and the next action. Omit secondary detail and repetition.

Keep all required facts, decisions, caveats, and next steps. Trim introductions,
repetition, generic reassurance, and optional background first.
```

Tone as concrete writing choices:

```
State the answer directly. If the user reports a problem, acknowledge the
specific issue before giving the next step. Use reassurance only when it is
relevant. Omit generic praise and unnecessary sign-offs.
```

Outcome-first task framing (works unchanged in pro mode):

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

## Programmatic Tool Calling (if the prompt orchestrates tools)

PTC lets the model write JavaScript to call eligible tools, pass results between calls, and
process intermediate outputs in a hosted runtime. It's ZDR-compatible with no extra
container cost.

**Fits** bounded workflows where code processes several tool results or large intermediate
outputs and returns a much smaller structured result: filtering, joining, ranking,
deduplication, aggregation, validation, other predictable processing.

**Prefer direct tool calls** when one call suffices, intermediate outputs are already small,
each result may change the next decision, an action requires approval, or the final output
must preserve citations or native artifacts. Multiple/parallel/dependent calls alone do not
justify PTC. If the model can't know a tool's return shape before writing the program, use
direct calling so it can inspect the result first.

Routing must be **task-specific** — generic "use Programmatic Tool Calling efficiently"
doesn't produce the right route. State which bounded stage uses PTC, which tools it may
call, the exact output schema and required evidence, concurrency/retry/stopping limits, and
which work stays direct. If both routes are needed, define one clear handoff and say not to
switch routes or repeat completed work:

```
<tool_orchestration>
Use Programmatic Tool Calling for [bounded stage] using only [eligible tools].
Run independent calls concurrently when safe. Use only documented tool input
and output fields.

Process and reduce the intermediate results, then emit exactly [output schema],
including the evidence needed for the final answer.

Stop when [condition] is met. Retry transient failures at most [R] times.
Do not repeat completed calls or perform side-effecting actions. If a required
result is still missing, return a clear structured failure.

Use direct tool calls for [semantic judgment, approval, or final validation].
</tool_orchestration>
```

Tool descriptions should document expected return fields, types, and error behavior. Note
that `program_output` and the final assistant `message` are separate outputs — a program can
return the right records while the message drops a required field, citation, or caveat.

## Checklist before finalizing a GPT-5.6 prompt

- [ ] Every instruction appears exactly **once**; no repeated guidance across system prompt
      and tool descriptions.
- [ ] Only task-relevant tools are exposed, with concise, precise descriptions.
- [ ] Examples survive only where they encode a product requirement or fix a measured gap.
- [ ] The prompt states the outcome and success criteria, not a rigid step list.
- [ ] Autonomy/approval boundaries are defined once, with safe local actions named.
- [ ] No repeated "ask first" / "wait for approval" language.
- [ ] Brevity instructions carried over from GPT-5.5 have been re-examined; where a short
      answer is needed, what it must *preserve* is stated.
- [ ] Tone is expressed as concrete writing choices, not a vague label.
- [ ] `ALWAYS`/`NEVER` are reserved for true invariants; judgment calls use decision rules.
- [ ] Explicit stop / "you're done when…" conditions are present for any multi-step task.
- [ ] It's stated when an important ambiguity should trigger a question.
- [ ] No redundant current-date injection; no in-prompt JSON schema if Structured Outputs
      can be used instead.
- [ ] For edits/rewrites: what to preserve is stated before what to improve.
- [ ] If PTC is in play: the bounded stage, eligible tools, output schema, and stop/retry
      limits are all named, and the rest is explicitly direct.
