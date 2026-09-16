#!/usr/bin/env python3
"""
ikea.py - a thin command-line client for IKEA's unofficial public APIs.

Standard library only (no pip installs). Every command needs a market in the
form <country>/<language>, e.g. gb/en, de/de, il/he, us/en. Pass --market or
set IKEA_MARKET in the environment.

Commands
  search QUERY        free-text product search (the ikea.com search box)
  list CATEGORY_ID    list a category (e.g. st001, 10382, or a UUID)
  filters             show the filter values the API accepts for a query/category
  product ITEMNO...   exact labelled dimensions, price, rating, packaging
  stock ITEMNO[,..]   stock per store (or one store with --store CODE)
  stores              list the stores in the market with their codes

Run `ikea.py <command> -h` for options. Add --json to any command for
machine-readable output. See ../references/api-reference.md for the raw API.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import signal
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

SEARCH_BASE = "https://sik.search.blue.cdtapps.com"
WEB_BASE = "https://www.ikea.com"
SALESITEM_BASE = "https://api.salesitem.ingka.com"
# Public client id used by ikea.com itself; see the X-Client-ID section of the
# reference doc for how to find a fresh one if this stops working.
DEFAULT_CLIENT_ID = "b6c117e5-ae61-4ef5-b4cc-e0b1e37f0631"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
BIDI_MARKS = "‎‏‪‫‬"


# ----------------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------------
def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def get_json(url: str, headers: dict | None = None) -> dict | list:
    status, body = http_get(url, headers)
    if status >= 400:
        detail = body.decode("utf-8", "replace")[:500]
        raise SystemExit(f"HTTP {status} from {url}\n{detail}")
    return json.loads(body)


def market_parts(market: str) -> tuple[str, str]:
    m = market.strip().strip("/").lower()
    if not re.fullmatch(r"[a-z]{2}/[a-z]{2}", m):
        raise SystemExit(
            f"Invalid market '{market}'. Use <country>/<language>, e.g. gb/en, de/de, il/he, us/en."
        )
    country, language = m.split("/")
    return country, language


# ----------------------------------------------------------------------------
# Measurement parsing
# ----------------------------------------------------------------------------
_FRACTIONS = {"1/2": 0.5, "1/4": 0.25, "3/4": 0.75, "1/8": 0.125, "3/8": 0.375, "5/8": 0.625, "7/8": 0.875}


def _parse_number(tok: str) -> float | None:
    tok = tok.strip()
    if not tok:
        return None
    m = re.fullmatch(r"(\d+)?\s*(\d/\d)?", tok)
    if m and (m.group(1) or m.group(2)):
        whole = float(m.group(1) or 0)
        frac = _FRACTIONS.get(m.group(2) or "", 0.0)
        return whole + frac
    try:
        return float(tok.replace(",", "."))
    except ValueError:
        return None


# Category codes (stable across markets) whose two-number sizes are a footprint
# (width x depth / length x width) rather than width x height.
FLAT_CATEGORY_KEYS = {"fu002", "fu004", "tl001", "bm001"}  # tables & chairs, desks, rugs & textiles, beds & mattresses
FLAT_TYPE_WORDS = re.compile(
    r"desk|table|top\b|worktop|bench|bed|mattress|rug|mat\b|"          # en
    r"שולחן|משטח|מיטה|מזרן|שטיח|ספסל|"                                     # he
    r"tisch|platte|bank|bett|matratze|teppich|"                           # de
    r"bureau|table|plateau|banc|lit\b|matelas|tapis|"                     # fr
    r"tafel|blad|bed\b|matras|tapijt|"                                    # nl
    r"bord|skiva|säng|madrass|matta|"                                     # sv
    r"mesa|escritorio|tablero|cama|colchón|alfombra|"                     # es
    r"tavolo|scrivania|piano|letto|materasso|tappeto",                    # it
    re.IGNORECASE,
)


def is_flat_item(product: dict) -> bool:
    keys = {c.get("key") for c in product.get("categoryPath") or []}
    if keys & FLAT_CATEGORY_KEYS:
        return True
    return bool(FLAT_TYPE_WORDS.search(product.get("typeName") or ""))


def parse_measure_text(text: str | None, flat: bool = False) -> dict:
    """
    Turn IKEA's itemMeasureReferenceText ("80x28x202 cm", "60x180 cm",
    '31 1/2x11x79 1/2 "', '‎60x180 ס"מ‏') into numbers.

    IKEA lists furniture as width x depth x height. When only two numbers are
    given: for upright storage it is width x height (depth omitted); for flat
    items (desks, tables, tabletops, beds, rugs) it is the footprint,
    width x depth (or length x width), and the height is not on the card.
    Pass flat=True (see is_flat_item) to get the footprint reading. Callers
    should still confirm with `product` for finalists.
    """
    out = {"text": text, "values_cm": [], "unit": None, "width": None, "depth": None, "height": None, "layout": None}
    if not text:
        return out
    clean = text
    for ch in BIDI_MARKS:
        clean = clean.replace(ch, "")
    clean = clean.strip()
    # Unit words first (Hebrew ס"מ contains a quote mark, so strip it before
    # looking for the inch symbol).
    clean = re.sub(r'\s*(ס"מ|סמ|cm|mm|in)\s*$', "", clean).strip()
    inches = '"' in clean or "''" in clean
    unit = "in" if inches else "cm"
    body = re.sub(r'\s*("|\'\')\s*$', "", clean).strip()
    parts = re.split(r"\s*[x×X]\s*", body)
    values = [v for v in (_parse_number(p) for p in parts) if v is not None]
    if not values:
        return out
    factor = 2.54 if inches else 1.0
    values_cm = [round(v * factor, 1) for v in values]
    out.update(unit=unit, values_cm=values_cm)
    if len(values_cm) == 3:
        out.update(width=values_cm[0], depth=values_cm[1], height=values_cm[2], layout="WxDxH")
    elif len(values_cm) == 2 and flat:
        out.update(width=values_cm[0], depth=values_cm[1], layout="WxD footprint (flat item; height not on card)")
    elif len(values_cm) == 2:
        out.update(width=values_cm[0], height=values_cm[1], layout="WxH (assumed; depth unknown)")
    else:
        out.update(width=values_cm[0], layout="single")
    return out


def fits(dims: dict, limits: dict, strict: bool = False) -> tuple[bool, list[str]]:
    """Return (passes, notes). Unknown dimensions pass but are noted, unless strict."""
    notes = []
    for key in ("width", "depth", "height"):
        val = dims.get(key)
        mx = limits.get(f"max_{key}")
        mn = limits.get(f"min_{key}")
        if val is None:
            if mx is not None or mn is not None:
                if strict:
                    return False, notes
                notes.append(f"{key} unknown")
            continue
        if mx is not None and val > mx:
            return False, notes
        if mn is not None and val < mn:
            return False, notes
    return True, notes


# ----------------------------------------------------------------------------
# Search API (sik.search.blue.cdtapps.com)
# ----------------------------------------------------------------------------
def build_filter_params(filters: list[str] | None) -> dict:
    """['f-colors=10156', 'f-measurement-buckets=WIDTH_60_80', 'f-measurement-buckets=HEIGHT_150_200']
    -> {'f-colors': '10156', 'f-measurement-buckets': 'WIDTH_60_80,HEIGHT_150_200'}"""
    params: dict[str, str] = {}
    for f in filters or []:
        if "=" not in f:
            raise SystemExit(f"Bad --filter '{f}'. Use KEY=VALUE, e.g. f-colors=10156")
        k, v = f.split("=", 1)
        k = k.strip()
        if not k.startswith("f-"):
            k = "f-" + k
        params[k] = f"{params[k]},{v}" if k in params else v
    return params


def slim_product(p: dict, market: str) -> dict:
    price = p.get("salesPrice") or {}
    dims = parse_measure_text(p.get("itemMeasureReferenceText"), flat=is_flat_item(p))
    return {
        "itemNo": p.get("itemNo") or p.get("id"),
        "itemType": p.get("itemType"),
        "name": p.get("name"),
        "typeName": p.get("typeName"),
        "design": p.get("validDesignText"),
        "measureText": p.get("itemMeasureReferenceText"),
        "dims": dims,
        "price": price.get("numeral"),
        "currency": price.get("currencyCode"),
        "previousPrice": _price_string(price.get("previous")),
        "rating": p.get("ratingValue"),
        "ratingCount": p.get("ratingCount"),
        "colors": [c.get("name") for c in p.get("colors") or [] if c.get("name")],
        "variants": (p.get("gprDescription") or {}).get("numberOfVariants"),
        "onlineSellable": p.get("onlineSellable"),
        "lastChance": p.get("lastChance"),
        "tag": p.get("tagText") or p.get("tag"),
        "category": " > ".join(c.get("name", "") for c in p.get("categoryPath") or []),
        "url": p.get("pipUrl") or f"{WEB_BASE}/{market}/p/-{p.get('itemNo')}/",
        "image": p.get("mainImageUrl"),
    }


def _price_string(block: dict | None) -> str | None:
    if not block:
        return None
    return f"{block.get('prefix','')}{block.get('wholeNumber','')}{block.get('separator','')}{block.get('decimals','')}{block.get('suffix','')}".strip() or None


def search_products(market: str, query: str, size: int, sort: str | None, filters: list[str] | None) -> tuple[list[dict], dict]:
    params = {"q": query, "size": min(max(size, 1), 1000)}
    if sort:
        params["sort"] = sort
    params.update(build_filter_params(filters))
    url = f"{SEARCH_BASE}/{market}/search-result-page?{urllib.parse.urlencode(params)}"
    data = get_json(url)
    page = data.get("searchResultPage") or {}
    products = page.get("products") or {}
    main = products.get("main") or {}
    items = [it.get("product") for it in main.get("items") or [] if it.get("type") == "PRODUCT" and it.get("product")]
    meta = {
        "total": main.get("max"),
        "returned": len(items),
        "didYouMean": [d.get("text") if isinstance(d, dict) else d for d in page.get("didYouMean") or []],
        "relatedSearches": [r.get("text") for r in page.get("relatedSearches") or []][:8],
        "filters": products.get("filters") or [],
        "sortOrders": [v.get("id") for v in (products.get("sortOrders") or {}).get("values") or []],
        "url": url,
    }
    return items, meta


def list_category(market: str, category: str, size: int, sort: str | None, filters: list[str] | None) -> tuple[list[dict], dict]:
    params = {"category": category, "size": min(max(size, 1), 1000)}
    if sort:
        params["sort"] = sort
    params.update(build_filter_params(filters))
    url = f"{SEARCH_BASE}/{market}/product-list-page?{urllib.parse.urlencode(params)}"
    data = get_json(url)
    page = data.get("productListPage") or {}
    items = page.get("productWindow") or []
    meta = {
        "total": page.get("productCount"),
        "returned": len(items),
        "category": (page.get("category") or {}).get("name"),
        "filters": page.get("dynamicFiltersV1") or [],
        "sortOrders": [v.get("id") for v in (page.get("sortOrders") or {}).get("values") or []],
        "url": url,
    }
    return items, meta


def describe_filters(filters: list[dict]) -> list[dict]:
    """Normalise the two filter shapes (search vs category) into one list."""
    out = []
    for f in filters:
        param = f.get("parameter") or f.get("filterParam")
        entry = {"id": f.get("id"), "name": f.get("name"), "param": param, "values": []}
        for t in f.get("types") or []:  # TYPED_CLASS_FILTER (measurement buckets)
            for v in t.get("values") or []:
                entry["values"].append({"id": v.get("id"), "name": f"{t.get('name')}: {v.get('name')}", "count": v.get("count")})
        for v in f.get("values") or []:
            entry["values"].append({"id": v.get("id"), "name": v.get("name"), "count": v.get("count")})
        out.append(entry)
    return out


# ----------------------------------------------------------------------------
# Product page (exact dimensions)
# ----------------------------------------------------------------------------
def _extract_balanced(text: str, start: int) -> str | None:
    """Return the JSON object/array starting at text[start] ('{' or '[')."""
    open_ch = text[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _json_after(text: str, key: str) -> dict | list | None:
    idx = text.find(key)
    if idx < 0:
        return None
    start = idx + len(key)
    while start < len(text) and text[start] not in "{[":
        start += 1
    blob = _extract_balanced(text, start)
    if not blob:
        return None
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def fetch_product(market: str, item_no: str) -> dict:
    item_no = re.sub(r"\D", "", item_no)
    if len(item_no) != 8:
        raise SystemExit(f"Item numbers are 8 digits (dots optional), got '{item_no}'")
    result: dict = {"itemNo": item_no, "market": market}

    # 1. Product page HTML: JSON-LD (most markets) + measurement blobs (all markets)
    status, body = http_get(f"{WEB_BASE}/{market}/p/-{item_no}/")
    if status >= 400:
        result["error"] = f"product page HTTP {status}"
    else:
        html = body.decode("utf-8", "replace")
        ld = _json_after(html, 'id="pip-range-json-ld">')
        if isinstance(ld, dict):
            result["name"] = ld.get("name")
            result["sku"] = ld.get("sku") or ld.get("mpn")
            result["category"] = ld.get("category")
            result["color"] = ld.get("color")
            result["material"] = ld.get("material")
            offers = ld.get("offers") or {}
            result["price"] = _to_float(offers.get("price"))
            result["currency"] = offers.get("priceCurrency")
            result["availabilitySchema"] = (offers.get("availability") or "").rsplit("/", 1)[-1] or None
            result["url"] = offers.get("url") or ld.get("url")
            rating = ld.get("aggregateRating") or {}
            result["rating"] = _to_float(rating.get("ratingValue"))
            result["ratingCount"] = _to_int(rating.get("reviewCount"))
            result["dimensions"] = {k: ld.get(k) for k in ("width", "depth", "height") if ld.get(k)}

        # Labelled measurement list: [{"measure":"80 cm","name":"Width","type":"00047"}, ...]
        # (the packaging blob also has a "measurements" key, so anchor on "measure")
        measurements = None
        anchor = html.find('"measurements":[{"measure"')
        if anchor >= 0:
            measurements = _json_after(html[anchor:], '"measurements":')
        if isinstance(measurements, list) and measurements and isinstance(measurements[0], dict) and "measure" in measurements[0]:
            result["measurements"] = [
                {"name": htmllib.unescape(str(m.get("name"))), "measure": htmllib.unescape(str(m.get("measure"))), "type": m.get("type")}
                for m in measurements
            ]
        else:
            rows = re.findall(
                r'pipf-measurements-tab__measurement-name">([^<]+)</span><span class="pipf-measurements-tab__measurement-value">([^<]+)',
                html,
            )
            if rows:
                result["measurements"] = [{"name": htmllib.unescape(n).strip(), "measure": htmllib.unescape(v).strip()} for n, v in rows]
        labelled = classify_measurements(result.get("measurements") or [])
        if labelled:
            # Prefer the page's own labelled list over JSON-LD, which maps
            # tabletops as width=short side, depth=long side.
            result["dimensions"] = {k: labelled[k] for k in ("width", "depth", "height", "length", "thickness") if k in labelled}
        dims = result.get("dimensions") or {}
        if "length" in dims and "depth" not in dims and "width" in dims:
            # Flat item (tabletop, worktop, rug, mattress): IKEA labels the long
            # side "length" and the short side "width". Placed as a desk it
            # is <length> wide and <width> deep.
            note = "from length x width" + (f"; height {dims['height']}" if dims.get("height") else "; height not listed")
            result["footprint"] = {"width": dims["length"], "depth": dims["width"], "note": note}

        packaging = _json_after(html, '"packaging":')
        if isinstance(packaging, dict) and "packages" in packaging:
            pkgs = []
            for p in packaging.get("packages") or []:
                meas = {}
                for g in p.get("measurementGroups") or []:
                    for m in g.get("measurements") or []:
                        meas[m.get("type") or m.get("label")] = m.get("text")
                if not meas:
                    continue  # combination header entry, no box of its own
                pkgs.append({"itemNo": p.get("itemNo"), "name": p.get("name"), "quantity": (p.get("quantity") or {}).get("value"), **meas})
            result["packaging"] = {"numberOfPackages": packaging.get("numberOfPackages"), "packages": pkgs}

        title = re.search(r"<title>([^<]+)</title>", html)
        if title and not result.get("name"):
            result["name"] = title.group(1).strip()
        result.setdefault("url", f"{WEB_BASE}/{market}/p/-{item_no}/")

    # 2. Catalog JSON: reliable name/type/price even where JSON-LD is missing
    if result.get("price") is None or not result.get("typeName"):
        status, body = http_get(f"{WEB_BASE}/{market}/products/{item_no[-3:]}/{item_no}.json", {"Accept": "application/json"})
        if status < 400:
            try:
                cat = json.loads(body)
                result.setdefault("name", cat.get("name"))
                result["typeName"] = cat.get("typeName")
                result["design"] = cat.get("validDesignText")
                if result.get("price") is None:
                    result["price"] = cat.get("priceNumeral")
                    result["currency"] = cat.get("currencyCode")
                result["url"] = cat.get("pipUrl") or result.get("url")
            except json.JSONDecodeError:
                pass
    return result


# Measurement type codes are stable across markets; labels are localized.
_MEASURE_TYPE_CODES = {"00001": "length", "00047": "width", "00044": "depth", "00041": "height", "00035": "thickness"}
_MEASURE_LABELS = {
    "length": re.compile(r"^(length|אורך|länge|longueur|lengte|längd|largo|lunghezza)\b", re.I),
    "width": re.compile(r"^(width|רוחב|breite|largeur|breedte|bredd|ancho|larghezza)\b", re.I),
    "depth": re.compile(r"^(depth|עומק|tiefe|profondeur|diepte|djup|fondo|profondità)\b", re.I),
    "height": re.compile(r"^(height|גובה|höhe|hauteur|hoogte|höjd|alto|altura|altezza)\b", re.I),
    "thickness": re.compile(r"^(thickness|עובי|dicke|épaisseur|dikte|tjocklek|grosor|spessore)\b", re.I),
}


def classify_measurements(measurements: list[dict]) -> dict:
    """Map the labelled list to length/width/depth/height/thickness, by type code then by label."""
    out: dict[str, str] = {}
    for m in measurements:
        key = _MEASURE_TYPE_CODES.get(str(m.get("type") or ""))
        if not key:
            name = (m.get("name") or "").strip()
            for k, rx in _MEASURE_LABELS.items():
                if rx.search(name):
                    key = k
                    break
        if key and key not in out:
            out[key] = m.get("measure")
    return out


def _to_float(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _to_int(v):
    try:
        return int(str(v))
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------------------
# Sales Item API (stock) and stores
# ----------------------------------------------------------------------------
def fetch_stores(market: str) -> list[dict]:
    data = get_json(f"{WEB_BASE}/{market}/meta-data/informera/stores-detailed.json", {"Accept": "application/json"})
    stores = []
    for s in data:
        addr = s.get("address") or {}
        stores.append(
            {
                "id": s.get("id"),
                "name": s.get("displayName") or s.get("name"),
                "city": addr.get("city"),
                "address": addr.get("displayAddress"),
                "lat": s.get("lat"),
                "lng": s.get("lng"),
                "type": (s.get("buClassification") or {}).get("code"),
                "url": s.get("storePageUrl"),
            }
        )
    return stores


def fetch_stock(market: str, item_nos: list[str], store: str | None, client_id: str) -> dict:
    country, _ = market_parts(market)
    unit_type, unit_code = ("sto", store) if store else ("ru", country.upper())
    expand = "Restocks" if store else "StoresList,Restocks"
    params = urllib.parse.urlencode({"itemNos": ",".join(item_nos), "expand": expand})
    url = f"{SALESITEM_BASE}/availabilities/{unit_type}/{unit_code}?{params}"
    return get_json(url, {"X-Client-ID": client_id, "Accept": "application/json;version=2"})


def summarise_availability(a: dict) -> dict:
    opt = a.get("buyingOption") or {}
    cc = (opt.get("cashCarry") or {}).get("availability") or {}
    prob = ((cc.get("probability") or {}).get("thisDay") or {}).get("messageType")
    restocks = cc.get("restocks") or []
    return {
        "itemNo": (a.get("itemKey") or {}).get("itemNo"),
        "itemType": (a.get("itemKey") or {}).get("itemType"),
        "unit": (a.get("classUnitKey") or {}).get("classUnitCode"),
        "unitType": (a.get("classUnitKey") or {}).get("classUnitType"),
        "inStoreQty": cc.get("quantity"),
        "inStoreStatus": prob,
        "clickCollect": ((opt.get("clickCollect") or {}).get("range") or {}).get("inRange"),
        "homeDelivery": ((opt.get("homeDelivery") or {}).get("range") or {}).get("inRange"),
        "restock": [{"from": r.get("earliestDate"), "to": r.get("latestDate"), "qty": r.get("quantity")} for r in restocks] or None,
        "updated": cc.get("updateDateTime"),
    }


# ----------------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------------
def fmt_dims(d: dict) -> str:
    if not d.get("values_cm"):
        return "-"
    parts = []
    for key in ("width", "depth", "height"):
        v = d.get(key)
        if v is not None:
            parts.append(f"{key[0].upper()}{v:g}")
    layout = d.get("layout") or ""
    suffix = " (depth?)" if layout.startswith("WxH") else " (footprint; height?)" if layout.startswith("WxD footprint") else ""
    return " ".join(parts) + " cm" + suffix


def print_products(products: list[dict], limit_notes: dict[str, list[str]] | None = None) -> None:
    if not products:
        print("(no products)")
        return
    for p in products:
        price = f"{p['price']:g} {p['currency']}" if p.get("price") is not None else "-"
        rating = f"{p['rating']}/5 ({p['ratingCount']})" if p.get("rating") is not None else "no rating"
        flags = []
        if p.get("lastChance"):
            flags.append("last chance")
        if p.get("onlineSellable") is False:
            flags.append("store only")
        if p.get("variants"):
            flags.append(f"{p['variants']} variants")
        if limit_notes and limit_notes.get(p["itemNo"]):
            flags.extend(limit_notes[p["itemNo"]])
        flag_txt = f"  [{', '.join(flags)}]" if flags else ""
        print(f"{p['itemNo']}  {p['name']} - {p['typeName']}" + (f" ({p['design']})" if p.get("design") else ""))
        print(f"          {p['measureText'] or '-'}  ->  {fmt_dims(p['dims'])}  |  {price}  |  {rating}{flag_txt}")
        print(f"          {p['url']}")


def apply_type_filters(products: list[dict], args) -> list[dict]:
    """--only / --exclude: regex on 'NAME TYPENAME' (case-insensitive) to keep furniture and drop accessories."""
    only = re.compile(args.only, re.I) if getattr(args, "only", None) else None
    excl = re.compile(args.exclude, re.I) if getattr(args, "exclude", None) else None
    out = []
    for p in products:
        hay = f"{p.get('name') or ''} {p.get('typeName') or ''}"
        if only and not only.search(hay):
            continue
        if excl and excl.search(hay):
            continue
        out.append(p)
    return out


def apply_limits(products: list[dict], args) -> tuple[list[dict], dict[str, list[str]]]:
    limits = {k: getattr(args, k) for k in ("max_width", "max_depth", "max_height", "min_width", "min_depth", "min_height")}
    if all(v is None for v in limits.values()):
        return products, {}
    kept, notes = [], {}
    for p in products:
        ok, n = fits(p["dims"], limits, strict=getattr(args, "strict", False))
        if ok:
            kept.append(p)
            if n:
                notes[p["itemNo"]] = n
    return kept, notes


# ----------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------
def cmd_search_or_list(args, mode: str) -> None:
    market = args.market
    if mode == "search":
        raw, meta = search_products(market, args.query, args.size, args.sort, args.filter)
    else:
        raw, meta = list_category(market, args.category, args.size, args.sort, args.filter)
    products = [slim_product(p, market) for p in raw]
    products = apply_type_filters(products, args)
    products, notes = apply_limits(products, args)
    if args.json:
        json.dump({"meta": {k: v for k, v in meta.items() if k != "filters"}, "products": products, "limitNotes": notes}, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return
    head = f"{meta['returned']} of {meta['total']} results" if meta.get("total") is not None else f"{meta['returned']} results"
    if len(products) != len(raw):
        head += f", {len(products)} after your type/size filters"
    print(head + f"  ({meta['url']})")
    if meta.get("didYouMean"):
        print(f"did you mean: {', '.join(meta['didYouMean'])}")
    if meta.get("relatedSearches"):
        print(f"related searches: {', '.join(meta['relatedSearches'])}")
    print()
    print_products(products, notes)
    if args.show_filters:
        print()
        print_filters(describe_filters(meta["filters"]))


def print_filters(filters: list[dict]) -> None:
    print("Available filters (pass as --filter PARAM=VALUE_ID; repeat or comma-join for several):")
    for f in filters:
        if not f["values"]:
            print(f"  {f['param']}  ({f['name']}, boolean: pass =true)")
            continue
        print(f"  {f['param']}  ({f['name']})")
        for v in f["values"][:40]:
            count = f"  x{v['count']}" if v.get("count") is not None else ""
            print(f"      {v['id']:<40} {v['name']}{count}")


def cmd_filters(args) -> None:
    if args.query:
        _, meta = search_products(args.market, args.query, 1, None, args.filter)
    elif args.category:
        _, meta = list_category(args.market, args.category, 1, None, args.filter)
    else:
        raise SystemExit("filters needs --query TEXT or --category ID")
    filters = describe_filters(meta["filters"])
    if args.json:
        json.dump({"sortOrders": meta["sortOrders"], "filters": filters}, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return
    print(f"Sort options: {', '.join(meta['sortOrders'])}")
    print_filters(filters)


def cmd_product(args) -> None:
    results = [fetch_product(args.market, n) for n in args.itemno]
    if args.json:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return
    for r in results:
        print(f"{r['itemNo']}  {r.get('name') or '?'}" + (f" - {r['typeName']}" if r.get("typeName") else ""))
        if r.get("error"):
            print(f"          {r['error']}")
        dims = r.get("dimensions") or {}
        if dims:
            print("          size: " + ", ".join(f"{k} {v}" for k, v in dims.items()))
        fp = r.get("footprint")
        if fp:
            print(f"          footprint as placed: {fp['width']} wide x {fp['depth']} deep  ({fp['note']})")
        shown = set(dims.values())
        for m in r.get("measurements") or []:
            if m["measure"] not in shown:
                print(f"          {m['name']}: {m['measure']}")
        price = f"{r['price']:g} {r.get('currency') or ''}".strip() if r.get("price") is not None else "-"
        rating = f"{r['rating']}/5 ({r.get('ratingCount')})" if r.get("rating") is not None else "no rating"
        print(f"          price: {price}  |  {rating}" + (f"  |  {r['material']}" if r.get("material") else ""))
        pk = r.get("packaging")
        if pk:
            print(f"          packaging: {pk.get('numberOfPackages')} package(s)")
            for p in pk["packages"]:
                dims_txt = " x ".join(str(p.get(k)) for k in ("length", "width", "height") if p.get(k))
                print(f"              {p.get('quantity') or 1} x {dims_txt}" + (f", {p['weight']}" if p.get("weight") else ""))
        print(f"          {r.get('url')}")


def cmd_stock(args) -> None:
    item_nos = [re.sub(r"\D", "", n) for n in ",".join(args.itemno).split(",") if n.strip()]
    data = fetch_stock(args.market, item_nos, args.store, args.client_id)
    rows = [summarise_availability(a) for a in data.get("availabilities") or []]
    errors = data.get("errors") or []
    if args.json:
        json.dump({"availabilities": rows, "errors": errors}, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return
    try:
        store_names = {s["id"]: s["name"] for s in fetch_stores(args.market)}
    except SystemExit:
        store_names = {}
    for item in item_nos:
        types = {r.get("itemType") for r in rows if r["itemNo"] == item}
        combo = "  (combination: quantity is the main article's; legs/doors may run out separately)" if "SPR" in types else ""
        print(f"{item}{combo}")
        skipped = 0
        for r in rows:
            if r["itemNo"] != item:
                continue
            if r["unitType"] == "RU":
                print(f"          {r['unit']} (country): home delivery {r['homeDelivery']}, click & collect {r['clickCollect']}")
                continue
            if r["inStoreQty"] is None and not r["inStoreStatus"]:
                skipped += 1  # plan-and-order points, pickup lockers: no stock data
                continue
            name = store_names.get(r["unit"], "")
            restock = ""
            if r["restock"]:
                rs = r["restock"][0]
                restock = f", restock {rs['from']}..{rs['to']} ({rs['qty']})"
            print(f"          store {r['unit']:<5} {name:<24} qty {str(r['inStoreQty']):<5} {r['inStoreStatus'] or ''}{restock}")
        if skipped:
            print(f"          ({skipped} pickup points without stock data omitted; use --json to see them)")
    for e in errors:
        print(f"error {e.get('code')}: {e.get('message')} {e.get('details') or ''}")


def cmd_stores(args) -> None:
    stores = fetch_stores(args.market)
    if args.json:
        json.dump(stores, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return
    print(f"{'code':<6} {'store':<28} address   (use the code with `stock --store CODE`)")
    for s in stores:
        print(f"{s['id']:<6} {s['name']:<28} {s.get('address') or ''}")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def add_common_listing_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--size", type=int, default=50, help="results to fetch, 1-1000 (default 50)")
    p.add_argument("--sort", help="RELEVANCE, PRICE_LOW_TO_HIGH, PRICE_HIGH_TO_LOW, NEWEST, RATING, MOST_POPULAR, WIDTH, HEIGHT, DEPTH, ...")
    p.add_argument("--filter", "-f", action="append", metavar="PARAM=VALUE", help="server-side filter, e.g. f-measurement-buckets=WIDTH_60_80 or f-colors=10156 (repeatable)")
    for dim in ("width", "depth", "height"):
        p.add_argument(f"--max-{dim}", type=float, metavar="CM", help=f"drop products whose parsed {dim} exceeds this (cm)")
        p.add_argument(f"--min-{dim}", type=float, metavar="CM", help=f"drop products whose parsed {dim} is below this (cm)")
    p.add_argument("--only", metavar="REGEX", help="keep only products whose name/type matches, e.g. 'desk|table top' or 'שולחן'")
    p.add_argument("--exclude", metavar="REGEX", help="drop products whose name/type matches, e.g. 'bracket|cover|door|insert|lamp'")
    p.add_argument("--strict", action="store_true", help="with --max/--min: also drop products whose constrained dimension is unknown (e.g. 2-number sizes with no depth)")
    p.add_argument("--show-filters", action="store_true", help="also print the filter values available for this result set")
    p.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--market", default=os.environ.get("IKEA_MARKET"), help="<country>/<language>, e.g. gb/en, de/de, il/he, us/en (or set IKEA_MARKET)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="free-text product search")
    p.add_argument("query")
    add_common_listing_args(p)

    p = sub.add_parser("list", help="list products in a category id")
    p.add_argument("category")
    add_common_listing_args(p)

    p = sub.add_parser("filters", help="show filter values for a query or category")
    p.add_argument("--query", "-q")
    p.add_argument("--category", "-c")
    p.add_argument("--filter", "-f", action="append", metavar="PARAM=VALUE", help="narrow first, then show remaining filter values")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("product", help="exact dimensions, price, rating, packaging for item numbers")
    p.add_argument("itemno", nargs="+")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("stock", help="stock per store for item numbers")
    p.add_argument("itemno", nargs="+", help="8-digit item numbers, space or comma separated")
    p.add_argument("--store", help="3-4 digit store code (see `stores`); default lists every store in the market")
    p.add_argument("--client-id", default=os.environ.get("IKEA_CLIENT_ID", DEFAULT_CLIENT_ID))
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("stores", help="list stores in the market")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if not args.market:
        raise SystemExit("Missing market. Pass --market <country>/<language> (e.g. gb/en, il/he) or set IKEA_MARKET.")
    args.market = "/".join(market_parts(args.market))

    if args.command == "search":
        cmd_search_or_list(args, "search")
    elif args.command == "list":
        cmd_search_or_list(args, "list")
    elif args.command == "filters":
        cmd_filters(args)
    elif args.command == "product":
        cmd_product(args)
    elif args.command == "stock":
        cmd_stock(args)
    elif args.command == "stores":
        cmd_stores(args)


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
