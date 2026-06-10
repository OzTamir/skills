# Prompting Claude Fable 5 (and Mythos 5)

Self-contained guide for optimizing a prompt that will run on **Claude Fable 5**
(`claude-fable-5`). Source of truth (fetch for the latest):
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
and the cross-model foundations at
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

The headline shift from Opus 4.8: Fable 5 is dramatically more capable on long, ambiguous,
multi-step work, and its instruction-following is strong enough that **brief, intent-rich
prompts beat long, prescriptive ones.** Over-specifying actively degrades it.

## What makes Fable 5 different (tune for these)

- **Less is more.** A short instruction now steers behaviors that used to require
  enumerating each case. Prompts and skills written for older models are often *too
  prescriptive* and hurt quality — strip them down. One clear brevity instruction does the
  work of a long list of "don't do X" rules.
- **Aim high.** It's strongest on genuinely hard, long-horizon, well-specified problems
  (work that takes a person hours to days). Testing it only on easy tasks undersells it.
- **Longer turns by default.** Hard tasks can run for many minutes; autonomous runs for
  hours. If the workflow is interactive, you may want to instruct it to act decisively
  rather than over-plan when a task is ambiguous (see snippet below).
- **It can over-deliver at higher effort** — surveying options it won't pursue, refactoring
  beyond scope, narrating reasoning. A short scope/brevity instruction reins this in.
- **Give the reason, not just the request.** It performs better when it understands intent;
  context lets it connect the task to relevant information instead of guessing.
- **Safety classifiers:** it declines offensive-cybersecurity and biology/life-sciences
  work (benign work can trip these too). Not a prompting lever, but worth knowing.

## High-value prompt snippets (lift these into the optimized prompt when they fit)

Keep Fable 5 from over-planning on ambiguous tasks:

```
When you have enough information to act, act. Do not re-derive facts already established,
re-litigate a decision already made, or narrate options you will not pursue. If you are
weighing a choice, give a recommendation, not an exhaustive survey.
```

Lead-with-the-outcome brevity (more effective than enumerating every verbosity rule):

```
Lead with the outcome. Your first sentence should answer "what happened" or "what did you
find" — the TLDR. Supporting detail comes after. Be selective about what you include
(drop details that don't change what the reader does next) rather than compressing into
fragments, arrow chains, or jargon.
```

Prevent unrequested tidying/refactoring at higher effort:

```
Don't add features, refactor, or introduce abstractions beyond what the task requires. Do
the simplest thing that works. Don't design for hypothetical future requirements, and
don't add error handling for scenarios that cannot happen.
```

Ground progress claims on long autonomous runs (nearly eliminates fabricated status):

```
Before reporting progress, audit each claim against an actual result from this session.
Report only work you can point to evidence for; if something isn't verified, say so.
```

Define when to pause vs. proceed (so it stops only where it must):

```
Pause for the user only when the work genuinely requires it: a destructive or irreversible
action, a real scope change, or input only they can provide. Otherwise keep going.
```

## API knobs worth setting (only if the user controls the API call)

- **Effort** is the primary intelligence/latency/cost control. Default `high`; `xhigh` for
  the hardest work; `medium`/`low` for routine work (lower effort on Fable 5 often beats
  `xhigh` on older models). Reduce effort if a task finishes but takes longer than needed.
- **Thinking** is adaptive-only; output is summarized. Don't instruct the model to echo,
  transcribe, or "show" its reasoning as response text — that can trip a refusal category.
  If you need reasoning visibility, read the structured `thinking` blocks instead.

## Foundational Claude prompting principles (apply on top, but lightly)

- **Be clear and direct**, and give the *why*. State the goal, the audience, and what the
  output must contain. The golden rule: if a colleague with minimal context would be
  confused, so will the model.
- **Examples still help** for locking format/tone — wrap in `<example>` tags. But you need
  fewer than with older models; don't bury a capable model in examples it doesn't need.
- **XML tags** to separate instructions / context / inputs when the prompt is complex.
- **Long context (20k+):** long data at the top, query at the end; wrap documents in XML.
- **Re-evaluate old guardrails.** Every instruction you carry over is a chance to ask
  "does this capable model still need this?" Usually the answer is no.

## Strong prompt shape for Fable 5

1. **Role + intent** — who the model is, and *why* this work matters / what it enables.
2. **Goal** — the outcome, stated as a destination rather than a step list.
3. **Context / long inputs** — relevant material in XML tags, near the top.
4. **Constraints & scope** — what's in and out of scope; a brevity/no-overbuild line.
5. **Success criteria & stop rules** — what "done" looks like; when to act vs. ask.
6. **Output** — format, length, tone (kept short).

## Checklist before finalizing a Fable 5 prompt

- [ ] The prompt is as short as it can be while still specifying the contract — no
      carried-over over-specification.
- [ ] Intent / "why" is present, not just the literal request.
- [ ] A brevity or no-overbuild line is included if over-delivery would be a problem.
- [ ] Scope boundaries and stop/checkpoint rules are explicit for long or agentic tasks.
- [ ] No instruction asks the model to reproduce/echo its internal reasoning as text.
