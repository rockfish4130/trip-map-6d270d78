# Publishing & deployment

The site is a GitHub Pages deployment of this repo. Pushing to `main` rebuilds it.

- **Live URL:** https://rockfish4130.github.io/trip-map-6d270d78/
- **Repo:** `rockfish4130/trip-map-6d270d78`
- **Pages source:** branch `main`, path `/` (root)

---

## Publish a change

One step (Windows):

```powershell
pwsh tools/publish.ps1 -Message "Describe the change"
```

Or manually (any platform):

```bash
python tools/stamp_build.py                       # 1. refresh the "Built ..." header label
git add -A
git commit -m "Describe the change"               # 2. commit
git push origin main                              # 3. push -> triggers Pages build
```

GitHub Pages rebuilds automatically, usually within **15–60 seconds**. There is no local
build step — the file that's committed is the file that's served.

## Verify the deploy

Confirm the *served bytes* changed (don't trust the build-status API alone — it can lag):

```bash
curl -s "https://rockfish4130.github.io/trip-map-6d270d78/?cb=$(date +%s)" | grep -c "buildstamp"
```

Or check the latest build status with the GitHub CLI:

```bash
gh api repos/rockfish4130/trip-map-6d270d78/pages/builds/latest --jq '.status + " " + .commit'
```

A hard refresh (or the `?cb=` cache-buster above) avoids the browser/CDN 10-minute cache.

## First-time / re-enabling Pages

Pages was enabled once via the API; you only need this if it ever gets turned off:

```bash
gh api -X POST repos/rockfish4130/trip-map-6d270d78/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

## Why the repo is public

GitHub Pages will not serve a **private** repo on the Free plan. If the account is on a
paid plan, the repo could be made private and Pages would still work; on Free it must be
public. Privacy therefore comes from the unguessable name + `noindex` + `robots.txt`, not
from access control (see the README's "Privacy & deployment"). Anyone with the URL can
view the page without logging in.

## Regenerating routes as part of a release

If a change moved any stop, regenerate the road geometry before publishing (needs
network access to the OSRM demo server):

```bash
python tools/reroute.py            # review
python tools/reroute.py --write    # apply, then publish as above
```

This calls a public router with the leg coordinates. That's a build-time action; the
shipped `index.html` contains only the resulting polylines — it never calls OSRM at
runtime. (It *does* call OpenStreetMap tiles and `api.weather.gov` at runtime — see the
README's "Runtime services" table.)

## Rolling back

Every publish is a commit. To revert the live site to the previous version:

```bash
git revert HEAD          # or: git checkout <good-sha> -- index.html
git push origin main
```
