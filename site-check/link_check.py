import json, sys
from urllib.parse import urldefrag, urlparse
from playwright.sync_api import sync_playwright

BASE = "https://tomasvicar.github.io/MLR-public/"
PAGES = ["", "lectures.html", "exercises.html", "schedule.html", "materials.html", "organisation.html"]
found = {}  # url -> [(page, link text)]

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context()
    pg = ctx.new_page()
    for name in PAGES:
        pg.goto(BASE + name, wait_until="networkidle")
        links = pg.eval_on_selector_all("a[href]", "els => els.map(a => [a.href, a.innerText.trim().slice(0,50) || a.getAttribute('aria-label') || a.title || '(no text)'])")
        for href, text in links:
            if not href.startswith(("http://", "https://")):
                continue
            url, _ = urldefrag(href)
            found.setdefault(url, []).append((name or "index.html", text))
    print(f"{len(found)} unique http(s) links on {len(PAGES)} pages", flush=True)

    out = []
    for i, (url, where) in enumerate(sorted(found.items()), 1):
        status, note = None, ""
        try:
            r = ctx.request.head(url, timeout=25000, max_redirects=8)
            status = r.status
            if status >= 400 or status == 405:
                r = ctx.request.get(url, timeout=25000, max_redirects=8, headers={"Range": "bytes=0-0"})
                status = r.status
        except Exception as e:
            note = f"{type(e).__name__}: {str(e)[:120]}"
        out.append({"url": url, "status": status, "note": note, "where": where[:3], "count": len(where),
                    "internal": urlparse(url).netloc == urlparse(BASE).netloc})
    b.close()

json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1)
bad = [o for o in out if o["status"] is None or o["status"] >= 400]
print(f"checked {len(out)}; ok: {len(out)-len(bad)}; problems: {len(bad)}")
for o in bad:
    print(o["status"], o["note"], o["url"], "| on:", o["where"][0][0], "|", o["where"][0][1], "| internal" if o["internal"] else "| external")
