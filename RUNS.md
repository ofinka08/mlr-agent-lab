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

## 2026-10-14 (slides)

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting.
- **Asked:** a short Quarto presentation about the game with an animation; then, against the written requirements: five slides with little text and speaker notes, the animation's first frame showing the final state with the last frame held, and a note with a dimensions table, a figure, rebuild commands, and links to the viewer and the script. Then: drop the head animation (unrelated to the game), animate the snake picture from the "twist" slide instead, and replace the animation slide with something about the game's files.
- **Done:** installed Quarto 1.10.19 (portable, `C:\dev\tools\quarto`, user PATH). Slides in `slides/snake.qmd`, rendered to `slides/snake.html`: title, the game, the twist (animated snake), the files, tested. Note in `slides/NOTE.md`. `slides/snake_pic.py` builds the animated picture (`snake-pic.svg`) and `snake-figure.svg`, reads `SOLID` and the ghost opacity from `snake/index.html`, and checks that slides, note, figures and game agree.
- **Fixed against the requirements:** the first version had 7 slides, no speaker notes, a looping animation that started closed, and no note. An empty extra slide appeared when notes came before the first heading; fixed. A mouth-head animation I had added was dropped as unrelated to the game.
- **Checked:**
  - `quarto render slides/snake.qmd` gives 5 `<section>` slides and 5 speaker-notes blocks.
  - `uv run --no-project slides/snake_pic.py --check` printed "ok" (uv 0.13.1); on a broken copy (game constant changed, animation set to loop) it reported 4 problems and exited 1.
  - Headless Edge screenshots of slide 3 at 4 points in time: snake restarted at 4 segments, then 9, then the full 12 held (8 solid + 4 ghosts). Slide 4 (files) and the figure looked right.
  - First frame: verified from the file (every animation's first and last value equals the shape shown without animation), not from a screenshot at time zero.
  - Not verified: pressing `S` for the speaker-notes view, and the animation replaying when you navigate back to slide 3 in a live browser.

## 2026-10-14 (LaTeX note)

- **Model:** Sonnet 5.5 (`claude-sonnet-5-5`), per the `/model` setting.
- **Asked:** a one-page LaTeX note about the game, with a figure; compile it and show the PDF.
- **Done:** `note/snake-note.tex` (pdfTeX from MiKTeX 24.1, packages geometry, fontenc, lmodern, xcolor, tikz, caption). The figure is drawn in TikZ: 12 segments, 8 solid and 4 ghosts at opacity 0.3, the same numbers as `SOLID` and the ghost opacity in `snake/index.html`. Output: `note/snake-note.pdf`.
- **Checked:** `cd note && pdflatex -interaction=nonstopmode snake-note.tex` from a clean folder: "1 page", no warnings. Viewed the page as an image. First draft was 2 pages and printed `--no-project` with an en dash; fixed (removed a redundant table, moved the commands into a verbatim block).
- **Not verified:** the figure's numbers are typed in the `.tex` (8, 0.3, 12), not read from the game, unlike the slides' figure; if `SOLID` changes, update them by hand. The 110 ms, 20×20 and 44 tests figures are also typed in.
