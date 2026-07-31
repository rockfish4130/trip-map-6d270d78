#!/usr/bin/env python3
"""Stamp index.html with the current local build date/time.

The header shows a "Built <timestamp>" label (a <span id="buildstamp">). Run this
right before publishing so the label reflects when the deployed file was built.

    python tools/stamp_build.py

Only the text inside the buildstamp span is changed. Nothing else is touched.
"""
import re, os, datetime

HTML = os.path.join(os.path.dirname(__file__), "..", "index.html")


def main():
    now = datetime.datetime.now().astimezone()
    tz = now.strftime("%Z")
    if " " in tz:  # Windows gives e.g. "Central Daylight Time" -> "CDT"
        tz = "".join(w[0] for w in tz.split())
    stamp = now.strftime("%Y-%m-%d %H:%M ") + tz
    html = open(HTML, encoding="utf-8").read()
    new, n = re.subn(r'(id="buildstamp"[^>]*>)Built [^<]*', r"\1Built " + stamp, html)
    if n != 1:
        raise SystemExit("expected exactly one buildstamp span, found {}".format(n))
    open(HTML, "w", encoding="utf-8", newline="").write(new)
    print("stamped build time:", stamp)


if __name__ == "__main__":
    main()
