# Plan

## Progress

- [x] Installed `gh` and `uv` into `C:\dev\tools\bin` (no admin rights)
- [x] Created the public GitHub repo `ofinka08/mlr-agent-lab` with `hello.py`
- [x] Added `AGENTS.md`, `CLAUDE.md`, `README.md`, `PLAN.md`, `RUNS.md`

- [x] `snake/index.html`: Snake in a single HTML file with a ghost-tail twist, rules in `snake/README.md`
- [x] Fixed: pressing left at the start did nothing (reversal check ran before the game started)
- [x] High-score table (top 5, kept in `localStorage`)
- [x] `snake/test_snake.py`: 44 logic tests, run with the command in `snake/README.md`
- [x] `slides/`: 5 Quarto slides with speaker notes; the snake picture on slide 3 grows back segment by segment (first frame is the final state, last frame held); `slides/NOTE.md` has the dimensions table, figure, rebuild commands and links
- [x] `note/snake-note.tex`: one-page LaTeX note with a TikZ figure, compiled to `note/snake-note.pdf`
- [ ] Not yet checked in a real browser (drawing, key handling, timing)

## Next step

Decide what the lab should actually do, then turn it into a `uv` project (`uv init`) so `uv add` and `uv run` have a `pyproject.toml` to work with.
