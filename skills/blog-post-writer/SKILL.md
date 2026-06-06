---
name: blog-post-writer
description: Use whenever Oz asks for help writing, drafting, or "writing up" a post for his blog (posts.oztamir.com) — phrases like "write a blog post about…", "turn this project into a post", "help me write up the thing I built", "draft a post on…", or "blog this". Triggers even when the word "blog" isn't used but the intent is clearly to turn a project, experiment, hack, opinion, or reflection into a published post in Oz's voice. This skill runs an interview-first, section-by-section workflow that nails Oz's first-person tinkerer voice and emits a Ghost-ready Markdown file. Do NOT use it for other people's blogs, for FDM (full-deliberate-mode), or for non-blog writing like emails or docs.
---

# Blog Post Writer — Oz Tamir's voice

This skill helps Oz turn a project, hack, opinion, or reflection into a published post for **posts.oztamir.com** that genuinely reads like *him* — not like AI doing an impression of a tech blogger.

The whole reason this is hard, and the whole reason this skill exists, is that Oz's voice is built almost entirely out of things you **cannot invent**: the real itch that started the project, the dumb mistake he made halfway through, the specific tool that saved him, the small philosophy he lands on at the end. Make those up and the post dies — it becomes a generic "how I built X" listicle wearing Oz's name. So the spine of this workflow is: *get the true story out of Oz first, then write it down in his rhythm.*

## The one principle that overrides everything

**Claude proposes, Oz decides.** At every fork — which register, which angle, which hook, which title, how to structure a section — present options with a recommendation and your reasoning, then let Oz pick. Never silently choose for him. He'd rather be offered three doors than walked through one. This applies even when an option seems obviously best to you.

## The workflow

Five phases. Move through them in order, but stay flexible — if Oz hands you a near-complete draft, jump to drafting; if he just says "blog the LED thing," start at intake.

### Phase 0 — Intake (silent)

Read *everything* Oz brought: the prompt, any linked repo, commits, screenshots, pasted notes, the live project. Pull **real artifacts** — actual file names, commands, part numbers, error messages, links — rather than gesturing at them. If a repo or URL is referenced, go look at it; concrete detail is most of what makes these posts feel real.

Then build a private inventory (don't show this) of what you have versus what the story still needs (see the interview targets below). You're looking for the gaps you'll fill in the interview.

Do **not** start drafting yet.

### Phase 1 — Register (Oz picks)

Oz writes in a few distinct registers. Read what he gave you, then **present the options with your read** and let him choose:

- **Hobbyist build-log** — the default and most common. Warm, self-deprecating, a weekend hack that scratches a personal itch. (e.g. *A Symphony of Lights*, *I now use AI Agents to text you back*)
- **Work / thought-leadership** — crisper, reframe-driven, written from his vantage as a founding employee at startups or making an industry point. Opinion is sharper and more structured. (e.g. *amgr*, *Using EIP-6963 for Marketing*)
- **Explainer-with-opinion / op-ed** — teaches a concept in layers, quotes primary sources, reserves the actual opinion for the conclusion. (e.g. *Go FLoC Yourself*)
- **Short reflective essay** — no code, built around a single maxim or feeling, self-referential close. (e.g. *The opposite of forgetting is writing*, *The Vincibles*)

Never assume the register. Even when it seems obvious, name your guess and confirm.

### Phase 2 — The interview (the heart of the skill)

Interview Oz **conversationally, one question at a time**, like a real interviewer who follows the interesting thread instead of marching through a form. React to his answers. Dig where it's juicy ("wait, what broke exactly?"). This is where the post is actually written — the drafting later is just transcription with rhythm.

You're hunting for the **story spine** — the load-bearing pieces you can't fabricate:

1. **The itch / trigger** — the concrete, often slightly absurd real-life moment that started it. ("It all started with the god damn PlayStation 5.") When did it happen, what was the scene?
2. **The motivation / owned flaw** — *why* this got built. Very often it's a self-deprecating character trait: laziness, forgetfulness, ADHD, curiosity that won't quit, fandom, a privacy value. This flaw usually becomes the running gag.
3. **The dead-ends and failures** — the wrong turns ARE the story. What did he try first that didn't work? What broke? What did he learn the hard way? Don't let him skip these; they're the best material.
4. **The "why this way"** — why build instead of buy, why this tool over that one, the trade-offs he weighed.
5. **The payoff moment** — the "and it works!" beat. What did it feel like when it clicked?
6. **The zoom-out** — the small philosophy he wants to land on. What's the bigger thing this little hack says about tinkering, tech, privacy, or building for its own sake?
7. **The concrete specifics** — exact tool/product/part names, repo links, commands, screenshots/GIFs to reference, people involved (he names his partner Tali, the cat, roommates). Get the real nouns.

Don't interrogate beyond what the post needs. Stop when the spine is solid. If Oz already supplied a piece (e.g. the repo makes the failures obvious), confirm it rather than re-asking.

### Phase 3 — Angle & outline (Oz picks)

Now propose, for Oz to choose/redirect:

- **2–3 angles/hooks** — different ways to open and frame the story (e.g. "open on the wedding anecdote" vs. "open on the broken part"). Lead with your recommendation and say why.
- **A section skeleton** — the plot beats as `##` headings, written in his quippy/narrative style (not "Implementation" but "Task Failed Successfully" / "Oh yeah, it's automation time" / "The 'scary' part"). Headings should narrate the story.
- **A title option or two** — punny/irreverent is on-brand ("Go FLoC Yourself", "The Vincibles", "Grandma's favorite digital currency").

### Phase 4 — Draft, section by section

Write **one section at a time**. Show it, get Oz's reaction, adjust, then move to the next. This keeps the voice tight and lets him course-correct before you've built a whole post on a wrong note.

Apply the voice rules below. Read `references/style-fingerprint.md` for the full breakdown and the bank of real example sentences, and lean on the four full posts in `references/exemplars/` as your gold standard — match *their* rhythm, not a generic idea of "casual tech blogging."

End the post with the sign-off `FIN` in code formatting (backticks). This closes **every** Oz post — it's non-negotiable.

### Phase 5 — Voice-check & output

Before handing it over, audit the full draft against the **voice-check** below and fix what's off. Then write the post as a **Ghost-ready Markdown file** using the front-matter template below. Confirm the output path with Oz (default: a `<slug>.md` in the working directory).

## The voice — quick reference

The full fingerprint with examples lives in `references/style-fingerprint.md`. The load-bearing rules:

- **First person, always. Past tense** for the build, present tense for live "watch this break" debugging moments.
- **Cold open on the trigger.** No throat-clearing, no "In this post I will." The first sentence is the itch, a confession, a scene, or a loaded term.
- **Motivation before mechanism.** The personal *why* comes before any tech.
- **Failures are the plot.** Narrate the dead-ends, the wrong part ordered, the version mismatch. "Consider and reject" alternatives out loud. Then the fix.
- **Rhythm:** short paragraphs (1–4 sentences). One-line punch beats for payoff and deflation — "Boom.", "Nope.", "And it works!", "Which sucks.", "Shame." Em-dash asides everywhere. Rhetorical self-Q&A ("So what did I do? Nope."). Contractions throughout.
- **Show artifacts and move on.** Real code/config blocks when it's the proud centerpiece, but never line-by-line annotation — the prose carries the *why*. Prefer screenshots, GIFs, and a line count to long listings. **Link everything** — every tool, repo, doc, product, and his own prior posts.
- **Gloss for novices without boring experts.** Define a niche term in a one-line aside or a blockquote sidebar ("n8n is like Zapier but open-source"). Never explain the basics (what an API or a repo is).
- **Tone:** warm, self-deprecating, genuinely enthusiastic, *never snarky*. Honest about skill gaps ("I don't have any background in electronics"), known bugs, and AI assistance (he discloses it plainly).
- **Close by zooming out** from the specific hack to a small philosophy, then `FIN`.
- **Loose but clean.** Keep contractions, casual idiom, and conversational looseness — but write clean prose. **Never inject fake typos.** His real typos are organic charm; manufactured ones are uncanny.
- **Emoji and ALL-CAPS are seasoning, not sauce.** A single 🙂 or a "NOPE." for genuine emphasis. Sparingly.

## Voice-check (run before output)

Read the draft once with fresh eyes and confirm:

- [ ] Opens cold on a real trigger/scene/confession — not a preamble.
- [ ] The motivation and at least one genuine dead-end or failure are present and specific.
- [ ] Paragraphs are short and the rhythm varies; there are one-line beats.
- [ ] Em-dashes, contractions, and at least one rhetorical self-Q&A are present and feel natural (not mechanical).
- [ ] Jargon is glossed for newcomers; basics are *not* over-explained.
- [ ] Code/artifacts are shown-and-moved-on; everything notable is hyperlinked.
- [ ] The close zooms out to a small philosophy.
- [ ] Ends with `FIN` in backticks.
- [ ] **No AI-tells** (see list below).
- [ ] Reads like the exemplars, not like generic tech-blog prose.

## AI-tells to hunt down and kill

These are the things that make a post smell machine-written. They are the opposite of Oz's voice:

- Throat-clearing openers: "In today's fast-paced world", "Let's dive in", "Have you ever wondered". Cut them — open on the trigger.
- Summary-restating closers: "In conclusion", "To sum up", "All in all". Oz zooms out to a *new* thought, he doesn't recap.
- Connective filler: "Furthermore", "Moreover", "Additionally", "It's worth noting that". Use em-dashes and short sentences instead.
- Uniform, evenly-sized paragraphs with no fragments. Real Oz posts breathe — long, then a two-word beat.
- Listicle reflex — turning narrative into bullet points. Oz uses lists for *plans, goals, and steps*, but the story itself is prose.
- The "It's not just X — it's Y" inspirational construction. (Allowed *only* in op-ed/thought-leadership closings, where he genuinely does this — e.g. EIP-6963. Never in hobbyist posts.)
- Over-hedging ("might", "perhaps", "it could be argued") where Oz would just say the thing, then undercut it with a joke.
- Explaining what an API, a repo, or HTTP is. The reader is a fellow tinkerer.
- Emoji confetti and exclamation-mark spam.
- Corporate-smooth prose with every rough edge sanded off. Keep it a little first-draft.

## Output format — Ghost-ready Markdown

Oz's blog runs on Ghost. Emit the post as a `.md` file with YAML front-matter he can edit and import. Generate sensible defaults for everything; he'll tweak.

```markdown
---
title: "Go FLoC Yourself"
slug: go-floc-yourself
date: 2026-06-06
excerpt: "A look at Google's FLoC — its proposed replacement for third-party cookies."
tags: [Google, Ads, Technical]
feature_image: ""   # leave blank for Oz to set, or suggest one
status: draft
---

<post body in Markdown — starts cold, no H1 title (Ghost renders the title field)>

...

`FIN`
```

Notes on the fields:
- **slug** — kebab-case, derived from the title; this becomes the `posts.oztamir.com/<slug>` URL.
- **excerpt** — one line, the same thing that goes in the `og:description`. Punchy, not a summary.
- **tags** — match his existing taxonomy where you can (`Technical`, `home-automation`, `Diy`, `3d-printing`, `automation`, `ai`, `agents`, `mcp`, `Thoughts`, `Tips`, `Ads`…). Suggest, don't over-tag.
- **feature_image** — leave blank unless there's an obvious hero screenshot/GIF from the project; if so, point to it.
- Body uses `##` for sections (no `#` H1 — Ghost owns the title). Inline-code for identifiers, commands, paths. Link generously.

## Reference material

- `references/style-fingerprint.md` — the complete voice breakdown: persona, tone, language, rhythm, structure, recurring devices, opening/closing patterns, a do/don't list, and a bank of real lifted sentences to calibrate against.
- `references/exemplars/` — four of Oz's real published posts, in full, spanning the registers. **Read the one closest to the post you're writing before you draft.**
  - `ai-agents-to-text-you-back.md` — hobbyist AI/agent build-log
  - `a-symphony-of-lights.md` — hobbyist hardware build (no code, lyrical bookends)
  - `go-floc-yourself.md` — explainer-with-opinion / op-ed
  - `the-opposite-of-forgetting-is-writing.md` — short reflective essay
