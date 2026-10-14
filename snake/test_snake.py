"""Logic tests for the Snake game.

The page's <script> is run unchanged in QuickJS with the browser parts
(canvas, DOM, localStorage, timers) stubbed. Ticks are driven by hand via
step(), so the tests cover game rules, not drawing.

Run:  uv run --no-project --with quickjs --with pytest pytest snake -q
"""
import json
import re
from pathlib import Path

import pytest
import quickjs

HERE = Path(__file__).parent

PRELUDE = """
const noop = () => {};
const ctx2d = new Proxy({}, { get: (t, k) => (k in t ? t[k] : noop), set: (t, k, v) => { t[k] = v; return true; } });
const els = {};
globalThis.document = {
  getElementById: id => els[id] || (els[id] = { textContent: "", width: 400, height: 400, getContext: () => ctx2d }),
  addEventListener: (type, f) => { globalThis.__keydown = f; },
};
globalThis.__store = {};
globalThis.localStorage = {
  getItem: k => (k in __store ? __store[k] : null),
  setItem: (k, v) => { __store[k] = String(v); },
};
globalThis.setInterval = f => { globalThis.__timer = f; return 1; };
globalThis.clearInterval = () => { globalThis.__timer = null; };
"""


class Game:
    def __init__(self, page="index.html", store=None):
        html = (HERE / page).read_text(encoding="utf-8")
        script = re.search(r"<script>(.*)</script>", html, re.S).group(1)
        self.page = page
        self.js = quickjs.Context()
        self.js.eval(PRELUDE)
        self.js.eval(f"__store = {json.dumps(store or {})};")
        self.js.eval(script)

    def get(self, expr):
        return json.loads(self.js.eval(f"JSON.stringify({expr})"))

    def run(self, code):
        self.js.eval(code)

    def press(self, key):
        self.js.eval(f"__keydown({{ key: {json.dumps(key)}, preventDefault() {{}} }})")

    def tick(self, n=1):
        for _ in range(n):
            self.js.eval("step()")

    def place(self, cells, direction=(1, 0), food=None):
        """Put the snake (head first) in a known state, as if already running."""
        self.run(
            f"snake = {json.dumps([{'x': x, 'y': y} for x, y in cells])};"
            f"dir = nextDir = {json.dumps({'x': direction[0], 'y': direction[1]})};"
            f"food = {json.dumps({'x': food[0], 'y': food[1]} if food else None)};"
            "state = 'running';"
        )

    @property
    def state(self):
        return self.get("state")

    @property
    def snake(self):
        return [(s["x"], s["y"]) for s in self.get("snake")]

    @property
    def score(self):
        return self.get("score")


@pytest.fixture
def game():
    return Game()


# --- basic rules ----------------------------------------------------------

def test_initial_state(game):
    assert game.state == "ready"
    assert game.snake == [(10, 10), (9, 10), (8, 10)]
    assert game.score == 0


def test_food_never_spawns_on_snake(game):
    for _ in range(200):
        game.run("food = placeFood()")
        f = game.get("food")
        assert (f["x"], f["y"]) not in game.snake


@pytest.mark.parametrize("key,vec", [
    ("ArrowRight", (1, 0)), ("ArrowUp", (0, -1)), ("ArrowDown", (0, 1)),
    ("ArrowLeft", (-1, 0)), ("a", (-1, 0)),
])
def test_any_direction_starts_the_game(game, key, vec):
    game.press(key)
    assert game.state == "running"
    assert game.get("dir") == {"x": vec[0], "y": vec[1]}
    head = game.snake[0]
    game.tick()
    assert game.snake[0] == (head[0] + vec[0], head[1] + vec[1])
    assert game.state == "running"


def test_left_start_turns_snake_around_without_self_hit(game):
    game.press("ArrowLeft")
    assert game.snake == [(8, 10), (9, 10), (10, 10)]
    game.tick(3)
    assert game.state == "running"


def test_reversal_is_ignored_while_running(game):
    game.press("ArrowRight")
    game.press("ArrowLeft")
    game.tick()
    assert game.state == "running"
    assert game.snake[0] == (11, 10)


def test_quick_up_then_left_does_not_reverse_into_self(game):
    game.press("ArrowRight")
    game.tick()
    game.press("ArrowUp")
    game.press("ArrowLeft")  # reversal of the direction actually moved: ignored
    game.tick()
    assert game.state == "running"
    assert game.snake[0] == (11, 9)  # went up from (11,10); the left press was dropped


def test_wall_collision_ends_game(game):
    game.place([(19, 5), (18, 5), (17, 5)])
    game.tick()
    assert game.state == "over"


@pytest.mark.parametrize("cells,direction", [
    ([(0, 0), (1, 0), (2, 0)], (-1, 0)),
    ([(5, 0), (5, 1), (5, 2)], (0, -1)),
    ([(5, 19), (5, 18), (5, 17)], (0, 1)),
])
def test_every_wall_kills(game, cells, direction):
    game.place(cells, direction)
    game.tick()
    assert game.state == "over"


def test_eating_grows_and_scores_and_respawns_food(game):
    game.place([(5, 5), (4, 5), (3, 5)], food=(6, 5))
    game.tick()
    assert game.score == 1
    assert game.snake == [(6, 5), (5, 5), (4, 5), (3, 5)]
    f = game.get("food")
    assert (f["x"], f["y"]) not in game.snake


def test_moving_without_eating_keeps_length(game):
    game.place([(5, 5), (4, 5), (3, 5)], food=(15, 15))
    game.tick(4)
    assert len(game.snake) == 3
    assert game.score == 0


def test_stepping_into_vacating_tail_is_allowed(game):
    # 2x2 loop: head at (5,5) turning down into the cell the tail leaves.
    game.place([(5, 4), (6, 4), (6, 5), (5, 5)], direction=(0, 1), food=(15, 15))
    # head (5,4) moves down to (5,5) where the tail is; the tail moves away this tick
    game.tick()
    assert game.state == "running"


def test_pause_and_resume(game):
    game.press("ArrowRight")
    game.press(" ")
    assert game.state == "paused"
    game.press("ArrowUp")  # ignored while paused
    assert game.get("dir") == {"x": 1, "y": 0}
    game.press(" ")
    assert game.state == "running"


def test_enter_restarts(game):
    game.place([(19, 5), (18, 5), (17, 5)])
    game.tick()
    assert game.state == "over"
    game.press("Enter")
    assert game.state == "ready"
    assert game.snake == [(10, 10), (9, 10), (8, 10)]
    assert game.score == 0


def test_no_input_after_game_over(game):
    game.place([(19, 5), (18, 5), (17, 5)])
    game.tick()
    game.press("ArrowUp")
    assert game.state == "over"


STORE_KEY, LEGACY_KEY = "snake-scores", "snake-best"


def _finish_with_score(g, n):
    """End a game with score n (set directly; scoring itself is tested elsewhere)."""
    g.run(f"score = {n}; gameOver()")


def _scores(g):
    return [e["score"] for e in g.get("scores")]


def test_score_survives_reload(game):
    game.place([(5, 5), (4, 5), (3, 5)], food=(6, 5))
    game.tick()  # score 1
    game.run("gameOver()")
    assert _scores(game) == [1]
    again = Game(game.page, store=game.get("__store"))  # "reload": new page, same localStorage
    assert _scores(again) == [1]
    assert again.get("best") == 1


def test_table_is_sorted_highest_first_and_kept_across_reloads(game):
    g = game
    for n in (3, 9, 5):
        _finish_with_score(g, n)
        g = Game(game.page, store=g.get("__store"))
    assert _scores(g) == [9, 5, 3]
    assert g.get("best") == 9


def test_table_keeps_only_top_five(game):
    for n in (4, 8, 1, 6, 2, 7, 3):
        _finish_with_score(game, n)
    assert _scores(game) == [8, 7, 6, 4, 3]


def test_equal_scores_keep_older_first(game):
    _finish_with_score(game, 5)
    first_at = game.get("scores")[0]["at"]
    game.run("score = 5; gameOver()")
    entries = game.get("scores")
    assert [e["score"] for e in entries] == [5, 5]
    assert entries[0]["at"] == first_at


def test_zero_score_is_not_recorded(game):
    game.run("score = 0; gameOver()")
    assert _scores(game) == []
    assert game.get("__store") == {}


def test_lower_score_does_not_replace_best(game):
    _finish_with_score(game, 5)
    _finish_with_score(game, 2)
    assert game.get("best") == 5
    assert _scores(game) == [5, 2]


def test_old_single_best_is_migrated(game):
    new_key, legacy_key = STORE_KEY, LEGACY_KEY
    g = Game(game.page, store={legacy_key: "5"})
    assert _scores(g) == [5]
    assert g.get("best") == 5
    _finish_with_score(g, 7)
    assert _scores(g) == [7, 5]
    assert new_key in g.get("__store")


@pytest.mark.parametrize("bad", [
    "not json", "{}", "null", "[1, 2]", '[{"score": -3}]', '[{"score": "9"}]',
    '[{"score": 2.5}]', '[null]',
])
def test_corrupt_stored_scores_are_ignored(game, bad):
    new_key = STORE_KEY
    g = Game(game.page, store={new_key: bad})
    assert _scores(g) == []
    assert g.get("best") == 0
    _finish_with_score(g, 4)  # and the game keeps working
    assert _scores(g) == [4]


def test_stored_table_is_cleaned_on_load(game):
    new_key = STORE_KEY
    raw = json.dumps([{"score": s, "at": "2026-01-01T00:00:00.000Z"} for s in (1, 9, 3, 7, 5, 8, 2)])
    g = Game(game.page, store={new_key: raw})
    assert _scores(g) == [9, 8, 7, 5, 3]


def test_table_is_rendered_into_the_page(game):
    _finish_with_score(game, 6)
    html = game.get("els.scores.innerHTML")
    assert "<b>6</b>" in html
    empty = Game(game.page)
    assert "No scores yet" in empty.get("els.scores.innerHTML")


def test_storage_failure_does_not_break_the_game(game):
    game.run("localStorage.setItem = () => { throw new Error('quota'); }")
    _finish_with_score(game, 3)
    assert game.state == "over"
    assert _scores(game) == [3]  # still shown for this session


def test_filling_the_board_ends_game(game):
    # Snake covers every cell but one; eating the last one is a win and must not crash.
    cells = [(x, y) for y in range(20) for x in (range(20) if y % 2 == 0 else range(19, -1, -1))]
    head_first = list(reversed(cells[:-1]))  # path ends adjacent to cells[-1]
    game.place(head_first, direction=(1, 0), food=None)
    game.run("food = placeFood()")
    f = game.get("food")
    assert (f["x"], f["y"]) == cells[-1]


# --- ghost tail ---------------------------------------------------------

def test_ghost_old_segments_are_harmless():
    g = Game("index.html")
    # Head (5,5) moving right into (6,5), which is segment index 9 (a ghost) after the move.
    cells = [(5, 5), (5, 6), (6, 6), (7, 6), (8, 6), (8, 5), (8, 4), (7, 4), (6, 4), (6, 5), (6, 3), (6, 2)]
    g.place(cells, direction=(1, 0), food=(15, 15))
    g.tick()
    assert g.state == "running"
    assert g.snake[0] == (6, 5)


def test_ghost_recent_segments_are_solid():
    g = Game("index.html")
    # Head moving right into a cell that will be segment index 3 after the move: still solid.
    cells = [(5, 5), (5, 6), (6, 6), (6, 5), (6, 4), (5, 4), (4, 4), (4, 5), (4, 6), (4, 7)]
    g.place(cells, direction=(1, 0), food=(15, 15))
    g.tick()  # head -> (6,5), currently index 3
    assert g.state == "over"


def test_ghost_boundary_index_7_solid_index_8_ghost():
    # Straight line of cells, head loops back onto a chosen index. After the move the
    # old index i becomes i+1, so old index 6 -> new 7 (solid), old index 7 -> new 8 (ghost).
    def snake_with_target_at(i):
        # head at (5,5); fill the rest along a path that places (6,5) at old index i.
        path = [(5, 5), (5, 6), (5, 7), (5, 8), (6, 8), (7, 8), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3)]
        # relocate: swap the target cell into position i
        target = (6, 5)
        path = [p for p in path if p != target]
        path.insert(i, target)
        return path

    solid = Game("index.html")
    solid.place(snake_with_target_at(6), (1, 0), food=(15, 15))
    solid.tick()
    assert solid.state == "over"

    ghost = Game("index.html")
    ghost.place(snake_with_target_at(7), (1, 0), food=(15, 15))
    ghost.tick()
    assert ghost.state == "running"


def test_ghost_short_snake_is_fully_solid():
    g = Game("index.html")
    # length 5 loop: head hits its own index-3 segment
    g.place([(5, 5), (5, 6), (6, 6), (6, 5), (6, 4)], direction=(1, 0), food=(15, 15))
    g.tick()
    assert g.state == "over"


def test_ghost_walls_still_kill():
    g = Game("index.html")
    g.place([(19, 5), (18, 5), (17, 5)])
    g.tick()
    assert g.state == "over"
