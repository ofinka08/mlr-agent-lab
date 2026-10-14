# mlr-agent-lab

A small lab for working with coding agents on Python projects.

## Goal

Try out an agent-driven workflow: clear working rules (`AGENTS.md`), a plan that stays up to date (`PLAN.md`), and a log of what was asked and how it was verified (`RUNS.md`).

## How to run things

Requires [uv](https://docs.astral.sh/uv/). No global `pip install`.

```
uv run hello.py     # prints "hello"
uv add <package>    # add a dependency
```

## Files

- `AGENTS.md` – working rules for agents (`CLAUDE.md` loads it)
- `PLAN.md` – progress and next step
- `RUNS.md` – log of sessions
- `note/` – one-page LaTeX note about the game, with a figure (`snake-note.pdf`)
- `slides/` – five-slide presentation about the game (`snake.html`), with a note on how it is built (`NOTE.md`)
