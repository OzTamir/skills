# Prompting Claude Opus 4.8

Self-contained guide for optimizing a prompt that will run on **Claude Opus 4.8**
(`claude-opus-4-8`). Source of truth (fetch for the latest):
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
and the cross-model foundations at
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Apply the version-specific levers first — they're what makes a prompt *for this model*
good rather than generic.

## What makes Opus 4.8 different (tune for these)

- **It interprets instructions literally and does not silently generalize.** If a rule
  should apply broadly, say so explicitly ("apply this to *every* section, not just the
  first"). Don't rely on it to infer a request you didn't make. This literalism is a
  feature: it gives precise, predictable behavior for well-specified prompts — so the
  payoff for a carefully scoped prompt is high.
- **It calibrates response length to perceived task complexity** rather than a fixed
  verbosity. If you need a specific length or style, state it. To reduce verbosity, a
  positive instruction works better than a negative one — e.g. "Provide concise, focused
  responses; skip non-essential context and keep examples minimal" beats "don't ramble."
  Positive examples of the desired concision outperform lists of what *not* to do.
- **It favors reasoning over tool calls** by default. If the prompt expects tool use
  (search, code execution), describe explicitly *when* and *why* to use each tool.
- **Direct, opinionated prose by default**, sparing emoji, minimal validation-forward
  phrasing. If you need a warmer/more conversational voice, ask for it explicitly
  ("Use a warm, collaborative tone; acknowledge the user's framing before answering").
- **Strong design defaults** (warm cream backgrounds, serif display type, terracotta
  accents) for frontend/visual work. Generic redirection ("make it clean") just swaps one
  fixed look for another. To get something else, either specify a concrete visual
  direction (palette hexes, typeface, spacing, radii) or instruct it to *propose 3–4
  distinct directions first and wait for a pick*.

## API knobs worth setting (only if the user controls the API call)

These are not prompt text, but they're part of "prompting" Opus 4.8. Mention them only if
the user is calling the API rather than typing into a chat UI:

- **Effort:** `xhigh` for coding/agentic work; minimum `high` for intelligence-sensitive
  tasks; `medium`/`low` only for scoped, latency-sensitive work (risk of under-thinking on
  complex tasks at low effort). If reasoning looks shallow, raise effort rather than
  prompting around it.
- **Thinking:** off unless `thinking: {type: "adaptive"}` is set. Steerable via prompt if
  it triggers too often on large system prompts.
- **Max output tokens:** start at 64k for `xhigh`/`max` so it has room to think and act.

## Foundational Claude prompting principles (apply on top)

- **Be clear and direct.** Treat the model as a brilliant new colleague with no context on
  your norms. The golden rule: if a person with minimal context would be confused by the
  prompt, so will Claude. Be specific about the desired output and constraints.
- **Give the reason, not just the request.** Explaining *why* you want something lets the
  model generalize correctly to cases you didn't enumerate.
- **Use examples (few-shot).** 3–5 relevant, diverse examples are one of the most reliable
  ways to lock format, tone, and structure. Wrap them in `<example>` / `<examples>` tags so
  they're distinguishable from instructions.
- **Structure with XML tags.** When a prompt mixes instructions, context, examples, and
  inputs, wrap each in its own descriptive tag (`<instructions>`, `<context>`, `<input>`)
  to prevent misinterpretation. Nest when there's a hierarchy.
- **Give a role.** A single system-level sentence ("You are a senior Python reviewer…")
  sharpens tone and focus.
- **Long context (20k+ tokens): put the long data at the top**, above the query and
  instructions — this can improve quality by up to ~30% on multi-document inputs. Wrap each
  document in `<document>` tags with `<document_content>` and `<source>`. For long-document
  tasks, ask the model to first quote the relevant passages, then answer.

## Strong prompt shape for Opus 4.8

1. **Role** — one or two sentences on who the model is and its job.
2. **Context / why** — the larger goal and who the output is for.
3. **Long inputs** (if any) — documents/data in XML tags, near the top.
4. **Task** — what to do, scoped explicitly (state breadth where it matters).
5. **Constraints** — hard rules, what to avoid, side-effect limits.
6. **Output format** — structure, length, tone, with a positive example if format matters.
7. **Examples** — a few `<example>` blocks for non-trivial format/tone.

## Checklist before finalizing an Opus 4.8 prompt

- [ ] Every instruction that should apply broadly says so explicitly (no reliance on
      silent generalization).
- [ ] Desired length/verbosity is stated if it matters, phrased positively.
- [ ] Tool-use expectations (when/why) are explicit if tools are in play.
- [ ] Tone is specified if anything other than direct/neutral is wanted.
- [ ] For visual/frontend work: a concrete direction or a "propose options first" step.
- [ ] Long inputs are at the top, wrapped in XML; query is at the end.
