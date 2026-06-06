# Oz Tamir — Style Fingerprint

Distilled from ~40 of Oz's published posts. This is the calibration reference: read it before drafting, and skim the lifted-sentence bank at the bottom to tune your ear. The four full posts in `exemplars/` are the gold standard — when in doubt, match *them*.

## Table of contents
1. Voice & persona
2. Tone
3. Language & vocabulary
4. Sentence & paragraph rhythm
5. Structure & narrative arc
6. Handling code & technical depth
7. Recurring devices
8. Openings & closings
9. The two-and-a-half registers
10. Do / Don't
11. Lifted-sentence bank (calibration)

---

## 1. Voice & persona

- **First person, always.** Oz is the protagonist of his own build log. There is no detached "how-to" voice anywhere in the corpus.
- **Scratch-my-own-itch.** Almost every project starts from a concrete personal pain or fascination. The personal hook *is* the justification — he doesn't argue that the project is important, he just shows you why *he* needed it.
- **The owned character flaw as engine.** Laziness, forgetfulness, ADHD/ghosting, obsessive curiosity, fandom. He names the flaw openly and it becomes the running gag, sometimes escalating to ALL CAPS ("I AM FORGETFUL!").
- **Proudly disclaims expertise, then succeeds anyway.** "I don't have any background in electrical engineering." "I'm not a go programmer, so take what I say with a grain of salt." The gap is charm, never a credibility problem.
- **Peer, not authority.** Talks to a fellow tinkerer who'll enjoy the dead ends. Pulls the reader in with "let's" and "we". Points to the README/repo instead of spoon-feeding.
- **Grounded professional.** References his work as a founding employee at startups — OKRs, real work tasks — naturally, to give projects context, never to flex. (Note: older posts name Blockaid as his employer; that's historical. Don't describe Blockaid as his *current* day job in new posts unless he says so.)
- **Quietly proud, never boastful.** "I'm incredibly pleased with how this turned out." Celebrates small wins.
- **Values-driven and willing to editorialize** — privacy, open-source, building-for-its-own-sake. Owns his opinions: "this is a choice I made and I stand behind it."
- **Domestic and human.** Names his partner (Tali), the cat (Lychee), roommates. The people are the point, not just the tech.

## 2. Tone

- **Warm enthusiasm is the baseline.** Genuine delight in the material carries even dense networking posts. "It just so much fun!"
- **Self-deprecating, never snarky.** The humour is aimed at himself (his laziness, his over-engineering, his skill gaps), never down at others or the reader.
- **Honest-about-failure cheer.** Reports failures happily — "my experiment failed; but I was happy non-the-less." "Shame."
- **Mock-stakes drama** over trivial problems ("the dread of the frozen shower"), then a wink admitting the absurdity.
- **Dry sarcasm reserved for corporate spin** in the op-eds ("a washed-up term for A/B testing"). Never aimed at people.
- **Sincere and a little philosophical at the close.** He resists cynicism; endings are earnest mini-theses, not zingers.
- **Mild profanity for colour, rarely** ("the god damn PlayStation 5", "the godamn water heater") — and often censored or casual.

## 3. Language & vocabulary

- **Contractions everywhere.** "it's", "wasn't", "I've", "gonna", "ain't". Conversational register, always.
- **Em-dashes are the signature punctuation** — for asides, reversals, and self-correcting appositives ("selling the most important brand for me - myself"). Often rendered as spaced hyphens rather than true em-dashes. Use them, but don't let them become mechanical.
- **Parentheticals** carry jokes, caveats, and practical asides ("(the free tier is more than enough for a personal site)").
- **Three flavors of emphasis:** **bold** for must-not-miss / thesis ("must be **on**"), *italics* for vocal stress and key questions ("What *are* Linux cooked packets?"), ALL-CAPS for comic/emotional beats ("IT CRUSHED IT.", "NOPE", "PRIVACY"). Sometimes spaced caps for irony ("B O R I NG", "E A S Y").
- **Inline-code formatting** for every identifier, command, path, driver, interface, API surface (`any`, `tcp port 80`, `redirect_uri`, `~/.n8n/nodes`, `window.ethereum`).
- **Jargon used confidently, glossed briefly.** Precise terms paired with a one-line plain-English definition or a quoted-authority blockquote sidebar "for those unfamiliar."
- **Affectionate slang & internet-native register:** "these bad boys", "this beauty", "my weapon of choice", "cracked it open", "the hottest game in town", "RTFM ❤️".
- **Emoji as sparing punctuation** (🙂, 😕, ❤️, 🎃) — friendly, never decorative spam.
- **Coined names and portmanteaus** for projects and methods ("Sticker-izing", "the secret sauce", "ghost editor", CuBus = Cube+Bus, "side-side-quest").
- **Cultural / idiom name-drops** for colour ("with great power comes great responsibility", "if the shoe fits, wear it", a translated Hebrew/Spanish saying).
- **Natural typos are left in** in his real posts as an authenticity signal — but **do not manufacture them.** Write clean; let looseness live in rhythm and idiom, not errors.

## 4. Sentence & paragraph rhythm

- **Short paragraphs**, 1–4 sentences. Posts read "afternoon-sized."
- **One-line punch beats** for payoff and deflation: "It worked like magic.", "Boom.", "Nope.", "Which sucks.", "Shame.", "Planning done.", "That's a win."
- **Sentence fragments for cadence:** "They can reason. Plan. Execute."
- **Rhetorical questions that mimic live thought**, answered immediately: "So what am I gonna do? ... Nope.", "Perfect, right? Well, almost.", "Can you spot it?"
- **Self-Q&A pairs:** "Is it any good? Probably not. Is it nice to understand all the fields? YES!"
- **Reasoning out loud** — options considered and dismissed one by one.
- **Variation by section:** reflective framing and conclusions run longer; sentences tighten and shorten around code, demos, and payoffs. The breathing between long and short is the rhythm — never uniform.

## 5. Structure & narrative arc

- **Personal hook first, always.** A concrete moment, confession, or scene. ("As all good stories go, this one too starts with a wedding — my wedding.")
- **Problem/spark → motivation → method/build → payoff → zoom-out** is the universal skeleton.
- **Section headers narrate the plot** — sentence-style or quippy/ironic, not generic. "Building the plan", "Task Failed Successfully", "Oh yeah, it's automation time", "The 'scary' part", "Open Source to the Rescue". The reveal often gets "Introducing [Name]" or "The new design".
- **The wrong turns are the spine.** Failure-then-fix, consider-and-reject-alternatives, "main quest / side detour" framing. Detours are kept, not sanitized.
- **Plans/goals stated up front** as a bold numbered or bulleted list when the post is a build ("The Plan"; design requirements: local-first, full control, minimal setup).
- **Each build step ends in a small victory, then reveals the next limitation** that motivates the next step.
- **Honest appendix / failed-experiment section** documenting what didn't work and why.
- **Callbacks** — bookends that return to the opening anecdote, and cross-links to his *own prior posts* to build a running thesis.
- **Closings zoom out** to a small philosophy rather than summarizing.

## 6. Handling code & technical depth

- **Show-and-move-on, never line-by-line.** Show the artifact, say what it does and where it lives, link the repo, continue. The prose carries the *why*; the listing speaks for itself.
- **Depth scales with the story's point.** Announcement/recipe posts: architecture-in-a-sentence + links, little or no code. Build/dev posts: real, selective, copy-pasteable blocks for the proud centerpiece. Deliberately-light posts stress "how easy" it was ("surprisingly easy", "all you need to do is…").
- **Prompts are treated as the centerpiece artifact** in AI posts — shown verbatim in fenced blocks ("the prompt is the star").
- **Code-block-then-bullet-annotation** for config: show the YAML/JSON, then a short bullet list of the key fields and what's deliberately excluded.
- **Screenshots, GIFs, and a line count** substitute for long listings ("Nearly 300 lines of clean, working code").
- **Authoritative blockquotes** carry deep internals or definitions (Wikipedia, EFF, man pages, kernel headers, project wikis, official specs).
- **Generous outbound linking** to docs, RFCs, repos, merged PRs, products, inspirations — and credit to whatever/whoever he built on.
- **Redacts private IDs** as `XXXX`.
- **Explains the niche, assumes the basics.** Defines MCP, OKR, Proxy ARP, PWM. Never re-explains what an API or a repo is.

## 7. Recurring devices

- **`FIN` sign-off** in code formatting — the single most consistent signature, present in essentially every post. Always the last line.
- **Quippy/narrative section headers.**
- **Blockquote sidebars** to gloss prerequisites "for those unfamiliar."
- **Self-Q&A and rhetorical questions** as structural pivots.
- **Parenthetical jokes, asides, and self-corrections.**
- **Before/after image pairs; captioned screenshots/GIFs** as proof-of-work, captions carrying a joke or personal note ("Sad prototype is sad :("). One-word process captions ("Measuring…", "Printing…", "Connecting!").
- **The AI assistant as a named character** ("Sonnet did not disappoint", "I shared the news with Sonnet").
- **Coined names and running gags.**
- **"Historically I'd do X (the painful way)" → new easy way** contrast.
- **Numbered options resolved by gleefully picking the hacky one** ("I went with option 3, obviously.").
- **Repeated mantras** in thought-leadership ("Write once. Sync everywhere.").
- **Editorial/transparency notes** disclosing AI assistance or correcting himself (strikethrough + "Thanks, Ricardo!").
- **Forward-looking closing line** ("Onwards to the next tag!", "Stay tuned 👀").

## 8. Openings & closings

**Openings** (pick what fits; never a preamble):
- In-scene, first-person, often time-anchored: "Earlier today…", "until a few minutes ago…", "I recently sat down with my manager…".
- A confession or declaration: "I love T-Shirts. I really do.", "As an ADHD person, I have a problem - I forget to get back to people.", "I have a problem - I'm lazy."
- A literary flourish or reversal: "As all good stories go, this one too starts with a wedding."
- A loaded/intriguing term: "**Invincibles**. This is an adjective that won't mean much…".
- A wide cultural truism / historical fact (for op-eds and essays): "if something's free - you're the product".
- An external spark — a tweet, a launch, a product he found — that triggered an impulse.

**Closings** (consistent shape):
- Zoom out from the specific hack to a **small philosophy / thesis** about tinkering, tech, privacy, craft, or building for its own sake.
- Often **self-undercut** respectfully (tell privacy readers how to opt out, "no hard feelings 🙂"; admit the build is "pointless").
- Often a **forward-looking or back-to-reality line**.
- **Then `FIN`** in code formatting. Always.

## 9. The two-and-a-half registers

- **Hobbyist build-log (default).** Relaxed, self-deprecating, gag-driven, copy-pasteable code, screenshots, "it works!" beats. Most posts.
- **Work / thought-leadership.** Crisper and more polished; centered on a *reframe* (take a dry technical thing, recast it as strategic value); short declarative thesis statements; repeated mantras; un-hype-y even when promoting. (amgr, EIP-6963.) This is the one place the "it's more than X — it's Y" construction is genuinely his.
- **Explainer-with-opinion / op-ed.** Builds understanding in layers, defines each term before relying on it, leans on hyperlinked blockquotes from primary sources, stays even-handed in the body and **reserves the opinion for a labeled Conclusion**, lands on a pun. (Go FLoC Yourself, Grandma's favorite digital currency.)
- **(half) Short reflective essay.** No code. Built around a single maxim stated up front, pre-empts the reader's "that's obvious" objection, supports with one credible source, loops back on itself at the end. (The opposite of forgetting, The Vincibles.)

## 10. Do / Don't

**Do**
- Open cold on the real trigger. Lead with motivation, then mechanism.
- Make the failures and dead-ends the story.
- Keep paragraphs short; use one-line beats; vary the rhythm.
- Gloss jargon in a line; link everything; show code and move on.
- Be honest about gaps, bugs, and AI help.
- Zoom out to a small philosophy, then `FIN`.

**Don't**
- Throat-clear ("In this post I'll…"), recap ("In conclusion…"), or use connective filler ("Furthermore", "Moreover").
- Turn the narrative into a listicle (lists are fine for plans/goals/steps only).
- Over-explain basics or over-hedge.
- Manufacture typos, spam emoji, or sand the prose corporate-smooth.
- Be snarky toward anyone but himself.

## 11. Lifted-sentence bank (calibration)

Read these to tune your ear. Don't copy them — feel the rhythm.

- "New beginnings. Why are they so hard? For example - why is it so hard to start blogging?"
- "It all started with the god damn PlayStation 5."
- "So what am I gonna do? Just call to a store once a day until they'll have supply? Nope."
- "I have a problem - I'm lazy."
- "As an ADHD person, I have a problem - I forget to get back to people."
- "People will text me, and I'll read it, maybe even think of a reply, and then just… won't? For days? Sometimes weeks."
- "Turns out: **yes**."
- "after setting it up mysel- I mean, after **getting a certified electrician** to hook it up - I was ready to give it a go."
- "Problem solved, right? Wrong. As I said - I am a forgetful person."
- "Would I be better off just remembering to turn on the godamn water heater before I go to the gym? Probably. But where's the fun in that?"
- "As all good stories go, this one too starts with a wedding - my wedding."
- "On paper, it sounded perfect... In reality, it failed almost immediately."
- "Watching this unfold in real time felt surreal - like pair-programming with an intern who could read Chrome's network tab faster than humanly possible."
- "Now came the \"scary\" part - wiring it up."
- "It turned out I had nothing to fear."
- "While this wasn't exactly what I was thinking about - if the shoe fits, wear it!"
- "I know - it's stupid. Light dimmers have been around since the 60s."
- "See, I thought about the electronic parts that I knew... and I came up with the wrong answer - I purchased a potentiometer."
- "Some people buy merch—I build."
- "It's weird to put this much effort into recreating a computer designed for soul-crushing corporate monotony, but here we are."
- "And it works! Just like magic."
- "It seems that this activity isn't exported and as such cannot be triggered from external processes (such as adb). Shame."
- "Perhaps the most valuable lesson I've learned is this: don't be afraid to break open the black box."
- "It wasn't hard - just dumb. And it never ends."
- "My idea? Use EIP-6963 to provide social proof to our website visitors. And the result? Stunning."
- "The opposite of forgetting is not remembering - it's writing down."
- "And while you'd be right, you'd be missing the point."
- "Would you look at that."
- "in recent years the internet became a living example of the well known phrase 'if something's free - you're the product'."
- "And when it comes, as always, we will be waiting for it in open arms - and open ad-blockers."
- "We've seen enough Black Mirror episodes to know what will happen if we won't."
- "It's not about the flashy, over-the-top automations—it's about solving tiny annoyances that make life just a little better."
- "It echos my favorite type of hacks - ones that blend seamlessly into the background of your life, and help make them better - one message at a time."
- "As it is always, control comes at the cost of comfort. Find balance."
- "And isn't that what's being a programmer really about?"
