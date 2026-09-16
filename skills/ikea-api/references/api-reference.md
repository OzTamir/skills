# IKEA unofficial API reference

Verified live on 2026-09-16 against gb/en, il/he, de/de and us/en. Source of
truth for the shapes: [idelsink/ikea-openapi](https://github.com/idelsink/ikea-openapi)
(MIT), which runs daily contract tests. Where this document and the upstream
spec disagree, this document reflects what the endpoints actually returned on
the date above; the spec is missing the free-text search endpoint and the
filter parameters entirely.

Contents

1. Conventions (markets, headers, item numbers)
2. Search API — free-text search
3. Search API — category listing
4. Filters and sort orders
5. Product schema (shared by search and listing)
6. Product page — exact dimensions
7. Product catalog JSON
8. Sales Item API — stock
9. Stores
10. Dead or unreliable endpoints
11. Error messages you will see

---

## 1. Conventions

**Market path.** `{country}/{language}` in lower case, e.g. `gb/en`, `de/de`,
`il/he`, `us/en`, `nl/en`, `se/sv`. The pair must exist on ikea.com; `il/en`
is a 404 while `il/he` works.

**Headers.** `www.ikea.com` requires a browser-like `User-Agent` (curl's
default gets 404/403 on some paths). The search API and the sales-item API
don't care about the user agent. No cookies or auth anywhere except the
`X-Client-ID` header on the sales-item API.

**Item numbers.** 8 digits, shown to humans with dots (`002.638.50`). Search
results expose both `itemNo` (market-local) and `itemNoGlobal`. In most
markets they are equal; in the US they differ (BILLY 80×28×202 is `00263850`
in GB and `20522046` in the US). Combination products (`itemType: SPR`) have a
URL slug prefixed with `s` (`s69287392`); the API fields carry the bare
digits.

**Units.** Metric markets return centimetres; the US returns inches with
vulgar fractions (`31 1/2x11x79 1/2 "`). Hebrew text is wrapped in bidi marks
(U+200E/U+200F) and uses `ס"מ` for cm.

---

## 2. Search API — free-text search

```
GET https://sik.search.blue.cdtapps.com/{country}/{language}/search-result-page
    ?q=<text>                 required
    &size=<1..1000>           default 24; 1001 -> 400
    &sort=<SORT_ID>           see §4
    &f-<filter>=<id>[,<id>]   see §4; repeatable per filter
```

Not in the upstream spec but it is what the ikea.com search box calls.
`start`, `end`, `moreToken` and `page` are all rejected with
`Unrecognized parameter`, so there is no pagination: raise `size` instead.

```sh
curl -s 'https://sik.search.blue.cdtapps.com/gb/en/search-result-page?q=bookcase&size=3&sort=PRICE_LOW_TO_HIGH&f-measurement-buckets=WIDTH_60_80,HEIGHT_150_200'
```

Response shape (trimmed):

```jsonc
{
  "searchResultPage": {
    "searchPhrase": "bookcase",
    "didYouMean": [{"text": "כונניות", "metadata": "…"}], // spelling suggestions, same object shape as relatedSearches
    "relatedSearches": [{"text": "billy bookcase", "count": 96}, ...],
    "retiredProducts": [],
    "storeWindow": [], "storeCount": 0,
    "products": {
      "main": {
        "items": [
          {"type": "PRODUCT", "product": { ...Product, see §5... }},
          {"type": "CONTENT", ...}             // occasionally, skip non-PRODUCT
        ],
        "start": 0, "end": 3, "max": 420,      // max = total matches
        "moreToken": "H4sI..."                 // not accepted anywhere; ignore
      },
      "filters": [ ...Filter, see §4... ],
      "sortOrders": {"values": [{"id": "RELEVANCE", "selected": true}, ...]},
      "shelves": [...], "badge": ..., "pageMessages": [...]
    },
    "content": {...}
  }
}
```

`main.max` is the total. Zero results still returns 200 with an empty `items`
and usually a populated `relatedSearches` — use those to retry.

---

## 3. Search API — category listing

```
GET https://sik.search.blue.cdtapps.com/{country}/{language}/product-list-page
    ?category=<id>            required; "st001", "10382", "bo003", or a UUID
    &size=<0..1000>
    &sort=<SORT_ID>
    &f-<filter>=<id>[,<id>]

GET .../product-list-page/more-products
    ?category=<id>&start=<n>&end=<n>   zero-based, end exclusive; defaults 0/24
```

Response shape:

```jsonc
{
  "productListPage": {
    "category": {"name": "Storage furniture", "key": "st001", "url": "...", "imageUrl": "..."},
    "productWindow": [ ...Product... ],
    "productCount": 2257,                      // total after filters
    "plannerWindow": [], "plannerCount": 0,
    "filters2":        [ {"id": "COLOR", "type": "CLASS_FILTER", "name": "Colour"}, ... ],
    "dynamicFiltersV1":[ ...Filter, same shape as search §4... ],
    "dynamicFilters":  [ flat list: {"filterId","filterValueId","count","filterParam","selected"} ],
    "sortOrders": {"name": "Sort", "values": [{"id": "RELEVANCE", "name": "Best match", "selected": true}, ...]}
  }
}
```

`more-products` returns `{"moreProducts": {"productWindow": [...]}}`.

The website's own category pages use a different, undocumented call:
`POST https://sik.search.blue.cdtapps.com/{c}/{l}/search?c=listaf&v=20241114`
with a JSON body naming the category and page. The GET `product-list-page`
above returns the same products and is what the bundled script uses.

Useful category codes (gb/en; the `stNNN`/`boNNN`-style codes are stable
across markets, numeric ones mostly are):

| Code | Category |
| --- | --- |
| `st001` | Storage furniture (all) |
| `st002` | Bookcases & shelving units |
| `10382` | Bookcases |
| `st003` | Cabinets & cupboards |
| `st004` | Sideboards, buffets & console tables |
| `st005` | TV & media furniture |
| `10412` | Chests of drawers |
| `19053` | Wardrobes |
| `fu002` | Tables & chairs (dining/coffee/side tables, chairs, benches) |
| `fu003` | Sofas & armchairs |
| `fu004` | Office furniture (desks, table tops, office chairs) |
| `20649` | Desks & computer desks |
| `20651` | Home office desks |
| `bm001` | Beds & mattresses |
| `bm003` | Beds |
| `tl001` | Home textiles & rugs |
| `ka001` | Kitchen |
| `28102` | BILLY series |

Discover others from `categoryPath[].key` on any product, the
`f-subcategories` filter values, or the breadcrumb on a product page.

---

## 4. Filters and sort orders

Filter parameters are `f-<name>=<valueId>`. Several values for one parameter
are comma-separated (or the parameter repeated — but a repeated
`f-measurement-buckets` only kept the first value, so prefer commas). Values
across different parameters are AND-ed; measurement buckets of different
types (WIDTH + HEIGHT) are AND-ed too.

Filter objects in the response:

```jsonc
// CLASS_FILTER / BOOLEAN
{"id": "COLOR", "name": "Colour", "parameter": "f-colors", "type": "CLASS_FILTER",
 "values": [{"id": "10156", "name": "white", "count": 234, "selected": false}, ...]}

// TYPED_CLASS_FILTER (measurement buckets)
{"id": "MEASUREMENT_BUCKETS", "name": "Size", "parameter": "f-measurement-buckets", "type": "TYPED_CLASS_FILTER",
 "types": [{"id": "WIDTH", "name": "Width",
            "values": [{"id": "WIDTH_60_80", "name": "60 - 79 cm", "count": 66}, ...]},
           {"id": "HEIGHT", ...}, {"id": "DEPTH", ...}, {"id": "LENGTH", ...}]}
```

Observed parameters (the set varies by category):

| Parameter | Filter id | Value ids | Notes |
| --- | --- | --- | --- |
| `f-measurement-buckets` | MEASUREMENT_BUCKETS | `WIDTH_60_80`, `HEIGHT_150_200`, `DEPTH_25_30`, `LENGTH_30_40`, open-ended `WIDTH_80_9223372036854775807` | Buckets are per-market and per-category: metric bookcases use width 0/20/40/60/80, height 0/50/100/150/200, depth 0/25/30/35/40; broader categories use 20 cm steps; the US uses inch buckets (`WIDTH_30_40` = 30–39"). Read them from the response, don't hardcode. |
| `f-price-buckets` | PRICE | `PRICE_0_5000`, `PRICE_5000_10000`, … `PRICE_20000_9223372036854775807` | Minor units: `PRICE_0_5000` = 0–49.99 in market currency. `f-price=0-100` is a 400. |
| `f-colors` | COLOR | numeric, e.g. `10156` white, `10139` black, `10028` grey, `10003` beige, `10019` brown, `10007` blue, `10033` green, `10124` red | Ids are stable across markets. |
| `f-type` | TYPE | either numeric or the literal type name, e.g. `Bookcase`, `Shelving unit` | Use what the response lists. |
| `f-materials` | MATERIAL | numeric | |
| `f-series` | SERIES | numeric (e.g. BILLY series id differs per market) | |
| `f-subcategories` | CATEGORIES | category codes like `st002`, `10382` | Handy for discovering categories. |
| `f-doors`, `f-appearance`, `f-feature`, `f-cube-hole`, `f-doors`, `f-form`, `f-shapes`, `f-storage-for`, `f-number-of-drawers` | various | numeric | Category-specific. |
| `f-top-seller`, `f-new-product`, `f-last-chance`, `f-home-smart`, `f-suitable-for-business` | BOOLEAN | `true` | |
| `f-ratings` | RATINGS | numeric | |
| `f-offers` | OFFERS | numeric | |

Sort ids (`sort=`): `RELEVANCE` (default), `PRICE_LOW_TO_HIGH`,
`PRICE_HIGH_TO_LOW`, `NEWEST`, `RATING`, `NAME_ASCENDING`, `MOST_POPULAR`,
`WIDTH`, `HEIGHT`, `DEPTH`, `LENGTH`. Dimension sorts return largest first.
Not every market offers every sort (il/he lacks RATING/NEWEST/MOST_POPULAR).

---

## 5. Product schema

Same object in `search-result-page` items (`items[].product`) and
`product-list-page` (`productWindow[]`). Fields worth using:

| Field | Example | Notes |
| --- | --- | --- |
| `itemNo` / `id` | `"00263850"` | market-local item number |
| `itemNoGlobal` | `"00263850"` | global; differs in the US |
| `itemType` | `"ART"` / `"SPR"` | article vs combination |
| `name` | `"BILLY"` | family name |
| `typeName` | `"Bookcase"` | localized product type |
| `validDesignText` | `"white"` | colour/finish variant |
| `itemMeasureReferenceText` | `"80x28x202 cm"`, `"60x180 cm"`, `"105x50 cm"`, `"70 cm"` | 3 numbers = W×D×H. 2 numbers: upright storage = W×H (depth omitted); desks, tables, table tops, beds, mattresses, rugs (`categoryPath` under `fu002`, `fu004`, `bm001`, `tl001`) = footprint W×D or L×W, height omitted. Localized unit; Hebrew wrapped in bidi marks |
| `ratingValue` / `ratingCount` | | absent in markets without reviews (all of il/he as of 2026-09) |
| `salesPrice.numeral` / `.currencyCode` | `55.0` / `"GBP"` | current price; `previous`, `lowestPreviousSalesPrice`, `validTo` exist on offers |
| `ratingValue` / `ratingCount` | `4.6` / `3126` | absent when unrated |
| `colors[]` | `{"name": "white", "id": "10156", "hex": "ffffff"}` | |
| `gprDescription.numberOfVariants` | `3` | other sizes/colours exist; `variants[]` lists them |
| `onlineSellable` | `true` | false = store only |
| `lastChance` | `false` | being discontinued |
| `tag` / `tagText` | `"FAMILY_PRICE"` / `"IKEA Family price"` | also `NEW`, `TOP_SELLER`, … |
| `quickFacts[]` | `{"type": "FEATURES", "name": "Large capacity"}` | |
| `categoryPath[]` | `[{"name": "Storage furniture", "key": "st001"}, …]` | |
| `businessStructure` | `productAreaName: "Bookcases"` … | IKEA's internal taxonomy |
| `pipUrl` | `https://www.ikea.com/gb/en/p/billy-bookcase-white-00263850/` | product page |
| `mainImageUrl`, `contextualImageUrl`, `allProductImage[]` | | images |
| `availability`, `features`, `heroBackoffData`, `optimizelyAttributes` | | usually empty; ignore |

---

## 6. Product page — exact dimensions

There is no JSON endpoint for measurements; they live in the product page
HTML. Fetch with a browser `User-Agent`:

```
GET https://www.ikea.com/{country}/{language}/p/-{itemNo}/     -> 301 to the full slug URL
GET https://www.ikea.com/{country}/{language}/p/{slug}-{itemNo}/
```

The short `/p/-{itemNo}/` form only redirects correctly when the item number
is valid in that market (a US request with a GB item number lands on a
category page).

Three places in the HTML carry the numbers, in order of convenience:

1. `<script type="application/ld+json" id="pip-range-json-ld">` — schema.org
   Product with `width`, `depth`, `height` (strings like `"80 cm"`),
   `name`, `sku`/`mpn`, `color`, `material`, `category`,
   `aggregateRating.{ratingValue,reviewCount}`,
   `offers.{price,priceCurrency,availability,url}`, and recent `review[]`.
   Present in gb, il, us; assume it can be missing.
2. A JSON blob `"measurements":[{"measure":"80 cm","name":"Width","type":"00047"},
   {"measure":"28 cm","name":"Depth","type":"00044"},{"measure":"202 cm","name":"Height","type":"00041"},
   {"measure":"30 kg","name":"Max. load/shelf",...}]` — labelled and
   localized; includes max load, seat height, etc. Type codes are stable:
   `00001` length, `00047` width, `00044` depth, `00041` height, `00035`
   thickness. Table tops, worktops and rugs list length × width (no depth):
   placed as a desk, length is the width and width is the depth. The
   JSON-LD for those items puts the short side in `width` and the long side
   in `depth`, which reads swapped — prefer the labelled list. Hebrew labels:
   אורך length, רוחב width, עומק depth, גובה height, עובי thickness.
3. HTML rows `<span class="pipf-measurements-tab__measurement-name">Width</span><span class="pipf-measurements-tab__measurement-value">80 cm</span>`.

Packaging is a JSON blob starting `"packaging":{"numberOfPackages":1,"packages":[{"itemNo":..., "measurementGroups":[{"measurements":[{"type":"width","text":"30 cm","value":30}, {"type":"height",...}, {"type":"length",...}, {"type":"weight","text":"36.85 kg"}]}], "quantity":{"value":1}}]}`.

The bundled `scripts/ikea.py product` command tries all three and prints
packaging too.

---

## 7. Product catalog JSON

```
GET https://www.ikea.com/{country}/{language}/products/{last3}/{itemNo}.json
```

`{last3}` is the last three digits of the item number
(`/products/850/00263850.json`). Needs a browser `User-Agent`. Returns
`name`, `typeName`, `validDesignText`, `price` (string), `priceNumeral`,
`priceExclTaxNumeral`, `currencyCode`, `pipUrl`, `mainImage`, `catalogRefs`
(category memberships), `globalId`. **No measurements.** Returns `{}` with
200 in the US. Good as a cheap price/name lookup in metric markets.

---

## 8. Sales Item API — stock

```
GET https://api.salesitem.ingka.com/availabilities/{classUnitType}/{classUnitCode}
    ?itemNos=<itemNo>[,<itemNo>...]         required, 8 digits each
    &expand=StoresList,Restocks[,ChildItems,SalesLocations,DisplayLocations,DeliveryTime,...]
Headers:
    X-Client-ID: b6c117e5-ae61-4ef5-b4cc-e0b1e37f0631     required
    Accept: application/json;version=2                     recommended
```

- `classUnitType` `ru` + `classUnitCode` = country code (`GB`, `DE`, `IL`;
  case-insensitive) gives the country-level row and, with `expand=StoresList`,
  one row per store.
- `classUnitType` `sto` + store code (`1010`, `066`, `217`) gives one store.
- An older alias, `https://api.ingka.ikea.com/cia/availabilities/…`, took the
  same parameters and header in one 2026-09 test and returned 404 in another;
  treat it as a last-resort fallback only.
- `expand=SalesLocations` adds aisle/bin per store (works for Israel too):
  `salesLocations[].childItems[].salesLocations[].aisleAndBin`.
- Without the `version=2` Accept header you get an older shape with only
  `homeDelivery`/`clickCollect` at country level and no store quantities.

Public client ids known to work (from ikea.com's own JavaScript, look for
`ciaApiClientKey` or the `X-Client-ID` header in DevTools on any product page):
`b6c117e5-ae61-4ef5-b4cc-e0b1e37f0631`, `ef382663-a2a5-40d4-8afe-f0634821c0ed`,
`da465052-7912-43b2-82fa-9dc39cdccef8`.

Response (version 2, trimmed):

```jsonc
{
  "availabilities": [
    {
      "classUnitKey": {"classUnitCode": "1010", "classUnitType": "STO"},
      "itemKey": {"itemNo": "00263850", "itemType": "ART"},
      "availableForCashCarry": true,
      "availableForClickCollect": true,
      "buyingOption": {
        "cashCarry": {
          "availability": {
            "quantity": 8,
            "probability": {"thisDay": {"messageType": "HIGH_IN_STOCK", "colour": {...}}},
            "restocks": [{"earliestDate": "2026-10-15", "latestDate": "2026-10-22", "quantity": 33, "type": "DELIVERY"}],
            "updateDateTime": "2026-09-15T10:36:38.000Z"
          },
          "range": {"inRange": true},
          "eligibleForStockNotification": false,
          "tags": ["CUSTOMER_PICKUP"],
          "unitOfMeasure": "PIECE"
        },
        "clickCollect": {"range": {"inRange": true}},
        "homeDelivery": {"range": {"inRange": true}}
      }
    }
  ],
  "salesLocations": [ {...aisle/bin per store when expand=SalesLocations...} ],
  "errors": [ {"code": 404, "message": "Not found", "details": {"itemNo": "...", ...}} ],
  "timestamp": "...", "traceId": "..."
}
```

`messageType` values: `HIGH_IN_STOCK`, `MEDIUM_IN_STOCK`, `LOW_IN_STOCK`,
`OUT_OF_STOCK`. `quantity` is the number actually on the shelf and is the
more useful figure; `MEDIUM_IN_STOCK` can be as few as 1–2 units. Plan-and-order points and lockers appear as `STO` rows with
no `cashCarry.availability`; skip them. Error codes: `404` item not found,
`405` bad class unit code, `602` missing `itemNos`, `604` item number too
short, `606` bad `expand` value.

---

## 9. Stores

```
GET https://www.ikea.com/{country}/{language}/meta-data/informera/stores-detailed.json
```

Needs a browser `User-Agent`. Array of stores:
`id` (the `classUnitCode` for `sto` stock lookups), `name`, `displayName`,
`address.{street,zipCode,city,displayAddress,timezone}`, `lat`, `lng`,
`hours.{normal,exceptions,restaurant,clickncollect,...}[]` with
`{day: "MON", open: "10:00", close: "20:00"}`, `storePageUrl`,
`buClassification.code` (`STORE`, `PLAN_AND_ORDER_POINT`, …), `hideStore`.

---

## 10. Dead or unreliable endpoints

| Endpoint | Status 2026-09-16 |
| --- | --- |
| `GET /{c}/{l}/meta-data/navigation/catalog-products-slim.json` (category tree) | **404 in every market tried** (gb, de, us, il, nl), with or without browser UA. Still listed in the upstream spec. Use `categoryPath`, `f-subcategories` values, or the table in §3 instead. |
| `GET .../search-result-page/more-products` | 404. Text search has no pagination. |
| `search-result-page?start=…` / `?moreToken=…` | 400 `Unrecognized parameter`. |
| `product-list-page?f-price=0-100` | 400. Use `f-price-buckets`. |
| `/{c}/{l}/products/{last3}/{itemNo}.json` in us/en | 200 with `{}`. |
| `/{c}/{l}/p/-{itemNo}/` with a foreign item number | Redirects to a category page, not a 404. Check the final URL contains `/p/`. |
| `api.salesitem.ingka.com` without `X-Client-ID` | 401/403. |

---

## 11. Error messages you will see

- Search API `400 {"status":400,"title":"Bad Request","detail":"Unrecognized parameter: start"}` — parameter not supported; the detail names it.
- Search API `400 … "Size parameter cannot exceed 1000"`.
- Search API `404` — market path doesn't exist (e.g. `il/en`) or category id unknown.
- `www.ikea.com` `404` plain text `Not found` — wrong path, or (for HTML pages) missing browser `User-Agent`.
- Sales Item `422` with `errors[].code` as in §8.
