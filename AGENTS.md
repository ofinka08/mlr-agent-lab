# Working rules

1. Read `README.md` and `PLAN.md` before starting; keep decisions in the repository.
2. Try the available tools before asking the user to do a technical step by hand.
3. Use `uv` for Python: `uv run` to run scripts, `uv add` for packages, no global `pip install`; record versions and commands.
4. Run meaningful checks before claiming completion, and report the actual result (including failures). Right now the check is `uv run hello.py`; add real checks here as the project grows.
5. Do not weaken a test to make it pass; explain the disagreement first.
6. Never publish secrets or private data; ask before publishing anything.
7. Keep `PLAN.md` current (progress, next step) and log each session in `RUNS.md`.
