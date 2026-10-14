"""The snake picture on the slides: one source of truth for the animation, the figure and the note.

    uv run --no-project slides/snake_pic.py           # write snake-pic.svg and snake-figure.svg, print the table
    uv run --no-project slides/snake_pic.py --check   # confirm slides, note, figures and the game agree

snake-pic.svg is pulled into snake.qmd with an include. Standard library only.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
GAME = HERE.parent / "snake" / "index.html"

W, H = 640, 150           # slide picture canvas (px)
SEG, PITCH, Y = 40, 44, 40  # segment size, distance between segments, top edge
N = 12                    # segments in the final state (head = segment 0)
HEAD_X = 500              # left edge of the head; the body extends to the left
SHORT = 3                 # length the snake restarts from
DUR = 5.5                 # seconds
HOLD_START = 0.5          # final state shown this long before the restart
FIRST_GROW, GROW_EVERY = 1.2, 0.45  # time the first new segment appears, then one per step
HEAD_COLOR, BODY_COLOR = "#6ee787", "#3fb950"


def game_constants():
    """SOLID and the ghost opacity, read from the game so the picture cannot drift from it."""
    html = GAME.read_text(encoding="utf-8")
    solid = int(re.search(r"const SOLID = (\d+);", html).group(1))
    ghost = float(re.search(r"i < SOLID \? 1 : ([0-9.]+)", html).group(1))
    return solid, ghost


SOLID, GHOST = game_constants()


def num(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def seg_x(i):
    return HEAD_X - PITCH * i


def final_opacity(i):
    return 1 if i < SOLID else GHOST


def appear_time(i):
    return FIRST_GROW + GROW_EVERY * (i - SHORT)


def anim(i, final):
    """Opacity animation: starts on the final value, vanishes at the restart, returns at appear_time(i), holds."""
    kt = f"0;{num(HOLD_START / DUR)};{num(appear_time(i) / DUR)};1"
    return (f'<animate attributeName="opacity" begin="indefinite" dur="{num(DUR)}s" repeatCount="1" '
            f'fill="freeze" calcMode="discrete" keyTimes="{kt}" values="{num(final)};0;{num(final)};{num(final)}"/>')


def pic():
    """The animated picture. Without animation it shows the final state (12 segments)."""
    lines = [f'<svg id="snake-pic" viewBox="0 0 {W} {H}" width="800" role="img" '
             f'aria-label="A snake grows one segment at a time: the {SOLID} newest segments are solid, older ones are faded ghosts">',
             f'<rect width="{W}" height="{H}" rx="12" fill="#1b1b1b"/>']
    for i in range(N):
        f = final_opacity(i)
        fill = HEAD_COLOR if i == 0 else BODY_COLOR
        rect = f'<rect x="{seg_x(i)}" y="{Y}" width="{SEG}" height="{SEG}" fill="{fill}" opacity="{num(f)}"'
        lines.append(rect + (f'>{anim(i, f)}</rect>' if i >= SHORT else '/>'))
    solid_center = (seg_x(SOLID - 1) + seg_x(0) + SEG) / 2
    ghost_center = (seg_x(N - 1) + seg_x(SOLID) + SEG) / 2
    lines.append(f'<text x="{num(solid_center)}" y="118" text-anchor="middle" fill="#e6e6e6" '
                 f'font-size="22" font-weight="700">{SOLID} solid{anim(SOLID - 1, 1)}</text>')
    lines.append(f'<text x="{num(ghost_center)}" y="118" text-anchor="middle" fill="#9aa4b2" '
                 f'font-size="22" font-weight="700">ghosts{anim(SOLID, 1)}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def table():
    rows = [
        ("Picture canvas", f"{W} × {H} px"),
        ("Segment", f"{SEG} × {SEG} px, one every {PITCH} px (gap {PITCH - SEG} px)"),
        ("Segments, final state", f"{N}: {SOLID} solid (opacity 1) + {N - SOLID} ghosts (opacity {num(GHOST)})"),
        ("Restart length", f"{SHORT} segments"),
        ("Animation", f"{num(DUR)} s, plays once: final state, restart at {num(HOLD_START)} s, "
                      f"one segment every {num(GROW_EVERY)} s, then holds the final state"),
    ]
    out = ["| Dimension | Value |", "| --- | --- |"]
    return "\n".join(out + [f"| {a} | {b} |" for a, b in rows])


def figure():
    """The final state with its dimensions marked (static)."""
    oy = 70  # the snake sits lower than on the slide, to leave room for dimension marks above it
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 210" width="640" height="210" '
           'font-family="system-ui, sans-serif">',
           '<rect width="640" height="210" rx="12" fill="#1b1b1b"/>']
    for i in range(N):
        fill = HEAD_COLOR if i == 0 else BODY_COLOR
        out.append(f'<rect x="{seg_x(i)}" y="{oy}" width="{SEG}" height="{SEG}" fill="{fill}" '
                   f'opacity="{num(final_opacity(i))}"/>')
    red = 'stroke="#e5484d" stroke-width="2"'
    x0, y = seg_x(0), oy - 14
    out += [f'<line x1="{x0}" y1="{y}" x2="{x0 + SEG}" y2="{y}" {red}/>',
            f'<line x1="{x0}" y1="{y - 5}" x2="{x0}" y2="{y + 5}" {red}/>',
            f'<line x1="{x0 + SEG}" y1="{y - 5}" x2="{x0 + SEG}" y2="{y + 5}" {red}/>',
            f'<text x="{x0 + SEG / 2}" y="{y - 10}" text-anchor="middle" fill="#e5484d" font-size="16" font-weight="700">{SEG} px</text>']
    c1, c2 = seg_x(1) + SEG / 2, seg_x(0) + SEG / 2
    y2 = oy + SEG + 14
    out += [f'<line x1="{c1}" y1="{y2}" x2="{c2}" y2="{y2}" {red}/>',
            f'<line x1="{c1}" y1="{y2 - 5}" x2="{c1}" y2="{y2 + 5}" {red}/>',
            f'<line x1="{c2}" y1="{y2 - 5}" x2="{c2}" y2="{y2 + 5}" {red}/>',
            f'<text x="{(c1 + c2) / 2}" y="{y2 + 22}" text-anchor="middle" fill="#e5484d" font-size="16" font-weight="700">{PITCH} px</text>']
    for label, a, b, color in ((f"{SOLID} solid", seg_x(SOLID - 1), seg_x(0) + SEG, "#e6e6e6"),
                               (f"{N - SOLID} ghosts, opacity {num(GHOST)}", seg_x(N - 1), seg_x(SOLID) + SEG, "#9aa4b2")):
        out += [f'<line x1="{a}" y1="{oy + SEG + 50}" x2="{b}" y2="{oy + SEG + 50}" stroke="{color}" stroke-width="2"/>',
                f'<text x="{(a + b) / 2}" y="{oy + SEG + 74}" text-anchor="middle" fill="{color}" font-size="17" font-weight="700">{label}</text>']
    out.append("</svg>")
    return "\n".join(out) + "\n"


def check():
    problems = []
    qmd = (HERE / "snake.qmd").read_text(encoding="utf-8")
    note = (HERE / "NOTE.md").read_text(encoding="utf-8")
    svg = (HERE / "snake-pic.svg").read_text(encoding="utf-8")
    if "{{< include snake-pic.svg >}}" not in qmd:
        problems.append("snake.qmd does not include snake-pic.svg")
    if svg != pic():
        problems.append("snake-pic.svg is out of date; run this script without --check")
    if (HERE / "snake-figure.svg").read_text(encoding="utf-8") != figure():
        problems.append("snake-figure.svg is out of date; run this script without --check")
    for row in table().splitlines():
        if row not in note:
            problems.append(f"NOTE.md: table row missing or different: {row}")
    # The animation contract: first frame = final state, last frame held, plays once.
    if "\n\n" in svg:
        problems.append("snake-pic.svg has a blank line (it would break the include)")
    for m in re.finditer(r'<rect [^>]*opacity="([0-9.]+)"[^>]*>\s*<animate[^>]*values="([^"]+)"', svg):
        base, vals = m.group(1), m.group(2).split(";")
        if not (vals[0] == base == vals[-1]):
            problems.append(f"an animation does not start and end on its final state ({base}): {vals}")
    anims = re.findall(r"<animate [^>]*>", svg)
    if not anims or any('fill="freeze"' not in a or 'repeatCount="1"' not in a for a in anims):
        problems.append("every animation must have fill=freeze and repeatCount=1")
    return problems


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # the table has × and the Windows default code page can't print it
    if "--check" in sys.argv:
        issues = check()
        print("\n".join(issues) if issues else f"ok: slides, note, figures and the game agree (SOLID={SOLID}, ghost opacity={GHOST})")
        sys.exit(1 if issues else 0)
    (HERE / "snake-pic.svg").write_text(pic(), encoding="utf-8")
    (HERE / "snake-figure.svg").write_text(figure(), encoding="utf-8")
    print(table())
