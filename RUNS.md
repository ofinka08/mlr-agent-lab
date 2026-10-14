# Runs

## 2026-10-14

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting. I could not run `/status` myself, so this is not copied from its output.
- **Asked:**
  1. Install `gh` and `uv` without admin rights into the dev folder, and check they work.
  2. Create a public GitHub repo `mlr-agent-lab` from this folder, showing what would be uploaded before pushing.
  3. Write `AGENTS.md`, make `CLAUDE.md` load it, and create `README.md`, `PLAN.md`, `RUNS.md`.
- **Checked:**
  1. `gh --version` printed 2.102.0 and `uv --version` printed 0.13.1.
  2. Listed the folder contents (only `hello.py`) and got a yes before pushing; the push output showed the new `main` branch.
  3. `uv run hello.py` printed `hello`; confirmed all five files exist and `CLAUDE.md` contains `@AGENTS.md`. Not verified: that a fresh Claude Code session actually loads `AGENTS.md` through the import.

## 2026-10-14 (snake)

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting.
- **Asked:** (1) a Snake game as one HTML file in `snake/`; (2) an unusual twist on the rules (the ghost tail); (3) fix: left arrow did not start the game; (4) write the rules into `snake/README.md` and test the logic, not only the drawing.
- **Checked:**
  - Logic: `uv run --no-project --with quickjs --with pytest pytest snake -q` gave 52 passed at that point (quickjs 1.19.4, pytest 8.0.0). The tests run the page's real script in QuickJS with the browser parts stubbed.
  - The tests can fail: on a broken copy (original left-arrow bug, ghost tail never harmless) 5 tests failed as expected.
  - One test of mine had a wrong expected value (my counting error); the game behavior was correct, so I fixed the test and kept its purpose. No other test was changed.
  - Not verified: drawing, real key events and timing in a browser.

## 2026-10-14 (high scores)

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting.
- **Asked:** add a high-score table that survives a page reload.
- **Checked:**
  - `uv run --no-project --with quickjs --with pytest pytest snake -q` gave 85 passed at that point (quickjs 1.19.4, pytest 8.0.0). A "reload" in the tests is a new page loaded with the same stored data.
  - Mutation check on a copy (scores not saved; table sorted lowest-first): 8 tests failed as expected.
  - Test change, on purpose: the old `test_best_score_saved_and_loaded` asserted the old storage format (`"1"`). The new feature changes that format, so I replaced it with table tests covering the same behavior (score survives reload). I also folded the old "lower score does not replace best" test into the new set.
  - Not verified: the table's look/layout and real `localStorage` in a browser.

## 2026-10-14 (one game)

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting.
- **Asked:** keep only one game file: remove the original (no-twist) game and everything tied to it, so the project reads as if the ghost tail had been made in `snake/index.html` from the start.
- **Done:** `snake/` now has a single game file, `index.html`, with the ghost tail as one of its rules. Removed the other game file, its tests and its storage names, and rewrote `snake/README.md` and `PLAN.md` for one game. Earlier entries in this log are history and are left as written.
- **Checked:** `uv run --no-project --with quickjs --with pytest pytest snake -q` gave 44 passed (quickjs 1.19.4, pytest 8.0.0).
- **Not verified:** the game in a real browser.
