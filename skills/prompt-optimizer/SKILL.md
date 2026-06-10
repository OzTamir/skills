---
name: prompt-optimizer
description: Use when the user wants to turn a rough request into a well-engineered prompt for an LLM — phrasings like "optimize my prompt", "improve/refine this prompt", "help me write a good prompt for…", "make this prompt better", "rewrite this so the model does X well", or when their opening message of a session is plainly a raw task they want to run *well in a fresh session* rather than have you execute right now. Rewrites the prompt according to the prompting guide for the specific target model (OpenAI GPT-5.5, Claude Opus 4.8, Claude Fable 5, and the closest fit for others). The skill NEVER assumes the user's intent — it interviews them with AskUserQuestion first. It is designed to run on the FIRST message of a session and to hand back a copy-ready prompt to paste into a NEW session; it only runs mid-session when the user explicitly asks, and it refuses to continue an unrelated conversation afterward.
---

# Prompt Optimizer

This skill turns a user's rough prompt into a strong, model-specific prompt — engineered
according to the official prompting guide for whatever model the prompt will actually run
on. The deliverable is a **prompt the user copies into a brand-new session**, not a task
you execute here.

## The two principles that override everything

1. **Never assume the user's intent.** A raw prompt is almost always under-specified, and
   guessing what they "probably meant" is exactly how a prompt optimizer produces a
   confidently-wrong rewrite. So you *interview first*. You may — and should — propose what
   you think they meant as concrete options, but every choice stays theirs. When you ask,
   propose options based on how you read their request, and always leave room for them to
   say what they actually intended (the AskUserQuestion "Other" field does this; lean on
   it).

2. **You optimize the prompt; you do not run it.** The whole point is a clean prompt for a
   fresh session with full context budget and no contamination from this back-and-forth.
   When the prompt is ready, you hand it over and stop (see *Finishing*).

## When this runs — the session-position rule

This skill is built to run on the **first message of a session**. That keeps the optimized
prompt unpolluted by prior context and makes "start a new session with this" a clean
handoff.

Decide which situation you're in **before** doing anything else:

- **First message of the session (normal case).** Run the full workflow below, then stop
  and refuse to continue (see *Finishing → Normal*).
- **Mid-session, and the user explicitly asked to optimize a prompt** ("optimize this
  prompt for me", "/prompt-optimizer", etc.). Run the full workflow, then at the end use
  AskUserQuestion to ask whether they want to continue here or start fresh (see
  *Finishing → Mid-session by request*).
- **Mid-session, no explicit request** (the skill seems to have triggered in the middle of
  unrelated work). Do **not** run it. Briefly say so and suggest they either start a new
  session and give you the raw prompt there, or explicitly ask you to optimize a prompt now
  if that's what they want. Then return to whatever you were doing.

"Mid-session" means there's already substantive prior work or conversation in this session
before this request. If you're genuinely unsure whether the user wants their message
*executed* or *optimized into a prompt*, ask — don't assume.

## Workflow

### Step 1 — Identify the target model

The prompt will run on some model, and the right guidance depends on it. You usually know
the model running this session from your own system context — **infer that as the default
target and say which one you assumed**, because the prompt is often meant for the same
model. But it may be intended for a different one, so confirm it as part of the interview
(Step 3) rather than locking it in silently.

Map the target model to its reference file (read the one that matches; each is
self-contained):

| Target model | Reference file | Live guide to fetch for freshest guidance |
|---|---|---|
| Claude Opus 4.8 (`claude-opus-4-8`) | `references/claude-opus-4-8.md` | platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8 |
| Claude Fable 5 / Mythos 5 (`claude-fable-5`) | `references/claude-fable-5.md` | platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 |
| OpenAI GPT-5.5 (`gpt-5.5`) | `references/openai-gpt-5-5.md` | developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5 |
| Other Claude model | closest of the two Claude files | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| Other OpenAI/GPT model | `references/openai-gpt-5-5.md` | developers.openai.com/api/docs/guides/latest-model |
| Anything else (Gemini, Llama, …) | apply the general principles in the closest file | — (tell the user the guidance is generic, not model-specific) |

### Step 2 — Load the guidance

Read the matching reference file. For the freshest possible guidance, also try to WebFetch
the live URL (these guides change as models ship); if the fetch fails or there's no
network, the bundled reference is the authoritative fallback — it's enough on its own. Let
the model-specific levers in that file drive the rewrite; a generic "good prompt" is not
the goal.

### Step 3 — Interview the user (the heart of the skill)

Use **AskUserQuestion**. Your job is to eliminate every assumption a good prompt would
otherwise bake in silently. Read their raw prompt, form a hypothesis for each open
question, and present that hypothesis as the recommended option — but always leave them a
way to answer in their own words.

Cover the dimensions that the target model's guide says matter most (the reference file
tells you which to prioritize — e.g. outcome + stop-rules for GPT-5.5; scope + brevity for
Fable 5; explicit scope + format for Opus 4.8). Across one or more rounds of questions,
nail down whichever of these are still ambiguous:

- **Target model** — confirm or correct your inferred default (recommend the inferred one).
- **The actual goal / outcome** — what "done and good" looks like, not just the topic.
- **Audience & context** — who the output is for; the larger task it feeds into; *why*.
- **Output format, length, and tone** — structure, how long, what voice.
- **Constraints & must/never rules** — hard requirements, things to avoid, side-effect limits.
- **Success criteria & stop conditions** — how the model should know it's finished.
- **Inputs & examples** — data/documents the prompt will include; any example of a good output.
- **Tools / API control** — whether the prompt involves tools, and whether the user
  controls API knobs (effort, verbosity, structured outputs) or is typing into a chat UI.

Guidance on asking well:
- Batch related questions into a single AskUserQuestion call (up to four), and run more
  rounds if needed. Don't interrogate beyond what the prompt actually needs — stop when the
  ambiguity is gone.
- Every option you offer should be a real, concrete interpretation of *their* request, with
  your recommendation first. Never smuggle in a choice you've secretly already made.
- If a dimension needs a free-form answer (their goal in their words, a specific example),
  ask it as a question whose options are genuine interpretations, and expect them to use
  "Other" to give their own — or simply tell them to type it.

### Step 4 — Write the optimized prompt

Apply the target model's guide and the prompt shape it recommends. Build the prompt only
from what the user actually told you — no invented requirements, no assumed audience.
Where the guide recommends specific structure (e.g. GPT-5.5's Role/Goal/Success
criteria/Constraints/Output/Stop-rules, or Claude's XML-tagged sections), use it.

### Step 5 — Finishing

Deliver the prompt in a single **copy-ready fenced code block**, followed by a short
**"What changed and why"** note (3–6 bullets tying the main edits to the model's guide so
the user learns, not just receives). Then:

**Normal (first-message) case:**
> Tell the user to **start a new session and paste this prompt as their first message**,
> and explain that a fresh session gives the prompt a clean context window. Then **stop**.
> Politely refuse to continue this conversation or to run the prompt here — that would
> defeat the purpose. If they push, restate briefly that this session exists only to build
> the prompt and point them to a new session. (If they explicitly change their mind and ask
> you to just run it here, that's their call — honor it.)

**Mid-session-by-request case:**
> Deliver the prompt the same way, then use **AskUserQuestion** to ask whether they want to
> **continue in this session** (you proceed with the optimized prompt as the new task) or
> **start a fresh session** (recommended, for a clean context window) — and follow their
> choice.

## Anti-patterns to avoid

- Rewriting the prompt before interviewing — you'll encode your guesses as their intent.
- Producing a generic "best-practices" prompt that ignores the target model's specific
  levers. The model-specific deltas are the whole value.
- Offering AskUserQuestion options that are all minor variants of one decision you already
  made. Give real alternatives, recommendation first.
- Continuing to chat / executing the task in the normal first-message case. Hand off and
  stop.
