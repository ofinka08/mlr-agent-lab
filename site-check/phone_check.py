import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://tomasvicar.github.io/MLR-public/"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
VW, VH = 360, 740
UA = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"
MEASURE = """() => {
  const vv = visualViewport.width;
  const wide = [...document.querySelectorAll('body *')].map(e => ({e, r: e.getBoundingClientRect()}))
    .filter(o => o.r.width > 0 && o.r.right > vv + 1)
    .sort((a, b) => b.r.right - a.r.right).slice(0, 3)
    .map(o => `${o.e.tagName.toLowerCase()}${o.e.className && typeof o.e.className === 'string' ? '.' + o.e.className.split(' ')[0] : ''} right=${Math.round(o.r.right)}`);
  const fs = getComputedStyle(document.body).fontSize;
  return {visual_w: vv, layout_w: innerWidth, doc_scroll_w: document.documentElement.scrollWidth, widest_offenders: wide, body_font: fs};
}"""
def log(*a): print(*a, flush=True)
rows = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": VW, "height": VH}, device_scale_factor=2, is_mobile=True, has_touch=True, user_agent=UA)
    ctx.set_default_timeout(10000)
    pg = ctx.new_page(); pg.goto(URL, wait_until="load"); pg.wait_for_timeout(500)
    toggler = pg.locator(".navbar-toggler").first
    setup = {"toggler_box": toggler.bounding_box(), "toggler_label": toggler.get_attribute("aria-label"),
             "visible_with_menu_closed": pg.eval_on_selector_all(".navbar a", "els => els.filter(a => {const r=a.getBoundingClientRect(); return r.width>0 && r.height>0}).map(a => a.innerText.trim() || '(icon) ' + a.href)")}
    pg.screenshot(path=str(OUT / "phone-00-menu-closed.png"))
    toggler.tap(); pg.wait_for_timeout(700)
    pg.screenshot(path=str(OUT / "phone-01-menu-open.png"))
    menu = pg.eval_on_selector_all(".navbar-collapse a", "els => els.map(a => { const r=a.getBoundingClientRect(); return {text: a.innerText.trim(), href: a.href, target: a.target, x:r.x, right:r.right, w:r.width, h:r.height}; })")
    pg.close()
    log("closed menu shows:", setup["visible_with_menu_closed"], "| toggler", setup["toggler_box"])

    for i, m in enumerate(menu, 1):
        label = m["text"] or "GitHub (icon)"
        slug = f"phone-{i+1:02d}-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        r = {"label": label, "href": m["href"], "tap_target": f"{m['w']:.0f}x{m['h']:.0f}", "right_edge": round(m["right"]),
             "partly_offscreen": m["right"] > VW + 1}
        page = ctx.new_page(); docs = []; errs = []
        page.on("response", lambda resp, d=docs: d.append((resp.status, resp.url)) if resp.request.resource_type == "document" else None)
        page.on("console", lambda msg, e=errs: e.append(msg.text) if msg.type == "error" else None)
        try:
            page.goto(URL, wait_until="load"); page.wait_for_timeout(400)
            page.locator(".navbar-toggler").first.tap(); page.wait_for_timeout(700)
            link = page.locator(f'.navbar-collapse a[href="{m["href"]}"]').first
            bb = link.bounding_box()
            r["hit_test_ok"] = page.evaluate("([x,y,h]) => { const a=document.elementFromPoint(x,y)?.closest('a'); return !!a && a.href===h; }",
                                             [min(bb["x"] + 60, VW - 5), bb["y"] + bb["height"]/2, m["href"]])
            page.evaluate("window.__marker = 1")
            if m["target"] == "_blank":
                with ctx.expect_page() as np_:
                    link.tap()
                tgt = np_.value
                tgt.on("response", lambda resp, d=docs: d.append((resp.status, resp.url)) if resp.request.resource_type == "document" else None)
                tgt.wait_for_load_state("load")
            else:
                link.tap()
                page.wait_for_function("window.__marker === undefined", timeout=10000)  # page really reloaded/navigated
                page.wait_for_load_state("load"); tgt = page
            tgt.wait_for_timeout(600)
            fin = [d for d in docs if d[1].rstrip("/") == tgt.url.rstrip("/")]
            r["status"] = fin[-1][0] if fin else None
            r["final_url"] = tgt.url; r["title"] = tgt.title()
            r["landed_on_expected"] = tgt.url.rstrip("/") == m["href"].rstrip("/")
            if "github.com" not in tgt.url:
                r["layout"] = tgt.evaluate(MEASURE)
                r["h_scroll_px"] = r["layout"]["doc_scroll_w"] - r["layout"]["visual_w"]
                r["menu_closed_after_nav"] = tgt.evaluate("() => !document.querySelector('.navbar-collapse').classList.contains('show')")
            tgt.screenshot(path=str(OUT / (slug + ".png")))
            tgt.screenshot(path=str(OUT / (slug + "-full.png")), full_page=True)
            if tgt is not page: tgt.close()
        except Exception as e:
            r["error"] = f"{type(e).__name__}: {str(e)[:160]}"
        r["console_errors"] = errs
        rows.append(r); page.close()
        log(label, "|", r.get("status"), "| landed ok:", r.get("landed_on_expected"), "| target", r["tap_target"], "| hit ok:", r.get("hit_test_ok"),
            "| h-scroll px:", r.get("h_scroll_px"), "| menu closes:", r.get("menu_closed_after_nav"), "|", r.get("error", ""))
        if r.get("layout") and r["layout"]["widest_offenders"]: log("     wide:", r["layout"]["widest_offenders"], "| layout width", r["layout"]["layout_w"])
    b.close()
json.dump({"setup": setup, "menu_when_open": menu, "links": rows}, open(OUT / "phone-results.json", "w", encoding="utf-8"), indent=1, default=str)
