# The Rules: Full Reference

This file contains detailed guidance for auditing against each of the 10 auditable rules. Use it to make accurate, specific, example-grounded judgments.

## Sources

- **David Ogilvy**, "How to Write" memo, September 7, 1982 — 10 rules, circulated to Ogilvy & Mather management.
- **Kenneth Roman & Joel Raphaelson**, *Writing That Works* (Harper & Row, 1981) — the book Ogilvy names in rule #1 and insists everyone read three times.

---

## Rule 1 — Natural voice (Ogilvy #2: "Write the way you talk. Naturally.")

**The test:** Read the sentence aloud. Would a real person say it that way to another real person?

**Violation patterns:**
- "Pursuant to our earlier discussion..." (no one talks like this)
- "It has come to my attention that..." (corporate throat-clearing)
- "We are writing to inform you that..." (bureaucratic opener)
- "Please be advised that..." (signals distance, not information)
- Passive voice where active would be natural: "A decision was made to..." → "We decided to..."
- Nominalizations: "make a decision" → "decide," "conduct an investigation" → "investigate"

**What "natural" doesn't mean:**
- It doesn't mean casual. Lawyers and doctors have natural voices that sound like lawyers and doctors.
- It doesn't mean slang. "LOL" in a board memo is as unnatural as "pursuant."
- It means: the writer sounds like themselves, speaking as they would to a respected peer.

**Example violation:**
> "It is incumbent upon the undersigned to communicate that the project timeline has experienced a delay."

**Fix:**
> "I need to tell you the project is running late."

---

## Rule 2 — Short units (Ogilvy #3: "Use short words, short sentences, and short paragraphs.")

**The tests:**
- **Words:** Is there a shorter word that means the same thing?
- **Sentences:** If a sentence runs past 25–30 words, does it need to? Can it split?
- **Paragraphs:** If a paragraph runs past 5–6 sentences (or ~100 words), does it cover one idea or several?

**Short-word swaps (Ogilvy's style):**
- utilize → use
- commence → start, begin
- endeavor → try
- facilitate → help, make easier
- terminate → end, fire
- implement → do, put in place
- demonstrate → show
- approximately → about
- subsequent → next, later
- in order to → to

**Long-sentence diagnostic:** Count clauses. If a sentence has more than two clauses joined by "and," "but," "which," or semicolons, it's usually hiding two or three sentences.

**Paragraph diagnostic:** Can you identify the single sentence that carries the paragraph's point? If you can't, the paragraph has more than one point and should split.

**Example violation:**
> "In order to facilitate the implementation of the aforementioned strategy, it will be necessary for all relevant stakeholders to convene at a subsequent date to be determined, at which point we will endeavor to finalize the operational details."

**Fix:**
> "We need to meet to finalize the plan. I'll send a date."

---

## Rule 3 — No jargon (Ogilvy #4: "Never use jargon words like reconceptualize, demassification, attitudinally, judgmentally. They are hallmarks of a pretentious ass.")

**The test:** Would someone outside this specific company or industry know what this word means? If not — and if a normal word would do — it's jargon.

**Common offenders:**
- leverage (as a verb), synergies, verticals, circle back, take offline
- bandwidth (when used metaphorically), drill down, deep dive, low-hanging fruit
- ideate, iterate (when used vaguely), pivot (when not talking about actual pivots)
- value-add, move the needle, boil the ocean, at the end of the day
- operationalize, incentivize, strategize, socialize (when used metaphorically)
- stakeholder (often — "stakeholder" sometimes has no referent)
- robust, scalable, holistic, ecosystem (outside biology), paradigm

**When jargon is OK:**
- Technical writing where the term has a precise meaning the audience shares. "API rate limit" in dev docs is fine.
- Legal, medical, and scientific terms of art, when the audience is in the field.

**When jargon is not OK:**
- Anywhere in customer-facing copy.
- When a plain word would carry the exact same meaning.
- When the writer is using it to sound important rather than to be precise.

**Example violation:**
> "We need to leverage our core competencies to ideate scalable solutions that move the needle on key stakeholder KPIs."

**Fix:**
> "We need to use what we're good at to come up with ideas that matter to our customers."

---

## Rule 4 — Suspicious quotations (Ogilvy #6: "Check your quotations.")

**The test:** Flag any quotation in the text. You can't verify them, but you can flag them for the writer to re-check.

**Violation patterns:**
- Attributed quotes ("As Einstein said...") — famously misattributed 90% of the time
- Paraphrases presented as quotations
- Quotes without a source
- Statistics presented as precise when they're probably rounded or approximate

**How to flag:**
Don't say the quote is wrong — you don't know that. Say: "Verify this quote; attributed quotations are a common source of error. Ogilvy's rule #6 is 'check your quotations.'"

If no quotations appear in the text, mark this rule as Pass and move on.

---

## Rule 5 — Read-aloud test (Ogilvy #7: "Never send a letter or a memo on the day you write it. Read it aloud the next morning — and then edit it.")

**The test:** When you (as auditor) read the sentence aloud in your head, does it stumble? Are there tongue-twisters, awkward rhythms, repeated sounds, or places where you run out of breath?

**Violation patterns:**
- Strings of similar sounds: "The situation's specification specifies..."
- Long sentences with no comma rest: a 35-word sentence without a breath is physically hard to read aloud.
- Unintentional rhymes or near-rhymes in prose: "The initiation of the presentation caused frustration..."
- Repeated words within a sentence where it wasn't stylistic: "We will review the review of the review process."

**Note:** You can't enforce "sleep on it" — that's behavioral (Rule 7 in your output). But you *can* audit whether the prose reads smoothly aloud, which is what the rule is actually about.

**Example violation:**
> "The comprehensive implementation of the recommendation requires examination of the documentation."

**Fix:**
> "To act on the recommendation, we'll need to review the docs."

---

## Rule 6 — Clear CTA (Ogilvy #9: "Before you send your letter or memo, make sure it is crystal clear what you want the recipient to do.")

**The test:** Read only the writing. Can you state, in one sentence, what the recipient is supposed to do next? If you have to guess, it fails.

**Violation patterns:**
- Information dumps with no ask at the end
- Multiple asks buried in the middle: "...and if possible also send over the Q3 numbers..."
- Vague requests: "Let me know your thoughts" (by when? in what format? for what decision?)
- Passive asks: "It would be great if someone could..."
- Asks hidden in final paragraphs after unrelated context
- FYI-framed messages that are actually requests

**When there's no CTA needed:**
- Pure informational updates where no action is required. These should explicitly say so: "No action needed — sharing for awareness."
- If the writer has made "no action required" clear, this rule passes.

**When the CTA is critical:**
- Any message that requests a decision, approval, deliverable, attendance, response, or change in behavior.

**Example violation (buried CTA):**
> "Hi team, wanted to share some thoughts on the Q3 roadmap. As you know we've been discussing priorities. There are a few tradeoffs worth considering. The engineering team has capacity concerns. I think we should probably decide on this by Friday so we can stay on track. Let me know."

**Fix:**
> "Hi team — I need a decision by Friday on whether to prioritize feature A or feature B in Q3. Please reply with your pick and any concerns. Context below."

---

## Rule 7 — Comprehension (R&R: "People seldom act on what they cannot understand.")

**The test:** Could the intended reader — not an insider, but the actual recipient — understand what's being said on first read?

**Violation patterns:**
- Unexplained acronyms (especially internal ones)
- References to prior context the reader may not share ("as discussed in the offsite")
- Compressed logic that skips steps
- Sentences that require re-reading to parse
- Assumed knowledge: "Obviously, given our Q2 pivot..."
- Pronouns without clear antecedents: "They said this would happen" — who is *they*?

**This is different from Rule 3 (jargon).** Jargon is specific bad words. Comprehension is the bigger question: after reading the whole thing, does the reader actually know what's going on?

**Diagnostic question:** If you handed this to someone who wasn't in the last meeting, would they get it?

**Example violation:**
> "Given the PM's view on the KR slippage and what Jake flagged yesterday, we should probably escalate to the ELT before the ops review."

**Fix:**
> "Jake flagged yesterday that we're going to miss our Q3 goal on customer response time. Our PM agrees this is serious. Can we get this in front of the leadership team before Thursday's ops review?"

---

## Rule 8 — Completeness (R&R: "When you say something, make sure you have said it. The chances of your having said it are only fair.")

**The test:** Did the writer actually state the thing they meant to state, or did they dance around it?

**Violation patterns:**
- Questions implied but not asked
- Requests implied but not made
- Conclusions implied but not stated
- The main point arriving halfway through, or not at all
- Subject lines or opening sentences that hint rather than declare

**Diagnostic:** What is the ONE thing the reader needs to take from this? Is that thing actually written down, in plain language, somewhere the reader will see it?

This rule overlaps with Rule 6 (CTA) but is broader. CTA is about action. Completeness is about whether the *message itself* is fully delivered. A message can have no CTA and still fail completeness by not stating its actual point.

**Example violation:**
> "I was thinking about the project timeline and some of the dependencies, and Sarah mentioned some concerns in our 1:1 last week. There's a lot going on with vendor availability too. Anyway, just some things on my mind."

**Fix:**
> "I think we're going to miss the November launch date. Sarah and I have each flagged concerns, and vendor availability is a new risk. I want to talk through pushing to December."

---

## Rule 9 — Honesty / no hedging (R&R: "Intelligent readers develop a nose for deceptive writing and are seldom taken in by it." Also: "Bad news is not made better by being baffling as well as unwelcome.")

**The test:** Is the writer saying what they mean, or hiding behind softening language?

**Violation patterns — euphemisms:**
- "right-sizing" → layoffs
- "we're going to part ways" → we're firing you / you're fired
- "challenging" → bad, failing
- "opportunity for improvement" → problem
- "reached out" → contacted, called, emailed (pick one)
- "circling back" → following up
- "we've decided to go in a different direction" → we're rejecting your proposal

**Violation patterns — weasel words:**
- "arguably," "somewhat," "perhaps," "it could be argued," "some might say" (when the writer actually holds the view)
- "we believe" / "we think" as a shield for controversial claims
- Hedging adverbs: "potentially," "possibly," "likely" stacked to avoid commitment
- Passive voice used to hide the actor: "mistakes were made"

**Violation patterns — bad news specifically:**
- Burying the lede in sympathy language
- Euphemisms for the actual decision
- Explaining the process instead of stating the outcome
- "After careful consideration..." openings that delay the point

**When hedging is OK:**
- Genuine uncertainty, honestly acknowledged: "I'm not sure — it might be either A or B" is fine.
- Calibrated confidence: "likely" used when the probability is actually around 70% is fine.

**When hedging is not OK:**
- When the writer knows the answer and is softening it.
- When the hedge lets the writer avoid accountability for a clear claim.
- When the reader has to decode what the writer actually means.

**Example violation:**
> "After careful consideration of a number of factors, and following extensive discussion among the leadership team, we have made the difficult decision to pursue a restructuring that will unfortunately impact approximately 15% of the workforce."

**Fix:**
> "We're laying off 15% of the company. Here's why, and here's what happens next."

---

## Rule 10 — Facts with context (R&R: "Never present facts on their own, like unstrung gems.")

**The test:** For each fact, number, or data point in the text: does the reader know why it matters? Is it connected to a point?

**Violation patterns:**
- Statistics dropped with no interpretation: "Revenue was $4.2M."
- Bullet lists of numbers with no accompanying argument
- "The data shows..." followed by data but no "...therefore..."
- Charts or tables referenced without the takeaway stated
- Cherry-picked metrics without context of what's normal
- Percentages without denominators: "engagement is up 40%" (from what, over what period, vs. what benchmark?)

**R&R's metaphor:** Facts are building materials. Most readers are not impressed by a pile of bricks. They want to see the building.

**Diagnostic:** For every fact in the text, ask: "So what?" If the text doesn't answer that question, the fact is unstrung.

**Example violation:**
> "Q3 revenue was $4.2M. Customer acquisition cost was $340. NPS was 62. Churn was 3.1%."

**Fix:**
> "Q3 was our best quarter yet. Revenue hit $4.2M (up 30% YoY), and we pulled CAC down to $340 while keeping NPS above 60. Churn did tick up to 3.1% — that's the one number we should worry about."

---

## Auditing judgment: calibration notes

**The rules are tools, not commandments.** A great piece of writing can technically violate a rule if the violation serves the piece. A 50-word sentence can be right if the rhythm requires it. Jargon can be right if the audience lives in it. Hedging can be right if the writer is genuinely uncertain.

Your job as auditor is not to apply rules mechanically. It's to notice when a rule is being violated *without serving the writing* — and to call that out with a specific, useful fix.

**When you're torn between two severity levels, ask:**
> "Would a sharp, time-pressed reader notice this and think worse of the writer?"

- Yes, and they'd stop reading → Critical
- Yes, and they'd frown → Moderate
- Only if they were looking for it → Minor

**When a piece violates many rules at once:**
Don't list all 40 violations. Find the pattern. Three examples of jargon is enough; the writer will see the pattern. Your audit is a diagnosis, not an exhaustive code review.

**When a piece is clean:**
Say so. "This is tight, clear writing — I don't see critical or moderate violations." A writer who gets a clean audit learns what "good" looks like and has something to aim for next time.
