#!/usr/bin/env python3
"""Build data/more-cases.json, grid entries, and screenshots for Mike's client list.

Copy is taken from a review prototype or, when that host does not answer, a live
site on the matching domain. Clients with neither are listed in data/skipped.md.
"""

import asyncio
import base64
import json
import re
import ssl
import subprocess
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import websockets
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "3 Nov 2026"
CTX = ssl.create_default_context()

ORDER = [
    "time2shine", "safespacefl", "leadfoundation", "saltandlight", "fbrn",
    "citylife", "tribeschurch", "boomerjacks", "rtrtexas", "aumakuadefense",
    "allplay", "assistedlivingfinder", "brakingnews", "igy6armory", "kdcollegeprep",
    "onehop", "monteslaw", "thegundrop", "thedreamersland", "ncutility", "ufixit",
    "valorem", "trialteamprep", "autobuilders", "harvestdirectory", "gildedage",
    "texasreconditioning", "meetthebishop", "startagainministries", "dentongopgrassroots",
    "freeformchiropractic", "alltex", "thejuicebardallas", "theamericanquiz",
    "catalystmktgagency", "radiant-nutrition", "ascendconsulting", "chiltonautobody",
    "bobthompsonhomes", "yourpoolrepairguy", "michaelrowanministries", "kpxofficial",
    "eddieinservice", "lonestararms", "playatthehive",
]

LIVE = {
    "autobuilders": "https://autobuilders.com/",
    "harvestdirectory": "https://harvestdirectory.com/",
    "eddieinservice": "https://eddieinservice.com/",
    "lonestararms": "https://lonestararms.com/",
}

REVIEW = {
    "radiant-nutrition": "https://radiantnutrition.clientreview.co/",
}

SKIP_TEXT = {
    "fbrn": "Review host fbrn.clientreview.co has no certificate for that name. Yavin-Digital/fbrn-prototype was not readable (HTTP 404). fbrn.org is a parking lander, not a client site.",
    "trialteamprep": "Review host trialteamprep.clientreview.co has no certificate for that name. Yavin-Digital/trialteamprep-prototype was not readable (HTTP 404). trialteamprep.com did not return a page.",
    "gildedage": "Review host gildedage.clientreview.co has no certificate for that name. Yavin-Digital/gildedage-prototype was not readable (HTTP 404). No live site on that name could be read.",
}

JUNK = (
    "developer note", "site speed", "lighthouse", "this page loaded",
    "projected react", "remove this banner", "function()", "json-ld",
    "estimated improvement", "html prototype",
)

GOOGLE = {
    "Poppins": "Poppins:wght@400;600;700",
    "Roboto": "Roboto:wght@400;500;700",
    "Roboto Slab": "Roboto+Slab:wght@500;700",
    "Montserrat": "Montserrat:wght@400;600;700",
    "Oswald": "Oswald:wght@500;600",
    "Inter": "Inter:wght@400;600",
    "Cormorant Garamond": "Cormorant+Garamond:wght@500;600",
    "Playfair Display": "Playfair+Display:wght@500;600",
    "Outfit": "Outfit:wght@400;600",
    "Work Sans": "Work+Sans:wght@400;600",
    "Archivo Black": "Archivo+Black",
    "Bitter": "Bitter:wght@500;700",
    "Public Sans": "Public+Sans:wght@400;600",
    "Source Serif 4": "Source+Serif+4:wght@500;600",
    "Jost": "Jost:wght@400;500;600",
    "Barlow Condensed": "Barlow+Condensed:wght@500;700",
    "Open Sans": "Open+Sans:wght@400;600",
    "Caveat": "Caveat:wght@500;600",
}


def fetch(url, limit=220000):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as response:
        return response.read(limit), response.geturl()


def html_text(html):
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", html)
    for a, b in (("&#x27;", "'"), ("&#39;", "'"), ("&amp;", "&"), ("&nbsp;", " "), ("&middot;", "·")):
        text = text.replace(a, b)
    return text.strip()


def junk(text):
    low = text.lower()
    return any(word in low for word in JUNK) or "${" in text


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text)
    good = []
    for part in parts:
        part = part.strip()
        if junk(part) or not (70 <= len(part) <= 340):
            continue
        if part.count("http") or part.lower().count("home ") > 2:
            continue
        good.append(part)
    return good


def lum(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ink_for(hex_color):
    return "#131419" if lum(hex_color) > 0.42 else "#faf6ee"


def client_from_title(title):
    for sep in (" | ", " — ", " – ", " · "):
        if sep in title:
            return title.split(sep)[0].strip()
    return title.strip()


def short_name(client, used):
    name = client
    if name.lower().startswith("the ") and len(name) > 16:
        name = name[4:]
    if len(name) > 18:
        name = " ".join(name.split()[:2])
    base = name
    n = 2
    while name in used:
        name = f"{base} {n}"
        n += 1
    used.add(name)
    return name


def load_fact(slug):
    path = Path(f"/tmp/facts/{slug}.json")
    if path.exists() and slug not in LIVE:
        return json.loads(path.read_text())
    url = LIVE.get(slug) or REVIEW.get(slug) or f"https://{slug}.clientreview.co/"
    data, final = fetch(url)
    html = data.decode("utf-8", "replace")
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else slug
    title = title.replace("&#x27;", "'").replace("&amp;", "&")
    desc_m = re.search(r'name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I)
    if not desc_m:
        desc_m = re.search(r'content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.I)
    h1s = []
    for h in re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", html, re.I)[:3]:
        t = re.sub(r"<[^>]+>", " ", h)
        t = re.sub(r"\s+", " ", t).strip().replace("&#x27;", "'").replace("&amp;", "&")
        if t:
            h1s.append(t)
    h2s = []
    for h in re.findall(r"<h2[^>]*>([\s\S]*?)</h2>", html, re.I)[:6]:
        t = re.sub(r"<[^>]+>", " ", h)
        t = re.sub(r"\s+", " ", t).strip().replace("&amp;", "&")
        if t:
            h2s.append(t[:180])
    fact = {
        "slug": slug,
        "review": final,
        "title": title[:180],
        "desc": (desc_m.group(1).strip()[:300] if desc_m else "").replace("&amp;", "&"),
        "h1": h1s,
        "h2": h2s,
        "colors": [],
        "fonts": [],
        "logos": [],
        "text": html_text(html),
    }
    return fact


def fact_text(fact):
    if fact.get("text"):
        return fact["text"]
    html_path = Path(f"/tmp/facts/{fact['slug']}.html")
    if html_path.exists():
        return html_text(html_path.read_text(errors="replace"))
    return " ".join(fact.get("paras") or [])


def palette(fact):
    colors = []
    seen = set()
    for token, hex_color in fact.get("colors") or []:
        hex_color = hex_color.upper() if len(hex_color) == 7 else hex_color
        if hex_color.lower() in seen:
            continue
        seen.add(hex_color.lower())
        colors.append({
            "role": token.strip("-"),
            "token": token,
            "hex": hex_color if hex_color.startswith("#") else f"#{hex_color}",
            "fg": ink_for(hex_color if hex_color.startswith("#") else f"#{hex_color}"),
            "line": lum(hex_color if hex_color.startswith("#") else f"#{hex_color}") > 0.7,
        })
        if len(colors) == 6:
            break
    return colors


def bands(colors):
    default = ("#0729aa", "#faf6ee", "#ffaf00", "#ffaf00", "#131419")
    if not colors:
        return default
    dark = [c for c in colors if lum(c["hex"]) < 0.35]
    light = [c for c in colors if 0.35 <= lum(c["hex"]) <= 0.85]
    brief = dark[0]["hex"] if dark else colors[0]["hex"]
    brief_ink = ink_for(brief)
    if light:
        band = light[0]["hex"]
    elif len(colors) > 1:
        band = colors[1]["hex"]
    else:
        band = "#ffaf00"
    return brief, brief_ink, "#ffaf00" if lum(brief) < 0.4 else brief_ink, band, ink_for(band)


def font_items(fact):
    blob = " ".join(fact.get("fonts") or [])
    found = []
    families = []
    for name in GOOGLE:
        if name.lower() in blob.lower() or name.lower() in fact_text(fact)[:500].lower():
            # only stylesheet names, not page text
            if name.lower() in blob.lower():
                found.append(name)
    for name in found[:2]:
        css = f'"{name}", sans-serif' if "Sans" in name or name in ("Poppins", "Roboto", "Inter", "Montserrat", "Oswald", "Outfit", "Jost", "Work Sans") else f'"{name}", serif'
        if name in ("Caveat",):
            css = f'"{name}", cursive'
        families.append({"css": css, "note": f"{name} · named in the stylesheet"})
    href = ""
    if found:
        href = "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,560&family=Sora:wght@400;500;600&family=" + "&family=".join(GOOGLE[n] for n in found[:2]) + "&display=swap"
    return families, href


def save_logo(slug, urls):
    for url in urls:
        if any(bad in url.lower() for bad in ("next/image", "font-awesome", "favicon", "icon.png")):
            continue
        try:
            data, final = fetch(url, 1_500_000)
        except Exception:
            continue
        kind = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg" if data[:2] == b"\xff\xd8" else "webp" if data[:4] == b"RIFF" else "svg" if b"<svg" in data[:400].lower() else ""
        if not kind or len(data) < 400:
            continue
        folder = ROOT / "assets" / "cases" / slug
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"logo.{kind}"
        path.write_bytes(data)
        width, height = 240, 80
        if kind == "png":
            import struct
            width, height = struct.unpack(">II", data[16:24])
        elif kind in ("jpg", "webp"):
            with Image.open(path) as im:
                width, height = im.size
        elif kind == "svg":
            m = re.search(br'viewBox=["\']\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)', data)
            if m:
                width, height = int(float(m.group(1))), int(float(m.group(2)))
        plate = "#131419" if "white" in url.lower() else "#fffcf7"
        ink = "#faf6ee" if plate == "#131419" else "#131419"
        return {
            "src": f"../../assets/cases/{slug}/logo.{kind}",
            "alt": slug,
            "width": width,
            "height": height,
            "note": f"Logo file from the source page. Shown smaller than the file." if width > 280 else "Logo file from the source page.",
            "plate": plate,
            "ink": ink,
        }
    return None


async def shoot(pages):
    subprocess.run(["pkill", "-f", "remote-debugging-port=9222"], check=False)
    await asyncio.sleep(0.4)
    profile = "/tmp/chrome-more"
    subprocess.Popen(
        ["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--user-data-dir={profile}", "--remote-debugging-port=9222", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            tabs = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json"))
            break
        except Exception:
            await asyncio.sleep(0.2)
    else:
        raise SystemExit("chrome did not start")
    page = next(t for t in tabs if t["type"] == "page")
    ws = await websockets.connect(page["webSocketDebuggerUrl"], max_size=40_000_000)
    n = 0

    async def call(method, **params):
        nonlocal n
        n += 1
        await ws.send(json.dumps({"id": n, "method": method, "params": params}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == n:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})

    await call("Page.enable")
    await call("Runtime.enable")
    out = {}
    for slug, url in pages:
        dims = {}
        for label, w, h in (("desktop", 1440, 900), ("phone", 390, 844)):
            await call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=(label == "phone"))
            await call("Page.navigate", url=url)
            for _ in range(40):
                state = await call("Runtime.evaluate", expression="document.readyState", returnByValue=True)
                if state["result"]["value"] == "complete":
                    break
                await asyncio.sleep(0.15)
            await asyncio.sleep(0.45)
            shot = await call("Page.captureScreenshot", format="png", fromSurface=True)
            png = base64.b64decode(shot["data"])
            folder = ROOT / "assets" / "shots"
            folder.mkdir(parents=True, exist_ok=True)
            raw = folder / f"{slug}-{label}.png"
            raw.write_bytes(png)
            with Image.open(raw) as im:
                im = im.convert("RGB")
                width, height = im.size
                im.save(folder / f"{slug}-{label}.jpg", quality=82, optimize=True)
                im.save(folder / f"{slug}-{label}.webp", quality=80, method=4)
                if label == "desktop":
                    blur = im.copy()
                    blur.thumbnail((48, 48))
                    blur = blur.filter(ImageFilter.GaussianBlur(radius=1.2))
                    blur.save(folder / f"{slug}-blur.webp", quality=60, method=4)
            raw.unlink()
            dims[label] = (width, height)
            print(f"shot {slug} {label} {width}x{height}")
        out[slug] = dims
    await ws.close()
    return out


def build_case(slug, number, fact, dims, used_short):
    text = fact_text(fact)
    sens = sentences(text)
    title = fact.get("title") or slug
    client = client_from_title(title)
    if slug == "saltandlight":
        client = "Salt and Light Council"
    if slug == "thegundrop":
        client = "US Drop Zone"
    if slug == "playatthehive":
        client = "The Hive"
    h1 = next((h for h in fact.get("h1") or [] if h and "${" not in h and "[" not in h and len(h) > 8), "")
    if not h1:
        h1 = client
    lede = fact.get("desc") or ""
    if len(lede) < 40 and sens:
        lede = sens[0]
    brief_p = next((s for s in sens if s != lede), lede or (sens[0] if sens else h1))
    h2s = [h for h in fact.get("h2") or [] if h and not junk(h) and "site speed" not in h.lower() and len(h) > 3]
    brief_h = h2s[0] if h2s else h1
    host = urlparse(fact["review"]).netloc.replace("www.", "")
    source_kind = "Live site" if slug in LIVE else "Review prototype"
    subtitle = ""
    for sep in (" | ", " — ", " – "):
        if sep in title:
            subtitle = title.split(sep, 1)[1].strip()
            break
    industry = subtitle[:80] if subtitle else source_kind
    scope = source_kind
    colors = palette(fact)
    brief, brief_ink, brief_kicker, band, band_ink = bands(colors)
    fonts, fonts_href = font_items(fact)
    if not fonts_href:
        fonts_href = "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,560&family=Sora:wght@400;500;600&display=swap"
    logo = save_logo(slug, fact.get("logos") or [])
    notes = []
    if slug == "saltandlight":
        notes.append("The review prototype title is the placeholder [MINISTRY NAME]. The page links to saltandlightcouncil.org and the Lewisville chapter page.")
    if slug == "valorem":
        notes.append("The prototype README calls Valorem a sample operator on The Rez. Coin names in the repo are Valorem and Ips.")
    if slug == "igy6armory":
        notes.append("The review page calls itself a demo site and a sample rez operator.")
    if slug == "aumakuadefense":
        notes.append("SCOPE.md says aumakuadefense.com was a coming-soon page on 13 Oct 2026. The prototype says product names and prices have not been supplied.")
    if slug == "playatthehive":
        notes.append("playatthehive.com returned HTTP 403. Figures and the founder quote on thetribemaker.com/work/the-hive were not copied.")
    if slug == "thedreamersland":
        notes.append("The prototype banner says all content and images are not final and are only there to show what is possible.")
    if slug == "citylife":
        notes.append("The prototype prints a Bennett Eye Institute campaign with impression and click counts. Those figures are not repeated as results.")
    if slug in LIVE:
        notes.append("The review host and the prototype repo were not reachable. This page uses the live site on the matching domain.")
    if slug == "harvestdirectory":
        notes.append("Yavin-Digital/harvestdirectory-prototype contains only a one-line README. The review host did not answer. Copy is from harvestdirectory.com.")
    if slug == "radiant-nutrition":
        notes.append("SCOPE.md names the production domain radiantnutrition.com. The review host that answered is radiantnutrition.clientreview.co.")
    desktop, phone = dims["desktop"], dims["phone"]
    repo_line = "Yavin-Digital/{0}-prototype was not readable from this account (HTTP 404), so PROJECT_GUIDE.md and SCOPE.md were not read.".format(slug)
    if slug == "playatthehive":
        repo_line = "Yavin-Digital/playatthehive and playatthehive-prototype were not readable from this account (HTTP 404)."
    if slug in ("aumakuadefense", "ufixit", "valorem", "radiant-nutrition", "michaelrowanministries", "harvestdirectory"):
        repo_line = f"Repo Yavin-Digital/{slug}-prototype was readable. " + ("SCOPE.md and PROJECT_GUIDE.md were read." if slug != "harvestdirectory" else "The repo has a README only.")
    log = [
        repo_line,
        "No project year, measured result, named quote, second phone screen, section crop, full-page scroll, or role credit was in the sources used here.",
    ]
    if not colors:
        log.append("No named color tokens were found in the stylesheet.")
    if not logo:
        log.append("No logo file was saved from the page.")
    if notes:
        log.extend(notes)
    case = {
        "slug": slug,
        "number": f"{number:02d}",
        "client": client,
        "title": f"{client} — Case Study | The Tribe Maker",
        "description": f"Case study for {client}. Copy is from the {source_kind.lower()} read on {CHECKED}.",
        "category": industry.lower() if industry != source_kind else source_kind.lower(),
        "kicker": f"{client} · {host}",
        "h1": h1,
        "lede": lede or h1,
        "industry": industry,
        "scope": scope,
        "year_gap": "No project year is written in a project guide or scope file this account could read.",
        "url": fact["review"],
        "host": host,
        "brief": brief,
        "brief_ink": brief_ink,
        "brief_kicker": brief_kicker,
        "band": band,
        "band_ink": band_ink,
        "brief_h": brief_h,
        "brief_p": brief_p,
        "identity": "Swatches are named tokens from the stylesheet." if colors else "A written identity story and named color tokens were not in the sources read for this page.",
        "colors": colors,
        "fonts_href": fonts_href,
        "fonts": fonts,
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is a screenshot of the same page, captured at phone width. It is not enlarged.",
        "results_gap": "No load time or before-and-after figure is in a project guide or scope file. Numbers printed on the source page are not repeated here as results.",
        "details": [
            {"label": source_kind, "title": brief_h[:80], "text": brief_p},
        ],
        "shots": {
            "desktop": list(desktop),
            "phone": list(phone),
            "desktop_alt": f"Homepage of {client}",
            "phone_alt": f"{client} homepage on a phone",
        },
        "sources": [{"href": fact["review"], "text": f"{source_kind}, fetched {CHECKED}"}, {"text": repo_line}],
        "log": log,
        "shortName": short_name(client, used_short),
        "headline": (lede or h1)[:220],
    }
    if notes:
        case["note"] = " ".join(notes)
    if logo:
        case["logo"] = {k: logo[k] for k in ("src", "alt", "width", "height", "note")}
        case["logo"]["alt"] = client
        case["logo_plate"] = logo["plate"]
        case["logo_ink"] = logo["ink"]
    # extra detail sentences that are not the brief
    extras = [s for s in sens if s not in (brief_p, lede)][:2]
    for extra in extras:
        case["details"].append({"label": source_kind, "title": "On the page", "text": extra})
    return case


def main():
    used = {"Kissee", "Doorstep", "APEX", "Peak", "MedReps", "DrinkFre", "Threads"}
    skipped = ["Custom Fit Coverage stays off this site. A DPA Branding-only credit conflicts with the Tribe Maker chrome. See the question above."]
    for slug, reason in SKIP_TEXT.items():
        skipped.append(f"- **{slug}** — {reason}")
    targets = []
    facts = {}
    number = 8
    planned = []
    for slug in ORDER:
        if slug in SKIP_TEXT:
            continue
        try:
            fact = load_fact(slug)
        except Exception as error:
            skipped.append(f"- **{slug}** — Could not read a review host or live site ({error}).")
            continue
        if not fact.get("title") and not fact.get("h1"):
            skipped.append(f"- **{slug}** — The page that answered had no title or heading.")
            continue
        facts[slug] = fact
        targets.append((slug, fact["review"]))
        planned.append((slug, number))
        number += 1
    print(f"shooting {len(targets)} pages")
    dims = asyncio.run(shoot(targets))
    cases = []
    projects = json.loads((ROOT / "projects.json").read_text())
    existing = {item["slug"] for item in projects["projects"]}
    for slug, num in planned:
        if slug not in dims:
            skipped.append(f"- **{slug}** — Screenshot failed, and the page was not added.")
            continue
        case = build_case(slug, num, facts[slug], dims[slug], used)
        cases.append(case)
        if slug in existing:
            continue
        desk_w, desk_h = dims[slug]["desktop"]
        phone_w, phone_h = dims[slug]["phone"]
        projects["projects"].append({
            "number": case["number"],
            "slug": slug,
            "shortName": case["shortName"],
            "client": case["client"],
            "category": case["category"],
            "headline": case["headline"],
            "url": case["url"],
            "pending": False,
            "images": {
                "desktop": {
                    "webp": f"assets/shots/{slug}-desktop.webp",
                    "fallback": f"assets/shots/{slug}-desktop.jpg",
                    "width": desk_w,
                    "height": desk_h,
                    "alt": case["shots"]["desktop_alt"],
                },
                "phone": {
                    "webp": f"assets/shots/{slug}-phone.webp",
                    "fallback": f"assets/shots/{slug}-phone.jpg",
                    "width": phone_w,
                    "height": phone_h,
                    "alt": case["shots"]["phone_alt"],
                },
                "blur": f"assets/shots/{slug}-blur.webp",
            },
        })
        print(f"{case['number']} {slug}: {case['h1'][:70]}")
    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    # JSON cannot rely on tuples; shots already lists
    (data / "more-cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    (data / "skipped.md").write_text("\n".join(skipped) + "\n", encoding="utf-8")
    (ROOT / "projects.json").write_text(json.dumps(projects, indent=2) + "\n", encoding="utf-8")
    print("cases", len(cases), "skipped lines", len(skipped))


if __name__ == "__main__":
    main()
