# Charuzit API reference (unofficial)

This file was reverse-engineered from the frontend bundle of
`wordplay.dicta.org.il` (`js/app.*.js`, Vue 2 + Vuex) and from live requests
in September 2026. It is not an official API, so it can change without
notice. The endpoints accept plain JSON POSTs from any client, with no
cookies, auth, or special headers.

Base URL: `https://charuzit-4-0.loadbalancer.dicta.org.il`

All endpoints: `POST`, `Content-Type: application/json`, UTF-8 Hebrew.

## `POST /tipsoundplay`: vocalize a word

```json
{"w": "שלום"}
```

Returns a JSON array of pointed candidates, most likely first:
`["שָׁלוֹם","שְׁלוֹם","שְׁלֹם", ...]`. The site calls this whenever the
search box has no nikud and then searches with `[0]`. `/api` returns empty
results for unpointed input, so this step is required.

## `POST /tipsemantic`: semantic-field typeahead

```json
{"w": "ים", "thresh": 30}
```

Returns an array of pointed keywords (`["יָם"]`) that are valid values for
`semantic_keywords`.

## `POST /api`: search (all four modes)

Request body (all fields are always sent by the site; the defaults are shown):

```json
{
  "soundplay_keyword": "שָׁלוֹם",
  "rhyme_mode": "half",
  "alit_num_of_lets": 2,
  "model": "Rhyme",
  "soundplay_settings": {"allowletswap": true, "allowvocswap": true},
  "semantic_keywords": [],
  "semantic_models": "both",
  "tavnit_search": [],
  "morph_filter": {
    "pos": 0, "person": 0, "status": 0, "number": 0, "gender": 0, "tense": 0,
    "suffix_person": 0, "suffix_number": 0, "suffix_gender": 0
  },
  "return_settings": {
    "min_syl": 1, "max_syl": 7,
    "accreturnsettings": "matchinput",
    "returnpropernames": false,
    "ignoreLoazi": false,
    "baseOnly": false
  }
}
```

(`has_suffix` is left out when set to "all"; otherwise it is `true` / `false`.)

| Field | Values | Sidebar control |
| --- | --- | --- |
| `soundplay_keyword` | pointed word; `""` for pattern or semantic-only searches | search box |
| `model` | `Rhyme`, `Xxsonance`, `Alliteration`, `tavnit` (lowercase) | top tabs |
| `rhyme_mode` | `half` (default, includes "שור/חמור"), `full` | כלול חרוזי שור וחמור |
| `alit_num_of_lets` | 1, 2, 3 | מספר עיצורים (alliteration) |
| `soundplay_settings.allowletswap` | bool | דמיון בעיצורים |
| `soundplay_settings.allowvocswap` | bool | דמיון בתנועות |
| `semantic_keywords` | list of pointed words from `/tipsemantic` | שדה סמנטי (בטא) |
| `semantic_models` | always `"both"` | — |
| `tavnit_search` | list of tokens (below) | pattern editor |
| `return_settings.min_syl` / `max_syl` | 1–7 (7 = "7+") | syllable slider |
| `return_settings.accreturnsettings` | `matchinput` (default), `returnall`, `acc0` (מלרע), `acc1` (מלעיל); pattern mode defaults to `returnall` and has no `matchinput` | הטעמה |
| `return_settings.returnpropernames` | bool | כלול שמות פרטיים |
| `return_settings.ignoreLoazi` | bool (true = exclude loanwords) | כלול מילים לועזיות (inverted) |
| `return_settings.baseOnly` | bool | כלול מילים שאינן צורת בסיס (inverted) |

### `morph_filter` bitmasks

Each value is a bitmask; `0` means "all".

| Field | Options → value |
| --- | --- |
| `pos` | noun 393216, adjective 65536, verb 851968, adverb 131072, preposition 524288, conjunction 196608, demonstrative (כינויי רמז) 589824 |
| `gender` | masculine 2097152, feminine 4194304 |
| `number` | singular 16777216, plural 33554432 |
| `person` | 1st 134217728, 2nd 268435456, 3rd 402653184 |
| `status` | absolute (נפרד) 1073741824, construct (נסמך) 2147483648 |
| `tense` | past 8589934592, present 25769803776, future 34359738368, imperative 42949672960, infinitive 51539607552 |
| `has_suffix` | omitted = all, `true`, `false` |
| `suffix_gender` | masculine 549755813888, feminine 1099511627776 |
| `suffix_number` | singular 4398046511104, plural 8796093022208 |
| `suffix_person` | 1st 35184372088832, 2nd 70368744177664, 3rd 105553116266496 |

### `tavnit_search` tokens

This is one object per letter slot, in reading order. The site allows up to
8 slots and drops trailing empty ones.

```json
{"letters": ["ל"], "dag": "M", "rootLetter": "M", "nikud": ["ֹ"]}
{"letters": [], "anyletter": true, "dag": "M", "rootLetter": "M", "nikud": [], "anynikud": true}
{"letters": ["ש"], "dag": "M", "rootLetter": "M", "nikud": ["ָ"], "shin": "ׁ"}
{"wildcard": true}
```

- `letters`: allowed letters (unpointed). Use `[]` together with `anyletter: true` for "any letter".
- `dag` / `rootLetter`: `M` = either (default), `Y` = required, `N` = forbidden.
- `nikud`: allowed vowel marks (U+05B0–U+05C7). `"!"` means "no vowel". Vowel
  classes expand to lists: A = ֲ ַ ָ, E = ֱ ֵ ֶ, I = ִ, O = ֹ ׇ ֳ, U = ֻ.
- `anynikud: true` means any vowel. The site sends it with `nikud` set to the full vowel list.
- `shin`: `"ׁ"` (U+05C1) or `"ׂ"` (U+05C2) to pin shin or sin.
- `{"wildcard": true}` stands for any run of letters. Consecutive wildcards collapse into one.

### Response

```json
{
  "fKnownInputAccent": true,
  "debug": null,
  "results": [
    {"mode": "Rhyme", "fMoreMatches": false, "results": [
      {"lex": "חלם_קל", "forms": ["חָלוֹם", "חֲלֹם", "..."], "has_more_forms": true}
    ]},
    {"mode": "Rhyme_Tanakh", "...": "..."}
  ]
}
```

- `results` is a list of groups, one per result tab:
  `<Model>`, `<Model>_Tanakh`, `<Model>_Common`, `<Model>_NoSuffix`,
  `<Model>_LongWords`, `<Model>_Feminine`. `Model` is `Rhyme`,
  `Alliteration`, `Tavnit`, or, for `Xxsonance`, 18 groups: the same six
  for each of `Xxsonance` (both), `Assonance` (vowels) and `Consonance`
  (consonants).
- A semantic-only search (empty keyword + `semantic_keywords`) returns a
  single `Semantic` group.
- `lex` is the lexeme: a pointed noun or adjective, or `ROOT_BINYAN` for verbs (`שׁלם_פיעל`).
- `forms` are the matching inflected forms. In `_Tanakh` groups, each form is
  instead a verse fragment with the match in `<b>…</b>`, a tab, and the
  reference (`בראשית כ, ג`).
- Each group is capped at 300 lexemes; `fMoreMatches: true` means it was truncated.
- `{"error": ...}` or no `results` means no results.
- Share URLs use query parameters such as `?search=…&type=rhyme&mode=half&accent=acc0&pos=3`,
  where the morph params are the dropdown **indexes**, not the bitmasks.
