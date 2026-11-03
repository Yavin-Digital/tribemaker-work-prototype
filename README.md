# Tribe Maker work page

A static prototype of The Tribe Maker work page. It lists live client sites in numbered, full-width sections. Copy stays with what each site actually is. There are no invented metrics, quotes, or testimonials.

The page is meant to be published with GitHub Pages from the `main` branch, root folder. `CNAME` sets the custom domain to `tribemakerwork.clientreview.co`. Turning the site on is a repository admin step: Settings → Pages → Deploy from a branch → `main` → `/ (root)`. The GitHub App token used for this prototype cannot create a Pages site (`pages: write` and `administration: write` are required).

## Run it locally

Any static server works. From this directory:

```bash
python3 -m http.server 4173
```

Open `http://127.0.0.1:4173`. `projects.json` is fetched by `js/work.js`, so opening `index.html` as a file will not load the sections.

## Adding a project

Sections are rendered from `projects.json`. Append one object to the `projects` array. Do not edit the HTML for a new case. DPA sites and client prototypes can be added the same way once they are approved for this page.

1. Capture the live homepage yourself. Save a desktop view and, if it helps the layout, a phone view.
2. Export an optimized WebP plus a JPG fallback for each view. Add a small blurred WebP for the section background.
3. Put the files in `assets/shots/`.
4. Add the object below. Set `number` to the two-digit position (`08`, `09`, …) and `slug` to a unique, URL-safe id.
5. If a site will not load, set `"pending": true` and omit `images`. The page shows a frame labeled “Screenshot pending”. Do not substitute a fake screenshot.

### Schema

`projects.json` is an object with one key, `projects`, whose value is an array. Each item:

| Field | Required | Type | What it is |
| --- | --- | --- | --- |
| `number` | yes | string | Two-digit label, e.g. `"01"`. Shown as `01 / Kissee`. |
| `slug` | yes | string | Section id and in-page link. Lowercase, hyphens only. |
| `shortName` | yes | string | Name after the slash. |
| `client` | yes | string | Heading. The full client or product name. |
| `category` | yes | string | Tag line, e.g. `home inspections · custom website`. |
| `headline` | yes | string | One factual sentence about what the live site is or does. No results, ratings, quotes, or testimonials that are not simply describing the site. |
| `url` | yes | string | Absolute `http` or `https` URL. Used by the Visit site link. |
| `venture` | no | string | Extra label. Texas Threads uses `a Tribe Maker venture`. |
| `pending` | yes | boolean | `true` renders the pending frame and skips images. |
| `images` | when `pending` is false | object | Screenshot set. See below. |

`images`:

| Field | Required | Type | What it is |
| --- | --- | --- | --- |
| `desktop` | yes | object | Crisp desktop screenshot. |
| `phone` | no | object | Phone screenshot. Used as the main image below 640px, and as an overlapping handset from 1024px. |
| `blur` | no | string | Path to a small blurred WebP. Painted full-bleed behind the section. |

`desktop` and `phone`:

| Field | Required | Type | What it is |
| --- | --- | --- | --- |
| `webp` | yes | string | Path beginning with `assets/`. |
| `fallback` | yes | string | JPG or PNG path beginning with `assets/`. |
| `width` | yes | number | Pixel width of the file. |
| `height` | yes | number | Pixel height of the file. |
| `alt` | yes | string | What is actually in the screenshot. |

Paths must start with `assets/` and must not contain `..`. The renderer ignores anything else.

### Example

```json
{
  "number": "08",
  "slug": "example",
  "shortName": "Example",
  "client": "Example Co",
  "category": "local service · custom website",
  "headline": "A one-sentence description of what the live site is.",
  "url": "https://example.com",
  "pending": false,
  "images": {
    "desktop": {
      "webp": "assets/shots/example-desktop.webp",
      "fallback": "assets/shots/example-desktop.jpg",
      "width": 1440,
      "height": 900,
      "alt": "Homepage of Example Co"
    },
    "phone": {
      "webp": "assets/shots/example-phone.webp",
      "fallback": "assets/shots/example-phone.jpg",
      "width": 780,
      "height": 1688,
      "alt": "Example Co homepage on a phone"
    },
    "blur": "assets/shots/example-blur.webp"
  }
}
```

## Case study pages

Each project in the grid links to `/work/{slug}/`. Later clients were added from review prototypes at `{slug}.clientreview.co`, or from the live site when that host did not answer. Clients with neither are listed under Skipped in `content-gaps.md`. Custom Fit Coverage stays off the grid. The pages follow the section order of the Hive study on thetribemaker.com: cover, brief, identity, mobile, detail, quote, long scroll, credits. Copy is taken from the live site, a review prototype when one is up, or this repo. Missing proof is a gap block. The log is `content-gaps.md`.

Regenerate the pages after editing `scripts/build_cases.py`:

```bash
python3 scripts/build_cases.py
```

## Layout

Mobile first. Breakpoints are 640px and 1024px. Content sits on a 12-column grid and is centered when it does not fill the row. Body text is at least 16px. Type is Fraunces and Sora. Color comes from The Tribe Maker: ink `#131419`, blue `#0729aa`, honey `#ffaf00`, cream `#faf6ee`.

Screenshots in this repo were captured from the live homepages in a headless browser, then exported as WebP with a JPG fallback. Texas Threads uses the homepage hero only.
