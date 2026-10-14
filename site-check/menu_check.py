import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://tomasvicar.github.io/MLR-public/"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
results = []

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    menu = page.eval_on_selector_all(
        ".navbar a", "els => els.map(a => ({text: a.innerText.trim(), href: a.href, target: a.target}))")
    # label icon-only links by their destination
    for m in menu:
        if not m["text"]:
            m["text"] = "GitHub (icon)" if "github.com" in m["href"] else "Site title (logo)"
    # "MPA-MLR ... Machine Learning" brand text link -> call it Site title
    seen = []
    for i, m in enumerate(menu):
        label = m["text"] if not m["text"].startswith("MPA-MLR") else "Site title"
        slug = f"{i+1:02d}-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        r = {"label": label, "href": m["href"], "screenshot": f"{slug}.png"}
        p2 = ctx.new_page()  # fresh tab per link so console/request logs are per page
        console_err, failed, docs = [], [], []
        ctx_docs = docs
        p2.on("console", lambda msg, ce=console_err: ce.append(msg.text) if msg.type == "error" else None)
        p2.on("response", lambda resp, f=failed: f.append(f"{resp.status} {resp.url}") if resp.status >= 400 else None)
        p2.on("response", lambda resp, d=docs: d.append((resp.status, resp.url)) if resp.request.resource_type == "document" else None)
        p2.on("requestfailed", lambda req, f=failed: f.append(f"FAILED {req.url} ({req.failure})"))
        try:
            p2.goto(URL, wait_until="networkidle")
            link = p2.locator(f'.navbar a[href="{m["href"]}"]').filter(has_text=m["text"] if not m["text"].startswith("MPA-MLR") else "") .first
            if not m["text"] or m["text"].startswith(("GitHub", "Site title")):
                link = p2.locator(f'.navbar a[href="{m["href"]}"]').nth(0 if "Site" in label else -1)
            if m["target"] == "_blank":
                with ctx.expect_page() as newp:
                    link.click()
                tgt = newp.value
                tgt.on("response", lambda resp, d=docs: d.append((resp.status, resp.url)) if resp.request.resource_type == "document" else None)
            else:
                with p2.expect_navigation(wait_until="load") as nav:
                    link.click()
                tgt = p2
            tgt.wait_for_load_state("networkidle")
            final = [d for d in docs if d[1].rstrip("/") == tgt.url.rstrip("/")]
            r["status"] = final[-1][0] if final else None
            r["document_responses"] = docs[1:] if len(docs) > 1 else docs
            r["final_url"] = tgt.url
            r["title"] = tgt.title()
            r["h1"] = (tgt.locator("h1").first.inner_text() if tgt.locator("h1").count() else "")[:80]
            body = tgt.inner_text("body")
            r["body_chars"] = len(body)
            r["looks_like_404"] = bool(re.search(r"\b404\b|page not found|not found", (r["title"] + " " + body[:400]), re.I))
            tgt.screenshot(path=str(OUT / r["screenshot"]), full_page=True)
            if tgt is not p2:
                tgt.close()
        except Exception as e:
            r["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        r["console_errors"] = console_err
        r["failed_requests"] = failed
        results.append(r)
        p2.close()
    b.close()

(OUT / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
for r in results:
    ok = r.get("status") == 200 and "error" not in r and not r.get("looks_like_404")
    print(("OK  " if ok else "FAIL"), r["label"], "|", r.get("status"), "|", r.get("title"), "|", r["href"])
    for k in ("error",): 
        if k in r: print("     ", r[k])
    for c in r["console_errors"]: print("      console:", c[:150])
    for f in r["failed_requests"]: print("      request:", f[:150])
