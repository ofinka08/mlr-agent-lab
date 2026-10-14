# Snake

A single-file browser game with one twist: a ghost tail. Open `index.html` directly in a browser; no build step.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Move (the first press also starts the game) |
| Space | Pause / resume |
| Enter | Restart |

## Rules

1. The board is a 20×20 grid. The snake starts with 3 segments at the center, facing right, and moves one cell every 110 ms.
2. Hitting any wall ends the game. There is no wrap-around.
3. Eating the red apple scores 1 point and grows the snake by 1 segment. A new apple appears on a random free cell, never on the snake.
4. Filling the whole board ends the game (a win).
5. You cannot reverse into the direction you just moved. Pressing the opposite key is ignored, so two quick key presses in one tick can't turn the snake back into its own neck.
6. Before the first move, any direction is allowed. Pressing the opposite way (left at the start) turns the snake around.
7. Input is ignored while paused or after game over. Only Enter (restart) works after game over.
8. **Ghost tail:** only the head and the next 7 segments (8 in total, `SOLID` in the code) are solid. Older segments are drawn faded and are harmless: you can pass through them.
   - Hitting a solid segment ends the game. Up to 8 segments long, every segment is solid.
   - The solid part is always the 8 newest segments, so once the snake is longer than 8, each apple adds one more ghost segment at the tail end.
   - The head may move into the cell the tail is leaving in the same tick, unless you eat on that move (the tail then stays).
9. **High scores:** the top 5 scores of finished games are shown under the board and kept in the browser's `localStorage`, so they survive a page reload.
   - A game with 0 points is not recorded.
   - Sorted highest first; on equal scores the older one stays above.
   - "Best" at the top is the first entry of the table.
   - Damaged or invalid stored data is ignored, and if the browser blocks storage the table still works until you reload.
   - Scores live only in this browser; they are not sent anywhere. Clearing site data erases them. Opening the file from a different location (another folder, or `file://` vs. a web server) counts as a different site and starts with an empty table.

## Tests

The tests run the page's real `<script>` in QuickJS with the canvas, DOM, `localStorage` and timers stubbed, and step the game by hand. They cover game logic (movement, collisions, eating, the ghost boundary, pause/restart, the high-score table and its storage), not drawing.

```
uv run --no-project --with quickjs --with pytest pytest snake -q
```

Last run: 44 passed (uv 0.13.1, Python 3.12.1, quickjs 1.19.4, pytest 8.0.0).

If pytest crashes while loading unrelated plugins from a global Python install, set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` first (PowerShell: `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`).
