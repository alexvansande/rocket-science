"""
Draw a lightweight schematic of the game board from data/board.json.

    data/board.json ──> build_board.py ──> build/board.svg

The board data is the source of truth (spaces, links, crossing types, parking);
this script only draws it. The digital prototype will read the same JSON.
Run from src/:  python3 build_board.py
"""
import json
import math

B = json.load(open("../data/board.json"))
SP = {s["id"]: s for s in B["spaces"]}

TRACK, TRACK_EDGE = "#fff4d2", "#2a2a2a"
RING = "#fbd97f"
CROSS = {
    "burn": ("#6b6360", None),
    "hatched": ("#6b6360", "3 2"),
    "aero": ("#5aaede", "3 2"),
    "mars_aero": ("#e07a5f", "3 2"),
    "dial": ("#5fb878", None),
    "forced": ("#6b6360", None),
}

# Orbit rings drawn under the tracks: (centre space, radius)
RINGS = [("earth", 237), ("moon", 57), ("mars", 105)]
PLANETS = [("earth", 19, "#3a95c9"), ("moon", 20, "#a8a8a8"), ("mars", 19, "#d9503a")]


RING_R = dict(RINGS)


def endpoint(s, other):
    """Where a link meets space s. Orbit spaces are whole rings, so links attach to
    the ring at the point nearest the other end, not to the orbit's marker."""
    if "ring" not in s:
        return s["x"], s["y"]
    c, r = SP[s["ring"]], RING_R[s["ring"]]
    dx, dy = other["x"] - c["x"], other["y"] - c["y"]
    n = math.hypot(dx, dy) or 1
    return c["x"] + dx / n * r, c["y"] + dy / n * r


def ends(link):
    a, b = SP[link["a"]], SP[link["b"]]
    (x1, y1), (x2, y2) = endpoint(a, b), endpoint(b, a)
    return x1, y1, x2, y2


def track(link):
    x1, y1, x2, y2 = (round(v, 1) for v in ends(link))
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{TRACK_EDGE}" stroke-width="19" stroke-linecap="round"/>',
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{TRACK}" stroke-width="16.5" stroke-linecap="round"/>')


def crossing(link):
    x1, y1, x2, y2 = ends(link)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    px, py = -dy / n * 9, dx / n * 9           # perpendicular half-length
    col, dash = CROSS[link["type"]]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out = f'<line x1="{mx - px:.1f}" y1="{my - py:.1f}" x2="{mx + px:.1f}" y2="{my + py:.1f}" stroke="{col}" stroke-width="3"{d}/>'
    if link["type"] == "forced":                # burn AND skip: grey bar with a green skip bar beside it
        ox, oy = dx / n * 3.5, dy / n * 3.5
        out += (f'<line x1="{mx - px + ox:.1f}" y1="{my - py + oy:.1f}" x2="{mx + px + ox:.1f}" '
                f'y2="{my + py + oy:.1f}" stroke="#5fb878" stroke-width="3" stroke-dasharray="3 2"/>')
    if link.get("consumables"):
        out += (f'<text x="{mx + px * 1.5:.1f}" y="{my + py * 1.5 + 3:.1f}" class="tiny">'
                f'x{link["consumables"]}</text>')
    return out


def marker(s):
    x, y = s["x"], s["y"]
    icon = s.get("icon")
    if icon == "triangle":
        return f'<polygon points="{x - 4},{y + 4} {x + 4},{y + 4} {x},{y - 4}" fill="#1a1a1a"/>'
    if icon == "diamond":
        return f'<rect x="{x - 3.5}" y="{y - 3.5}" width="7" height="7" transform="rotate(45 {x} {y})" fill="#1a1a1a"/>'
    if icon == "rocket":
        return f'<polygon points="{x},{y - 5} {x + 3.5},{y + 4} {x - 3.5},{y + 4}" fill="#b01818"/>'
    if s["park"] and s.get("label") and s["kind"] in ("orbit", "surface") and s["id"] not in ("earth", "mars", "moon"):
        return f'<circle cx="{x}" cy="{y}" r="4" fill="#1a1a1a"/>'
    return ""


def label(s):
    if not s.get("label") or s["id"] in ("earth", "mars", "moon"):
        return ""
    if s["kind"] == "deep":
        return f'<text x="{s["x"]}" y="{s["y"] + 3.5}" class="lad">{s["label"]}</text>'
    if s.get("label_side") == "left":
        return f'<text x="{s["x"] - 8}" y="{s["y"] + 4}" class="lbl" text-anchor="end">{s["label"].upper()}</text>'
    dy = 16 if "ring" in s else -8
    return f'<text x="{s["x"] + 7}" y="{s["y"] + dy}" class="lbl">{s["label"].upper()}</text>'


def main():
    under, over = [], []
    for link in B["links"]:
        u, o = track(link)
        under.append(u); over.append(o)
    rings = "".join(
        f'<circle cx="{SP[c]["x"]}" cy="{SP[c]["y"]}" r="{r}" fill="none" stroke="{TRACK_EDGE}" stroke-width="25"/>'
        f'<circle cx="{SP[c]["x"]}" cy="{SP[c]["y"]}" r="{r}" fill="none" stroke="{RING}" stroke-width="22.5"/>'
        for c, r in RINGS)
    planets = "".join(
        f'<circle cx="{SP[p]["x"]}" cy="{SP[p]["y"]}" r="{r}" fill="{col}" stroke="#1a1a1a" stroke-width="1.2"/>'
        f'<text x="{SP[p]["x"]}" y="{SP[p]["y"] + 3.5}" class="planet">{SP[p]["label"].upper()}</text>'
        for p, r, col in PLANETS)
    legend_items = [("burn", "Burn 1 Δv to cross, either direction"),
                    ("aero", "Free going down with heatshields"),
                    ("dial", "Burn, or skip a turn + eat food (x4 / x2)"),
                    ("forced", "Burn AND skip a turn + 1 food")]
    legend = ""
    for i, (t, txt) in enumerate(legend_items):
        y = 610 + i * 20
        col, dash = CROSS[t]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        legend += f'<line x1="30" y1="{y}" x2="52" y2="{y}" stroke="{col}" stroke-width="4"{d}/>'
        if t == "forced":
            legend += f'<line x1="30" y1="{y + 4}" x2="52" y2="{y + 4}" stroke="#5fb878" stroke-width="3" stroke-dasharray="3 2"/>'
        legend += f'<text x="62" y="{y + 4}" class="leg">{txt}</text>'
    legend += '<circle cx="41" cy="690" r="4" fill="#1a1a1a"/><text x="62" y="694" class="leg">Parking spot   ▲ no parking</text>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 707" width="1000" height="707">
<style>
  text {{ font-family: Helvetica, Arial, sans-serif; fill: #1a1a1a; }}
  .lbl {{ font-size: 11px; font-weight: bold; letter-spacing: 0.3px; }}
  .lad {{ font-size: 10px; font-weight: bold; text-anchor: middle; }}
  .planet {{ font-size: 8.5px; font-weight: bold; text-anchor: middle; }}
  .tiny {{ font-size: 9px; font-weight: bold; }}
  .leg {{ font-size: 11px; font-weight: bold; }}
</style>
<rect width="1000" height="707" fill="#fffdf7"/>
{rings}
{"".join(under)}
{"".join(over)}
{"".join(crossing(l) for l in B["links"])}
{planets}
{"".join(marker(s) for s in B["spaces"])}
{"".join(label(s) for s in B["spaces"])}
{legend}
<text x="440" y="700" class="leg" transform="rotate(-90 440 700)">DEEP SPACE TRAJECTORY</text>
</svg>'''
    with open("../build/board.svg", "w") as f:
        f.write(svg)
    print(f"Wrote ../build/board.svg ({len(svg):,} bytes, {len(B['spaces'])} spaces, {len(B['links'])} links)")


if __name__ == "__main__":
    main()
