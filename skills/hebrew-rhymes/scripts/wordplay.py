#!/usr/bin/env python3
"""Tiny CLI client for Dicta's Charuzit (https://wordplay.dicta.org.il).

Charuzit finds Hebrew rhymes, assonance/consonance, alliteration and words
matching a letter/vowel pattern. This script calls the same JSON endpoints the
site's frontend calls. Standard library only, Python 3.9+.

    python3 wordplay.py rhyme שלום
    python3 wordplay.py rhyme שָׁלוֹם --pos verb --max-syl 3 --flat
    python3 wordplay.py sound שמש --kind consonance
    python3 wordplay.py alliteration שמש --letters 3
    python3 wordplay.py pattern "? לֹ ם"
    python3 wordplay.py semantic ים
    python3 wordplay.py vocalize שלום

Run `wordplay.py <command> -h` for every option.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request

BASE = "https://charuzit-4-0.loadbalancer.dicta.org.il"
API = BASE + "/api"                  # main search (all four modes)
VOCALIZE = BASE + "/tipsoundplay"    # unpointed word -> candidate vocalizations
SEMANTIC_TIP = BASE + "/tipsemantic"  # typeahead for semantic-field keywords

NIKUD_RE = re.compile("[֑-ׇ]")
HEB_LETTER_RE = re.compile("[א-ת]")
MARK_RE = re.compile("[ְ-ׇ]")

# ---------------------------------------------------------------------------
# Morphology filters. The site sends each sidebar dropdown as a bitmask; the
# lists below are copied from the frontend bundle, indexed by dropdown position.
# ---------------------------------------------------------------------------
MORPH = {
    "pos": {
        "noun": 393216, "adjective": 65536, "verb": 851968, "adverb": 131072,
        "preposition": 524288, "conjunction": 196608, "demonstrative": 589824,
    },
    "gender": {"masculine": 2097152, "feminine": 4194304},
    "number": {"singular": 16777216, "plural": 33554432},
    "person": {"1": 134217728, "2": 268435456, "3": 402653184},
    "status": {"absolute": 1073741824, "construct": 2147483648},
    "tense": {
        "past": 8589934592, "present": 25769803776, "future": 34359738368,
        "imperative": 42949672960, "infinitive": 51539607552,
    },
    "suffix_gender": {"masculine": 549755813888, "feminine": 1099511627776},
    "suffix_number": {"singular": 4398046511104, "plural": 8796093022208},
    "suffix_person": {"1": 35184372088832, "2": 70368744177664, "3": 105553116266496},
}

ACCENTS = {  # "הטעמה" radio in the rhyme settings
    "match": "matchinput",  # match the stress of the search word (default)
    "all": "returnall",     # מלעיל ומלרע
    "milra": "acc0",        # stress on the last syllable
    "milel": "acc1",        # stress on the penultimate syllable
}

# Result groups. Each response is a list of {"mode", "fMoreMatches", "results"}
# where mode is "<Model><suffix>"; these are the tabs on the results page.
GROUPS = {
    "main": "", "tanakh": "_Tanakh", "common": "_Common",
    "nosuffix": "_NoSuffix", "long": "_LongWords", "feminine": "_Feminine",
}

VOWEL_CLASSES = {  # the A/E/I/O/U shortcuts in the pattern editor
    "a": ["ֲ", "ַ", "ָ"],  # hataf patah, patah, qamatz
    "e": ["ֱ", "ֵ", "ֶ"],  # hataf segol, tsere, segol
    "i": ["ִ"],                      # hiriq
    "o": ["ֹ", "ׇ", "ֳ"],  # holam, qamatz qatan, hataf qamatz
    "u": ["ֻ"],                      # qubutz
}
DAGESH, SHIN_DOT, SIN_DOT = "ּ", "ׁ", "ׂ"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def post(url: str, payload: dict, timeout: int = 150):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Origin": "https://wordplay.dicta.org.il",
            "Referer": "https://wordplay.dicta.org.il/",
            "User-Agent": "Mozilla/5.0 (oz-skills hebrew-rhymes)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"error: HTTP {e.code} from {url}: {e.read()[:300]!r}")
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f"error: could not reach {url}: {e}")


def has_nikud(word: str) -> bool:
    return bool(NIKUD_RE.search(word))


def strip_nikud(word: str) -> str:
    return NIKUD_RE.sub("", word)


def vocalize(word: str) -> list[str]:
    """Candidate vocalizations for an unpointed word, most likely first."""
    return post(VOCALIZE, {"w": word}) or []


def semantic_tips(word: str, thresh: int = 30) -> list[str]:
    return post(SEMANTIC_TIP, {"w": word, "thresh": thresh}) or []


def resolve_keyword(word: str, pick: int) -> str:
    """The search API only understands pointed words; the site vocalizes first."""
    if not word or has_nikud(word):
        return word
    options = vocalize(word)
    if not options:
        sys.exit(f"error: Dicta has no vocalization for {word!r}; add nikud yourself")
    if pick >= len(options):
        sys.exit(f"error: --pick {pick} out of range; options: {' '.join(options)}")
    chosen = options[pick]
    if len(options) > 1:
        others = [f"[{i}]{o}" for i, o in enumerate(options) if i != pick][:6]
        more = f" +{len(options) - 7} more" if len(options) > 7 else ""
        print(f"# vocalized {word} -> {chosen}   (others: {' '.join(others)}{more};"
              " see `vocalize`, choose with --pick N)", file=sys.stderr)
    return chosen


def resolve_semantic(words: list[str]) -> list[str]:
    out = []
    for w in words:
        if has_nikud(w):
            out.append(w)
            continue
        tips = semantic_tips(w)
        if not tips:
            sys.exit(f"error: {w!r} is not in Dicta's semantic vocabulary "
                     "(try `semantic-tips` for suggestions)")
        if strip_nikud(tips[0]) != w:
            print(f"# semantic keyword {w} -> {tips[0]}", file=sys.stderr)
        out.append(tips[0])
    return out


# ---------------------------------------------------------------------------
# Word pattern (תבנית מילה) parsing
# ---------------------------------------------------------------------------
def parse_pattern(text: str, bare_letter_means_no_vowel: bool = False) -> list[dict]:
    """Turn a compact pattern string into the site's `tavnit_search` tokens.

    One token per letter slot:
      א..ת      a specific letter        [בכ]    any of these letters
      ?         any single letter         *       any run of letters (wildcard)
    followed optionally by pointing and/or a {modifier,...} block:
      nikud marks typed after the letter (e.g. לֹ, שָׁ, בּ) are used as-is;
      a dagesh mark requires a dagesh; shin/sin dots pick שׁ / שׂ.
      {a} {e} {i} {o} {u}   vowel classes, combinable: {a,e}
      {-}                   no vowel on this letter
      {any}                 any vowel (the default for a bare letter)
      {dag} / {nodag}       require / forbid dagesh
      {root} / {noroot}     letter must / must not be a root letter
    Whitespace is ignored, so "? לֹ ם" == "?לֹם".
    """
    tokens: list[dict] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "*":
            if not tokens or not tokens[-1].get("wildcard"):
                tokens.append({"wildcard": True})
            i += 1
            continue
        if ch == "?":
            letters, anyletter = [], True
            i += 1
        elif ch == "[":
            j = text.index("]", i)
            letters = [c for c in text[i + 1:j] if HEB_LETTER_RE.match(c)]
            anyletter = False
            i = j + 1
        elif HEB_LETTER_RE.match(ch):
            letters, anyletter = [ch], False
            i += 1
        else:
            raise ValueError(f"unexpected character {ch!r} at position {i} in pattern")

        marks = ""
        while i < n and MARK_RE.match(text[i]):
            marks += text[i]
            i += 1
        mods: list[str] = []
        if i < n and text[i] == "{":
            j = text.index("}", i)
            mods = [m.strip().lower() for m in text[i + 1:j].split(",") if m.strip()]
            i = j + 1

        tok = {"letters": letters, "dag": "M", "rootLetter": "M", "nikud": []}
        if anyletter:
            tok["anyletter"] = True
        if DAGESH in marks:
            tok["dag"] = "Y"
        if SHIN_DOT in marks:
            tok["shin"] = SHIN_DOT
        elif SIN_DOT in marks:
            tok["shin"] = SIN_DOT
        vowels = [m for m in marks if m not in (DAGESH, SHIN_DOT, SIN_DOT)]
        tok["nikud"].extend(vowels)
        any_vowel = False
        for m in mods:
            if m in VOWEL_CLASSES:
                tok["nikud"].extend(VOWEL_CLASSES[m])
            elif m == "-":
                tok["nikud"].append("!")
            elif m == "any":
                any_vowel = True
            elif m == "dag":
                tok["dag"] = "Y"
            elif m == "nodag":
                tok["dag"] = "N"
            elif m == "root":
                tok["rootLetter"] = "Y"
            elif m == "noroot":
                tok["rootLetter"] = "N"
            else:
                raise ValueError(f"unknown pattern modifier {{{m}}}")
        if not tok["nikud"]:
            if bare_letter_means_no_vowel and not any_vowel:
                tok["nikud"] = ["!"]
            else:
                any_vowel = True
        if any_vowel:
            tok["nikud"] = []
            tok["anynikud"] = True
        tokens.append(tok)
    if not tokens:
        raise ValueError("empty pattern")
    if len([t for t in tokens if not t.get("wildcard")]) > 8:
        raise ValueError("the site supports at most 8 letter slots")
    return tokens


# ---------------------------------------------------------------------------
# Request building
# ---------------------------------------------------------------------------
def build_body(args, model: str, keyword: str, semantic: list[str],
               tavnit: list[dict] | None = None) -> dict:
    morph: dict = {}
    for key in MORPH:
        val = getattr(args, key, None)
        morph[key] = MORPH[key][val] if val else 0
    suffix = getattr(args, "suffix", None)
    if suffix:
        morph["has_suffix"] = suffix == "yes"

    accent = getattr(args, "accent", None) or ("all" if model == "tavnit" else "match")
    return {
        "soundplay_keyword": keyword,
        "rhyme_mode": "full" if getattr(args, "strict", False) else "half",
        "alit_num_of_lets": getattr(args, "letters", 2),
        "model": model,
        "soundplay_settings": {
            "allowletswap": not getattr(args, "no_consonant_swap", False),
            "allowvocswap": not getattr(args, "no_vowel_swap", False),
        },
        "semantic_keywords": semantic,
        "semantic_models": "both",
        "tavnit_search": tavnit or [],
        "morph_filter": morph,
        "return_settings": {
            "min_syl": args.min_syl,
            "max_syl": args.max_syl,
            "accreturnsettings": ACCENTS[accent],
            "returnpropernames": args.proper_names,
            "ignoreLoazi": args.no_foreign,
            "baseOnly": args.base_only,
        },
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r"</?b>")


def select_groups(results: list[dict], group: str, kind: str | None) -> list[dict]:
    if results and "mode" not in results[0]:
        return [{"mode": "Results", "fMoreMatches": False, "results": results}]
    out = []
    for g in results:
        mode = g.get("mode", "")
        base, _, rest = mode.partition("_")
        suffix = "_" + rest if rest else ""
        if kind and base.lower() != kind:
            continue
        if group != "all" and suffix != GROUPS[group] and base != "Semantic":
            continue
        out.append(g)
    return out


def print_groups(groups: list[dict], args) -> None:
    if args.json:
        json.dump(groups, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    seen: set[str] = set()
    for g in groups:
        items = g["results"][: args.limit] if args.limit else g["results"]
        more = "+" if g.get("fMoreMatches") else ""
        if not args.flat:
            print(f"## {g['mode']}  ({len(g['results'])}{more} entries)")
        is_tanakh = "Tanakh" in g["mode"]
        for item in items:
            forms = item.get("forms") or [item.get("lex", "")]
            if args.flat:
                for f in forms if not is_tanakh else []:
                    key = strip_nikud(f) if args.plain else f
                    if key not in seen:
                        seen.add(key)
                        print(key)
                continue
            if is_tanakh:
                print(f"- {item['lex']}")
                for verse in forms[: args.forms]:
                    text, _, ref = TAG_RE.sub("*", verse).partition("\t")
                    print(f"    {ref.strip()}: {text.strip()}")
                continue
            shown = forms[: args.forms]
            tail = " …" if item.get("has_more_forms") or len(forms) > len(shown) else ""
            words = list(dict.fromkeys(strip_nikud(f) if args.plain else f for f in shown))
            print(f"- {', '.join(words)}{tail}   [{item['lex']}]")
        if not args.flat:
            print()


def run_search(args, model: str, keyword: str, tavnit=None, kind=None) -> None:
    semantic = resolve_semantic(args.semantic or [])
    body = build_body(args, model, keyword, semantic, tavnit)
    if args.dump_request:
        json.dump(body, sys.stderr, ensure_ascii=False, indent=2)
        print(file=sys.stderr)
    data = post(API, body)
    if not isinstance(data, dict) or data.get("error") or not data.get("results"):
        sys.exit("no results")
    groups = select_groups(data["results"], args.group, kind)
    if not any(g["results"] for g in groups):
        counts = ", ".join(f"{g['mode']}={len(g['results'])}"
                           for g in data["results"] if g.get("results"))
        print(f"no results in group {args.group!r}" +
              (f"; non-empty groups: {counts}" if counts else ""), file=sys.stderr)
        sys.exit(1)
    print_groups(groups, args)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def syl(value: str) -> int:
    v = int(value.rstrip("+"))
    if not 1 <= v <= 7:
        raise argparse.ArgumentTypeError("syllables must be 1..7 (7 means 7+)")
    return v


def add_common(p: argparse.ArgumentParser, pattern_mode: bool = False) -> None:
    f = p.add_argument_group("word filters (sidebar: מאפייני מילה)")
    f.add_argument("--pos", choices=MORPH["pos"], help="part of speech")
    f.add_argument("--gender", choices=MORPH["gender"])
    f.add_argument("--number", choices=MORPH["number"])
    f.add_argument("--person", choices=MORPH["person"])
    f.add_argument("--status", choices=MORPH["status"], help="נפרד / נסמך")
    f.add_argument("--tense", choices=MORPH["tense"])
    f.add_argument("--suffix", choices=["yes", "no"], help="has a pronominal suffix")
    f.add_argument("--suffix-gender", dest="suffix_gender", choices=MORPH["suffix_gender"])
    f.add_argument("--suffix-number", dest="suffix_number", choices=MORPH["suffix_number"])
    f.add_argument("--suffix-person", dest="suffix_person", choices=MORPH["suffix_person"])

    a = p.add_argument_group("advanced (sidebar: הגדרות מתקדמות / סגנון טקסט)")
    a.add_argument("--min-syl", type=syl, default=1, help="min syllables (1-7)")
    a.add_argument("--max-syl", type=syl, default=7, help="max syllables (1-7, 7 = 7+)")
    a.add_argument("--accent", choices=ACCENTS,
                   help="stress filter: match (default; 'all' in pattern mode), "
                        "all, milra (ultimate), milel (penultimate)")
    a.add_argument("--proper-names", action="store_true", help="include proper names")
    a.add_argument("--no-foreign", action="store_true", help="exclude loanwords")
    a.add_argument("--base-only", action="store_true",
                   help="only base forms (no inflections)")
    a.add_argument("--semantic", action="append", metavar="WORD",
                   help="restrict to a semantic field (שדה סמנטי); repeatable")
    if not pattern_mode:
        a.add_argument("--pick", type=int, default=0, metavar="N",
                       help="which vocalization to use for an unpointed word")

    o = p.add_argument_group("output")
    o.add_argument("--group", choices=list(GROUPS) + ["all"], default="main",
                   help="result tab: main (default), tanakh, common, nosuffix, "
                        "long, feminine, all")
    o.add_argument("--limit", type=int, default=40, help="entries per group (0 = all)")
    o.add_argument("--forms", type=int, default=4, help="forms shown per entry")
    o.add_argument("--flat", action="store_true",
                   help="one unique word per line, no grouping")
    o.add_argument("--plain", action="store_true", help="strip nikud in output")
    o.add_argument("--json", action="store_true", help="raw result groups as JSON")
    o.add_argument("--dump-request", action="store_true",
                   help="print the request body to stderr")


def add_swaps(p: argparse.ArgumentParser) -> None:
    s = p.add_argument_group("sound similarity (sidebar: חרוזים)")
    s.add_argument("--no-consonant-swap", action="store_true",
                   help="disable similar-sounding consonants (ב/ו, ט/ת, כ/ח, כ/ק, ס/ש)")
    s.add_argument("--no-vowel-swap", action="store_true",
                   help="disable near-identical vowels (patah/qamatz, tsere/segol)")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(
        description="Hebrew rhymes & wordplay via Dicta Charuzit.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("rhyme", help="rhymes (חרוזים)")
    p.add_argument("word")
    p.add_argument("--strict", action="store_true",
                   help="full last-syllable rhymes only (turns off שור/חמור rhymes)")
    add_swaps(p)
    add_common(p)

    p = sub.add_parser("sound", help="assonance / consonance (מצלול)")
    p.add_argument("word")
    p.add_argument("--kind", choices=["xxsonance", "assonance", "consonance"],
                   default="xxsonance",
                   help="xxsonance = both (default), assonance = vowels, "
                        "consonance = consonants")
    add_swaps(p)
    add_common(p)

    p = sub.add_parser("alliteration", help="alliteration (אליטרציה)")
    p.add_argument("word")
    p.add_argument("--letters", type=int, choices=[1, 2, 3], default=2,
                   help="how many opening consonants must match (default 2)")
    add_common(p)

    p = sub.add_parser("pattern", help="word pattern (תבנית מילה)",
                       description=parse_pattern.__doc__,
                       formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pattern", nargs="?", default="",
                   help='e.g. "? לֹ ם", "[בכ]{a} ? ?{i} ם", "מ{-} * ה"')
    p.add_argument("--from-word", metavar="WORD",
                   help="build the pattern from a pointed word, like the site's "
                        "import button (unpointed letters mean 'no vowel')")
    add_swaps(p)
    add_common(p, pattern_mode=True)

    p = sub.add_parser("semantic",
                       help="words in a semantic field only (no sound matching)")
    p.add_argument("words", nargs="+", help="one or more field keywords")
    add_common(p, pattern_mode=True)

    p = sub.add_parser("vocalize", help="list vocalizations Dicta suggests for a word")
    p.add_argument("word")

    p = sub.add_parser("semantic-tips", help="semantic-field keyword suggestions")
    p.add_argument("word")

    args = ap.parse_args(argv)

    if args.cmd == "vocalize":
        for i, v in enumerate(vocalize(args.word)):
            print(f"[{i}] {v}")
        return
    if args.cmd == "semantic-tips":
        for v in semantic_tips(args.word):
            print(v)
        return

    if args.cmd == "rhyme":
        run_search(args, "Rhyme", resolve_keyword(args.word, args.pick))
    elif args.cmd == "sound":
        run_search(args, "Xxsonance", resolve_keyword(args.word, args.pick),
                   kind=args.kind)
    elif args.cmd == "alliteration":
        run_search(args, "Alliteration", resolve_keyword(args.word, args.pick))
    elif args.cmd == "pattern":
        try:
            if args.from_word:
                tokens = parse_pattern(args.from_word, bare_letter_means_no_vowel=True)
            elif args.pattern:
                tokens = parse_pattern(args.pattern)
            else:
                ap.error("pattern: give a PATTERN or --from-word")
        except ValueError as e:
            sys.exit(f"error: {e}")
        run_search(args, "tavnit", "", tavnit=tokens)
    elif args.cmd == "semantic":
        args.semantic = (args.semantic or []) + args.words
        run_search(args, "Rhyme", "")


if __name__ == "__main__":
    main()
