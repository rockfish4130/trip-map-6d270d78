# SE Arizona Sky Islands — trip map

An interactive, **single-file** trip map for a birding/riding road trip through the
sky islands of southeast Arizona (Aug 6–20, 2026). It's one self-contained
`index.html` — a Leaflet map with the itinerary, stops, and driving routes baked in —
deployed as an unlisted GitHub Pages site.

- **Live site:** https://rockfish4130.github.io/trip-map-6d270d78/
- **Repo:** `rockfish4130/trip-map-6d270d78` (public; GitHub Pages serves `main` at `/`)

> **Why the weird repo name and "noindex"?** The site is *unlisted*, not private.
> It's public (GitHub Pages requires a public repo on the Free plan), so privacy
> rests on three things: an unguessable random repo name, a `noindex` meta tag, and
> `robots.txt` disallowing all crawlers. None of these are hard access control —
> anyone who has the URL can view it without logging in. See
> [Privacy & deployment](#privacy--deployment).

---

## Repository layout

```
index.html          The entire app: HTML + inlined CSS + inlined Leaflet + data + JS.
robots.txt          "User-agent: * / Disallow: /"  — asks crawlers to skip the site.
.nojekyll           Empty file; tells GitHub Pages to serve files as-is (no Jekyll build).
README.md           This file.
docs/
  DATA_MODEL.md     Schema of the embedded `const D = {...}` data object.
  EDITING.md        Recipes: add a stop, add a day, change colors, fix routes.
  PUBLISHING.md     How to build-stamp, deploy, and what GitHub Pages does.
tools/
  reroute.py        Regenerate route polylines from real roads (OSRM). Build-time only.
  stamp_build.py    Update the "Built <timestamp>" label in the header.
  publish.ps1       Stamp + commit + push in one step.
```

## The one hard rule: keep `index.html` a single self-contained file

Everything the page *needs to boot* is in the one file: all CSS and the entire Leaflet
library are inlined — there are **no companion asset files, no CDN, and no build step**
for the code. You can open `index.html` from disk and it works.

Do not add `<script src=...>`, `<link rel=stylesheet href=...>`, web fonts, or bundled
remote images. If you need a library or asset, inline it.

### Runtime services the page *does* call (by design)

Being a single file is not the same as making zero network requests. Once running, the
page talks to four external services. This is intentional and expected:

| Service | What for | If it's unavailable |
|---|---|---|
| `tile.openstreetmap.org` | base map tiles | map background is blank; markers/lines still draw |
| `a.tile.opentopomap.org` | optional "Terrain / relief" layer | that layer is blank until switched back |
| `api.weather.gov` | live NWS forecast for near-term days | days silently fall back to climate normals |
| `nominatim.openstreetmap.org` | the place-search box (geocoding) | search shows "not found"/"error"; the trip is unaffected |

There are no API keys; all four send permissive CORS headers, so the browser can call
them directly. See [docs/DATA_MODEL.md](docs/DATA_MODEL.md#weather) for how forecasts are
merged with the built-in normals, and [the search note](docs/EDITING.md#change-the-place-search)
for the geocoder.

### Two invariants that are easy to break

1. **The `noindex` meta tag must stay immediately after `<head>`** (line 2–3):
   ```html
   <head>
   <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
   ```
2. **No bundled remote assets.** Don't add `src=`/`href=` to remote stylesheets,
   scripts, fonts, or images. Quick check:
   ```bash
   grep -oE 'src="https?://[^"]+"' index.html   # expect no output
   ```
   (The three runtime services above live in `fetch()`/`L.tileLayer(...)` calls, not in
   `src=` attributes — that's the intended, documented exception.)

## How it works (30-second tour)

`index.html` has three parts, in order:

1. **`<style>`** — a small design system driven by CSS custom properties
   (`--text-primary`, `--p-bike`, phase colors, etc.), with light/dark themes and a
   `@media(max-width:820px)` block for phones.
2. **The data** — one line, `const D = { days, pois, phases, routes, total, total_alt }`.
   This is the single source of truth for everything drawn. See
   [docs/DATA_MODEL.md](docs/DATA_MODEL.md).
3. **The app JS** — builds the Leaflet map, day markers, POI markers (grouped into
   toggleable layers), route polylines, the sidebar day cards, the collapsible legend,
   and the table view; plus theme + layer toggles.

Key functions to know: `pc(phaseId)` (phase color), `pop(day)` / `iolLink()` (popup
HTML), `dtime(day)` (pulls the drive time out of `drive_txt`), `select(n)` (focus a
day), `repaint()` (re-color everything after a theme change), `mileFlag(route)`
(detects a big listed-vs-road mileage gap), and `enrichForecasts()` /
`wxLabel(day)` (merge the live NWS forecast over the built-in climate normals).

## Editing and publishing

Edit `index.html`, then publish. The short version:

```bash
python tools/stamp_build.py              # refresh the "Built ..." label
git add -A && git commit -m "..." && git push origin main
```

or, on Windows, one step:

```powershell
pwsh tools/publish.ps1 -Message "your message"
```

GitHub Pages rebuilds automatically ~15–60 s after the push. Full details, common
edit recipes, and the route-regeneration workflow are in
[docs/EDITING.md](docs/EDITING.md) and [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Privacy & deployment

- **Visibility:** the repo is **public**. GitHub Pages will not serve a private repo
  on the Free plan, so public is required for the site to build.
- **What protects it:** the unguessable name `trip-map-<random hex>`, the `noindex`
  meta tag, and `robots.txt`. These are *requests* honored by well-behaved crawlers,
  not enforcement. Anyone with the link can open the page without logging in.
- **Pages config:** source = `main` branch, path = `/` (root). Enabled once via the
  GitHub API; see [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Known caveats

- **Displayed mileage vs. drawn route length.** The `mi` shown per leg (and the trip
  total) are the *planner's estimates*. `tools/reroute.py` redraws the lines to follow
  real roads but deliberately does **not** rewrite those numbers, so a line may be a
  little longer than its label. This is intentional; the labels are the plan. Where the
  gap is large (≥10 mi **and** ≥20%), the leg stores a `road_mi` value and the map flags
  the line with a `*` and a popup explaining the difference.
- **Live weather only near the trip.** The NWS forecast horizon is ~7 days, so most days
  show August climate normals; a day flips to the live forecast (labeled "forecast")
  only once you view the map within a week of that date.
- **Dirt/forest legs** (e.g. FR 42 over Onion Saddle) depend on those roads existing in
  OpenStreetMap. `reroute.py` forces a via-point over the saddle and falls back to the
  original hand-drawn points if the router can't follow the dirt.
- **Weather** shown is August *climate normals*, not a forecast. Every stop links to
  its live NWS point forecast.
