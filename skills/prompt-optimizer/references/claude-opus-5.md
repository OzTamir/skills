# Prompting Claude Opus 5

Self-contained guide for optimizing a prompt that will run on **Claude Opus 5**
(`claude-opus-5`). Source of truth (fetch for the latest):
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5
plus the cross-model foundations at
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
and the context-engineering shifts in `context-engineering-claude-5.md` (read that one too
when the "prompt" is really a system prompt, CLAUDE.md, skill, or agent harness).

Opus 5 is built for complex agentic coding and enterprise work, with particular strength on
long-horizon agentic tasks. It performs well out of the box on prompts written for Opus 4.8
— so the job here is usually **subtraction**, not addition. The most common failure mode is
a prompt carrying over scaffolding (verification steps, re-check instructions, heavy
guardrails) that Opus 5 does natively and that now causes over-verification and wasted
tokens.

## What makes Opus 5 different (tune for these)

- **Delete verification and re-check instructions.** Opus 5 verifies its own work and
  catches its own mistakes without being told to. Lines like "include a final verification
  step for any non-trivial task", "use a subagent to verify", "double-check your answer",
  or "re-verify before responding" *compound* with its native behavior: they cause
  over-verification, burn tokens, and don't improve quality. Same for legacy harness
  scaffolding that adds a separate verification pass.
- **It scopes up if you let it.** Opus 5 can add steps that weren't requested and apply its
  own judgment about what the task "should" be. For narrow tasks, constrain scope
  explicitly (snippet below).
- **Responses run longer than prior Opus models', and effort doesn't fix that.** Effort
  controls how much it *thinks*, not how much it *says*. If length matters, prompt for it
  (snippet below). This applies separately to chat responses and to files it writes to disk
  — documents/reports it authors also skew long and need their own length calibration.
- **It narrates a lot during agentic work.** It announces what it's about to do, and
  per-message output in agentic sessions is longer than prior models'. Specify the cadence
  and shape of progress updates you actually want.
- **It narrates its own corrections more than prior models.** Undesirable in user-facing
  products; scope corrections to ones that matter (snippet below).
- **It delegates to subagents readily.** Great for genuinely independent, sizeable tracks;
  expensive when applied to small tasks. If the harness has subagents, say when delegation
  is warranted or cap it.
- **Literal on "be conservative" instructions.** In code review, "only report high-severity
  issues" or "be conservative" makes it report *less*. Ask it to report everything and
  filter in a separate pass. Its review precision and recall are high enough that filtering
  downstream beats suppressing upstream.
- **1M token context window** as both default and maximum, with instruction following, tool
  calling, and reasoning holding up throughout the window.
- **Strong vision** (charts, documents, diagrams, UI/frontend replication). Re-validate any
  vision workarounds tuned for older models — they're probably unnecessary now. Vision is
  best when the model has tools to iteratively analyze, crop, and visually verify; tool use
  beats thinking alone as a lever there.
- **Office/document tasks** (multi-sheet spreadsheets with real formulas, slide decks) work
  well — but supply the specific styles or templates it should follow.

## High-value prompt snippets (lift these into the optimized prompt when they fit)

Conciseness for a user-facing, multi-turn product:

```
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and spend
most of the response on the main answer. When asked to explain something, give a high-level
summary unless an in-depth explanation is specifically requested.
```

In a long system prompt, pair that with a short reminder near the end:

```
<tone_preference>
Keep outputs reasonably concise.
</tone_preference>
```

Progress-update cadence for agentic work (tuning narration *down*):

```
Before your first tool call, say in one sentence what you're about to do. While working,
give a brief update only when you find something important or change direction. When you
finish, lead with the outcome: your first sentence should answer "what happened" or "what
did you find," with supporting detail after it for readers who want it.
```

Length calibration for written deliverables (files, reports, Markdown docs):

```
Match the length of written documents to what the task needs: cover the substance, but do
not pad with filler sections, redundant summaries, or boilerplate.
```

Scope control for narrow tasks:

```
Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and
check in only when different readings of the request would lead to materially different
work. If the request seems mistaken or a better approach exists, say so in a sentence and
continue with the task as asked rather than quietly narrowing, widening, or transforming
it. Finish the whole task, and stop short of actions that are clearly beyond what was asked.
```

Subagent delegation caps (only if the harness supports subagents):

```
Delegate to a subagent only for large tasks that are genuinely independent and
parallelizable, such as a wide multi-file investigation. Do not delegate work you can
finish yourself in a handful of tool calls, and do not use subagents to verify or
double-check your own work. If one subagent can complete the task, use one rather than
several, and keep spawn counts low.
```

Limiting correction narration in user-facing products:

```
Only correct an earlier statement when the error would change the user's code, conclusions,
or decisions. State corrections plainly and briefly, then continue the task. For slips that
change nothing for the user, make the fix and move on without noting it.
```

To tune narration *up* or change its style, the same lever applies in reverse: describe
what updates should look like and give positive examples. Positive examples of the wanted
style beat instructions about what not to do.

## API knobs worth setting (only if the user controls the API call)

- **Effort:** `high` is the default and the recommended starting point. Step up to `xhigh`
  for demanding coding and agentic work, `max` when a task justifies unconstrained token
  spend. Use `low` and `medium` **liberally** as the primary control for cost and latency
  wherever evals show quality holds — Opus 5 gets strong quality at a fraction of the
  tokens at those levels, and code-review accuracy in particular holds up at lower effort.
  If effort defaults were carried over from an older model, re-run an effort sweep.
- **Effort is not a length control.** Lowering effort reduces thinking, not visible
  response length. Prompt for length.
- **Thinking is on by default.** It can only be disabled at effort `high` or below —
  `thinking: {"type": "disabled"}` at `xhigh` or `max` returns a 400.
- **Prefer thinking-on at low effort over thinking-off.** For most tasks, thinking enabled
  at `low` effort beats thinking disabled at similar cost, and it avoids the two artifacts
  below.
- **Max output tokens:** start at 64k for `xhigh`/`max` so it has room to think and act
  across tool calls and subagents.

### If thinking must stay disabled

Two artifacts can occasionally appear:

1. **Tool calls emitted as text** instead of a structured `tool_use` block. The turn
   completes, the call never runs, and in agentic loops the leaked text stays in history
   and pollutes later turns. Most common on tool-heavy workloads like search.
2. **Internal XML tags** (`<thinking>` and friends) leaking into the visible response. If
   the system prompt tells the model not to think or not to reason, **remove that rule** —
   it increases leakage.

One combined instruction mitigates both (don't name thinking tags specifically; the general
form works better):

```
When you use a tool, you may say a brief sentence first. If no tool can express what the
user asked for, say so instead of guessing. Do not include internal or system XML tags in
your response.
```

## Foundational Claude prompting principles (apply on top, but lightly)

- **Be clear and direct, and give the reason.** Explaining *why* lets the model generalize
  correctly to cases you didn't enumerate. The golden rule: if a colleague with minimal
  context would be confused by the prompt, so will the model.
- **Give the complete task specification up front and let it run.** Opus 5 is strongest on
  multi-file features, larger refactors, and end-to-end work when it has the whole spec —
  it completes tasks rather than leaving stubs.
- **Examples still lock format and tone** — wrap them in `<example>` tags — but you need
  fewer than with older models, and over-exampling constrains its exploration space. Prefer
  well-designed inputs/interfaces over piles of examples.
- **XML tags** to separate instructions / context / inputs when the prompt is complex.
- **Long context:** long data at the top, query at the end; wrap documents in XML tags.
- **Re-evaluate every carried-over guardrail.** Ask of each line: "does this capable model
  still need this?" For verification, re-checking, and defensive rules, the answer is
  usually no.

## Strong prompt shape for Opus 5

1. **Role + intent** — who the model is and *why* the work matters.
2. **Goal** — the complete task specification, stated as an outcome.
3. **Context / long inputs** — relevant material in XML tags, near the top.
4. **Scope boundaries** — what's in and out; the scope-control line if the task is narrow.
5. **Constraints** — hard rules, side-effect limits, delegation caps if subagents exist.
6. **Output** — format, length, tone; separate calibration for chat vs. written files.
7. **Communication** — narration/progress-update cadence if the run is agentic.

## Checklist before finalizing an Opus 5 prompt

- [ ] No verification, re-check, or "double-check your work" instructions survive from an
      older prompt.
- [ ] No "be conservative / only report the worst" instruction where the goal is coverage
      (report everything, filter in a second pass).
- [ ] Response length is prompted for explicitly if it matters — effort won't do it.
- [ ] Written-deliverable length is calibrated separately if the model writes files.
- [ ] Narration/progress-update cadence is specified for agentic runs.
- [ ] Scope is constrained explicitly for narrow tasks.
- [ ] Subagent delegation is bounded if the harness supports subagents.
- [ ] Correction-narration is scoped if the product is user-facing.
- [ ] The full task spec is given up front rather than drip-fed.
- [ ] If thinking is disabled: no "don't think/reason" rule, and the combined
      tool-call/XML-tag instruction is present.
