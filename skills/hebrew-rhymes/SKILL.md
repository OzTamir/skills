---
name: hebrew-rhymes
description: Use whenever the user wants Hebrew rhymes or Hebrew wordplay — "מה מתחרז עם שלום", "find a rhyme for אהבה", "חרוז ל…", words that sound like / alliterate with a Hebrew word, assonance or consonance (מצלול), words matching a letter-and-nikud pattern (תבנית מילה, e.g. "3-letter words ending in -ום"), or rhymes limited to a topic (semantic field, "rhymes for ים about the sea"). Also use when writing Hebrew poetry, song lyrics, piyyut, slogans, jingles, or children's rhymes and the agent needs real rhyming words instead of guessing. Wraps Dicta's Charuzit (wordplay.dicta.org.il) in a bundled stdlib-only Python CLI with every sidebar filter (part of speech, gender, number, person, tense, suffix, syllables, stress, loanwords, proper names, Tanakh). Do NOT use for rhymes in other languages or for Hebrew translation.
---

# Hebrew Rhymes (Dicta Charuzit)

[Charuzit](https://wordplay.dicta.org.il) ("חרוזית") is Dicta's free Hebrew
rhyme and wordplay engine. It knows the pointing, stress and morphology of
the full modern Hebrew lexicon plus the Tanakh. That makes it far more
reliable than an LLM guessing at Hebrew rhymes. The skill calls the same JSON API the site's
frontend calls. You don't need an account or a key.

Everything goes through the bundled script:

```
python3 <skill-dir>/scripts/wordplay.py <command> WORD [options]
```

It is standard-library-only Python 3.9+. Run `wordplay.py <command> -h` for
every option. The full API is documented in
[references/api.md](references/api.md) in case you need to go beyond the CLI.

## The commands (the site's four tabs + helpers)

| Command | Site tab | What it finds |
| --- | --- | --- |
| `rhyme WORD` | חרוזים | Rhymes. By default includes loose "שור/חמור" rhymes (same last vowel + final consonant); `--strict` keeps only full last-syllable rhymes. |
| `sound WORD` | מצלול | Words with the same sound pattern across the word. `--kind assonance` = matching vowels, `consonance` = matching consonants, `xxsonance` (default) = both. |
| `alliteration WORD` | אליטרציה | Words that start with the same consonants. `--letters 1/2/3` sets how many (default 2). |
| `pattern PATTERN` | תבנית מילה | Words matching a letter/vowel template (syntax below). |
| `semantic WORD…` | שדה סמנטי | Only words from a semantic field, with no sound matching. |
| `vocalize WORD` | — | Lists the pointings Dicta suggests for an unpointed word. |
| `semantic-tips WORD` | — | Suggests semantic-field keywords (the site's typeahead). |

## Pointing (nikud) matters

The search API only accepts **pointed** words. The site vocalizes unpointed
input first and silently takes the top guess. The script does the same and
prints the guess and the alternatives to stderr:

```
# vocalized שמש -> שֶׁמֶשׁ   (others: [1]שַׁמָּשׁ [2]שִׁמֵּשׁ ... ; choose with --pick N)
```

Check that guess. When a word is ambiguous (ספר = סֵפֶר / סַפָּר / סִפֵּר,
שמש = שֶׁמֶשׁ / שַׁמָּשׁ), the rhymes are completely different. Pick the
right reading from context with `--pick N`, or pass the pointed word
directly. Stress follows the pointing, and by default results match the
input's stress (`--accent match`).

## Filters (every sidebar option)

Word features (מאפייני מילה). You can combine any of them:

- `--pos` noun | adjective | verb | adverb | preposition | conjunction | demonstrative
- `--gender` masculine | feminine; `--number` singular | plural
- `--person` 1 | 2 | 3; `--status` absolute | construct (נפרד / נסמך)
- `--tense` past | present | future | imperative | infinitive
- `--suffix` yes | no (pronominal suffix), plus `--suffix-gender`, `--suffix-number`, `--suffix-person`

Sound settings (חרוזים). These apply to `rhyme`, `sound` and `pattern`:

- `--strict`: turns off "כלול חרוזי שור וחמור"
- `--no-consonant-swap`: turns off similar-sounding consonants (ב/ו, ט/ת, כ/ח, כ/ק, ס/ש)
- `--no-vowel-swap`: turns off near-identical vowels (patah/qamatz, tsere/segol)
- `--accent` match | all | milra | milel

Advanced settings (הגדרות מתקדמות / סגנון טקסט):

- `--min-syl N`, `--max-syl N` (1–7, 7 means "7+")
- `--proper-names` includes proper names; `--no-foreign` drops loanwords; `--base-only` drops inflected forms
- `--semantic WORD` (repeatable) restricts any search to a semantic field, e.g. `rhyme שלום --semantic ים`. Unpointed keywords are resolved through `semantic-tips`.
- `--letters N` (alliteration only): the number of consonants to match

## Output

Results come back in the same tabs the site shows. Pick one with `--group`:
`main` (default, all matches), `common` (common words, usually the best
place to start for lyrics), `tanakh` (biblical verses with references),
`nosuffix`, `long`, `feminine`, or `all`. The site's "כלול מילים תנכיות"
checkbox in pattern mode only shows or hides the `tanakh` tab.

By default the output is one entry per lexeme: up to `--forms` inflected forms and the
lexeme in brackets. Useful switches:

- `--flat` prints one unique word per line, which is best for picking or piping
- `--plain` strips nikud
- `--limit N` sets the number of entries per group (default 40, 0 = all). The server caps each group at 300, and `300+` means there are more.
- `--json` prints raw groups; `--dump-request` shows the exact request body

## Pattern syntax

Each slot is one letter, optionally followed by pointing or a `{…}` modifier
block. Whitespace is ignored, and the site allows up to 8 slots.

| Token | Meaning |
| --- | --- |
| `ל` | that letter |
| `[בכ]` | any one of these letters |
| `?` | any single letter |
| `*` | any run of letters |
| `לֹ`, `שָׁ`, `בּ` | pointing typed after a letter: a vowel, a shin/sin dot, or a dagesh (dagesh required) |
| `{a}` `{e}` `{i}` `{o}` `{u}` | vowel class; combine them as `{a,e}` |
| `{-}` | no vowel on this letter |
| `{any}` | any vowel (what a bare letter means) |
| `{dag}` / `{nodag}` | dagesh required / forbidden |
| `{root}` / `{noroot}` | must / must not be a root letter |

Examples:

```bash
wordplay.py pattern "? לֹ ם"            # הֲלֹם, חֲלֹם, בְּלֹם …
wordplay.py pattern "מ{-} * ה" --pos noun  # nouns starting with unpointed מ, ending in ה
wordplay.py pattern --from-word שָׁלוֹם    # copy a word's exact pattern, like the site's import button
```

Holam male and shuruk sit on the ו as their own slot: שָׁלוֹם is
`שָׁ ל{-} וֹ ם{-}`. With `--from-word`, an unpointed letter means "no vowel",
the same as the site. In a hand-written pattern, a bare letter means "any vowel".

## Workflow: finding rhymes for a line

1. **Get the rhyme word and its reading.** If the word is unpointed and
   ambiguous, choose the reading from the line's meaning, or run `vocalize`
   and pick one.
2. **Start with common words.** Run `rhyme WORD --group common --flat --plain`.
   If you need more options, drop `--group` and use `main`.
3. **Narrow by what the line needs.** Match part of speech and
   gender/number to the slot the rhyme has to fill (`--pos verb --tense past
   --person 1`). Use `--max-syl` to fit the meter and `--semantic` to stay on topic.
4. **Loosen when results are thin.** The defaults are already loose (שור/חמור
   and letter swaps are on). After that, try `sound --kind assonance` for
   slant rhymes, or `--accent all`.
5. **Choose; don't just dump.** Suggest a handful of rhymes that fit the
   meaning and meter, and say which reading or filter you used. Don't paste
   300 words.

## Notes

- The servers are slow sometimes, and `sound` can take 30–60 s. The script waits up to 150 s.
- `fKnownInputAccent: false` in `--json` output means Dicta guessed the input's stress.
- A Tanakh verse can be opened at `https://search.dicta.org.il/he/result?text=<word>`.
