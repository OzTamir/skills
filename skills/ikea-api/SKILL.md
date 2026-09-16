---
name: ikea-api
description: Use whenever the user wants to find, compare, size-check, price, or stock-check IKEA products — "find me an IKEA bookcase that fits a 70cm gap", "what IKEA desk would fit under this window", "is the BILLY in stock near me", "cheapest IKEA wardrobe under 200cm tall", "look for IKEA furniture for this space", or any mention of IKEA product names (BILLY, KALLAX, PAX, BESTÅ, MALM…), item numbers, or ikea.com links. Also use when an agent needs programmatic access to IKEA's catalogue for any purpose. Wraps IKEA's unofficial public APIs (search, category listing, product dimensions, per-store stock) in a bundled stdlib-only Python CLI, so the agent can search autonomously instead of asking the user to browse. Do NOT use for non-IKEA retailers or for assembly instructions.
---

# IKEA API

Search IKEA's live catalogue, filter by size and price, pull exact labelled
dimensions, and check per-store stock — all from the terminal, without a
browser. The endpoints are the same ones ikea.com's own frontend calls; they
are documented (unofficially) at
[idelsink/ikea-openapi](https://github.com/idelsink/ikea-openapi). No account
or API key is needed.

Everything goes through the bundled script:

```
python3 <skill-dir>/scripts/ikea.py --market gb/en <command> ...
```

It is standard-library-only Python 3.9+. Add `--json` to any command for
structured output. Run `ikea.py <command> -h` for the full option list.

## Step 0: pin down the market

Prices, currency, product range, item numbers (in the US) and stock are all
per-country, so every call needs a market as `<country>/<language>`:
`gb/en`, `de/de`, `nl/en`, `il/he`, `us/en`, `se/sv`, `fr/fr`, `pl/pl`…
Not every language works for every country (`il/en` is a 404; `il/he` works).

If the user hasn't said where they are and nothing in the conversation or
their environment tells you, ask once. Then either pass `--market` every time
or prefix each command with `IKEA_MARKET=il/he python3 …` — shell state
usually doesn't persist between an agent's tool calls, so a bare `export`
will be forgotten. Don't silently default to a market: a great match in the
wrong country is useless.

## The commands

| Command | What it does | Typical use |
| --- | --- | --- |
| `search "QUERY"` | Free-text search, same engine as the ikea.com search box. Returns item no, name, type, size text, parsed W/D/H, price, rating, URL. | First pass for any product hunt. |
| `list CATEGORY_ID` | Everything in a category (`st001`, `10382`, `bo003`…). Same output as search. | Exhaustive sweep of one product type. |
| `filters -q "QUERY"` / `-c ID` | Lists the server-side filter values (size buckets, colours, types, price buckets, series…) and sort orders valid for that result set. | Discover ids before filtering. |
| `product ITEMNO…` | Exact labelled width/depth/height, max load, materials, price, rating, package sizes and weights. | Verify finalists. |
| `stock ITEMNO[,…] [--store CODE]` | Stock quantity and status per store, plus restock windows. | "Is it in stock near me?" |
| `stores` | Store codes, names and addresses for the market. | Find the user's store code. |

Common options on `search` and `list`:

- `--size N` results to fetch (1–1000, default 50). Use 200–500 when sweeping.
- `--sort` `RELEVANCE`, `PRICE_LOW_TO_HIGH`, `PRICE_HIGH_TO_LOW`, `RATING`, `MOST_POPULAR`, `NEWEST`, `WIDTH`, `HEIGHT`, `DEPTH` (dimension sorts run largest-first).
- `--filter PARAM=VALUE` (repeatable) server-side filters, e.g. `-f f-measurement-buckets=WIDTH_60_80 -f f-measurement-buckets=HEIGHT_100_150 -f f-colors=10156 -f f-price-buckets=PRICE_0_5000`. Same param twice is AND-ed.
- `--only REGEX` / `--exclude REGEX` client-side filter on name + type. Searches for "bookcase" or "desk" return roughly half accessories (brackets, doors, inserts, desk pads, lamps); `--only "bookcase|shelving unit"` or `--exclude "bracket|cover|door|insert|pad|lamp"` keeps the output readable. Works in any language: `--only "שולחן כתיבה"`.
- `--max-width/--max-depth/--max-height CM` and the `--min-*` twins: client-side filter on the parsed size text. Products with an unknown dimension are kept and flagged; add `--strict` to drop them (useful against desk-and-chair bundles and combinations that carry no size text at all).
- `--show-filters` append the available filter values to the output.

## Workflow: "find something that fits this space"

This is the flow the skill exists for. The user gives you a gap and a purpose;
you come back with a short ranked list of real products that fit, with links.

1. **Turn the brief into constraints.** Which dimensions are hard limits
   (usually width and depth for an alcove, height for under a window/desk),
   what the piece is for (books, shoes, TV, clothes), any style/colour/budget
   hints, and the market. Ask only if the answer would materially change the
   search; otherwise state your assumption and proceed. Leave a few
   centimetres of margin for skirting, wonky walls and assembly clearance,
   and say what margin you used.

2. **Search wide, then narrow.** IKEA's product-type vocabulary is specific,
   so run two to four queries with different type words (e.g. "bookcase",
   "shelving unit", "cabinet", "storage combination") rather than one long
   sentence. Narrow server-side with `f-measurement-buckets` (the buckets are
   coarse: width 0/20/40/60/80, height 0/50/100/150/200, depth 0/25/30/35/40 cm
   in metric markets) and then precisely with `--max-*`. Pull a large
   `--size` so the client-side filter has enough to work with.
   Zero results? The output prints `did you mean` and `related searches` —
   try those, or the product family name (IKEA names like "billy" work in
   every market and language). Modular systems (PLATSA, SMÅSTAD, BESTÅ, PAX)
   surface badly in text search because the results are mostly doors and
   frames; use `list` on their category or search the family name and read
   the "combination" rows.

3. **Read the size text carefully.** The size on listing cards has three
   numbers (width × depth × height) or two, and the two-number case depends
   on the product type:
   - Upright storage (bookcases, cabinets, wardrobes): width × height, depth
     omitted. The script prints `(depth?)`. Treat these as *not yet known to
     fit* — a 42×147 KALLAX turned out to be 39 cm deep.
   - Desks, tables, table tops, beds, mattresses, rugs: the footprint,
     width × depth, height omitted. The script detects these from the
     category and prints `(footprint; height?)`, so `--max-depth` works.
   The rule is a heuristic. US markets use inches with fractions; the script
   converts to cm for `--max-*` checks.

4. **Verify the shortlist.** Run `product` on the 5–10 finalists. It returns
   the product page's own labelled width/depth/height (so a wrongly-guessed
   layout gets caught), max load, and package dimensions — useful when the
   user must carry it up a staircase or fit it in a car. Table tops and
   worktops are labelled length × width; the script adds a "footprint as
   placed" line (length = how wide it sits, width = how deep). Each `product`
   call downloads about 1 MB, so verify a shortlist, not the whole result set.

5. **Check stock if location matters.** `stores` for the code, then
   `stock ITEMNO,ITEMNO --store CODE`. Without `--store` you get every store
   in the country plus a country-level row that says whether home delivery
   and click & collect are in range — about 25 lines per item, so do that
   for the top two or three only. Status is `HIGH_IN_STOCK` /
   `MEDIUM_IN_STOCK` / `LOW_IN_STOCK` / `OUT_OF_STOCK`; quote the quantity,
   since "medium" can mean two units. Restock windows appear when known.

6. **Present a ranked table**, best fit first: name and type, exact W×D×H,
   how much room is left against each limit, price, rating and count where
   the market has them (Israel returns no ratings at all), and the product
   URL. Say what you assumed, what you couldn't verify, and mention variants
   (colours/sizes) when the listing says there are some. Six well-chosen
   options beat thirty.

### Example

Brief: "an alcove 72 cm wide and 32 cm deep, ceiling 240 cm, I need book storage, white, UK."

```
IKEA_MARKET=gb/en python3 scripts/ikea.py search "bookcase" --size 400 -f f-colors=10156 \
    --only "bookcase|shelving unit" --max-width 70 --max-depth 30 --sort PRICE_LOW_TO_HIGH
IKEA_MARKET=gb/en python3 scripts/ikea.py search "shelving unit" --size 400 -f f-colors=10156 \
    --only "bookcase|shelving unit" --max-width 70 --max-depth 30
IKEA_MARKET=gb/en python3 scripts/ikea.py product 50263838 20436713 39603684
IKEA_MARKET=gb/en python3 scripts/ikea.py stock 50263838,20436713 --store 1010
```

Then answer with the fitting BILLY 40 / BAGGEBO / LASTARE variants, their
exact sizes, the 2 cm margin you kept, prices, and links. (Ranges differ by
market: GERSBY, for instance, is sold in Israel but not in the UK.)

Hebrew brief: "שולחן כתיבה לפינה של 110 על 60, ראשון לציון"

```
IKEA_MARKET=il/he python3 scripts/ikea.py stores                    # ראשון לציון = 217
IKEA_MARKET=il/he python3 scripts/ikea.py search "שולחן כתיבה" --size 300 --only "שולחן כתיבה|שולחן עבודה|שולחן מחשב" \
    --exclude "מנורת|פד|ארגונית|כיסא|כסא" --strict --max-width 108 --max-depth 60
IKEA_MARKET=il/he python3 scripts/ikea.py search "desk" --size 300 --only "שולחן" --exclude "מנורת|פד|ארגונית|כיסא|כסא" \
    --strict --max-width 108 --max-depth 60
IKEA_MARKET=il/he python3 scripts/ikea.py product 80213074 00251135
IKEA_MARKET=il/he python3 scripts/ikea.py stock 80213074,00251135 --store 217
```

Product family names ("micke", "linnmon", "billy") work as queries in every
market, so mixing an English family name with a Hebrew type word is fine.
Hebrew type words are compound ("מדף", "מדף קיר", "מדף פנימי נוסף"), so an
`--exclude` for accessories in Hebrew storage searches usually looks like
`--exclude "מדף קיר|מדף נוסף|דלת|תוספת|הגבהה|קופסה|סלסלה|מחיצה|מסילה|רגליים"`.
Colour ids (`f-colors=10156` white, `10139` black, `10028` grey, `10003`
beige, `10019` brown) are the same in every market.

## Other things people ask for

- **"Is X in stock near me?"** `search "x"` to get the item number, `stores`,
  then `stock … --store CODE`. Combination products (`s`-prefixed URLs) and
  their main article often report the same quantity; quote the article.
- **"Cheapest / best-rated Y"** `search "y" --sort PRICE_LOW_TO_HIGH` or
  `--sort RATING`, then filter out accessories.
- **"All the KALLAX sizes"** `search "kallax" --size 200`, or `filters -q
  kallax` to get the `f-series` id and `f-type` values, then filter.
- **"What's in this ikea.com link?"** The 8-digit item number is at the end
  of the URL (`…-00263850/`, sometimes prefixed with `s` for combinations —
  drop the `s`). Run `product` on it.
- **"Will it fit in my car?"** `product` prints package dimensions and weights.

## Gotchas

- **Unofficial and unversioned.** These endpoints can change or break without
  notice. If a call starts failing, read the error body the script prints —
  the search API returns helpful `{"detail": "Unrecognized parameter: …"}`
  messages — and check `references/api-reference.md` for what has already
  been observed to be dead.
- **No pagination on text search.** `search-result-page` rejects `start`;
  use `--size` up to 1000. Category listing does support `start`/`end` via a
  `more-products` endpoint (see the reference) if you ever need more.
- **Israel runs on ikea.com too.** `ikea.co.il` redirects to
  `www.ikea.com/il/he/`; use market `il/he` (Hebrew only, `il/en` is a 404).
  Hebrew size text is wrapped in bidi marks and uses `ס"מ`; the script handles
  both. Stores: 206 נתניה, 217 ראשון לציון, 318 קריית אתא, 531 באר שבע, 613 אשתאול.
  Many items are `store only` (not sold online) and there are no ratings.
  Out-of-stock items in Israel usually show no restock window, even when
  they are out in all five stores, so say "no restock date published"
  rather than guessing.
- **US item numbers are local.** `itemNo` in US results differs from the
  global one (`itemNoGlobal`). Always feed `product`/`stock` the item number
  you got from the same market.
- **Price buckets are in minor units.** `PRICE_0_5000` means 0–50 in the
  market currency. Colour, type, material and series filters use numeric
  ids — get them from `filters`, don't guess.
- **The category-tree endpoint is gone** (404 in every market as of
  Sept 2026). Discover categories from the `categoryPath` on products, the
  `f-subcategories` filter values, or the well-known codes in the reference.
- **Be a polite client.** Don't hammer the endpoints in tight loops; a few
  hundred results per call is fine, thousands of calls are not. The product
  page fetch is ~1 MB of HTML each, so verify a shortlist, not the whole
  result set.

## Reference

`references/api-reference.md` — every endpoint, parameter, filter id, response
field, error code, and known-dead endpoint, with curl examples. Read it when
the script doesn't expose what you need, or when you're debugging a failure.
