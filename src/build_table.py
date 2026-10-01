"""
Tabletop layout: the game as it sits on a real table, at real size (millimetres).

    data/*.json + site/board.webp ──> build_table.py ──> build/table.html

Static setup view: the printed board in the middle, a Space Center board at each of
the four seats, the shared decks / market rows / token bowls between them. No game
logic yet: pan, zoom (wheel / pinch / slider), a soft CSS tilt, and hands you can
flip and pull a card from. Cards are the real kit cards (build_kit renderer).
Run from src/:  python3 build_table.py
"""
import json
import shutil

from build_kit import (load_cards, engine_card_html, equipment_card_html,
                       objective_card_html, bundle_card_html, CSS as KIT_CSS)

DATA, _ = load_cards()
OBJS = json.load(open("../data/objectives.json"))
BOARD = json.load(open("../data/board.json"))
ENG = {e["name"]: e for e in DATA["engines"]}
EQ = {q["name"]: q for q in DATA["equipment"]}
OBJ = {o["name"]: o for o in OBJS}

# ---- geometry (mm) -------------------------------------------------------
TABLE_W, TABLE_H = 1300, 1240
CARD_W, CARD_H, GAP = 47, 66, 6
BOARD_W, BOARD_H = 594, 420            # printed at A2
BOARD_X, BOARD_Y = 353, 410
SEAT_W, SEAT_H = 440, 285              # Space Center board (180 deep) + hand in front
PB_H = 180

PLAYERS = [  # seat, colour, rotation, centre
    ("bottom", "Blue",   "#2f6db5", 0,   (BOARD_X + BOARD_W / 2, 1081)),
    ("left",   "Green",  "#2f8f5b", 90,  (BOARD_X - 20 - SEAT_H / 2, BOARD_Y + BOARD_H / 2)),
    ("top",    "Purple", "#7a4bb0", 180, (BOARD_X + BOARD_W / 2, 152)),
    ("right",  "White",  "#e9e6df", 270, (BOARD_X + BOARD_W + 20 + SEAT_H / 2, BOARD_Y + BOARD_H / 2)),
]

# ---- card registry: every card gets an id; the page's game script uses these ----
def _shown_rows(e):
    """The strip rows exactly as printed on the card (same cut as build_kit)."""
    if e.get("kind") == "fixed" or not e.get("strip"):
        return []
    eq = [r for r in e["strip"] if r.get("eq")]
    tok = [r for r in e["strip"] if not r.get("eq")]
    return tok[: max(0, 9 - len(eq))] + eq


CARDS = {}
for i, e in enumerate(DATA["engines"]):
    CARDS[f"e{i}"] = {"kind": "engine", "name": e["name"], "T": e["total_mass_t"], "ign": e.get("ignition", ""),
                      "carry": e.get("equipment_carry", 0),
                      "rows": [{"cargo": r["cargo_t"], "dv": r["dv"], "eq": r.get("eq", 0)} for r in _shown_rows(e)],
                      "html": engine_card_html(e)}
for i, q in enumerate(DATA["equipment"]):
    CARDS[f"q{i}"] = {"kind": "equipment", "name": q["name"], "T": 2.5, "rows": [], "html": equipment_card_html(q)}
for i, b in enumerate(DATA["bundles"]):
    CARDS[f"b{i}"] = {"kind": "bundle", "name": f"x{b['mult']} {b['token']} BUNDLE", "T": 0, "rows": [],
                      "html": bundle_card_html(b)}
BY_NAME = {c["name"]: cid for cid, c in CARDS.items()}


def cid(name):
    return BY_NAME[name]


# Sample hands. Blue ("bottom") is you: a hand that can reach orbit on the basic pad.
HAND_IDS = {
    "bottom": [cid("KEROLOX SUSTAINER"), cid("LIGHT SOLID BOOSTER"), cid("CREW CAPSULE"),
               cid("ATMOSPHERIC RETURN"), cid("SCIENCE PACKAGE")],
    "left": [cid("HEAVY KEROLOX BOOSTER"), cid("HEAVY HYDROLOX CORE"), cid("HEAVY HYDROLOX UPPER"),
             cid("LARGE ANTENNA"), cid("RTG")],
    "top": [cid("SUPER HEAVY"), cid("STARSHIP"), cid("METHALOX BOOSTER"), cid("SOLAR ARRAY"), cid("ROVER")],
    "right": [cid("HEAVY SOLID BOOSTER"), cid("x2 K BUNDLE"), cid("HYDROLOX DROP TANK"), cid("ORBITER"),
              cid("LANDING GEAR")],
}
HANDS = {k: [CARDS[c]["html"] for c in v] for k, v in HAND_IDS.items()}
MARKET_IDS = [cid("SOLID KICK MOTOR"), cid("HYDROLOX UPPER"), cid("KEROLOX BOOSTER"), cid("CONSUMABLES")]
DECK_IDS = [c for c in CARDS if c not in MARKET_IDS and not any(c in h for h in HAND_IDS.values())]
LAUNCH_TOKENS = "R"         # the basic pad's lift: 1 red = 160t, single-stage suborbital start (docs/07)

# Goals: FIRSTs always open; a 5-card market; the rest shuffle into the missions deck.
# Transient contracts come in "copies" (docs/09); each copy gets its own id (obj17, obj17b, obj17c).
GOALS = {o["id"] + ("" if k == 0 else "bcdefgh"[k - 1]):
         {"name": o["name"], "type": o["type"], "vp": o["vp"], "check": o.get("check"),
          "html": objective_card_html(o)} for o in OBJS for k in range(o.get("copies", 1))}
GOAL_FIRSTS = [o["id"] for o in OBJS if o["type"] == "FIRST"]
GOAL_MARKET = [o["id"] for o in OBJS if o["name"] in
               ("SPECIAL DELIVERY", "UNNAMED PAYLOAD", "INTERCONTINENTAL EXPRESS", "COMSAT", "WEATHER WATCH")]
GOAL_DECK = [g for g in GOALS if g not in GOAL_FIRSTS and g not in GOAL_MARKET]

TOKEN_COLORS = {"K": "#1c1c1c", "R": "#b3261e", "O": "#e07b00", "Y": "#f0b400"}


def at(x, y, w=None, h=None, extra=""):
    size = (f"width:{w}mm;" if w is not None else "") + (f"height:{h}mm;" if h is not None else "")
    return f'style="left:{x}mm;top:{y}mm;{size}{extra}"'


def card(html, x, y, rot=0):
    return f'<div class="slot" {at(x, y, CARD_W, CARD_H, f"transform:rotate({rot}deg);")}>{html}</div>'


CARD_THICK = 0.3   # mm per card


def stack(kind, label, x, y, n, dom_id=None):
    """A face-down deck as a real CSS 3D box: the card back is the top face, lifted
    n x 0.3mm off the table, and four side faces carry a card-edge texture. The
    browser shows whichever sides actually face the viewer (no painted-on side view)."""
    t = round(n * CARD_THICK, 2)
    idattr = f' id="{dom_id}"' if dom_id else ""
    return (f'<div class="deck"{idattr} {at(x, y, CARD_W, CARD_H, f"--t:{t}mm;")}>'
            f'<div class="dshadow"></div>'
            f'<div class="dside front"></div><div class="dside back"></div>'
            f'<div class="dside left"></div><div class="dside right"></div>'
            f'<div class="dtop"><div class="card cback {kind}"><span>{label}</span></div></div></div>')


def zone_label(text, x, y, w=None, align="left"):
    return f'<div class="zlabel" {at(x, y, w, None, f"text-align:{align};")}>{text}</div>'


def _shade(hex_, k):
    """Darken (k<1) or lighten (k>1) a #rrggbb colour."""
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    f = (lambda v: round(v * k)) if k < 1 else (lambda v: round(v + (255 - v) * (k - 1)))
    return "#%02x%02x%02x" % tuple(max(0, min(255, f(v))) for v in (r, g, b))


def tri_svg(color, cls="", style="", rot=0):
    """A delta-shaped wooden cargo meeple. The triangle may be rotated (tokens lie at any angle),
    but its thickness is drawn as darker copies pushed DOWN the screen, so the side always faces
    the viewer the way a real token's does under one light."""
    c, side = TOKEN_COLORS[color], _shade(TOKEN_COLORS[color], .55)
    tri = "12,2.5 21,18 3,18"
    rt = f'transform="rotate({rot:.0f} 12 12.8)"'
    body = "".join(f'<g transform="translate(0 {k * 0.6:.1f})"><polygon points="{tri}" {rt} fill="{side}" '
                   f'stroke="{side}" stroke-width="0.5" stroke-linejoin="round"/></g>' for k in range(5, 0, -1))
    return (f'<svg class="tok {cls}" {style} viewBox="0 0 24 24">{body}'
            f'<polygon points="{tri}" {rt} fill="{c}" stroke="rgba(0,0,0,.3)" stroke-width="0.5" stroke-linejoin="round"/>'
            f'<polygon points="12,2.5 12,13 3,18" {rt} fill="rgba(255,255,255,.17)"/>'
            f'<polyline points="3.7,17.6 12,3.4 20.3,17.6" {rt} fill="none" stroke="rgba(255,255,255,.28)" stroke-width="0.5"/></svg>')


def cargo(color, x, y, rot=0, size=12):
    return tri_svg(color, style=at(x, y, size, size), rot=rot)


# Mission badges: a round wooden disc in the player's colour, one symbol per mission slot
GLYPHS = [
    '<polygon points="12,4.6 13.9,9.6 19.2,9.8 15,13.1 16.5,18.3 12,15.3 7.5,18.3 9,13.1 4.8,9.8 10.1,9.6" fill="{g}"/>',   # star
    '<path d="M15 5.4 A7 7 0 1 0 15 18.6 A5.4 5.4 0 1 1 15 5.4 Z" fill="{g}"/>',                                          # crescent
    '<circle cx="12" cy="12" r="4.3" fill="{g}"/><ellipse cx="12" cy="12" rx="8.2" ry="2.4" fill="none" stroke="{g}" '
    'stroke-width="1.3" transform="rotate(-22 12 12)"/>',                                                                  # ringed planet
    '<polygon points="12.7,6.7 17.3,11.3 5,19" fill="{g}" opacity=".65"/><circle cx="15" cy="9" r="3.3" fill="{g}"/>',     # comet
]
BADGE_NAMES = ["star", "crescent", "ringed planet", "comet"]


def badge_svg(color, i, cls="badge", style=""):
    g = "#2a2a2a" if sum(int(color[k:k + 2], 16) for k in (1, 3, 5)) > 600 else "#ffffff"
    return (f'<svg class="tok {cls}" {style} viewBox="0 0 24 26">'
            f'<circle cx="12" cy="14.3" r="11" fill="{_shade(color, .55)}" stroke="rgba(0,0,0,.45)" stroke-width="0.6"/>'
            f'<circle cx="12" cy="12" r="11" fill="{color}" stroke="rgba(0,0,0,.35)" stroke-width="0.6"/>'
            f'<circle cx="12" cy="12" r="9.3" fill="none" stroke="{g}" stroke-opacity=".45" stroke-width="0.7"/>'
            f'{GLYPHS[i].format(g=g)}</svg>')


def bowl(color, label, cx, cy, r=30):
    import random
    rnd = random.Random(color)
    toks = "".join(cargo(color, cx - 6 + rnd.uniform(-r * 0.5, r * 0.5), cy - 5 + rnd.uniform(-r * 0.45, r * 0.45),
                         rnd.uniform(0, 360)) for _ in range(9))
    return (f'<div class="bowl" id="bowl-{color}" {at(cx - r, cy - r, 2 * r, 2 * r)}></div>{toks}'
            + zone_label(label, cx - r, cy + r + 3, 2 * r, "center"))


# ---- Space Center (player board) -----------------------------------------
ACTIONS = [
    ("RESEARCH", "Buy one card: from the deck, the open market, or your own discard pile."),
    ("LAUNCH", "Put a mission token on Earth. Place <b>1 red</b> cargo token (your pad's 160t) in its mission area. Then take a <b>free Mission Control</b>."),
    ("MISSION CONTROL", "Spend a mission's cargo tokens to place a rocket card on it. Discard the rest, or pass them to another mission (separation)."),
]
TAP = ('<svg viewBox="0 0 20 20" class="tap"><path d="M15 6 A7 7 0 1 0 17 11" fill="none" stroke="currentColor" '
       'stroke-width="2.2" stroke-linecap="round"/><polygon points="12,2 18,6 12,9" fill="currentColor"/></svg>')
MCOL_X, MCOL_W, MCOL_GAP = 172, 62, 4


ACT_KEYS = ["research", "launch", "mc"]


def space_center(name, color, you=False):
    """you=True: the interactive board (ids the game script drives)."""
    acts = "".join(
        f'<div class="action"{f' id="act-{ACT_KEYS[i]}" data-act="{ACT_KEYS[i]}"' if you else ""} {at(8 + i * (CARD_W + 5), 20, CARD_W, CARD_H)}>'
        f'<div class="ahead">{TAP}<span>{t}</span></div><div class="atext">{txt}</div></div>'
        for i, (t, txt) in enumerate(ACTIONS))
    missions = ""
    for i in range(4):
        mx = MCOL_X + i * (MCOL_W + MCOL_GAP)
        slot = f'<div class="cslot" {at(7.5, 9, CARD_W, CARD_H)}><span>rocket</span></div>'
        if you:   # empty shells; the game script fills card, cargo and token
            missions += (f'<div class="marea mcol" id="mcol-{i}" data-i="{i}" {at(mx, 20, MCOL_W, 152)}>'
                         f'<div class="mname">{badge_svg(color, i, "mini-badge")}MISSION {"I II III IV".split()[i]}</div>'
                         f'<div class="ctag" {at(0, 79, MCOL_W, None)}>cargo</div>{slot}'
                         f'<div class="slot mslot" id="mslot-{i}" {at(7.5, 9, CARD_W, CARD_H)}></div>'
                         f'<div class="mcargo" id="mcargo-{i}" {at(2, 86, MCOL_W - 4, 34)}></div>'
                         f'<div class="rest" id="mrest-{i}" {at(23, 126, 16, 20)}></div></div>')
            continue
        body = slot + f'<div class="rest" {at(23, 126, 16, 20)}>{badge_svg(color, i)}</div>'
        missions += (f'<div class="marea" {at(mx, 20, MCOL_W, 152)}><div class="mname">{badge_svg(color, i, "mini-badge")}MISSION {"I II III IV".split()[i]}</div>'
                     f'<div class="ctag" {at(0, 79, MCOL_W, None)}>cargo</div>{body}</div>')
    return f'''<div class="pboard" style="--pc:{color};">
  <div class="pb-title">SPACE CENTER <span>· {name}</span>{' <b id="vp-you" class="vp"></b>' if you else ''}</div>
  {acts}
  <div class="improve"{' id="cgoals-you"' if you else ''} {at(8, 92, 3 * CARD_W + 10, 80)}><span class="cg-hint">completed goals<br>reward side up</span></div>
  {missions}
</div>'''


def seat(seat_name, pname, color, rot, center):
    cx, cy = center
    x, y = cx - SEAT_W / 2, cy - SEAT_H / 2
    cards = HANDS[seat_name]
    n = len(cards)
    fan = ""
    for k, front in enumerate(cards):
        o = k - (n - 1) / 2
        vars_ = (f"--cx:{o * 22:.1f};--cy:{abs(o) * 3:.1f};--cr:{o * 7:.1f};"
                 f"--ox:{o * 44:.1f};--oy:{abs(o) * 2:.1f};--or:{o * 2.5:.1f};z-index:{k + 1};")
        fan += (f'<div class="hc" style="{vars_}"><div class="flip">'
                f'<div class="face back"><div class="card cback rockets"><span>ROCKETS</span></div></div>'
                f'<div class="face front">{front}</div></div></div>')
    you = seat_name == "bottom"
    if you:
        fan = ""   # the game script deals your hand
    fan = f'<div class="hand"{' id="hand-you"' if you else ""} {at(SEAT_W / 2 - CARD_W / 2, PB_H + 14, CARD_W, CARD_H)}>{fan}</div>'
    discard = (f'<div class="dslot"{' id="discard-you"' if you else ""} {at(SEAT_W + 8, 50, CARD_W, CARD_H)}><span>DISCARD</span></div>')
    return (f'<div class="seat" {at(x, y, SEAT_W, SEAT_H, f"transform:rotate({rot}deg);")}>'
            f'{space_center(pname, color, you)}{discard}{fan}'
            f'<div class="zlabel handlabel" {at(0, PB_H + 14 + CARD_H + 16, SEAT_W, None, "text-align:center;")}>{pname} player’s hand</div></div>')


def board_pos(space_id):
    s = next(s for s in BOARD["spaces"] if s["id"] == space_id)
    return BOARD_X + s["x"] / 1000 * BOARD_W, BOARD_Y + s["y"] / 707 * BOARD_H


def main():
    parts = []
    # Main board
    parts.append(f'<img class="mainboard" src="board.webp" alt="Earth to Mars board" draggable="false" {at(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)}>')
    parts.append(f'<div id="boardlayer" {at(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)}></div>')

    # Goals: FIRSTs (always open) + missions deck and 5-card market
    firsts = [o for o in OBJS if o["type"] == "FIRST"]
    fx = BOARD_X - 25
    parts.append(zone_label("FIRSTS · always open", fx, 305))
    for i, o in enumerate(firsts):
        parts.append(f'<div class="slot gslot" id="goal-f{i}" {at(fx + i * (CARD_W + GAP), 318, CARD_W, CARD_H)}>{objective_card_html(o)}</div>')
    mx = fx + 6 * (CARD_W + GAP) + 24
    parts.append(zone_label("MISSIONS · deck + 5 open", mx, 305))
    parts.append(stack("missions", "MISSIONS", mx, 318, len(GOAL_DECK), "deck-missions"))
    for i, gid in enumerate(GOAL_MARKET):
        parts.append(f'<div class="slot gslot" id="goal-m{i}" {at(mx + (i + 1) * (CARD_W + GAP) - 2, 318, CARD_W, CARD_H)}>{GOALS[gid]["html"]}</div>')

    # Rockets & tech: main deck + open market
    ry = BOARD_Y + BOARD_H + 22
    parts.append(zone_label("ROCKETS &amp; TECH · deck + open market", BOARD_X, ry - 13))
    parts.append(stack("rockets", "ROCKETS", BOARD_X, ry, len(DECK_IDS), "deck-rockets"))
    for i, c in enumerate(MARKET_IDS):
        parts.append(f'<div class="slot mkslot" id="mk-{i}" {at(BOARD_X + (i + 1) * (CARD_W + GAP), ry, CARD_W, CARD_H)}>{CARDS[c]["html"]}</div>')

    # Cargo token bowls
    bx = BOARD_X + 5 * (CARD_W + GAP) + 45
    parts.append(zone_label("CARGO TOKENS", bx - 30, ry - 13))
    for i, (c, lbl) in enumerate([("K", "K · 640t"), ("R", "R · 160t"), ("O", "O · 40t"), ("Y", "Y · 10t")]):
        parts.append(bowl(c, lbl, bx + i * 70, ry + 30))

    for s_, pname, color, rot, center in PLAYERS:
        parts.append(seat(s_, pname, color, rot, center))

    game = {
        "cards": CARDS, "deck": DECK_IDS, "hand": HAND_IDS["bottom"], "launch": LAUNCH_TOKENS, "market": MARKET_IDS,
        "you": PLAYERS[0][2], "tokenColors": TOKEN_COLORS,
        "spaces": {sp["id"]: {"x": round(sp["x"] / 1000 * BOARD_W, 2), "y": round(sp["y"] / 707 * BOARD_H, 2),
                              "stop": sp["stop"], "label": sp.get("label", ""), "kind": sp["kind"]} for sp in BOARD["spaces"]},
        "aero": [[l["a"], l["b"]] for l in BOARD["links"] if l["type"] in ("aero", "mars_aero")],
        "links": [[l["a"], l["b"]] for l in BOARD["links"]],
        "board": [BOARD_X, BOARD_Y],
        # camera targets (table mm): your Space Center + hand + discard, and the whole board
        "focusYou": [PLAYERS[0][4][0] - SEAT_W / 2 - 10, PLAYERS[0][4][1] - SEAT_H / 2 - 70,
                     PLAYERS[0][4][0] + SEAT_W / 2 + 60, PLAYERS[0][4][1] + SEAT_H / 2 + 5],
        "focusBoard": [BOARD_X - 10, BOARD_Y - 10, BOARD_X + BOARD_W + 10, BOARD_Y + BOARD_H + 10],
        "focusGoals": [BOARD_X - 35, 296, BOARD_X - 25 + 12 * (CARD_W + GAP) + 30, 392],
        "goals": GOALS, "goalFirsts": GOAL_FIRSTS, "goalMarket": GOAL_MARKET, "goalDeck": GOAL_DECK,
        "tri": {c: tri_svg(c) for c in TOKEN_COLORS},
        "badges": [badge_svg(PLAYERS[0][2], i) for i in range(4)], "badgeNames": BADGE_NAMES,
    }
    game_json = json.dumps(game).replace("</", "<\\/")

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Table Layout</title>
<style>
{KIT_CSS}
{TABLE_CSS}
</style>
</head>
<body>
<div id="viewport">
  <div id="tilt">
    <div id="table" style="width:{TABLE_W}mm;height:{TABLE_H}mm;" data-lamp="{BOARD_X + BOARD_W / 2},{BOARD_Y + BOARD_H / 2},2600">
      {"".join(parts)}
    </div>
  </div>
</div>
<div class="hud">
  <span class="ttl">Rocket Science · table layout</span>
  <button id="zout" aria-label="Zoom out">&minus;</button>
  <input id="zslider" type="range" min="0" max="1000" value="300" aria-label="Zoom">
  <button id="zin" aria-label="Zoom in">+</button>
  <button id="zfit">Fit</button>
  <button id="endturn" class="endturn">End turn</button>
</div>
<div id="toast" role="status"></div>
<div id="prompt" role="status"></div>
<button id="donebtn" hidden>Done loading</button>
<div id="closeup" hidden><div class="cu-inner"><div class="cu-card"></div></div></div>
<script type="application/json" id="game-data">{game_json}</script>
<script>{PANZOOM_JS}</script>
<script>{GAME_JS}</script>
</body>
</html>'''
    with open("../build/table.html", "w") as f:
        f.write(html)
    shutil.copy("../site/board.webp", "../build/board.webp")   # so build/table.html previews locally
    print(f"Wrote ../build/table.html ({len(html):,} bytes)")


TABLE_CSS = r'''
html, body { margin: 0; height: 100%; overflow: hidden; background: #332d29; font-size: 9px; }
#viewport { position: fixed; inset: 0; overflow: hidden; cursor: grab; touch-action: none; user-select: none; -webkit-user-select: none; perspective: 1900px; perspective-origin: 50% 35%; }
#viewport.drag { cursor: grabbing; }
#tilt { position: absolute; inset: 0; transform: rotateX(18deg); transform-origin: 50% 55%; transform-style: preserve-3d; }
#table { position: absolute; left: 0; top: 0; transform-origin: 0 0; will-change: transform; transform-style: preserve-3d; }

#table > *, .seat > *, .pboard > *, .marea > * { position: absolute; }
/* In a preserve-3d context Chrome hit-tests the tilted parent planes in front of their
   children, so the planes ignore the pointer and only the things on the table take it. */
#tilt, #table { pointer-events: none; }
#table > * { pointer-events: auto; }
#viewport img, #viewport svg { -webkit-user-drag: none; user-drag: none; }
.mainboard { border-radius: 2mm; box-shadow: 0 0.6mm 0 #cfc6b4, 0 1.2mm 0 #b9ae98, 0 3mm 8mm rgba(0,0,0,.55); background: #fff; }
.slot > .card { width: 100%; height: 100%; border-radius: 1.8mm; box-shadow: 0 1.2mm 3mm rgba(0,0,0,.45); }
/* 3D decks: a box whose top face is the card back; sides show stacked card edges */
.deck { transform-style: preserve-3d; }
.deck > div { position: absolute; }
.dtop { inset: 0; transform: translateZ(var(--t)); }
.dtop > .card { width: 100%; height: 100%; border-radius: 1.2mm; }
.dside { background: repeating-linear-gradient(var(--dir), #f4efe4 0 0.22mm, #cbc2b1 0.22mm 0.3mm); }
.dside.front { left: 0; top: 100%; width: 100%; height: var(--t); transform-origin: top; transform: rotateX(90deg); --dir: to bottom; filter: brightness(.93); }
.dside.back { left: 0; bottom: 100%; width: 100%; height: var(--t); transform-origin: bottom; transform: rotateX(-90deg); --dir: to bottom; }
.dside.left { top: 0; right: 100%; width: var(--t); height: 100%; transform-origin: right; transform: rotateY(90deg); --dir: to right; filter: brightness(.85); }
.dside.right { top: 0; left: 100%; width: var(--t); height: 100%; transform-origin: left; transform: rotateY(-90deg); --dir: to right; filter: brightness(.85); }
.dshadow { inset: -1mm; border-radius: 3mm; background: rgba(0,0,0,.45); filter: blur(2.2mm); transform: translate(0.8mm, 1.6mm); }
.card.cback span { font-size: 13pt; }
.zlabel { color: rgba(255,236,200,.62); font: 700 3.3mm/1 Helvetica, Arial, sans-serif; letter-spacing: 0.5mm; text-transform: uppercase; white-space: nowrap; }
.tok { filter: drop-shadow(0 0.7mm 0.6mm rgba(0,0,0,.55)); }
.bowl { border-radius: 50%;
  background: radial-gradient(circle at 50% 45%, #3b2718 0 55%, #5a3b22 70%, #8a6038 86%, #4a2f1b 100%);
  box-shadow: 0 2mm 5mm rgba(0,0,0,.5), inset 0 2mm 5mm rgba(0,0,0,.6); }

.pboard { left: 0; top: 0; width: 440mm; height: 180mm; border-radius: 4mm;
  background: linear-gradient(#f7f2e7, #efe7d6); border: 2.2mm solid var(--pc);
  box-shadow: 0 0.6mm 0 #d8cdb6, 0 1.2mm 0 #c3b69c, 0 3mm 8mm rgba(0,0,0,.5); font-family: Helvetica, Arial, sans-serif; color: #1d1d1d; }
.pb-title { left: 8mm; top: 5mm; font-weight: 800; font-size: 5mm; letter-spacing: 0.6mm; }
.pb-title span { font-weight: 600; color: #6b6356; }
.action { background: #fff; border: 0.35mm solid #2a2a2a; border-radius: 1.8mm; overflow: hidden; }
.ahead { display: flex; align-items: center; gap: 1.5mm; background: #1d1d1d; color: #fff; padding: 2mm 2mm; font-weight: 800; font-size: 3.1mm; letter-spacing: 0.2mm; white-space: nowrap; }
.tap { width: 4mm; height: 4mm; color: #f0b400; flex: none; }
.atext { padding: 2.5mm; font-size: 3.1mm; line-height: 1.4; color: #333; }
.improve { border: 0.4mm dashed #b3a78f; border-radius: 1.8mm; color: #a0947c; font-size: 2.8mm; display: flex; align-items: center; justify-content: center; text-align: center; padding: 4mm; }
.marea { border: 0.4mm solid #cbbd9f; border-radius: 1.8mm; background: rgba(255,255,255,.5); }
.mname { left: 3mm; top: 2.5mm; font-weight: 800; font-size: 3mm; letter-spacing: 0.4mm; color: #6b6356; }
.rest { border-radius: 50%; border: 0.4mm dashed #b3a78f; }
.cslot { border: 0.4mm dashed #c9bc9f; border-radius: 1.8mm; display: flex; align-items: center; justify-content: center; }
.cslot span, .ctag { color: #b3a78f; font-size: 2.6mm; font-weight: 700; letter-spacing: 0.4mm; text-transform: uppercase; text-align: center; }
.inflight { font-size: 2.6mm; color: #8a7e66; font-style: italic; text-align: center; }
.dslot { border: 0.5mm dashed rgba(255,236,200,.45); border-radius: 1.8mm; display: flex; align-items: center; justify-content: center; }
.dslot span { color: rgba(255,236,200,.55); font: 700 3mm Helvetica, Arial, sans-serif; letter-spacing: 0.5mm; transform: rotate(-90deg); }
.hand { overflow: visible; }
.hc { position: absolute; inset: 0; cursor: pointer; perspective: 600mm; transform-origin: 50% 130%;
  --x: var(--cx); --y: var(--cy); --r: var(--cr); --s: 1;
  transform: translate(calc(var(--x) * 1mm), calc(var(--y) * 1mm)) rotate(calc(var(--r) * 1deg)) scale(var(--s));
  transition: transform .45s cubic-bezier(.2,.8,.2,1); }
.hand.open .hc { --x: var(--ox); --y: var(--oy); --r: var(--or); }
.hand.open .hc.sel { --y: -62; --r: 0; --s: 1.7; z-index: 20 !important; }
.flip { position: absolute; inset: 0; transform-style: preserve-3d; transition: transform .55s cubic-bezier(.3,.7,.2,1); }
.hand.open .flip { transform: rotateY(180deg); }
.face { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; }
.face.front { transform: rotateY(180deg); }
.face > .card { width: 100%; height: 100%; border-radius: 1.8mm; box-shadow: 0 1.2mm 3mm rgba(0,0,0,.45); }
.hc.sel .face > .card { box-shadow: 0 4mm 10mm rgba(0,0,0,.55); }
.hc.nudge .flip { animation: nudge .35s; }
@keyframes nudge { 25% { transform: rotateY(180deg) rotate(-3deg); } 75% { transform: rotateY(180deg) rotate(3deg); } }
#toast { position: fixed; left: 50%; bottom: 70px; transform: translateX(-50%); background: rgba(25,20,16,.92); color: #f3e6cf;
  font: 600 13px Helvetica, Arial, sans-serif; padding: 10px 16px; border-radius: 8px; opacity: 0; transition: opacity .25s; pointer-events: none; }
#toast.on { opacity: 1; }
.handlabel { font-size: 2.8mm; }

.hud { position: fixed; right: 16px; bottom: 16px; display: flex; align-items: center; gap: 6px; font: 600 12px Helvetica, Arial, sans-serif;
  background: rgba(25,20,16,.55); padding: 6px 8px; border-radius: 22px; }
.hud input[type=range] { width: 140px; accent-color: #d9a441; }
.hud .ttl { color: rgba(255,236,200,.7); margin-right: 8px; }
.hud button { font: 700 14px Helvetica, Arial, sans-serif; min-width: 34px; height: 34px; border-radius: 17px; border: 1px solid rgba(255,236,200,.35);
  background: rgba(30,20,12,.75); color: #f3e6cf; cursor: pointer; padding: 0 12px; }
.hud button:hover { background: rgba(60,40,24,.9); }


/* ---- game: clickable glow, used/free markers, mission columns, board highlights ---- */
@keyframes glow { 0%,100% { box-shadow: 0 0 0 0.5mm rgba(255,196,64,.95), 0 0 2.5mm 0.6mm rgba(255,196,64,.55); }
                  50% { box-shadow: 0 0 0 1.1mm rgba(255,196,64,.6), 0 0 7mm 2.5mm rgba(255,196,64,.3); } }
.action.can, .mslot.can > .card, .mcol.target, .hand.can .face.front > .card { animation: glow 1.4s ease-in-out infinite; }
.action.can, .mslot.can, .mcol.target { cursor: pointer; }
.action { transition: filter .3s, opacity .3s; }
.action.used { filter: grayscale(1); opacity: .55; }
.action.used::after { content: 'USED'; position: absolute; right: 3mm; bottom: 3mm; font: 800 3.2mm Helvetica, Arial, sans-serif; color: #8a2a1a;
  border: 0.5mm solid #8a2a1a; padding: 0.3mm 1.2mm; border-radius: 1mm; transform: rotate(-12deg); }
.action.free .ahead::after { content: 'FREE'; margin-left: auto; background: #f0b400; color: #1d1d1d; font-size: 2.5mm; padding: 0.3mm 1mm; border-radius: 1mm; }
.mcargo { display: flex; flex-wrap: wrap; gap: 1mm; align-content: flex-start; justify-content: center; }
.mcargo .tok { position: static; width: 11mm; height: 11mm; }
.mcargo .tok.spent { opacity: .35; }
.minis { display: flex; gap: 1mm; width: 100%; justify-content: center; }
.mini { width: 16.9mm; height: 23.8mm; flex: none; position: relative; }
.mini > .card { position: absolute; left: 0; top: 0; width: 47mm; height: 66mm; transform: scale(.36); transform-origin: 0 0; border-radius: 3mm;
  box-shadow: 0 1mm 2.5mm rgba(0,0,0,.4); }
.hand.loading .hc:not(.eqc) .face.front > .card { animation: none; filter: grayscale(.8) brightness(.8); }
#donebtn { position: fixed; top: 62px; left: 50%; transform: translateX(-50%); font: 700 14px Helvetica, Arial, sans-serif;
  background: #d9a441; color: #1d1d1d; border: 0; border-radius: 18px; padding: 8px 18px; cursor: pointer; box-shadow: 0 4px 14px rgba(0,0,0,.4); }
#donebtn[hidden] { display: none; }
.eqchip { font-size: 2.6mm; font-weight: 700; color: #1b3a6b; background: #e6ecf5; border-radius: 1mm; padding: 0.6mm 1.2mm; }
.rest .tok { position: absolute; left: 1.5mm; top: 3mm; width: 13mm; height: 14mm; }
.mname .mini-badge { position: static; width: 4.2mm; height: 4.5mm; vertical-align: -1.3mm; margin-right: 1.2mm; filter: none; }
.mkslot.can > .card, #deck-rockets.can .dtop > .card, #discard-you.can > .slot > .card { animation: glow 1.4s ease-in-out infinite; }
.mkslot.can, #deck-rockets.can, #discard-you.can { cursor: pointer; }
.btok.can { pointer-events: auto; cursor: pointer; border-radius: 50%; animation: glow 1.3s ease-in-out infinite; }
.gslot.claim > .card { animation: glow 1.2s ease-in-out infinite; }
.gslot.claim { cursor: pointer; }
.improve .cg { position: absolute; width: 47mm; height: 66mm; }
.improve .cg > .card { width: 100%; height: 100%; border-radius: 1.8mm; box-shadow: 0 1mm 3mm rgba(0,0,0,.35); }
.pb-title .vp { margin-left: 3mm; color: #b8860b; }
.mslot.fired > .card { filter: saturate(.35) brightness(.92); }
.mslot.fired::after { content: 'FIRED'; position: absolute; left: 50%; top: 45%; transform: translate(-50%,-50%) rotate(-14deg);
  font: 800 5mm Helvetica, Arial, sans-serif; color: rgba(140,40,20,.8); border: 0.7mm solid rgba(140,40,20,.8); padding: 0.5mm 2mm; border-radius: 1mm; }
.dslot { overflow: visible; }
.dslot em { position: absolute; right: -2mm; top: -2mm; background: #1d1d1d; color: #fff; font: 700 3mm Helvetica; font-style: normal; border-radius: 3mm; padding: 0.5mm 1.5mm; }
.flycard { position: absolute; width: 47mm; height: 66mm; z-index: 50; pointer-events: none; transform: translateZ(18mm);
  transition: left 1.1s cubic-bezier(.3,.7,.2,1), top 1.1s cubic-bezier(.3,.7,.2,1); }
.flytok { position: absolute; width: 11mm; height: 11mm; z-index: 50; pointer-events: none; transform: translateZ(14mm);
  transition: left .9s cubic-bezier(.3,.7,.2,1), top .9s cubic-bezier(.3,.7,.2,1); }
.flytok .tok { width: 100%; height: 100%; }
#boardlayer { pointer-events: none; }
.btok { position: absolute; width: 10mm; height: 10.8mm; margin: -5.4mm 0 0 -5mm; pointer-events: none;
  transition: left 1.4s cubic-bezier(.3,.7,.2,1), top 1.4s cubic-bezier(.3,.7,.2,1); }
.btok .tok { position: static; width: 100%; height: 100%; }

@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.2); } }
.hl { position: absolute; width: 9mm; height: 9mm; margin: -4.5mm 0 0 -4.5mm; border-radius: 50%; pointer-events: auto; cursor: pointer;
  border: 0.8mm solid #ffbf3c; background: rgba(255,191,60,.3); animation: pulse 1.2s ease-in-out infinite; }
.hl.nopark { border-style: dashed; border-color: #ff7a2e; background: rgba(255,122,46,.18); }
.hl.here { border-color: #fff; background: rgba(255,255,255,.3); }
.hl:hover { background: rgba(255,191,60,.7); }
.hl::before { content: ''; position: absolute; inset: -3mm; border-radius: 50%; }   /* bigger, invisible click target */

#prompt { position: fixed; top: 14px; left: 50%; transform: translateX(-50%); max-width: min(92vw, 760px); text-align: center;
  background: rgba(25,20,16,.88); color: #f3e6cf; font: 600 14px/1.4 Helvetica, Arial, sans-serif; padding: 9px 18px; border-radius: 20px;
  opacity: 0; transition: opacity .25s; pointer-events: none; }
#prompt.on { opacity: 1; }
#closeup { position: fixed; inset: 0; background: rgba(20,15,10,.62); display: flex; align-items: center; justify-content: center; z-index: 5; }
#closeup[hidden] { display: none; }
.cu-inner { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.cu-card { --cuz: 3; width: 47mm; height: 66mm; transform: scale(var(--cuz));
  margin: calc(33mm * (var(--cuz) - 1)) calc(23.5mm * (var(--cuz) - 1)); }
.cu-card > .card { width: 100%; height: 100%; border-radius: 1.5mm; box-shadow: 0 2mm 8mm rgba(0,0,0,.5); }
#closeup tr.pick { cursor: pointer; }
#closeup tr.pick:hover td { background: #ffe29a; }
.hud .endturn { background: #d9a441; color: #1d1d1d; border-color: #d9a441; }
.hud .endturn:hover { background: #e9b451; }

/* phones: last, so these win over the base rules above */
@media (max-width: 600px) {
  .hud .ttl { display: none; } .hud input[type=range] { width: 80px; }
  .hud { right: 8px; left: 8px; bottom: 8px; justify-content: space-between; }
  #prompt { top: 8px; font-size: 12px; line-height: 1.35; padding: 6px 12px; border-radius: 12px; max-width: 94vw; }
  #toast { bottom: 76px; font-size: 12px; max-width: 90vw; text-align: center; }
  #donebtn { top: auto; bottom: 120px; }
}
'''

PANZOOM_JS = r'''
(() => {
  const vp = document.getElementById('viewport'), tb = document.getElementById('table');
  const slider = document.getElementById('zslider'), toast = document.getElementById('toast');
  const W = tb.offsetWidth, H = tb.offsetHeight;
  const MIN = 0.1, MAX = 4, TILT = Math.cos(18 * Math.PI / 180);
  let s = 1, x = 0, y = 0;

  // ---- view --------------------------------------------------------------
  const toSlider = v => Math.round(1000 * Math.log(v / MIN) / Math.log(MAX / MIN));
  const fromSlider = v => MIN * Math.pow(MAX / MIN, v / 1000);
  // Lamp: a warm pool of light over the board, painted on the viewport background (a giant
  // element would get clipped by the GPU's max layer size), following pan and zoom.
  const MM = 96 / 25.4, [lcx, lcy, lr] = tb.dataset.lamp.split(',').map(Number);
  const lamp = () => {
    const px = x + lcx * MM * s, py = innerHeight * 0.55 + (y + lcy * MM * s - innerHeight * 0.55) * TILT, r = lr * MM * s;
    vp.style.background = `radial-gradient(circle ${r}px at ${px}px ${py}px, #8a7c70 0%, #75685d 12%, #5e534a 26%, #4a413b 42%, #3b3430 62%, #332d29 80%) #332d29`;
  };
  const apply = () => { tb.style.transform = `translate(${x}px,${y}px) scale3d(${s},${s},${s})`; slider.value = toSlider(s); lamp(); };
  const fit = () => {
    s = Math.min(innerWidth / W, innerHeight / (H * TILT)) * 0.9;
    x = (innerWidth - W * s) / 2; y = (innerHeight - H * s) / 2; apply();
  };
  const zoomAt = (ns, cx, cy) => {
    ns = Math.min(MAX, Math.max(MIN, ns));
    x = cx - (cx - x) * ns / s; y = cy - (cy - y) * ns / s; s = ns; apply();
  };
  // Scroll (wheel, trackpad, Magic Mouse) always zooms toward the pointer; drag pans.
  // Camera: glide to a table-mm rectangle (used by the game to follow the action).
  // Any wheel/drag by the player stops a glide in progress.
  let anim = null;
  const stopAnim = () => { if (anim) cancelAnimationFrame(anim); anim = null; };
  const focus = ([x0, y0, x1, y1], maxZoom = 1.6) => {
    stopAnim();
    const ts = Math.min(MAX, maxZoom, innerWidth / ((x1 - x0) * MM), innerHeight / ((y1 - y0) * MM * TILT)) * 0.88;
    const tc = [(x0 + x1) / 2, (y0 + y1) / 2];
    const c0 = [(innerWidth / 2 - x) / (MM * s), (innerHeight * 0.55 - y) / (MM * s)], s0 = s, t0 = performance.now();
    const step = now => {
      const k = Math.min(1, (now - t0) / 650), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      s = s0 * Math.pow(ts / s0, e);
      const cx = c0[0] + (tc[0] - c0[0]) * e, cy = c0[1] + (tc[1] - c0[1]) * e;
      x = innerWidth / 2 - cx * MM * s; y = innerHeight * 0.55 - cy * MM * s; apply();
      anim = k < 1 ? requestAnimationFrame(step) : null;
    };
    anim = requestAnimationFrame(step);
  };
  window.view = { focus };
  vp.addEventListener('wheel', e => {
    e.preventDefault(); stopAnim();
    const dy = e.deltaMode === 1 ? e.deltaY * 40 : e.deltaMode === 2 ? e.deltaY * 800 : e.deltaY;
    const k = e.ctrlKey ? 0.01 : 0.002;                                                        // ctrl = trackpad pinch
    zoomAt(s * Math.exp(-Math.max(-150, Math.min(150, dy)) * k), e.clientX, e.clientY);
  }, { passive: false });
  vp.addEventListener('dragstart', e => e.preventDefault());
  slider.addEventListener('input', () => stopAnim() || zoomAt(fromSlider(+slider.value), innerWidth / 2, innerHeight / 2));
  document.getElementById('zin').onclick = () => zoomAt(s * 1.3, innerWidth / 2, innerHeight / 2);
  document.getElementById('zout').onclick = () => zoomAt(s / 1.3, innerWidth / 2, innerHeight / 2);
  document.getElementById('zfit').onclick = fit;
  // Resizing keeps whatever is at the centre of the screen there (no snap back to fit)
  let vw = innerWidth, vh = innerHeight;
  addEventListener('resize', () => { x += (innerWidth - vw) / 2; y += (innerHeight - vh) / 2; vw = innerWidth; vh = innerHeight; apply(); });

  // ---- hands ---------------------------------------------------------------
  let toastTimer;
  const say = msg => { toast.textContent = msg; toast.classList.add('on'); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('on'), 2200); };
  const closeAll = except => document.querySelectorAll('.hand.open').forEach(h => {
    if (h === except) return; h.classList.remove('open'); h.querySelectorAll('.hc.sel').forEach(c => c.classList.remove('sel'));
  });
  const tap = target => {
    if (window.game && game.tap(target)) { closeAll(document.getElementById('hand-you')); return; }
    const card = target.closest && target.closest('.hc');
    if (!card) { closeAll(); return; }                        // anything else flips hands back
    const hand = card.parentElement;
    if (!hand.classList.contains('open')) { closeAll(hand); hand.classList.add('open'); return; }   // flip the whole hand
    if (card.classList.contains('sel')) {                     // second click: activate (needs the engine)
      card.classList.remove('nudge'); void card.offsetWidth; card.classList.add('nudge');
      say('Playing a card needs the game engine. Coming next.'); return;
    }
    hand.querySelectorAll('.hc.sel').forEach(c => c.classList.remove('sel'));
    card.classList.add('sel');                                // first click: pull it forward
  };

  // ---- pointers: drag pans, pinch zooms, a still tap clicks ----------------
  const pts = new Map(); let pinch = null, moved = false, downAt = null;
  vp.addEventListener('pointerdown', e => {
    if (e.button > 0) return;
    stopAnim();
    e.preventDefault();                                   // no native image drag / text selection
    pts.set(e.pointerId, e); moved = false; downAt = { x: e.clientX, y: e.clientY, t: e.target }; pinch = null;
  });
  vp.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    const prev = pts.get(e.pointerId); pts.set(e.pointerId, e);
    if (!moved && downAt && Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) < 5 && pts.size === 1) return;
    if (!moved) { moved = true; vp.setPointerCapture(e.pointerId); vp.classList.add('drag'); }
    if (pts.size === 1) { x += e.clientX - prev.clientX; y += (e.clientY - prev.clientY) / TILT; apply(); }
    else if (pts.size === 2) {
      const [a, b] = [...pts.values()];
      const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      const mx = (a.clientX + b.clientX) / 2, my = (a.clientY + b.clientY) / 2;
      if (pinch) { x += mx - pinch.mx; y += my - pinch.my; zoomAt(s * d / pinch.d, mx, my); }
      pinch = { d, mx, my };
    }
  });
  const up = e => {
    if (!pts.has(e.pointerId)) return;
    pts.delete(e.pointerId);
    if (!moved && downAt && !pts.size && e.type === 'pointerup') tap(downAt.t);
    if (!pts.size) { vp.classList.remove('drag'); pinch = null; downAt = null; }
  };
  vp.addEventListener('pointerup', up); vp.addEventListener('pointercancel', up);
  addEventListener('keydown', e => { if (e.key === 'Escape') closeAll(); });

  // #view=x,y,zoom (table mm + scale) opens on a given spot: handy for sharing a view
  const m = location.hash.match(/view=([\d.]+),([\d.]+),([\d.]+)/);
  if (m) { s = +m[3]; x = innerWidth / 2 - m[1] * MM * s; y = innerHeight * 0.55 - m[2] * MM * s; apply(); }
  else fit();
})();
'''

GAME_JS = r'''
// Minimal game loop for YOUR seat (Blue): Research, Launch, Mission Control, fire a
// rocket (pick a row), move the spacecraft, End turn. State lives here; the table
// HTML is the view. No rules engine yet beyond what these actions need.
(() => {
  const G = JSON.parse(document.getElementById('game-data').textContent);
  const MM = 96 / 25.4, $ = id => document.getElementById(id);
  const VAL = { K: 640, R: 160, O: 40, Y: 10 }, ROMAN = ['I', 'II', 'III', 'IV'];
  const shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const mass = toks => toks.reduce((m, t) => m + VAL[t], 0);
  const tokensFor = t => { const out = []; for (const k of 'KROY') while (t >= VAL[k] - 1e-9) { out.push(k); t -= VAL[k]; } return out; };
  const tri = (c, cls = '') => G.tri[c].replace('class="tok ', `class="tok ${cls} `);
  const BACK = '<div class="card cback rockets"><span>ROCKETS</span></div>';
  const adj = {}; for (const [a, b] of G.links) { (adj[a] = adj[a] || []).push(b); (adj[b] = adj[b] || []).push(a); }
  const aadj = {}; for (const [a, b] of G.aero) { (aadj[a] = aadj[a] || []).push(b); (aadj[b] = aadj[b] || []).push(a); }

  const st = {
    turn: 1, deck: shuffle(G.deck.slice()), hand: G.hand.slice(), discard: [], market: G.market.slice(),
    used: { research: false, launch: false, mc: false }, freeMC: 0,
    missions: [0, 1, 2, 3].map(i => ({ i, active: false, space: null, tokens: [], paid: false, eq: 0, equip: [], card: null, fired: false })),
    mode: 'idle', handOpen: false, sel: null, pending: null, firing: null, move: null, load: null,
    goals: { firsts: G.goalFirsts.slice(), market: G.goalMarket.slice(), deck: shuffle(G.goalDeck.slice()), mine: [] },
    vp: 0, claimable: [], afterClaim: null,
  };
  const hand = $('hand-you'), toastEl = $('toast'), promptEl = $('prompt'), closeup = $('closeup');

  // ---- helpers --------------------------------------------------------------
  let tt; const toast = msg => { toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('on'), 2800); };
  const prompt = msg => { promptEl.textContent = msg || idlePrompt(); promptEl.classList.add('on'); };
  const idlePrompt = () => innerWidth < 600 ? `Turn ${st.turn} · tap anything glowing, then End turn.`
    : `Turn ${st.turn} · Research, Launch or Mission Control (glowing), click a glowing rocket to fire it, or a glowing badge to aerobrake home. Then End turn.`;
  const posOf = el => { let x = 0, y = 0; while (el && el.id !== 'table') { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; } return { x: x / MM, y: y / MM }; };
  const centerOf = el => { const p = posOf(el); return { x: p.x + el.offsetWidth / MM / 2, y: p.y + el.offsetHeight / MM / 2 }; };
  function flyTokens(list, fromOf, toOf, done) {               // wooden deltas hop one by one, lifted off the table
    if (!list.length) return done && done();
    let left = list.length;
    list.forEach((c, i) => setTimeout(() => {
      const spread = (i - (list.length - 1) / 2) * 11;
      const a = centerOf(fromOf(c, i)), b = centerOf(toOf(c, i)), f = document.createElement('div');
      f.className = 'flytok'; f.innerHTML = G.tri[c];
      f.style.left = (a.x - 5) + 'mm'; f.style.top = (a.y - 5) + 'mm';
      $('table').appendChild(f); void f.offsetWidth;
      f.style.left = (b.x - 5 + spread) + 'mm'; f.style.top = (b.y - 5) + 'mm';
      let fin = false; const end = () => { if (fin) return; fin = true; f.remove(); if (--left === 0) done && done(); };
      f.addEventListener('transitionend', e => e.propertyName === 'top' && end()); setTimeout(end, 1300);
    }, i * 200));
  }
  function fly(html, fromEl, toEl, done) {                    // a card lifted off the table and slid across
    const a = posOf(fromEl), b = posOf(toEl), f = document.createElement('div');
    f.className = 'slot flycard'; f.innerHTML = html; f.style.left = a.x + 'mm'; f.style.top = a.y + 'mm';
    $('table').appendChild(f); void f.offsetWidth;
    f.style.left = b.x + 'mm'; f.style.top = b.y + 'mm';
    let fin = false; const end = () => { if (fin) return; fin = true; f.remove(); done && done(); };
    f.addEventListener('transitionend', e => e.propertyName === 'top' && end()); setTimeout(end, 1500);
  }
  function reach(from, n) {                                    // spaces within n crossings (1 dv each)
    const d = { [from]: 0 }, q = [from], par = {};
    while (q.length) { const s = q.shift(); if (d[s] >= n) continue; for (const t of adj[s] || []) if (!(t in d)) { d[t] = d[s] + 1; par[t] = s; q.push(t); } }
    Object.defineProperty(d, 'par', { value: par });
    return d;
  }
  const pendingCard = () => st.pending == null ? null : G.cards[st.hand[st.pending]];
  const lightsOnEarth = c => ['earth', 'both'].includes(c.ign);
  const cam = r => window.view && window.view.focus(r);
  const camYou = () => cam(G.focusYou);
  function camReach(d) {                                      // frame every reachable space, with margin
    const pts = Object.keys(d).map(k => G.spaces[k]);
    const xs = pts.map(p => p.x + G.board[0]), ys = pts.map(p => p.y + G.board[1]);
    let x0 = Math.min(...xs) - 30, x1 = Math.max(...xs) + 30, y0 = Math.min(...ys) - 30, y1 = Math.max(...ys) + 30;
    const w = Math.max(x1 - x0, 180), h = Math.max(y1 - y0, 120), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    cam([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]);
  }
  const spendable = m => m.active && m.tokens.length > 0;
  const eligible = m => { const c = pendingCard(); if (!c || !m.active) return false;
    if (c.kind === 'equipment') return spendable(m);
    return !m.paid && mass(m.tokens) >= c.T - 1e-9 && (m.space !== 'earth' || lightsOnEarth(c)); };
  const reason = m => { const c = pendingCard(); if (!m.active) return 'That mission slot is empty. Launch first.';
    if (c.kind === 'equipment') return `Mission ${ROMAN[m.i]} has no cargo tokens left to turn into equipment.`;
    if (m.paid) return `Mission ${ROMAN[m.i]} already has a rocket waiting to fire.`;
    if (mass(m.tokens) < c.T) return `Mission ${ROMAN[m.i]} has ${mass(m.tokens)}t of cargo; ${c.name} costs ${c.T}t.`;
    return `${c.name} can't light on Earth. It's an upper stage.`; };

  // ---- view -----------------------------------------------------------------
  function buildHand() {
    const n = st.hand.length, squeeze = Math.min(1, 5 / Math.max(n, 1)), spread = n > 6 ? 264 / n : 44;
    hand.innerHTML = st.hand.map((id, k) => { const o = k - (n - 1) / 2;
      return `<div class="hc${G.cards[id].kind === 'equipment' ? ' eqc' : ''}" data-k="${k}" style="--cx:${(o * 22 * squeeze).toFixed(1)};--cy:${(Math.abs(o) * 3).toFixed(1)};--cr:${(o * 7 * squeeze).toFixed(1)};--ox:${(o * spread).toFixed(1)};--oy:${(Math.abs(o) * 2).toFixed(1)};--or:${(o * 2.5).toFixed(1)};z-index:${k + 1}"><div class="flip"><div class="face back">${BACK}</div><div class="face front">${G.cards[id].html}</div></div></div>`; }).join('');
  }
  function syncHand() {
    void hand.offsetWidth;                                     // let a freshly built hand flip, not jump
    hand.classList.toggle('open', st.handOpen);
    hand.querySelectorAll('.hc').forEach((el, k) => el.classList.toggle('sel', st.sel === k));
  }
  function can() {
    const idle = st.mode === 'idle';
    return {
      research: idle && !st.used.research && (st.deck.length > 0 || st.market.some(Boolean) || st.discard.length > 0),
      launch: idle && !st.used.launch && st.missions.some(m => !m.active),
      mc: idle && (!st.used.mc || st.freeMC > 0) && st.missions.some(spendable),
    };
  }
  function render() {
    const c = can();
    for (const k of ['research', 'launch', 'mc']) {
      const el = $('act-' + k);
      el.classList.toggle('used', st.used[k] && !(k === 'mc' && st.freeMC > 0));
      el.classList.toggle('can', c[k]);
      el.classList.toggle('free', k === 'mc' && st.freeMC > 0);
    }
    for (const m of st.missions) {
      const slot = $('mslot-' + m.i);
      slot.innerHTML = m.card ? G.cards[m.card].html : '';
      slot.classList.toggle('fired', !!m.card && m.fired);
      slot.classList.toggle('can', st.mode === 'idle' && !!m.card && !m.fired);
      $('mcargo-' + m.i).innerHTML = m.tokens.map(t => tri(t, m.paid ? 'spent' : '')).join('')
        + (st.load && st.load.m === m ? `<span class="eqchip">${st.load.n} slot${st.load.n > 1 ? 's' : ''} to fill</span>` : '')
        + (m.equip.length ? `<div class="minis">${m.equip.map(e => `<div class="mini" title="${G.cards[e].name}">${G.cards[e].html}</div>`).join('')}</div>` : '');
      $('mrest-' + m.i).innerHTML = m.active ? '' : G.badges[m.i];
      $('mcol-' + m.i).classList.toggle('target', st.mode === 'mc-target' && eligible(m));
      let bt = $('btok-' + m.i);
      if (m.active) {
        if (!bt) { bt = document.createElement('div'); bt.id = 'btok-' + m.i; bt.className = 'btok'; bt.title = `Mission ${ROMAN[m.i]} (${G.badgeNames[m.i]})`; bt.innerHTML = G.badges[m.i]; $('boardlayer').appendChild(bt); }
        const p = G.spaces[m.space], off = st.missions.filter(o => o.active && o.space === m.space && o.i < m.i).length;
        bt.style.left = (p.x + off * 5) + 'mm'; bt.style.top = p.y + 'mm';
      } else if (bt) bt.remove();
    }
    hand.classList.toggle('can', st.mode === 'mc-pick' || st.mode === 'load');
    hand.classList.toggle('loading', st.mode === 'load');
    $('donebtn').hidden = st.mode !== 'load';
    const deck = $('deck-rockets');
    deck.style.setProperty('--t', (st.deck.length * 0.3).toFixed(2) + 'mm'); deck.style.visibility = st.deck.length ? '' : 'hidden';
    renderGoals();
    st.market.forEach((id, i) => { const el = $('mk-' + i);
      if (el.dataset.id !== (id || '')) { el.innerHTML = id ? G.cards[id].html : ''; el.dataset.id = id || ''; }
      el.classList.toggle('can', st.mode === 'research' && !!id); });
    $('deck-rockets').classList.toggle('can', st.mode === 'research' && st.deck.length > 0);
    $('discard-you').classList.toggle('can', st.mode === 'research' && st.discard.length > 0);
    for (const m of st.missions) { const bt = $('btok-' + m.i); if (bt) bt.classList.toggle('can', st.mode === 'idle' && !!aeroPath(m)); }
    const top = st.discard[st.discard.length - 1], ds = $('discard-you');
    ds.innerHTML = top ? `<div class="slot" style="inset:0">${G.cards[top].html}</div><em>${st.discard.length}</em>` : '<span>DISCARD</span>';
  }

  // ---- actions --------------------------------------------------------------
  function research() {                                        // choose: top of the deck, an open market card, or your discard
    st.mode = 'research'; render();
    cam([G.board[0] - 10, G.board[1] + 400, G.board[0] + 360, G.board[1] + 520]);
    prompt(`Research: take the top card of the deck${st.market.some(Boolean) ? ', one of the open market cards' : ''}${st.discard.length ? ', or the top of your discard pile' : ''}.`);
  }
  function takeCard(id, fromEl, faceUp, after) {
    st.used.research = true; st.mode = 'anim'; render();
    fly(faceUp ? G.cards[id].html : BACK, fromEl, hand, () => {
      after && after();
      st.hand.push(id); buildHand(); st.mode = 'idle'; st.handOpen = true; st.sel = st.hand.length - 1; syncHand(); render(); camYou();
      toast(`Research: ${G.cards[id].name} joins your hand.`); prompt();
    });
  }
  const researchDeck = () => takeCard(st.deck.pop(), $('deck-rockets'), false);
  function researchMarket(i) {
    const id = st.market[i]; st.market[i] = null; render();
    takeCard(id, $('mk-' + i), true, () => { st.market[i] = st.deck.pop() || null; });
  }
  const researchDiscard = () => takeCard(st.discard.pop(), $('discard-you'), true);
  function launch() {
    const m = st.missions.find(m => !m.active), toks = G.launch.split('');
    Object.assign(m, { active: true, space: 'earth', tokens: [], paid: false, eq: 0, equip: [], card: null, fired: false, visited: ['earth'], arrived: st.turn });
    st.used.launch = true; st.freeMC++; st.mode = 'anim';
    render(); camYou();
    setTimeout(() => flyTokens(toks, c => $('bowl-' + c), () => $('mcargo-' + m.i), () => {
      m.tokens = toks; st.mode = 'idle'; render();
      toast(`Mission ${ROMAN[m.i]} is on the pad with ${mass(m.tokens)}t of lift.`);
      startMC();
    }), 500);
  }
  function startMC() {
    st.mode = 'mc-pick'; st.handOpen = true; st.sel = null; syncHand(); render(); camYou();
    prompt(`Mission Control${st.freeMC ? ' (free)' : ''}: pick a rocket from your hand, then click it again to confirm. Click the table to cancel.`);
  }
  function handClick(k) {
    if (st.mode === 'mc-pick') {
      if (st.sel !== k) { st.sel = k; syncHand(); return; }
      const c = G.cards[st.hand[k]];
      if (c.kind === 'bundle') return toast('Bundles can\'t be played yet. Coming soon.');
      if (c.kind === 'engine' && !c.rows.length) return toast(`${c.name} is a fixed-function card; it can't be flown yet.`);
      st.pending = k;
      const ok = st.missions.filter(eligible);
      if (!ok.length) { const m = st.missions.find(m => m.active) || st.missions[0]; toast(reason(m)); st.pending = null; return; }
      if (ok.length === 1) return place(ok[0]);               // only one mission can take it: no need to ask
      st.mode = 'mc-target'; st.handOpen = false; syncHand(); render();
      return prompt(`Choose the glowing mission for ${c.name}${c.kind === 'equipment' ? ' (uses 1 equipment slot)' : ` (costs ${c.T}t)`}.`);
    }
    if (st.mode === 'load') {
      if (G.cards[st.hand[k]].kind !== 'equipment') return toast('Only equipment cards can fill these slots.');
      if (st.sel !== k) { st.sel = k; return syncHand(); }
      return loadCard(k);
    }
    if (st.mode !== 'idle') return;
    if (!st.handOpen) { st.handOpen = true; st.sel = null; return syncHand(); }
    if (st.sel === k) return toast('Play cards with Mission Control.');
    st.sel = k; syncHand();
  }
  function place(m) {
    const k = st.pending, id = st.hand[k], c = G.cards[id], old = m.card;
    if (st.freeMC > 0) st.freeMC--; else st.used.mc = true;
    st.hand.splice(k, 1); st.pending = null; st.sel = null; st.mode = 'idle'; st.handOpen = false;
    buildHand(); syncHand();
    if (c.kind === 'equipment') {          // break the smallest token into slots; this card takes one,
      const t = [...m.tokens].sort((a, b) => VAL[a] - VAL[b])[0];   // the rest must be filled now or are lost
      m.tokens.splice(m.tokens.indexOf(t), 1);
      const slots = VAL[t] / 2.5;
      render(); flyTokens([t], () => $('mcargo-' + m.i), () => $('bowl-' + t), null);
      return fly(c.html, hand, $('mcargo-' + m.i), () => {
        m.equip.push(id); render();
        toast(`${c.name} is aboard Mission ${ROMAN[m.i]}. Your ${t} token made ${slots} equipment slots.`);
        startLoad(m, slots - 1, null);
      });
    }
    const from = hand; render();
    fly(c.html, from, $('mslot-' + m.i), () => {
      if (old) st.discard.push(old);
      m.card = id; m.fired = false; m.paid = true; render();
      prompt(`Click ${c.name} on Mission ${ROMAN[m.i]} to fire it.`);
    });
  }
  function openCloseup(m) {
    const c = G.cards[m.card];
    st.mode = 'row'; st.firing = m;
    const box = closeup.querySelector('.cu-card');
    box.innerHTML = c.html;
    box.style.setProperty('--cuz', Math.min(3.6, innerHeight * 0.78 / (66 * MM), innerWidth * 0.9 / (47 * MM)).toFixed(2));
    box.querySelectorAll('table.strip tr').forEach((tr, r) => { tr.classList.add('pick'); tr.dataset.r = r; });
    closeup.hidden = false; render();
    prompt(`${c.name}: pick a row. Its tokens stay aboard; its Δv is how far you can move.`);
  }
  function pickRow(r) {
    const m = st.firing, c = G.cards[m.card], row = c.rows[r];
    const had = mass(m.tokens), spare = had - c.T;
    closeup.hidden = true;
    const old = m.tokens.slice(), fresh = row.eq ? [] : tokensFor(row.cargo);
    const slots = (row.eq || 0) + (c.carry || 0);
    m.tokens = []; m.paid = false; m.fired = true; st.mode = 'anim'; render();
    toast(`Paying ${c.T}t${spare > 0 ? ` (${spare}t left over, discarded)` : ''}…`);
    flyTokens(old, () => $('mcargo-' + m.i), t => $('bowl-' + t), () =>          // spent cargo back to the bowls
      setTimeout(() => flyTokens(fresh, t => $('bowl-' + t), () => $('mcargo-' + m.i), () => {   // the row's cargo aboard
        m.tokens = fresh; st.mode = 'idle'; render();
        toast(`Paid ${c.T}t${spare > 0 ? `, ${spare}t discarded` : ''}.${row.eq ? '' : ` ${row.cargo}t aboard.`}${slots ? ` ${slots} equipment slot${slots > 1 ? 's' : ''} to fill now.` : ''}`);
        const go = () => startMove(m, row.dv);
        slots ? startLoad(m, slots, go) : go();
      }), 250));
  }
  function startMove(m, dv) {
    st.mode = 'move'; st.move = { m, reach: reach(m.space, dv) };
    render(); showReach(); camReach(st.move.reach);
    prompt(`Move Mission ${ROMAN[m.i]} up to ${dv} space${dv > 1 ? 's' : ''}: click a glowing space. Dashed = you can't end your turn there.`);
  }
  // Equipment slots are never kept (there's no token for them): fill them from your hand now, or lose them.
  const equipInHand = () => st.hand.some(id => G.cards[id].kind === 'equipment');
  function startLoad(m, n, then) {
    if (n <= 0) return then && then();
    if (!equipInHand()) { toast(`No equipment in your hand: ${n} slot${n > 1 ? 's' : ''} lost.`); return then && then(); }
    st.mode = 'load'; st.load = { m, n, then }; st.handOpen = true; st.sel = null;
    syncHand(); render(); camYou();
    prompt(`Load up to ${n} equipment card${n > 1 ? 's' : ''} onto Mission ${ROMAN[m.i]}: click one, then again to load it. Done when finished; unfilled slots are lost.`);
  }
  function loadCard(k) {
    const L = st.load, id = st.hand[k], c = G.cards[id];
    st.hand.splice(k, 1); st.sel = null; L.n--;
    buildHand(); syncHand(); render();
    fly(c.html, hand, $('mcargo-' + L.m.i), () => {
      L.m.equip.push(id); render();
      if (L.n <= 0 || !equipInHand()) finishLoad();
      else prompt(`Load up to ${L.n} more equipment card${L.n > 1 ? 's' : ''}, or Done.`);
    });
  }
  function finishLoad() {
    const L = st.load; if (!L) return;
    st.load = null; st.mode = 'idle'; st.handOpen = false; st.sel = null; syncHand(); render();
    if (L.n > 0) toast(`${L.n} equipment slot${L.n > 1 ? 's' : ''} left empty and lost.`);
    if (L.then) L.then(); else if (!checkGoals()) prompt();
  }
  function showReach() {
    const layer = $('boardlayer'), { m, reach: d } = st.move;
    for (const sid in d) {
      const p = G.spaces[sid], h = document.createElement('div');
      h.className = 'hl' + (sid === m.space ? ' here' : '') + (G.spaces[sid].stop === 'none' ? ' nopark' : '');
      h.dataset.s = sid; h.style.left = p.x + 'mm'; h.style.top = p.y + 'mm';
      h.title = (p.label || sid) + (d[sid] ? ` · ${d[sid]} Δv` : ' · stay');
      layer.appendChild(h);
    }
  }
  const clearReach = () => $('boardlayer').querySelectorAll('.hl').forEach(h => h.remove());
  function moveTo(sid) {
    const m = st.move.m, par = st.move.reach.par, path = [], from = m.space;
    for (let s = sid; s && s !== m.space; s = par[s]) path.push(s);
    for (const s of path) if (!m.visited.includes(s)) m.visited.push(s);
    if (sid !== m.space) m.arrived = st.turn;
    m.space = sid; clearReach(); st.mode = 'idle'; st.move = null; render();
    const sp = G.spaces[sid];
    setTimeout(() => { if (sid === 'earth' && from !== 'earth') landed(m); else if (!checkGoals()) camYou(); }, 1600);  // landed home? a goal? else back to you
    if (sp.stop === 'none') toast(`Mission ${ROMAN[m.i]} can't stop here. Fire another stage before you end your turn, or it fails.`);
    else toast(`Mission ${ROMAN[m.i]} reached ${sp.label || 'its new position'}.`);
    prompt();
  }
  // ---- aerobraking: with Atmospheric Return aboard, blue (and Mars red) crossings are free going down ----
  const hasHeatShield = m => m.equip.some(e => G.cards[e].name === 'ATMOSPHERIC RETURN');
  function aeroPath(m) {                                        // path down to a surface using only aero crossings, or null
    if (!m.active || !hasHeatShield(m) || G.spaces[m.space].kind === 'surface') return null;
    const par = { [m.space]: null }, q = [m.space];
    while (q.length) { const s = q.shift();
      if (G.spaces[s].kind === 'surface') { const path = []; for (let t = s; t; t = par[t]) path.unshift(t); return path; }
      for (const t of aadj[s] || []) if (!(t in par)) { par[t] = s; q.push(t); } }
    return null;
  }
  function aerobrake(m, then) {
    const path = aeroPath(m); if (!path) return;
    for (const s of path) if (!m.visited.includes(s)) m.visited.push(s);
    m.space = path[path.length - 1]; m.arrived = st.turn; st.mode = 'anim'; render();
    toast(`Mission ${ROMAN[m.i]} aerobrakes: heat shield, then parachutes…`);
    setTimeout(() => { st.mode = 'idle'; landed(m, then); }, 1600);
  }
  function landed(m, then) {                                    // goals first, then the mission is recovered
    const done = () => { recover(m); then && then(); };
    if (!checkGoals(done)) done();
  }
  function recover(m) {
    if (m.card) st.discard.push(m.card);
    st.discard.push(...m.equip);
    const toks = m.tokens.slice();
    Object.assign(m, { active: false, space: null, tokens: [], paid: false, eq: 0, equip: [], card: null, fired: false, visited: [] });
    render(); flyTokens(toks, () => $('mrest-' + m.i), t => $('bowl-' + t), null);
    toast(`Mission ${ROMAN[m.i]} is home and recovered. Its cards go to your discard pile.`); camYou(); prompt();
  }
  function cancel() {
    if (st.mode === 'move') { clearReach(); toast('Stayed in place.'); }
    closeup.hidden = true; st.mode = 'idle'; st.pending = null; st.firing = null; st.move = null;
    st.handOpen = false; st.sel = null; syncHand(); render(); prompt();
  }
  function endTurn() {
    if (st.mode !== 'idle') cancel();
    const falling = st.missions.filter(m => m.active && G.spaces[m.space].stop === 'none' && aeroPath(m));
    if (falling.length) {                                       // a mid-climb crew with a heat shield falls home safely
      const m = falling[0]; toast(`Mission ${ROMAN[m.i]} can't stay up there; it falls back under its heat shield.`);
      return setTimeout(() => aerobrake(m, endTurn), 900);
    }
    const lost = [];
    for (const m of st.missions) if (m.active && G.spaces[m.space].stop === 'none') {
      lost.push(ROMAN[m.i]); if (m.card) st.discard.push(m.card);
      Object.assign(m, { active: false, space: null, tokens: [], paid: false, eq: 0, equip: [], card: null, fired: false, visited: [] });
    }
    st.used = { research: false, launch: false, mc: false }; st.freeMC = 0; st.turn++;
    render(); prompt();
    toast(lost.length ? `Mission ${lost.join(' & ')} couldn't stop mid-flight and was lost.` : `Turn ${st.turn}.`);
    setTimeout(checkGoals, 600);
  }

  // ---- goals ------------------------------------------------------------------
  const deepN = sid => { const r = /^ds(\d+)$/.exec(sid); return r ? +r[1] : 0; };
  function meets(m, g) {                                      // equipCount ignores the Crew Capsule: crew isn't a satellite
    const c = g.check; if (!c || !m.active) return false;
    const names = m.equip.map(e => G.cards[e].name);
    return (!c.at || c.at.includes(m.space)) && (!c.deep || deepN(m.space) >= c.deep)
      && (!c.visited || c.visited.every(v => m.visited.includes(v)))
      && (!c.equip || c.equip.every(n => names.includes(n))) && (!c.without || !c.without.some(n => names.includes(n)))
      && (!c.equipCount || names.filter(n => n !== 'CREW CAPSULE').length >= c.equipCount) && (!c.cargo || mass(m.tokens) >= c.cargo)
      && (!c.turns || st.turn - m.arrived >= c.turns);
  }
  const openGoals = () => [...st.goals.firsts, ...st.goals.market].filter(Boolean);
  function checkGoals(then) {                                   // true if we switched to claiming
    const hits = [];
    for (const gid of openGoals()) { const m = st.missions.find(m => meets(m, G.goals[gid])); if (m) hits.push({ gid, m }); }
    if (!hits.length || st.mode !== 'idle') return false;
    st.claimable = hits; st.afterClaim = then || null; st.mode = 'claim'; render(); cam(G.focusGoals);
    const h = hits[0], g = G.goals[h.gid];
    prompt(`Mission ${ROMAN[h.m.i]} achieved ${g.name}! Click the glowing goal card to claim it (+${g.vp}★).`);
    return true;
  }
  const slotOfGoal = gid => { let i = st.goals.firsts.indexOf(gid); if (i >= 0) return $('goal-f' + i); i = st.goals.market.indexOf(gid); return i >= 0 ? $('goal-m' + i) : null; };
  function claim(gid) {
    const g = G.goals[gid], from = slotOfGoal(gid), hit = st.claimable.find(h => h.gid === gid);
    if (g.check && g.check.cargo && hit) {                       // "N t at …": the payload is delivered, so it leaves the mission
      const m = hit.m, toks = m.tokens.slice(); m.tokens = [];
      flyTokens(toks, () => $('mcargo-' + m.i), t => $('bowl-' + t), null);
    }
    let i = st.goals.firsts.indexOf(gid);
    if (i >= 0) st.goals.firsts[i] = null;
    else { i = st.goals.market.indexOf(gid); st.goals.market[i] = st.goals.deck.pop() || null; }
    st.claimable = st.claimable.filter(h => h.gid !== gid); st.mode = st.claimable.length ? 'claim' : 'anim';
    from.innerHTML = ''; render();
    fly(g.html, from, $('cgoals-you'), () => {
      st.goals.mine.push(gid); st.vp += g.vp; if (st.mode === 'anim') st.mode = 'idle'; render();
      toast(`${g.name} claimed! +${g.vp}★${g.check && g.check.cargo ? ' The payload is delivered.' : ''}`);
      if (st.mode === 'idle') claimDone();
    });
  }
  function claimDone() {
    const then = st.afterClaim; st.afterClaim = null; st.claimable = []; st.mode = 'idle'; render();
    if (then) then(); else { prompt(); setTimeout(camYou, 700); }
  }
  function renderGoals() {
    const fill = (el, gid) => { if (!el) return;
      if (el.dataset.gid !== (gid || '')) { el.innerHTML = gid ? G.goals[gid].html : ''; el.dataset.gid = gid || ''; }
      el.classList.toggle('claim', st.mode === 'claim' && st.claimable.some(h => h.gid === gid)); };
    st.goals.firsts.forEach((gid, i) => fill($('goal-f' + i), gid));
    st.goals.market.forEach((gid, i) => fill($('goal-m' + i), gid));
    const gd = $('deck-missions'); gd.style.setProperty('--t', (st.goals.deck.length * 0.3).toFixed(2) + 'mm'); gd.style.visibility = st.goals.deck.length ? '' : 'hidden';
    const cg = $('cgoals-you');
    if (cg.dataset.n !== String(st.goals.mine.length)) {
      cg.dataset.n = st.goals.mine.length;
      cg.innerHTML = st.goals.mine.length ? st.goals.mine.map((gid, k) => `<div class="slot cg" style="left:${3 + k * 15}mm;top:7mm">${G.goals[gid].html}</div>`).join('')
        : '<span class="cg-hint">completed goals<br>reward side up</span>';
    }
    $('vp-you').textContent = st.vp ? `★ ${st.vp}` : '';
  }
  const why = k => ({
    research: st.used.research ? 'You already researched this turn.' : 'The deck is empty.',
    launch: st.used.launch ? 'You already launched this turn.' : 'All four mission tokens are in use.',
    mc: st.used.mc && !st.freeMC ? 'Mission Control is used for this turn.'
      : st.missions.some(m => m.active) ? 'Your missions have no cargo tokens or equipment slots left to spend.'
      : 'Mission Control spends a mission\'s cargo, and you have no mission in flight. Launch one first (Launch includes a free Mission Control).',
  })[k];

  // ---- input (called from the table's pointer handler) -------------------------
  window.game = {
    _st: st,                                                   // read-only peek for debugging/tests
    tap(target) {
      const t = target.closest ? target : target.parentElement;
      if (st.mode === 'anim') return true;
      if (st.mode === 'claim') {
        const gs = t.closest('.gslot.claim');
        if (gs) { const gid = gs.dataset.gid; claim(gid); return true; }
        claimDone();                                            // skipping a claim doesn't swallow the click
      }
      if (st.mode === 'research') {
        if (t.closest('#deck-rockets') && st.deck.length) { researchDeck(); return true; }
        const mk = t.closest('.mkslot'); if (mk && mk.dataset.id) { researchMarket(+mk.id.slice(3)); return true; }
        if (t.closest('#discard-you') && st.discard.length) { researchDiscard(); return true; }
        st.mode = 'idle'; render(); prompt(); camYou(); return true;
      }
      const bt = t.closest('.btok.can');
      if (bt && st.mode === 'idle') { aerobrake(st.missions[+bt.id.slice(5)]); return true; }
      const act = t.closest('[data-act]');
      if (act) { const k = act.dataset.act; if (st.mode !== 'idle') cancel(); if (can()[k]) ({ research, launch, mc: startMC })[k](); else toast(why(k)); return true; }
      const hc = t.closest('#hand-you .hc');
      if (hc) { handClick(+hc.dataset.k); return true; }
      const hl = t.closest('.hl');
      if (hl && st.mode === 'move') { moveTo(hl.dataset.s); return true; }
      const col = t.closest('.mcol');
      if (col) {
        const m = st.missions[+col.dataset.i];
        if (st.mode === 'mc-target') { eligible(m) ? place(m) : toast(reason(m)); return true; }
        if (st.mode === 'idle' && t.closest('.mslot') && m.card) { m.fired ? toast('This stage has fired. Place the next one with Mission Control.') : openCloseup(m); return true; }
        return true;
      }
      if (st.mode === 'move') { toast('Click a glowing space to move, or press Esc to stay put.'); return true; }
      if (st.mode === 'load') { finishLoad(); return true; }
      if (st.mode !== 'idle') cancel();
      else if (st.handOpen) { st.handOpen = false; st.sel = null; syncHand(); }
      return false;
    },
  };
  closeup.addEventListener('click', e => { const tr = e.target.closest('tr.pick'); if (tr) pickRow(+tr.dataset.r); else cancel(); });
  $('endturn').addEventListener('click', endTurn);
  addEventListener('keydown', e => { if (e.key !== 'Escape') return; if (st.mode === 'load') finishLoad(); else if (st.mode !== 'idle') cancel(); });
  $('donebtn').addEventListener('click', finishLoad);

  buildHand(); syncHand(); render(); prompt();
  if (innerWidth < 700 && !location.hash) setTimeout(camYou, 300);   // phones: start on your Space Center
})();
'''

if __name__ == "__main__":
    main()
