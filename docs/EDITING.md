# Editing recipes

All edits happen in `index.html`. The data lives in the `const D = {...}` object; the
look lives in the `<style>` block; behavior lives in the `<script>`. After any change,
[publish](PUBLISHING.md).

> Sanity-check before publishing (needs Node just for the check):
> ```bash
> node -e 'const h=require("fs").readFileSync("index.html","utf8");JSON.parse(h.match(/const D = (\{[\s\S]*?\});/)[1]);console.log("D parses OK")'
> ```

---

## Add a point of interest (a stop marker)

Append an object to `D.pois`. Pick `kind` to control the shape and which toggle layer it
lands in:

```json
{ "name": "Some Feeders", "lat": 31.55, "lon": -110.13, "elev": 3900,
  "phase": "hua", "kind": "bird", "day": "Day 7", "note": "What you'll see there." }
```

- `kind`: `"bird"` (open circle), `"bike"` (violet square, bike glyph), or `"other"` (neutral square).
- `phase`: must match a `D.phases[].id`.
- `note` may contain HTML (`<b>`, `⚠`, etc.).

No JS change is needed — `D.pois.forEach(...)` renders whatever is in the array.

## Add or change an itinerary day

Edit/append a `D.days` entry (see [DATA_MODEL.md](DATA_MODEL.md#days--the-itinerary-one-per-calendar-day)
for every field). Watch these interactions:

- **Markers are shared by location.** Two days with the same rounded `lat`/`lon`
  (3 decimals) collapse into one map pin whose popup lists both. Give a day a distinct
  `lat`/`lon` if you want its own pin.
- **Zoom presets** (`VIEWS.all`) auto-fit to all days, but `VIEWS.tx` / `VIEWS.az` are
  hard-coded bounding boxes near the bottom of the script — adjust if you add days well
  outside them.
- **`drive_txt`** is what feeds the drive-time chip; keep the `~Nh Nm` shape if you want
  `dtime()` to find it.

## Change a phase color or name

Edit the relevant `D.phases` entry's `light`/`dark`/`name`. Colors flow everywhere
automatically (markers, lines, cards, legend) through the `--p-<id>` CSS variable and
`pc()` / `repaint()`. Don't hard-code hex anywhere else.

## Fix or regenerate the route lines

The `pts` arrays are generated from real roads by `tools/reroute.py` (OSRM). To
regenerate after adding/moving a leg:

```bash
# Windows: prefix with  set PYTHONUTF8=1 & set PYTHONIOENCODING=utf-8 &
python tools/reroute.py            # dry run — review the per-leg table
python tools/reroute.py --write    # apply
```

- To force a leg through a specific corridor (dirt vs. paved, a mountain pass), add its
  index to `VIAS` in `reroute.py` with one or two `(lat, lon)` via-points.
- Legs that fail the distance sanity check keep their original points; dirt/forest spurs
  are listed in `DIRT` so a routing failure there is expected, not a bug.
- Route order in `D.routes` is what the `VIAS`/`DIRT` indices refer to — if you insert a
  leg, those indices shift.

## Tune the "big mileage gap" flag

`mileFlag(r)` in the script decides which legs get a `*` and a mileage-note popup.
Default: flag when the road distance differs from the listed `mi` by **≥10 mi and ≥20%**.
Change the `>=10` / `>=1.2` / `<=0.8` constants there to widen or narrow it. A leg only
qualifies if it has a `road_mi` (i.e. `reroute.py` accepted its geometry).

## Change the build-date label

It's auto-stamped by `tools/stamp_build.py` at publish time (see
[PUBLISHING.md](PUBLISHING.md)). To change wording/placement, edit the
`<span id="buildstamp">` in the header — but keep the `id`, or the stamper's regex won't
find it.

## Common gotchas

- **Never break the `noindex` line or inline-only rule** — see the README's
  "one hard rule".
- **`D` must stay valid JSON** (no comments/trailing commas) or `reroute.py` and the
  sanity check above will fail.
- **`[lat, lon]` order** everywhere (Leaflet convention), including new `pts`.
- Popup/label strings are HTML — escape `<`, `>`, `&` if they're literal text.
