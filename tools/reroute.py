#!/usr/bin/env python3
"""Regenerate the map's route polylines by snapping each leg to real roads.

Why this exists
---------------
`index.html` embeds a `const D = {...}` data blob whose `routes[]` entries each
hold a `pts` array of [lat, lon] points that Leaflet draws as a polyline. Those
points were originally hand-placed and cut across open country. This script
replaces each leg's `pts` with road-following geometry from the public OSRM
demo router, then writes the file back. It runs at BUILD time only -- the shipped
index.html stays fully self-contained (no runtime network calls).

Usage
-----
    python tools/reroute.py            # dry run: prints a per-leg proposal
    python tools/reroute.py --write    # apply changes to index.html

Notes
-----
* Uses only the Python standard library (urllib). No pip installs.
* On Windows, force UTF-8 so the console can print the route labels:
      set PYTHONUTF8=1 & set PYTHONIOENCODING=utf-8 & python tools/reroute.py
* The displayed `mi` values are the trip planner's estimates and are NOT changed
  here -- only the drawn geometry. Real road distance (printed as `osrm=`) can
  differ; that's expected.
* VIAS forces a corridor for legs that would otherwise collapse onto a different
  road (e.g. the dirt route over Onion Saddle vs. the paved way around).
* OSRM is a best-effort public service. Legs that fail the sanity check keep
  their original hand-drawn points rather than accept a bad route.
"""
import json, re, sys, time, urllib.request, urllib.error, os

HTML = os.path.join(os.path.dirname(__file__), "..", "index.html")
OSRM = "http://router.project-osrm.org/route/v1/driving/{}?overview=simplified&geometries=geojson"

# Forced via-points (lat, lon) that preserve the intended corridor for legs
# where a straight origin->destination route would take the wrong roads.
VIAS = {
    7: [(32.2100, -108.9600), (32.2529, -109.8318)],  # Day 5 paved: force the I-10 + Willcox loop
    8: [(31.9553, -109.2803), (32.0121, -109.3416)],  # Day 5 ALT DIRT: Onion Saddle (FR 42) + Chiricahua NM
}
# Dirt / forest spurs: if OSRM can't route them, we keep the original points.
DIRT = {4, 5, 6, 8, 13}


def osrm(waypts):
    coords = ";".join("{:.5f},{:.5f}".format(lon, lat) for (lat, lon) in waypts)
    with urllib.request.urlopen(OSRM.format(coords), timeout=30) as r:
        return json.load(r)


def load_D(html):
    m = re.search(r"const D = (\{.*?\});", html, re.S)
    return m, json.loads(m.group(1))


def main():
    write = "--write" in sys.argv
    html = open(HTML, encoding="utf-8").read()
    m, D = load_D(html)
    routes = D["routes"]
    changed = 0
    for i, leg in enumerate(routes):
        pts = leg["pts"]
        waypts = [tuple(pts[0])] + VIAS.get(i, []) + [tuple(pts[-1])]
        orig_mi = leg["mi"]
        try:
            resp = osrm(waypts)
            if resp.get("code") != "Ok" or not resp.get("routes"):
                raise RuntimeError("code=" + str(resp.get("code")))
            route = resp["routes"][0]
            geom = route["geometry"]["coordinates"]          # [lon, lat]
            osrm_mi = route["distance"] / 1609.34
            new_pts = [[round(lat, 5), round(lon, 5)] for (lon, lat) in geom]
            lo, hi = (0.45, 2.4) if orig_mi >= 12 else (0.4, 3.5)
            ok = len(new_pts) >= 2 and lo * orig_mi <= osrm_mi <= hi * orig_mi
            verdict = "ACCEPT" if ok else ("FALLBACK(dirt)" if i in DIRT else "FALLBACK(sanity)")
            if ok:
                leg["pts"] = new_pts
                leg["road_mi"] = round(osrm_mi, 1)   # actual road distance, for discrepancy flagging
                changed += 1
            print("idx {:2d}  {:<50.50}  orig={:>4} mi  osrm={:>6.1f} mi  pts {:>3}->{:<3}  {}".format(
                i, leg["label"], orig_mi, osrm_mi, len(pts), len(new_pts), verdict))
        except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
            print("idx {:2d}  {:<50.50}  orig={:>4} mi  OSRM ERROR: {}  -> keep original".format(
                i, leg["label"], orig_mi, e))
        time.sleep(0.4)
    print("\n{} of {} legs re-snapped to roads.".format(changed, len(routes)))
    if write:
        new_blob = "const D = " + json.dumps(D, ensure_ascii=False) + ";"
        out = html[:m.start()] + new_blob + html[m.end():]
        open(HTML, "w", encoding="utf-8", newline="").write(out)
        _, D2 = load_D(open(HTML, encoding="utf-8").read())
        print("WROTE index.html; D re-parses OK, {} routes.".format(len(D2["routes"])))


if __name__ == "__main__":
    main()
