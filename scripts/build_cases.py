#!/usr/bin/env python3
"""Write work/{slug}/index.html and content-gaps.md from sourced case data.

Copy in CASES is taken from the live site, a review prototype, or this repo's
project list. Missing proof stays a gap block. Do not add metrics or quotes here.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "3 Nov 2026"

GAPS_ONLY = """# Content gaps

Logged {checked}. Case pages use the live site, a review prototype when one answered, and files already in this repo. Nothing here is a measured result, a quote, or a testimonial unless that wording is on the source.

## Question for Mike

Custom Fit Coverage (Marcelo Campon & Associates) has a prototype at https://customfitcoverage.clientreview.co. It is not in the #work grid, and this repo does not name it. The rule for that client is a DPA Branding credit and no Yavin or Tribe Maker mention. This work site carries The Tribe Maker in the header, footer, and title, so a page here would break that rule. No page was built.

Should Custom Fit Coverage be on tribemakerwork.clientreview.co at all? If it should, where does a DPA Branding-only credit go so the Tribe Maker chrome does not apply? The prototype HTML fetched on {checked} does not contain the strings DPA, Yavin, or Tribe.

## Skipped

{skipped}

## Pages

{pages}
""".format(checked=CHECKED, pages="{pages}", skipped="{skipped}")


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def gap(label, text, kind=""):
    cls = "gap-block"
    if kind == "color":
        cls += " gap-on-color"
    elif kind == "dark":
        cls += " gap-on-dark"
    return (
        f'<div class="{cls}" role="note">'
        f'<p class="gap-label">{esc(label)}</p>'
        f"<p>{esc(text)}</p></div>"
    )


def picture(shot, alt):
    webp = esc(shot["webp"])
    fallback = esc(shot["fallback"])
    return (
        "<picture>"
        f'<source type="image/webp" srcset="{webp}">'
        f'<img src="{fallback}" alt="{esc(alt)}" width="{shot["width"]}" height="{shot["height"]}">'
        "</picture>"
    )


def swatches(items):
    if not items:
        return gap(
            "Color pending — content needed",
            "No named color tokens were found in a stylesheet this page could read.",
        )
    cards = []
    for item in items:
        line = " is-line" if item.get("line") else ""
        cards.append(
            "<li class=\"swatch{line}\" style=\"background:{bg};color:{fg}\">"
            "<p class=\"role\">{role}</p>"
            "<p><span class=\"token\">{token}</span><span class=\"hex\">{hex}</span></p>"
            "</li>".format(
                line=line,
                bg=esc(item["hex"]),
                fg=esc(item["fg"]),
                role=esc(item["role"]),
                token=esc(item["token"]),
                hex=esc(item["hex"]),
            )
        )
    return '<ul class="cs-palette">{}</ul>'.format("".join(cards))


def fonts_block(fonts):
    if not fonts:
        return gap(
            "Type pending — content needed",
            "No font family was named in a stylesheet this page could read.",
        )
    blocks = []
    for font in fonts:
        family = esc(font["css"])
        blocks.append(
            "<div>"
            f'<p class="specimen" style="font-family:{family}">Aa Bb</p>'
            f'<p class="specimen-alpha" style="font-family:{family}">'
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ · abcdefghijklmnopqrstuvwxyz · 0123456789</p>"
            f'<p class="specimen-note">{esc(font["note"])}</p>'
            "</div>"
        )
    return "".join(blocks)


def logo_block(case):
    logo = case.get("logo")
    plate = esc(case.get("logo_plate", "#fffcf7"))
    ink = esc(case.get("logo_ink", "#131419"))
    if not logo:
        inner = gap(
            "Logo pending — content needed",
            "No logo file was found on the live site or a review prototype. A wordmark was not drawn for this page.",
        )
        note = ""
    else:
        inner = (
            f'<img src="{esc(logo["src"])}" alt="{esc(logo["alt"])}" '
            f'width="{logo["width"]}" height="{logo["height"]}">'
        )
        note = f'<p>{esc(logo["note"])}</p>'
    return (
        f'<div class="cs-logo-card" style="background:{plate};color:{ink}">'
        '<p class="cs-label">Logo</p>'
        f"{inner}{note}</div>"
    )


def header():
    return """<a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="grid header-grid">
      <a class="brand" href="https://thetribemaker.com">
        <img src="../../assets/logo.svg" alt="" width="36" height="36">
        <span>The Tribe Maker</span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="../../#work" aria-current="page">Work</a>
        <a href="../../#process">Process</a>
        <a href="../../#contact">Contact</a>
      </nav>
    </div>
  </header>"""


def footer():
    return """<footer class="site-footer">
    <div class="grid footer-grid">
      <a class="brand brand-foot" href="https://thetribemaker.com">
        <img src="../../assets/logo.svg" alt="" width="28" height="28">
        <span>The Tribe Maker</span>
      </a>
      <p class="fine">A work-page prototype. Live sites and review prototypes. No added results, quotes, or testimonials.</p>
      <p class="fine"><a href="https://thetribemaker.com">thetribemaker.com</a></p>
    </div>
  </footer>"""


def render(case, nxt):
    shots = case["shots"]
    desktop = picture(
        {
            "webp": f"../../assets/shots/{case['slug']}-desktop.webp",
            "fallback": f"../../assets/shots/{case['slug']}-desktop.jpg",
            "width": shots["desktop"][0],
            "height": shots["desktop"][1],
        },
        shots["desktop_alt"],
    )
    phone = picture(
        {
            "webp": f"../../assets/shots/{case['slug']}-phone.webp",
            "fallback": f"../../assets/shots/{case['slug']}-phone.jpg",
            "width": shots["phone"][0],
            "height": shots["phone"][1],
        },
        shots["phone_alt"],
    )
    cited = ""
    if case.get("cited"):
        cited = (
            '<p class="source-line"><span>Line on the live homepage</span>'
            f'{esc(case["cited"])}</p>'
        )
    note = ""
    if case.get("note"):
        note = f'<div class="note-block"><p>{esc(case["note"])}</p></div>'
    details = []
    for item in case["details"]:
        details.append(
            "<li class=\"detail-card\">"
            f'<p class="eyebrow">{esc(item["label"])}</p>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<p>{esc(item["text"])}</p></li>'
        )
    sources = []
    for src in case["sources"]:
        if src.get("href"):
            sources.append(
                f'<li><a href="{esc(src["href"])}">{esc(src["text"])}</a></li>'
            )
        else:
            sources.append(f'<li>{esc(src["text"])}</li>')
    venture = ""
    if case.get("venture"):
        venture = f'<p class="venture">{esc(case["venture"])}</p>'
    style = (
        f'--brief:{case["brief"]};--brief-ink:{case["brief_ink"]};'
        f'--brief-kicker:{case["brief_kicker"]};--band:{case["band"]};'
        f'--band-ink:{case["band_ink"]}'
    )
    title = esc(case["title"])
    desc = esc(case["description"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://tribemakerwork.clientreview.co/work/{case['slug']}/">
  <meta name="theme-color" content="#faf6ee">
  <link rel="icon" href="../../assets/icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{esc(case["fonts_href"])}" rel="stylesheet">
  <link rel="stylesheet" href="../../css/styles.css">
  <link rel="stylesheet" href="../../css/case.css">
</head>
<body>
  {header()}
  <main id="main">
    <article class="case" style="{style}">
      <header class="cs-cover">
        <div class="cs-wrap">
          <div class="cs-cover-nav">
            <p><a href="../../#work">Selected Work</a> / Case Study № {esc(case["number"])}</p>
            <p>{esc(case["category"])}</p>
          </div>
          <div class="cs-cover-grid">
            <div>
              <p class="cs-kicker"><span></span>{esc(case["kicker"])}</p>
              <h1>{esc(case["h1"])}</h1>
            </div>
            <p class="cs-lede">{esc(case["lede"])}</p>
          </div>
          <dl class="cs-meta">
            <div><dt>Client</dt><dd>{esc(case["client"])}</dd></div>
            <div><dt>Industry</dt><dd>{esc(case["industry"])}</dd></div>
            <div><dt>Scope</dt><dd>{esc(case["scope"])}</dd></div>
            <div><dt>Year</dt><dd>{gap("Year pending — content needed", case["year_gap"])}</dd></div>
          </dl>
          <div class="cs-actions">
            <a class="visit" href="{esc(case["url"])}" target="_blank" rel="noopener noreferrer">Visit site</a>
          </div>
        </div>
      </header>

      <section class="cs-brief" id="brief" aria-labelledby="brief-title">
        <div class="cs-wrap">
          <div class="browser">
            <div class="browser-bar">
              <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
              <span class="browser-url">{esc(case["host"])}</span>
            </div>
            {desktop}
          </div>
          <div class="cs-brief-split">
            <div>
              <p class="cs-kicker"><span></span>The Brief</p>
              <h2 id="brief-title">{esc(case["brief_h"])}</h2>
            </div>
            <div class="cs-brief-copy">
              <p>{esc(case["brief_p"])}</p>
              {cited}
              {note}
            </div>
          </div>
        </div>
      </section>

      <section class="cs-identity" id="identity" aria-labelledby="identity-title">
        <div class="cs-wrap">
          <div class="cs-intro">
            <div>
              <p class="cs-kicker"><span></span>02 — Identity</p>
              <h2 id="identity-title">Tokens from the stylesheet</h2>
            </div>
            <p>{esc(case["identity"])}</p>
          </div>
          <p class="cs-label">Color</p>
          {swatches(case["colors"])}
          <div class="cs-type-logo">
            <div class="cs-type-card">
              <p class="cs-label">Type</p>
              {fonts_block(case["fonts"])}
            </div>
            {logo_block(case)}
          </div>
        </div>
      </section>

      <section class="cs-mobile" id="mobile" aria-labelledby="mobile-title">
        <div class="cs-wrap cs-2col">
          <div class="cs-phones">
            <figure class="phone">
              <div class="phone-screen">{phone}</div>
              <figcaption>{esc(shots["phone_alt"])}</figcaption>
            </figure>
            {gap("Screenshot pending — content needed", "A second mobile screen was not in the prototype files or this repo. The Hive study shows two phones. This page has the one homepage capture stored for the work grid.", "color")}
          </div>
          <div>
            <p class="cs-kicker"><span></span>03 — Mobile</p>
            <h2 id="mobile-title">{esc(case["mobile_h"])}</h2>
            <p>{esc(case["mobile_p"])}</p>
            <div style="margin-top:1.25rem">
              {gap("Results pending — content needed", case["results_gap"], "color")}
            </div>
          </div>
        </div>
      </section>

      <section class="cs-detail" id="detail" aria-labelledby="detail-title">
        <div class="cs-wrap">
          <div class="cs-intro">
            <div>
              <p class="cs-kicker"><span></span>04 — In Detail</p>
              <h2 id="detail-title">Lines from the live homepage</h2>
            </div>
            {gap("Screenshot pending — content needed", "Section crops were not in the source files. The three notes below are homepage lines, not separate screenshots.")}
          </div>
          <ul class="cs-3col">{"".join(details)}</ul>
        </div>
      </section>

      <section class="cs-quote" id="quote" aria-label="Quote">
        <div class="cs-wrap">
          {gap("Quote pending — content needed", "No named quote or testimonial was copied. Homepage review counts, where the site prints them, stay in the brief as the site's own line.", "dark")}
        </div>
      </section>

      <section class="cs-scroll" id="scroll" aria-labelledby="scroll-title">
        <div class="cs-wrap">
          <div class="cs-intro">
            <div>
              <p class="cs-kicker"><span></span>05 — The long scroll</p>
              <h2 id="scroll-title">Homepage viewport</h2>
            </div>
            <div>
              <p>The image is the homepage capture already in this repo. It is the top of the page, not a stitched full-page scroll.</p>
              <div style="margin-top:1rem">
                {gap("Screenshot pending — content needed", "A full-page scroll capture is not in the source files.")}
              </div>
            </div>
          </div>
          <figure>
            {desktop}
            <figcaption>{esc(shots["desktop_alt"])} Viewport only.</figcaption>
          </figure>
        </div>
      </section>

      <footer class="cs-end">
        <div class="cs-wrap cs-end-grid">
          <div>
            <h2>Credits</h2>
            {venture}
            {gap("Credits pending — content needed", "Design, writing, and build roles are not split out in a project guide or scope file this account could read.")}
          </div>
          <div>
            <h2>Sources checked</h2>
            <ul class="cs-sources">{"".join(sources)}</ul>
          </div>
        </div>
        <div class="cs-wrap cs-next">
          <p class="cs-label">Up next</p>
          <a href="../{esc(nxt["slug"])}/">Case Study № {esc(nxt["number"])} · {esc(nxt["client"])}</a>
        </div>
      </footer>
    </article>
  </main>
  {footer()}
</body>
</html>
"""


def shot(slug, desktop, phone, desktop_alt, phone_alt):
    return {
        "desktop": desktop,
        "phone": phone,
        "desktop_alt": desktop_alt,
        "phone_alt": phone_alt,
    }


BASE_FONTS = "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,560;1,9..144,500&family=Sora:wght@400;500;600"

YEAR = "No project year is written in the project list, a project guide, or a scope file this account could read."
RESULTS = (
    "No load time or before-and-after figure is in a project guide or scope file. "
    "Numbers that appear above are lines printed on the live homepage, not a measured outcome of this page."
)
REPO = "Yavin-Digital prototype repo was not readable from this account (HTTP 404 for the slug names that were tried)."

CASES = [
    {
        "slug": "kissee",
        "number": "01",
        "client": "Kissee Inspections",
        "title": "Kissee Inspections — Case Study | The Tribe Maker",
        "description": "Case study for Kissee Inspection Services. Copy is from the live site and the review prototype. No added results or testimonials.",
        "category": "home inspections · custom website",
        "kicker": "Kissee Inspection Services · kisseeinspections.com",
        "h1": "DFW's Most Trusted Home Inspector",
        "lede": "Get a thorough property inspection in Frisco, TX, with Kissee Inspection Services. We provide peace of mind for your home or business.",
        "industry": "Home inspections",
        "scope": "Custom website",
        "year_gap": YEAR,
        "url": "https://kisseeinspections.com",
        "host": "kisseeinspections.com",
        "brief": "#002ebe",
        "brief_ink": "#faf6ee",
        "brief_kicker": "#FECB38",
        "band": "#FECB38",
        "band_ink": "#0f1631",
        "brief_h": "What Sets Kissee Inspections Apart",
        "brief_p": "Your home is your biggest investment. Kissee Inspection Services gives you the clarity, confidence, and detailed reporting you need — with same-day digital reports and 10,000+ inspections of experience behind every walk-through.",
        "cited": "4.9 Google · 800+ Reviews · CMI Certified Master Inspector · Est. 2009 · TREC Licensed & Insured",
        "identity": "The prototype stylesheet css/style.css labels these as house brand tokens. The same hex values are in the live site CSS. A written identity story was not in a project guide this account could read.",
        "colors": [
            {"role": "Primary", "token": "--brand", "hex": "#002ebe", "fg": "#faf6ee"},
            {"role": "Mid", "token": "--brand-mid", "hex": "#243e90", "fg": "#faf6ee"},
            {"role": "Dark", "token": "--brand-dark", "hex": "#1a1f6e", "fg": "#faf6ee"},
            {"role": "Accent", "token": "--accent", "hex": "#FECB38", "fg": "#0f1631"},
            {"role": "Ink", "token": "--ink", "hex": "#0f1631", "fg": "#faf6ee"},
            {"role": "Surface", "token": "--paper", "hex": "#f5f7fc", "fg": "#0f1631", "line": True},
        ],
        "fonts_href": BASE_FONTS + "&family=Open+Sans:wght@400;600&family=Poppins:wght@600;700&display=swap",
        "fonts": [
            {"css": "Poppins, sans-serif", "note": "Poppins · prototype loads weights 600–800"},
            {"css": "Open Sans, sans-serif", "note": "Open Sans · prototype loads weights 400–600"},
        ],
        "logo": {
            "src": "../../assets/cases/kissee/logo.png",
            "alt": "Kissee Inspection Services",
            "width": 1000,
            "height": 660,
            "note": "File img/logo.png from the review prototype. Shown smaller than the file.",
        },
        "logo_plate": "#f5f7fc",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page. The review prototype says no speed score is claimed.",
        "results_gap": RESULTS + " The prototype banner says numbers on its performance panel come from that browser visit only.",
        "details": [
            {
                "label": "Homepage",
                "title": "Same-day digital report",
                "text": "Your full digital report — with color photos and prioritized findings — is delivered the same day. No waiting days while the market moves.",
            },
            {
                "label": "Menu",
                "title": "Services named on the site",
                "text": "Homebuyer Inspection, Pre-Listing Inspection, New Construction, Home Warranty Inspection, Commercial Inspection, Infrared Thermal Imaging, Pool & Spa, Termite / WDI, Sprinkler Inspection, Septic & Well, Sewer Scope, 4-Point Inspection, Elevation Measurements.",
            },
            {
                "label": "Header",
                "title": "Where the site says it works",
                "text": "Serving All DFW and surrounding areas, including Frisco, Plano, North Dallas, Denton & Aubrey. Office hours on the page: M-F 8:00 am – 7:00 pm; Sat 9:00 am – 5:00 pm.",
            },
        ],
        "shots": shot(
            "kissee",
            (1440, 900),
            (780, 1688),
            "Homepage of Kissee Inspections, a DFW home inspection site",
            "Kissee Inspections homepage on a phone",
        ),
        "sources": [
            {"href": "https://kisseeinspections.com", "text": "Live site, fetched 3 Nov 2026"},
            {"href": "https://kisseeinspections.clientreview.co", "text": "Review prototype"},
            {"text": REPO + " Tried kissee-prototype and kisseeinspections-prototype."},
            {"text": "Screenshots already in assets/shots/. Logo from the prototype img/logo.png."},
        ],
        "log": [
            "Yavin-Digital/kissee-prototype and kisseeinspections-prototype returned HTTP 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "Homepage prints 4.9 Google, 800+ reviews, 10,000+ inspections, and Est. 2009. Those lines are quoted. They are not an independent measurement.",
            "Prototype banner: no speed score or projected improvement is claimed.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "doorstep",
        "number": "02",
        "client": "Doorstep Local",
        "title": "Doorstep Local — Case Study | The Tribe Maker",
        "description": "Case study for Doorstep Local. Copy follows the live site. The review prototype uses different offer text, which is noted and not mixed in.",
        "category": "neighborhood directories · custom website",
        "kicker": "Doorstep Local · doorsteplocal.com",
        "h1": "Get found by the neighbors who are already looking for you.",
        "lede": "One neighborhood at a time. A real profile, in front of the people on your street — not a listing lost on the whole internet.",
        "industry": "Neighborhood directories",
        "scope": "Custom website",
        "year_gap": YEAR,
        "url": "https://doorsteplocal.com",
        "host": "doorsteplocal.com",
        "brief": "#064180",
        "brief_ink": "#faf6ee",
        "brief_kicker": "#ffffff",
        "band": "#005f13",
        "band_ink": "#ffffff",
        "brief_h": "You're invisible where it matters most.",
        "brief_p": "The places you show up today were built for search engines and shareholders, not for your street.",
        "cited": "90 days free for founding members. The first 20 spots in each neighborhood are open. Your 90 free days start on launch day. No credit card. No spam.",
        "note": "The review prototype at doorsteplocal.clientreview.co uses a different headline and says 90 days free for the first 30 founders, then $29/mo. This page follows the live site linked from the work grid.",
        "identity": "Swatches are the live site's data-theme=light tokens. The logo file logo-dark.svg uses #0f172a and #0ea5e9. The prototype stylesheet records a different primary, #0284c7. Those are separate sources and are not combined into one palette.",
        "colors": [
            {"role": "Primary", "token": "--color-primary", "hex": "#005f13", "fg": "#ffffff"},
            {"role": "Secondary", "token": "--color-secondary", "hex": "#064180", "fg": "#edf2f9"},
            {"role": "Accent", "token": "--color-accent", "hex": "#31aa40", "fg": "#ffffff"},
            {"role": "Surface", "token": "--color-base-100", "hex": "#ffffff", "fg": "#051223", "line": True},
            {"role": "Text", "token": "--color-base-content", "hex": "#051223", "fg": "#ffffff"},
        ],
        "fonts_href": BASE_FONTS + "&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "fonts": [
            {"css": '"Plus Jakarta Sans", sans-serif', "note": "Plus Jakarta Sans · named on the live page and in the prototype font link"},
        ],
        "logo": {
            "src": "../../assets/cases/doorstep/logo.svg",
            "alt": "Doorstep Local",
            "width": 226,
            "height": 40,
            "note": "File logo-dark.svg from the live site.",
        },
        "logo_plate": "#ffffff",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page.",
        "results_gap": RESULTS,
        "details": [
            {
                "label": "Homepage",
                "title": "Your listing is a ghost town",
                "text": "A name and a phone number. Nothing that gives a neighbor a reason to choose you.",
            },
            {
                "label": "Homepage",
                "title": "Built for the whole internet",
                "text": "You line up next to every business in the country. The people on your street never see you.",
            },
            {
                "label": "Homepage",
                "title": "Easy to scroll past",
                "text": "A tiny logo and a generic profile. Neighbors move on before they ever call.",
            },
        ],
        "shots": shot(
            "doorstep",
            (1440, 900),
            (780, 1688),
            "Homepage of Doorstep Local, a neighborhood directory site",
            "Doorstep Local homepage on a phone",
        ),
        "sources": [
            {"href": "https://doorsteplocal.com", "text": "Live site, fetched 3 Nov 2026"},
            {"href": "https://doorsteplocal.clientreview.co", "text": "Review prototype (different headline and offer)"},
            {"text": REPO + " Tried doorstep-prototype and doorsteplocal-prototype."},
            {"text": "Screenshots already in assets/shots/. Logo from the live logo-dark.svg."},
        ],
        "log": [
            "Prototype headline and founding-spot offer differ from the live site (30 founders and $29/mo on the prototype; 20 spots and no $29 line on the live homepage). The page does not merge them.",
            "Live light-theme primary is #005f13. Logo SVG fills are #0f172a and #0ea5e9. Prototype primary is #0284c7.",
            "Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "apex",
        "number": "03",
        "client": "APEX Peptide IQ",
        "title": "APEX Peptide IQ — Case Study | The Tribe Maker",
        "description": "Case study for APEX Peptide IQ. Copy and colors are from the live site. No review prototype hostname answered.",
        "category": "research reference · digital product",
        "kicker": "APEX Peptide IQ · apexpeptideiq.com",
        "h1": "Build a peptide protocol or stack in 60 seconds.",
        "lede": "Stop guessing doses from forum threads and PDFs. APEX Peptide IQ is the research reference for the whole workflow — lookup, syringe math, cycle planning, and export — in one pass.",
        "industry": "Research reference",
        "scope": "Digital product",
        "year_gap": YEAR,
        "url": "https://apexpeptideiq.com",
        "host": "apexpeptideiq.com",
        "brief": "#03112b",
        "brief_ink": "#ffffff",
        "brief_kicker": "#a87f2e",
        "band": "#a87f2e",
        "band_ink": "#03112b",
        "brief_h": "From scattered notes to one clinical instrument",
        "brief_p": "If you work with peptides, you already know the ritual: a folder of PDFs, a notes app of half-saved doses, a reconstitution spreadsheet, and a forum thread arguing about units. Every protocol starts with tab-switching.",
        "cited": "Get 12-Month Access — $199. One-time payment · $199 · 12 months of full access.",
        "identity": "Swatches are the live data-theme=apex tokens. The file icon.png on the live site is a blue mark; it is not recolored to the gold accent token.",
        "colors": [
            {"role": "Primary", "token": "--color-primary", "hex": "#03112b", "fg": "#ffffff"},
            {"role": "Secondary", "token": "--color-secondary", "hex": "#0a1b36", "fg": "#ffffff"},
            {"role": "Accent", "token": "--color-accent", "hex": "#a87f2e", "fg": "#03112b"},
            {"role": "Surface", "token": "--color-base-100", "hex": "#ffffff", "fg": "#1a1a1a", "line": True},
            {"role": "Raised", "token": "--color-base-200", "hex": "#f4f5f7", "fg": "#1a1a1a", "line": True},
            {"role": "Text", "token": "--color-base-content", "hex": "#1a1a1a", "fg": "#ffffff"},
        ],
        "fonts_href": BASE_FONTS + "&family=Inter:wght@400;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap",
        "fonts": [
            {"css": "Newsreader, Georgia, serif", "note": "Newsreader · --font-display on the live stylesheet"},
            {"css": "Inter, sans-serif", "note": "Inter · --font-inter on the live stylesheet. JetBrains Mono is also named."},
        ],
        "logo": {
            "src": "../../assets/cases/apex/icon.png",
            "alt": "APEX mark from the live site file icon.png",
            "width": 1254,
            "height": 1254,
            "note": "Live file icon.png, 1254×1254. Shown smaller than the file. No separate wordmark file was found.",
        },
        "logo_plate": "#03112b",
        "logo_ink": "#ffffff",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page.",
        "results_gap": RESULTS + " The homepage also labels 66 peptides profiled, 20+ therapeutic categories, 11 clinical protocols, and 12 mo full access. Those labels are not repeated here as results.",
        "details": [
            {
                "label": "Homepage",
                "title": "Profiles",
                "text": "66 peptide profiles in one format — mechanism, cycle notes, and storage.",
            },
            {
                "label": "Homepage",
                "title": "Math",
                "text": "Reconstitution math and dosing tiers, without a spreadsheet.",
            },
            {
                "label": "Homepage",
                "title": "Export",
                "text": "11 protocols, a stack view, and PDF export from the same selection.",
            },
        ],
        "shots": shot(
            "apex",
            (1440, 900),
            (780, 1688),
            "Homepage of APEX Peptide IQ, a peptide research reference",
            "APEX Peptide IQ homepage on a phone",
        ),
        "sources": [
            {"href": "https://apexpeptideiq.com", "text": "Live site, fetched 3 Nov 2026"},
            {"text": "No review host answered for apex, apexpeptide, or apexpeptideiq on clientreview.co (certificate hostname mismatch)."},
            {"text": REPO + " Tried apex-prototype, apexpeptide-prototype, and apexpeptideiq-prototype."},
            {"text": "Screenshots already in assets/shots/. Mark from the live icon.png."},
        ],
        "log": [
            "No standing prototype at apex.clientreview.co, apexpeptide.clientreview.co, or apexpeptideiq.clientreview.co.",
            "Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "Homepage price is $199 for 12 months. Count labels (66, 20+, 11, 12 mo) stay off the results grid.",
            "icon.png is blue; the theme accent is #a87f2e. Both are from the live site.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "peak",
        "number": "04",
        "client": "Peak Chain Peptides",
        "title": "Peak Chain Peptides — Case Study | The Tribe Maker",
        "description": "Case study for Peak Chain Peptides. Copy, colors, and the logo are from the live site. No review prototype hostname answered.",
        "category": "research peptides · custom website",
        "kicker": "Peak Chain Peptides · peakchainpeptides.com",
        "h1": "Peakchain",
        "lede": "Peptides are short chains of amino acids that act as biological signaling molecules, interacting with specific receptors, enzymes, and cellular pathways to regulate physiological processes. This platform supports researchers studying these mechanisms with access to research-grade compounds and peer-reviewed educational resources.",
        "industry": "Research peptides",
        "scope": "Custom website",
        "year_gap": YEAR,
        "url": "https://peakchainpeptides.com",
        "host": "peakchainpeptides.com",
        "brief": "#0048a0",
        "brief_ink": "#f8f8f8",
        "brief_kicker": "#ffffff",
        "band": "#62cddb",
        "band_ink": "#001529",
        "brief_h": "Built Bond by Bond",
        "brief_p": "A peptide is a short chain of amino acids — a precise molecular sequence carrying targeted biological instruction. Every compound we supply is synthesized to that exact standard: the right sequence, the right purity, the right result. All compounds are for in vitro research use only.",
        "cited": "For research purposes only",
        "identity": "Swatches are the light set in the live stylesheet whose primary is #0048a0, matching the blue Product Catalog button in the stored homepage shot. A darker set is also in that file and is not shown.",
        "colors": [
            {"role": "Primary", "token": "--color-primary", "hex": "#0048a0", "fg": "#f8f8f8"},
            {"role": "Secondary", "token": "--color-secondary", "hex": "#008eb0", "fg": "#f8f8f8"},
            {"role": "Accent", "token": "--color-accent", "hex": "#62cddb", "fg": "#001529"},
            {"role": "Surface", "token": "--color-base-100", "hex": "#ffffff", "fg": "#001529", "line": True},
            {"role": "Text", "token": "--color-base-content", "hex": "#001529", "fg": "#ffffff"},
        ],
        "fonts_href": BASE_FONTS + "&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@400;500&display=swap",
        "fonts": [
            {"css": '"IBM Plex Serif", Georgia, serif', "note": "IBM Plex Serif · named in the live stylesheet"},
            {"css": '"IBM Plex Sans", sans-serif', "note": "IBM Plex Sans · named in the live stylesheet. IBM Plex Mono is also named."},
        ],
        "logo": {
            "src": "../../assets/cases/peak/logo.png",
            "alt": "Peakchain",
            "width": 931,
            "height": 536,
            "note": "Live file logo.png, 931×536. Shown smaller than the file. The work grid name is Peak Chain Peptides. The homepage heading is Peakchain.",
        },
        "logo_plate": "#ffffff",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page.",
        "results_gap": RESULTS,
        "details": [
            {
                "label": "Homepage",
                "title": "Research purposes only",
                "text": "For research purposes only.",
            },
            {
                "label": "Homepage",
                "title": "In vitro",
                "text": "All compounds are for in vitro research use only.",
            },
            {
                "label": "Homepage",
                "title": "Science and mission",
                "text": "Research integrity and documentation quality are the same obligation.",
            },
        ],
        "shots": shot(
            "peak",
            (1440, 900),
            (780, 1688),
            "Homepage of Peak Chain Peptides, a research compound catalog",
            "Peak Chain Peptides homepage on a phone",
        ),
        "sources": [
            {"href": "https://peakchainpeptides.com", "text": "Live site, fetched 3 Nov 2026"},
            {"text": "No review host answered for peak, peakchain, or peakchainpeptides on clientreview.co."},
            {"text": REPO + " Tried peak-prototype, peakchain-prototype, and peakchainpeptides-prototype."},
            {"text": "Screenshots already in assets/shots/. Logo from the live logo.png."},
        ],
        "log": [
            "No standing prototype hostname. Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "A published Tribe Maker page exists at https://thetribemaker.com/work/peak-chain-peptides. Its figures were not copied onto this page.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "medreps",
        "number": "05",
        "client": "MedReps Medical Solutions",
        "title": "MedReps Medical Solutions — Case Study | The Tribe Maker",
        "description": "Case study for MedReps Medical Solutions. The work grid labels this project MedRepsRx. Copy and colors are from the live site.",
        "category": "regenerative health · custom website",
        "kicker": "MedReps Medical Solutions · medrepsrx.com",
        "h1": "Prescribed to heal, not to manage.",
        "lede": "Three regenerative product lines. Every therapy physician-partnered. Every protocol precision-matched to the person receiving it. Nothing off the shelf.",
        "industry": "Regenerative health",
        "scope": "Custom website",
        "year_gap": YEAR,
        "url": "https://medrepsrx.com",
        "host": "medrepsrx.com",
        "brief": "#0f1b33",
        "brief_ink": "#faf6ee",
        "brief_kicker": "#d9bd82",
        "band": "#d9bd82",
        "band_ink": "#1a2b4a",
        "brief_h": "Not anti-medicine. Anti-mass-market.",
        "brief_p": "MedReps was built on a conviction: patients deserve treatments that help them heal — not medications designed to manage a symptom for life while creating new ones.",
        "note": "The work grid labels this project MedRepsRx. The live title is MedReps Medical Solutions.",
        "identity": "Swatches are the :root tokens on the live stylesheet (--navy, --gold, --cream, --ink). The page data-theme attribute is light. DaisyUI default purple and pink values appear earlier in the file and are not the :root set shown here.",
        "colors": [
            {"role": "Navy", "token": "--navy", "hex": "#1a2b4a", "fg": "#faf6ee"},
            {"role": "Navy deep", "token": "--navy-deep", "hex": "#0f1b33", "fg": "#faf6ee"},
            {"role": "Gold", "token": "--gold", "hex": "#c9a961", "fg": "#1a2b4a"},
            {"role": "Gold soft", "token": "--gold-soft", "hex": "#d9bd82", "fg": "#1a2b4a"},
            {"role": "Emerald", "token": "--emerald", "hex": "#2f7f5b", "fg": "#faf6ee"},
            {"role": "Cream", "token": "--cream", "hex": "#faf6ee", "fg": "#141414", "line": True},
            {"role": "Ink", "token": "--ink", "hex": "#141414", "fg": "#faf6ee"},
        ],
        "fonts_href": BASE_FONTS + "&family=Inter+Tight:wght@400;500;600&display=swap",
        "fonts": [
            {"css": "Fraunces, Georgia, serif", "note": "Fraunces · --serif on the live stylesheet"},
            {"css": '"Inter Tight", sans-serif', "note": "Inter Tight · --sans on the live stylesheet"},
        ],
        "logo_plate": "#0f1b33",
        "logo_ink": "#faf6ee",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page.",
        "results_gap": RESULTS + " The homepage also prints product figures, including 20 billion exosomes per mL. They are not repeated here as results.",
        "details": [
            {
                "label": "Homepage",
                "title": "MedReps Peps",
                "text": "A curated Professional Use Only peptide catalog — not research-chemical grade — accessible only after a health intake and medical clearance by a licensed provider.",
            },
            {
                "label": "Homepage",
                "title": "503a Pharmacy Network",
                "text": "MedReps providers gain access to one of the country's most extensive 503a peptide formularies through our vetted pharmacy network — physician-prescribed, patient-specific, compounded by licensed pharmacists, and reachable in all 50 states.",
            },
            {
                "label": "Homepage",
                "title": "Human MSC Stem Cell Exosomes",
                "text": "A physician-directed regenerative line sourced from whole human umbilical cord tissue in a native liquid formulation. Manufactured to ISO-5 cGMP standards for providers working in orthopedics, sports medicine, neurology, autoimmune, and aesthetics.",
            },
        ],
        "shots": shot(
            "medreps",
            (1440, 680),
            (780, 1560),
            "Homepage of MedRepsRx, the MedReps Medical Solutions site",
            "MedRepsRx homepage on a phone",
        ),
        "sources": [
            {"href": "https://medrepsrx.com", "text": "Live site, fetched 3 Nov 2026"},
            {"text": "No review host answered for medreps or medrepsrx on clientreview.co."},
            {"text": REPO + " Tried medreps-prototype and medrepsrx-prototype."},
            {"text": "Screenshots already in assets/shots/. No logo file found at logo.svg or logo.png."},
        ],
        "log": [
            "No standing prototype hostname. Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "No logo file found. The header in the screenshot is set in type.",
            "Homepage product figures (including 20 billion exosomes per mL and 185+ protein genes) were not placed in the results grid.",
            "Grid name MedRepsRx and live name MedReps Medical Solutions are both shown.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "drinkfre",
        "number": "06",
        "client": "DrinkFrē",
        "title": "DrinkFrē — Case Study | The Tribe Maker",
        "description": "Case study for DrinkFrē. The work grid spells the name DrinkFre. Copy, colors, and the logo are from the live site.",
        "category": "product website · holographic card",
        "kicker": "DrinkFrē · drinkfre.com",
        "h1": "Most pours are rushed. This one is different.",
        "lede": "DrinkFrē is a reusable holographic card that turns the first few minutes of a pour into a deliberate ritual. Place your glass on it. Wait. Then actually taste what's in it.",
        "industry": "Product website",
        "scope": "Holographic card",
        "year_gap": YEAR,
        "url": "https://drinkfre.com",
        "host": "drinkfre.com",
        "brief": "#0e6e72",
        "brief_ink": "#f8f8f8",
        "brief_kicker": "#d39562",
        "band": "#d39562",
        "band_ink": "#180501",
        "brief_h": "Place. Pause. Sip.",
        "brief_p": "The programmed holographic element never touches your beverage. The experience begins beneath the glass and fits naturally into the first few minutes of a pour.",
        "cited": "For responsible adults. DrinkFrē does not reduce impairment or make alcohol consumption safe.",
        "note": "The work grid spells the name DrinkFre. The live title and logo use DrinkFrē.",
        "identity": "Swatches are the color tokens in the live stylesheet. --df-font-body is Sora and --df-font-serif is Fraunces. Geist is also named in that file.",
        "colors": [
            {"role": "Primary", "token": "--color-primary", "hex": "#0e6e72", "fg": "#f8f8f8"},
            {"role": "Secondary", "token": "--color-secondary", "hex": "#d39562", "fg": "#180501"},
            {"role": "Accent", "token": "--color-accent", "hex": "#d39a62", "fg": "#180501"},
            {"role": "Surface", "token": "--color-base-100", "hex": "#fff5ed", "fg": "#041419", "line": True},
            {"role": "Text", "token": "--color-base-content", "hex": "#041419", "fg": "#faf4ef"},
        ],
        "fonts_href": BASE_FONTS + "&family=Geist:wght@400;600&display=swap",
        "fonts": [
            {"css": "Fraunces, Georgia, serif", "note": "Fraunces · --df-font-serif"},
            {"css": "Sora, sans-serif", "note": "Sora · --df-font-body. Geist is also named in the stylesheet."},
        ],
        "logo": {
            "src": "../../assets/cases/drinkfre/logo.svg",
            "alt": "DrinkFrē",
            "width": 1200,
            "height": 300,
            "note": "Live file brand/drinkfre-logo-color.svg.",
        },
        "logo_plate": "#fff5ed",
        "mobile_h": "Mobile-first discovery",
        "mobile_p": "Those three words are a label on the live homepage, next to the product. The phone frame is the homepage screenshot stored with this work page.",
        "results_gap": RESULTS,
        "details": [
            {
                "label": "Homepage",
                "title": "Place",
                "text": "Set your wine or spirits glass directly over the holographic side of the card.",
            },
            {
                "label": "Homepage",
                "title": "Pause",
                "text": "Leave the glass in place for 3–5 minutes. Nothing is added to the beverage.",
            },
            {
                "label": "Homepage",
                "title": "Sip",
                "text": "Taste with intention and notice the experience for yourself. Results may vary.",
            },
        ],
        "shots": shot(
            "drinkfre",
            (1440, 900),
            (780, 1688),
            "Homepage of DrinkFrē, a holographic card product site",
            "DrinkFrē homepage on a phone",
        ),
        "sources": [
            {"href": "https://drinkfre.com", "text": "Live site, fetched 3 Nov 2026"},
            {"text": "No review host answered for drinkfre or drink-fre on clientreview.co."},
            {"text": REPO + " Tried drinkfre-prototype and drinkfre-card-prototype."},
            {"text": "Screenshots already in assets/shots/. Logo from the live brand SVG."},
        ],
        "log": [
            "No standing prototype hostname. Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "The homepage has a section titled What people say after the first pour. Individual quotes were not copied because a named, complete quotation was not pulled into the page.",
            "Grid spelling DrinkFre versus live DrinkFrē is noted on the page.",
            "No second phone screen. No full-page scroll. No role credits. No project year.",
        ],
    },
    {
        "slug": "threads",
        "number": "07",
        "client": "Texas Threads",
        "title": "Texas Threads — Case Study | The Tribe Maker",
        "description": "Case study for Texas Threads. The project list calls it a Tribe Maker venture. Copy and colors are from the live site.",
        "category": "texas apparel · custom shop",
        "kicker": "Texas Threads · weartexasthreads.com",
        "h1": "Wear the Texas Standard.",
        "lede": "Elevated Texas style. Built for where you're going.",
        "industry": "Texas apparel",
        "scope": "Custom shop",
        "year_gap": YEAR,
        "url": "https://weartexasthreads.com",
        "host": "weartexasthreads.com",
        "brief": "#0d0b09",
        "brief_ink": "#faf7f2",
        "brief_kicker": "#b85a36",
        "band": "#b85a36",
        "band_ink": "#ffffff",
        "brief_h": "We Don't Follow The Standard. We Set It.",
        "brief_p": "Not fast fashion. Not a brand chasing trends. Texas Threads is built for Texans who know exactly who they are — in the city, at the ranch, at the table, or anywhere in between. Quality that endures. Style that means something.",
        "cited": "Texas Owned & Operated. Complimentary Shipping on $75+. 30-Day Returns. Premium Quality Guaranteed.",
        "venture": "The project list on this work page calls Texas Threads a Tribe Maker venture.",
        "identity": "Swatches are the live [data-theme=texas] tokens. --font-display is Cormorant Garamond and --font-body is Plus Jakarta Sans.",
        "colors": [
            {"role": "Primary", "token": "--color-primary", "hex": "#0d0b09", "fg": "#faf7f2"},
            {"role": "Accent", "token": "--color-accent", "hex": "#b85a36", "fg": "#ffffff"},
            {"role": "Surface", "token": "--color-base-100", "hex": "#ffffff", "fg": "#0d0b09", "line": True},
            {"role": "Base 200", "token": "--color-base-200", "hex": "#f3ede3", "fg": "#0d0b09", "line": True},
            {"role": "Base 300", "token": "--color-base-300", "hex": "#e2d9cc", "fg": "#0d0b09"},
            {"role": "Warning", "token": "--color-warning", "hex": "#b08a52", "fg": "#0d0b09"},
        ],
        "fonts_href": BASE_FONTS + "&family=Cormorant+Garamond:wght@500;600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap",
        "fonts": [
            {"css": '"Cormorant Garamond", Georgia, serif', "note": "Cormorant Garamond · --font-display"},
            {"css": '"Plus Jakarta Sans", sans-serif', "note": "Plus Jakarta Sans · --font-body"},
        ],
        "logo_plate": "#f3ede3",
        "mobile_h": "Homepage on a phone",
        "mobile_p": "The phone frame is the homepage screenshot stored with this work page. The stored desktop shot is the homepage hero only.",
        "results_gap": RESULTS,
        "details": [
            {
                "label": "Banner",
                "title": "Shipping line",
                "text": "Complimentary Shipping on Orders $75+.",
            },
            {
                "label": "Header",
                "title": "Texas — Since Day One",
                "text": "Texas — Since Day One.",
            },
            {
                "label": "Homepage row",
                "title": "Four labels under the hero",
                "text": "Texas Owned & Operated. Complimentary Shipping on $75+. 30-Day Returns. Premium Quality Guaranteed.",
            },
        ],
        "shots": shot(
            "threads",
            (1440, 900),
            (780, 1688),
            "Homepage of Texas Threads, a Texas apparel shop",
            "Texas Threads homepage on a phone",
        ),
        "sources": [
            {"href": "https://weartexasthreads.com", "text": "Live site, fetched 3 Nov 2026"},
            {"text": "No review host answered for threads, texasthreads, or weartexasthreads on clientreview.co."},
            {"text": REPO + " Tried threads-prototype, texasthreads-prototype, and weartexasthreads-prototype."},
            {"text": "Screenshots already in assets/shots/. No logo.svg on the live host. Product photos were not used as a logo."},
        ],
        "log": [
            "No standing prototype hostname. Repo 404, so PROJECT_GUIDE.md and SCOPE.md were not read.",
            "No logo file found. Header wordmark is set in type on the live page.",
            "The only venture label in this repo is the project-list line, a Tribe Maker venture. Role credits beyond that are not documented.",
            "Homepage policy lines ($75 shipping, 30-day returns) are quoted, not independently checked.",
            "No named testimonial copied. No second phone screen. No full-page scroll. No project year.",
        ],
    },
]


def page_log(case):
    lines = [f"### {case['client']} — /work/{case['slug']}/", ""]
    for item in case["log"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main():
    cases = list(CASES)
    extra_path = ROOT / "data" / "more-cases.json"
    if extra_path.exists():
        import json
        extra = json.loads(extra_path.read_text(encoding="utf-8"))
        cases.extend(extra)
    for index, case in enumerate(cases):
        nxt = cases[(index + 1) % len(cases)]
        folder = ROOT / "work" / case["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        html = render(case, nxt)
        (folder / "index.html").write_text(html, encoding="utf-8")
        for needle in ("+62%", "Lighthouse", "Kelsey"):
            if needle in html:
                raise SystemExit(f"unexpected invented string {needle} in {case['slug']}")
    pages = "\n".join(page_log(case) for case in cases)
    skipped_path = ROOT / "data" / "skipped.md"
    skipped = skipped_path.read_text(encoding="utf-8") if skipped_path.exists() else "None.\n"
    (ROOT / "content-gaps.md").write_text(
        GAPS_ONLY.format(pages=pages, skipped=skipped),
        encoding="utf-8",
    )
    print(f"wrote {len(cases)} pages")


if __name__ == "__main__":
    main()
