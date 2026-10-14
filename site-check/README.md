# Site check: https://tomasvicar.github.io/MLR-public/

A Playwright check of the course website's menu, on a desktop-size window and on a narrow phone, run on 14 October 2026.

## Result

- **Broken links: none.** `broken-links.json` is an empty list (`[]`).
- Desktop (1280 px wide): all 8 menu links load (HTTP 200) with the right page: site title (logo and text), Home, Lectures, Exercises, Schedule, Materials, Organisation, and the GitHub icon (leaves the site, opens in a new tab).
- All 158 links found inside the six site pages (102 internal, 56 external) answered 200.
- Phone (360 × 740, emulated): the menu collapses into a hamburger button and all 8 links work when tapped. Layout rough edges are listed below.

Screenshots: [`screenshots/desktop`](screenshots/desktop) (full page) and [`screenshots/phone`](screenshots/phone) (`phone-00` menu closed, `phone-01` menu open, then each page as a screen and as a full page). `01` and `02` on desktop are the Home page, reached through the two site-title links.

### Phone: what is rough

1. The Home page is 419 px wide on a 360 px screen (the top-bar title does not wrap), so it pans about 59 px sideways.
2. The top-bar title is cut off ("MPA-MLR · Ma…"), and on the other pages the small logo text is clipped to "M".
3. The hamburger button is 34 × 34 px, below the usual 44 px guideline.
4. The Schedule table is wider than the screen and scrolls inside its own box; the right-hand columns are cut off until you swipe.

## What "broken" means here, and the limits

- A menu link counts as broken if the page does not load, does not return 200, or shows an error page.
- For links inside the pages, a request (HEAD, falling back to a one-byte range request) returning 400 or more, or failing, counts as broken. A 200 means the server answered, not that the right content is behind it: links behind a university login (Moodle, SharePoint) return 200 for the login page, and Colab answers for any address. Anchors (`#section`) were not checked.
- The phone run is Edge's phone emulation at one size (360 × 740) with emulated touch, not a real phone. Other widths (320 px, tablets) were not tried.

## Scripts

- [`menu_check.py`](menu_check.py): desktop. Clicks every menu link, records status, title and console errors, and takes a full-page screenshot of each page.
- [`link_check.py`](link_check.py): collects every link on the six site pages and checks each one once. Writes a JSON file of results.
- [`phone_check.py`](phone_check.py): phone. Opens the hamburger, taps every link, measures tap targets and sideways overflow, and takes screenshots.

They need [uv](https://docs.astral.sh/uv/) and Microsoft Edge (they use it through Playwright, so no browser download). Used: uv 0.13.1, Playwright 1.64.0. From the repository root:

```
uv run --no-project --with playwright python -I site-check/menu_check.py  out/desktop
uv run --no-project --with playwright python -I site-check/link_check.py  out/links.json
uv run --no-project --with playwright python -I site-check/phone_check.py out/phone
```

In a Windows console the "·" in the page titles may print as "�"; that is display only. The scripts print a line per link and write their screenshots and a results file into the folder or file you give them. The results files are not kept here; the screenshots and `broken-links.json` are.
