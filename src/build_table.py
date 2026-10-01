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
                       objective_card_html, mission_back_html, bundle_card_html, CSS as KIT_CSS)

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
FP_MIDDLE = (BOARD_X - 40, BOARD_Y + BOARD_H + 40)
BANK_XY = (BOARD_X - 110, BOARD_Y + BOARD_H + 22)   # first player token, unclaimed
GOALS_X = 10                           # the goal rows run above the board, from the table's left edge
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
                      "price": e["price"], "html": engine_card_html(e)}
for i, q in enumerate(DATA["equipment"]):
    CARDS[f"q{i}"] = {"kind": "equipment", "name": q["name"], "T": 2.5, "rows": [], "price": q["price"],
                      "html": equipment_card_html(q)}
for i, b in enumerate(DATA["bundles"]):
    CARDS[f"b{i}"] = {"kind": "bundle", "name": f"x{b['mult']} {b['token']} BUNDLE", "T": 0, "rows": [],
                      "price": b["price"], "html": bundle_card_html(b)}


def price_html(p):
    return " + ".join(x for x in (f"${p['money']}" if p.get("money") else "", f"⚛{p['science']}" if p.get("science") else "") if x) or "free"


def xcard_html(kind, head, name, sub, text, foot):
    """Disaster / action / Space Center improvement cards (docs/09): a simple text card, no silhouette yet."""
    return (f'<div class="card xcard {kind}"><div class="xhead">{head}</div><div class="xname">{name}</div>'
            f'<div class="xsub">{sub}</div><div class="xtext">{text}</div><div class="xfoot">{foot}</div></div>')


for i, x in enumerate(DATA["disasters"]):
    foot = "one-shot: gone after use" if x["kind"] == "one-shot" else f"recurring · fixed by {x['fix'].title()}"
    CARDS[f"d{i}"] = {"kind": "disaster", "name": x["name"], "id": x["id"], "effect": x["effect"], "also": x.get("also"),
                      "slot": x.get("slot"), "launched": x.get("launched", False), "recurring": x["kind"] == "recurring", "family": x.get("family"),
                      "text": x["text"],
                      "html": xcard_html("disaster", "DISASTER", x["name"], x["history"], x["text"] + "<br><i>Shuffle your deck.</i>", foot)}
for i, a in enumerate(DATA["actions"]):
    CARDS[f"a{i}"] = {"kind": "action", "name": a["name"], "effect": a["effect"], "price": a["price"], "copies": a["copies"],
                      "html": xcard_html("action", "ACTION", a["name"], "play for free", a["text"], price_html(a["price"]))}
for i, u in enumerate(DATA["improvements"]):   # Space Center improvements: bought, then they stay in front of you
    CARDS[f"u{i}"] = {"kind": "improvement", "name": u["name"], "sub": u["kind"], "fixes": u.get("fixes"), "tokens": u.get("tokens"),
                      "draw": u.get("draw", 0), "launch": u.get("launch", 0), "mc": u.get("mc", 0),
                      "price": u["price"], "copies": u.get("copies", 1),
                      "html": xcard_html("improvement", "SPACE CENTER IMPROVEMENT", u["name"], "stays in front of you", u["text"], price_html(u["price"]))}
BY_NAME = {c["name"]: cid for cid, c in CARDS.items()}


def cid(name):
    return BY_NAME[name]


# Sample hands for the other seats (static, not played yet). Blue ("bottom") is you.
HAND_IDS = {
    "bottom": [],
    "left": [cid("HEAVY KEROLOX BOOSTER"), cid("HEAVY HYDROLOX CORE"), cid("HEAVY HYDROLOX UPPER"),
             cid("LARGE ANTENNA"), cid("RTG")],
    "top": [cid("SUPER HEAVY"), cid("STARSHIP"), cid("METHALOX BOOSTER"), cid("SOLAR ARRAY"), cid("ROVER")],
    "right": [cid("HEAVY SOLID BOOSTER"), cid("x2 K BUNDLE"), cid("HYDROLOX DROP TANK"), cid("ORBITER"),
              cid("LANDING GEAR")],
}
HANDS = {k: [CARDS[c]["html"] for c in v] for k, v in HAND_IDS.items()}
# Your own deck (docs/09): the starting cards + every disaster. Draw from the top, used cards to the bottom.
# Infrastructure disasters (Station Fire, Orbital Debris, Dust Storm) aren't in it: each joins your deck when you
# win your first card of that family (owning infrastructure brings its own risks).
START_DECK = [cid(n) for n in DATA["starting_deck"]] + [c for c in CARDS if CARDS[c]["kind"] == "disaster" and not CARDS[c]["family"]]
# The shared main deck: every rocket, equipment, bundle, action and Space Center improvement (with copies). The Crew Capsule
# is retired: a crewed slot's first equipment slot is the crew (docs/09).
MAIN_DECK = [c for c, v in CARDS.items() if v["kind"] in ("engine", "equipment", "bundle") and v["name"] != "CREW CAPSULE"] \
    + [c for c, v in CARDS.items() if v["kind"] in ("action", "improvement") for _ in range(v["copies"])]
MARKET_N = 4
MARKET_SURCHARGE = [2, 1, 0, 0]   # newest (left) market cards cost extra money (docs/09)
GOAL_ROW_N = 5
GOAL_DV_SURCHARGE = 3             # the first 3 goal-row cards need +1 Δv (fly now = no launch window)
LAUNCH_TOKENS = "R"         # the basic pad's lift: 1 red = 160t, single-stage suborbital start (docs/07)

# Goals (docs/09): permanent goals are all face-up and pay VP; transient contracts come in "copies",
# cycle through a 5-card row and pay resources. Each copy gets its own id (fil01, fil01b, fil01c).
PERMANENT_TYPES = ("FIRST", "MOST", "RESCUE", "ENDURANCE")
GOALS = {o["id"] + ("" if k == 0 else "bcdefgh"[k - 1]):
         {"name": o["name"], "type": o["type"], "vp": o["vp"], "check": o.get("check"),
          "reward": o["reward"], "family": o.get("family"), "king": o.get("king"),
          "html": objective_card_html(o), "back": mission_back_html(o)} for o in OBJS for k in range(o.get("copies", 1))}
GOAL_PERM = [o["id"] for o in OBJS if o["type"] in PERMANENT_TYPES]
GOAL_DECK = [g for g, v in GOALS.items() if v["type"] not in PERMANENT_TYPES]

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
    ("LAUNCH", "Put a mission token on Earth in a free slot (I–II crewed, III–IV uncrewed) with your pad's cargo tokens, then a <b>free Mission Control</b>. Launched but met no goal this turn? Discard the rightmost mission card and take a 💰1 card."),
    ("MISSION CONTROL", "Spend a mission's cargo to place a rocket from your hand on it. Spent stages stay on the slot until the mission is done."),
]
TAP = ('<svg viewBox="0 0 20 20" class="tap"><path d="M15 6 A7 7 0 1 0 17 11" fill="none" stroke="currentColor" '
       'stroke-width="2.2" stroke-linecap="round"/><polygon points="12,2 18,6 12,9" fill="currentColor"/></svg>')
MCOL_X, MCOL_W, MCOL_GAP = 172, 62, 4


ACT_KEYS = ["launch", "mc"]
SLOT_KIND = ["CREWED", "CREWED", "UNCREWED", "UNCREWED"]


def space_center(name, color, you=False):
    """you=True: the interactive board (ids the game script drives)."""
    acts = "".join(
        f'<div class="action"{f' id="act-{ACT_KEYS[i]}" data-act="{ACT_KEYS[i]}"' if you else ""} {at(8 + i * (CARD_W + 5), 20, CARD_W, CARD_H)}>'
        f'<div class="ahead">{TAP}<span>{t}</span></div><div class="atext">{txt}</div></div>'
        for i, (t, txt) in enumerate(ACTIONS))
    acts += (f'<div class="upgrades"{' id="upg-you"' if you else ""} {at(8 + 2 * (CARD_W + 5), 20, CARD_W, CARD_H)}>'
             f'<div class="ahead"><span>IMPROVEMENTS</span></div><div class="upg-list"></div></div>')
    missions = ""
    for i in range(4):
        mx = MCOL_X + i * (MCOL_W + MCOL_GAP)
        slot = f'<div class="cslot" {at(7.5, 9, CARD_W, CARD_H)}><span>rocket</span></div>'
        if you:   # empty shells; the game script fills card, cargo and token
            missions += (f'<div class="marea mcol" id="mcol-{i}" data-i="{i}" {at(mx, 20, MCOL_W, 152)}>'
                         f'<div class="mname">{badge_svg(color, i, "mini-badge")}{"I II III IV".split()[i]} · {SLOT_KIND[i]}</div>'
                         f'<div class="ctag" {at(0, 79, MCOL_W, None)}>cargo</div>{slot}'
                         f'<div class="slot mslot" id="mslot-{i}" {at(7.5, 9, CARD_W, CARD_H)}></div>'
                         f'<div class="mcargo" id="mcargo-{i}" {at(2, 86, MCOL_W - 4, 34)}></div>'
                         f'<div class="rest" id="mrest-{i}" {at(23, 126, 16, 20)}></div></div>')
            continue
        body = slot + f'<div class="rest" {at(23, 126, 16, 20)}>{badge_svg(color, i)}</div>'
        missions += (f'<div class="marea" {at(mx, 20, MCOL_W, 152)}><div class="mname">{badge_svg(color, i, "mini-badge")}{"I II III IV".split()[i]} · {SLOT_KIND[i]}</div>'
                     f'<div class="ctag" {at(0, 79, MCOL_W, None)}>cargo</div>{body}</div>')
    return f'''<div class="pboard" style="--pc:{color};">
  <div class="pb-title">SPACE CENTER <span>· {name}</span>{' <b id="vp-you" class="vp"></b>' if you else ''}</div>
  {acts}
  <div class="improve"{' id="cgoals-you"' if you else ''} {at(8, 92, 3 * CARD_W + 10, 80)}><span class="cg-hint">goals you've won<br>reward side up</span></div>
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
    discard = (f'<div class="dslot"{' id="deck-you"' if you else ""} {at(SEAT_W + 8, 50, CARD_W, CARD_H)}><span>YOUR DECK</span></div>')
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

    # Goals: permanent goals (all face-up, VP) + the transient contract deck and its 5-card row
    fx = GOALS_X
    parts.append(zone_label("PERMANENT GOALS · always open · victory points", fx, 305))
    for i, gid in enumerate(GOAL_PERM):
        parts.append(f'<div class="slot gslot" id="goal-f{i}" {at(fx + i * (CARD_W + GAP), 318, CARD_W, CARD_H)}>{GOALS[gid]["html"]}</div>')
    mx = fx + len(GOAL_PERM) * (CARD_W + GAP) + 24
    parts.append(zone_label("MISSIONS · money & science · newest on the left", mx, 305))
    parts.append(stack("missions", "MISSIONS", mx, 318, len(GOAL_DECK), "deck-missions"))
    for i in range(GOAL_ROW_N):
        gx = mx + (i + 1) * (CARD_W + GAP) - 2
        parts.append(f'<div class="slot gslot" id="goal-m{i}" {at(gx, 318, CARD_W, CARD_H)}></div>')
        if i < GOAL_DV_SURCHARGE:
            parts.append(f'<div class="ptag dv" {at(gx, 386, CARD_W, None)}>+1 Δv</div>')

    # Rockets & tech: main deck + open market (newest on the left costs more)
    ry = BOARD_Y + BOARD_H + 22
    parts.append(zone_label("ROCKETS &amp; TECH · newest on the left", BOARD_X, ry - 13))
    parts.append(stack("rockets", "ROCKETS", BOARD_X, ry, len(MAIN_DECK) - MARKET_N, "deck-rockets"))
    for i in range(MARKET_N):
        kx = BOARD_X + (i + 1) * (CARD_W + GAP)
        parts.append(f'<div class="slot mkslot" id="mk-{i}" {at(kx, ry, CARD_W, CARD_H)}></div>')
        parts.append(f'<div class="ptag" id="mkp-{i}" {at(kx, ry + CARD_H + 2, CARD_W, None)}></div>')

    # The bank: a small deck of 💰1 cards (same on both sides) for change and the launch consolation
    bank = stack("missions", "", BANK_XY[0], BANK_XY[1], 32, "bank")
    bank = bank.replace('<div class="card cback missions"><span></span></div>', mission_back_html(amount=1))
    parts.append(zone_label("BANK · 💰1", BANK_XY[0], BANK_XY[1] - 13))
    parts.append(bank)

    # First player token: starts in the middle; pay $1 (discarding the rightmost market card) to take it
    parts.append(f'<div id="fp-token" class="fptoken" {at(FP_MIDDLE[0], FP_MIDDLE[1], 16, 16)}>1st</div>')

    # Cargo token bowls
    bx = BOARD_X + 5 * (CARD_W + GAP) + 45
    parts.append(zone_label("CARGO TOKENS", bx - 30, ry - 13))
    for i, (c, lbl) in enumerate([("K", "K · 640t"), ("R", "R · 160t"), ("O", "O · 40t"), ("Y", "Y · 10t")]):
        parts.append(bowl(c, lbl, bx + i * 70, ry + 30))

    for s_, pname, color, rot, center in PLAYERS:
        parts.append(seat(s_, pname, color, rot, center))

    game = {
        "cards": CARDS, "startDeck": START_DECK, "mainDeck": MAIN_DECK, "launch": LAUNCH_TOKENS,
        "marketN": MARKET_N, "marketSurcharge": MARKET_SURCHARGE, "goalRowN": GOAL_ROW_N, "goalDvSurcharge": GOAL_DV_SURCHARGE,
        "you": PLAYERS[0][2], "tokenColors": TOKEN_COLORS,
        "spaces": {sp["id"]: {"x": round(sp["x"] / 1000 * BOARD_W, 2), "y": round(sp["y"] / 707 * BOARD_H, 2),
                              "stop": sp["stop"], "label": sp["name"], "kind": sp["kind"]} for sp in BOARD["spaces"]},
        "aero": [[l["a"], l["b"]] for l in BOARD["links"] if l["type"] in ("aero", "mars_aero")],
        "links": [[l["a"], l["b"]] for l in BOARD["links"]],
        "board": [BOARD_X, BOARD_Y],
        # camera targets (table mm): your Space Center + hand + discard, and the whole board
        "focusYou": [PLAYERS[0][4][0] - SEAT_W / 2 - 10, PLAYERS[0][4][1] - SEAT_H / 2 - 70,
                     PLAYERS[0][4][0] + SEAT_W / 2 + 60, PLAYERS[0][4][1] + SEAT_H / 2 + 5],
        "focusBoard": [BOARD_X - 10, BOARD_Y - 10, BOARD_X + BOARD_W + 10, BOARD_Y + BOARD_H + 10],
        "focusGoals": [GOALS_X - 10, 296, GOALS_X + (len(GOAL_PERM) + GOAL_ROW_N + 1) * (CARD_W + GAP) + 40, 396],
        "focusMarket": [BOARD_X - 10, BOARD_Y + BOARD_H + 5, BOARD_X + 5 * (CARD_W + GAP) + 10, BOARD_Y + BOARD_H + 100],
        "fpMiddle": FP_MIDDLE, "fpYou": (PLAYERS[0][4][0] - SEAT_W / 2 - 22, PLAYERS[0][4][1] - SEAT_H / 2 + 8),
        "goals": GOALS, "goalPerm": GOAL_PERM, "cashHtml": mission_back_html(amount=1), "goalDeck": GOAL_DECK,
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
<div id="choice" hidden><div class="ch-box"><div class="ch-card"></div><div class="ch-text"></div><div class="ch-btns"></div></div></div>
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
.mkslot.can > .card, .gslot.can > .card { animation: glow 1.4s ease-in-out infinite; }
.mkslot.can, .gslot.can { cursor: pointer; }
.mkslot.take > .card, .gslot.take > .card { animation: glow 1.4s ease-in-out infinite; outline: 0.8mm dashed #7fd3ff; outline-offset: 0.8mm; }
.mkslot.take, .gslot.take { cursor: pointer; }

/* ---- docs/09: disaster / action / improvement cards, prices, rows, resources, choice dialog ---- */
.card.xcard { flex-direction: column; font-family: Helvetica, Arial, sans-serif; color: #1d1d1d; }
.xcard .xhead { padding: 1.6mm 2.4mm; color: #fff; font: 800 3.2mm Helvetica, Arial, sans-serif; letter-spacing: 0.6mm; }
.xcard.disaster { background: #fbe9e4; } .xcard.disaster .xhead { background: #8a1c12; }
.xcard.action { background: #eef3fb; } .xcard.action .xhead { background: #1b3a6b; }
.xcard.improvement { background: #eef7ef; } .xcard.improvement .xhead { background: #2f6b3a; font-size: 2.6mm; letter-spacing: 0.3mm; }
.xcard .xname { padding: 2.5mm 2.4mm 0.6mm; font-weight: 800; font-size: 4.1mm; line-height: 1.1; }
.xcard .xsub { padding: 0 2.4mm; font-size: 2.6mm; color: #6b6356; font-style: italic; }
.xcard .xtext { padding: 2.4mm; font-size: 3.1mm; line-height: 1.35; flex: 1; }
.xcard .xfoot { padding: 1.4mm 2.4mm; font-size: 2.6mm; font-weight: 700; color: #6b6356; border-top: 0.3mm solid rgba(0,0,0,.15); }
.card.rwd { flex-direction: column; align-items: center; justify-content: center; text-align: center; font-family: Helvetica, Arial, sans-serif; }
.card.rwd.vp { background: #b8860b; color: #fff; } .card.rwd.money { background: #2f6b3a; color: #fff; } .card.rwd.science { background: #46237a; color: #fff; }
.card.rwd b { font-size: 16mm; line-height: 1; } .card.rwd span { font-size: 3mm; font-weight: 700; padding: 0 3mm; margin-top: 2mm; }
.card.rwd.spent, .card.mback.spent { opacity: .3; }
.dtop > .card.mback { border-width: 1.6mm; }
.fptoken { border-radius: 50%; background: radial-gradient(circle at 40% 35%, #ffe08a, #d9a441 60%, #a8741f); color: #3a2608;
  font: 800 4.6mm/16mm Helvetica, Arial, sans-serif; text-align: center; box-shadow: 0 1mm 0 #7a5214, 0 2mm 4mm rgba(0,0,0,.5);
  transition: left 1.2s cubic-bezier(.3,.7,.2,1), top 1.2s cubic-bezier(.3,.7,.2,1); }
.peekrow { display: flex; gap: 3mm; justify-content: center; margin-top: 3mm; }
.peek { width: 28.2mm; height: 39.6mm; position: relative; }
.peek > .card { position: absolute; left: 0; top: 0; width: 47mm; height: 66mm; transform: scale(.6); transform-origin: 0 0; border-radius: 2mm; }
.ptag { color: #ffd98a; font: 800 3.4mm Helvetica, Arial, sans-serif; text-align: center; white-space: nowrap; }
.ptag.dv { color: #9fd4ff; }
.ptag .sur { color: #ff9a7a; }
.upgrades { background: rgba(255,255,255,.55); border: 0.35mm dashed #2a2a2a; border-radius: 1.8mm; overflow: hidden; }
.upgrades .ahead { background: #2f6b3a; }
.upg-list { display: flex; flex-wrap: wrap; gap: 1mm; padding: 1.5mm; }
.upg-list .mini { width: 13.6mm; height: 19.1mm; }
.upg-list .mini > .card { transform: scale(.29); }
.crewchip { font-size: 2.6mm; font-weight: 800; color: #fff; background: #2f6db5; border-radius: 1mm; padding: 0.6mm 1.2mm; }
.crewchip.no { background: #b3a78f; }
.stackchip { width: 100%; text-align: center; font-size: 2.6mm; font-weight: 700; color: #6b6356; }
#deck-you { overflow: visible; }
#deck-you > .card { position: absolute; inset: 0; width: 100%; height: 100%; border-radius: 1.8mm; box-shadow: 0 1.2mm 3mm rgba(0,0,0,.45); }
#choice { position: fixed; inset: 0; background: rgba(20,15,10,.62); display: flex; align-items: center; justify-content: center; z-index: 6; }
#choice[hidden] { display: none; }
.ch-box { display: flex; flex-direction: column; align-items: center; gap: 14px; max-width: min(92vw, 560px); }
.ch-card:empty { display: none; }
.ch-card { --cuz: 2.2; width: 47mm; height: 66mm; transform: scale(var(--cuz)); margin: calc(33mm * (var(--cuz) - 1)) calc(23.5mm * (var(--cuz) - 1)); }
.ch-card > .card { width: 100%; height: 100%; border-radius: 1.5mm; box-shadow: 0 2mm 8mm rgba(0,0,0,.5); }
.ch-text { color: #f3e6cf; font: 600 15px/1.45 Helvetica, Arial, sans-serif; text-align: center; background: rgba(25,20,16,.9); padding: 10px 16px; border-radius: 12px; }
.ch-btns { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.ch-btns button { font: 700 14px Helvetica, Arial, sans-serif; border-radius: 18px; padding: 8px 16px; border: 1px solid rgba(255,236,200,.4);
  background: rgba(30,20,12,.85); color: #f3e6cf; cursor: pointer; }
.ch-btns button.main { background: #d9a441; color: #1d1d1d; border-color: #d9a441; }
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
// Game loop for YOUR seat (Blue), docs/09 rules: your own deck (draw at the END of your turn,
// used cards to the bottom), Launch / Mission Control, buy from the market, take the rightmost
// card instead of launching, disasters, end-of-turn prizes. State lives here; the HTML is the view.
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
  const C = id => G.cards[id];

  const blank = i => ({ i, crewed: i < 2, active: false, space: null, tokens: [], paid: false, equip: [], cards: [], card: null,
    fired: false, visited: [], crew: false, home: false, launchedTurn: null, arrived: null, done: false });
  const st = {
    turn: 1, deck: shuffle(G.startDeck.slice()), hand: [], main: shuffle(G.mainDeck.slice()), market: [],
    used: { launch: 0, mc: 0 }, freeMC: 0, extraMC: 0, noLaunch: false, noLaunchNext: false,
    missions: [0, 1, 2, 3].map(blank), upgrades: [], removed: [],
    mode: 'idle', handOpen: false, sel: null, pending: null, firing: null, move: null, load: null,
    goals: { perm: G.goalPerm.slice(), row: [], deck: shuffle(G.goalDeck.slice()) },
    won: [], spent: new Set(), cash: 0, penalty: 0, firstPlayer: false,
  };
  for (let i = 0; i < G.marketN; i++) st.market.push(st.main.pop() || null);
  for (let i = 0; i < G.goalRowN; i++) st.goals.row.push(st.goals.deck.pop() || null);
  {                                                            // starting hand: 3 cards, disasters drawn now go back
    const aside = [];
    while (st.hand.length < 3 && st.deck.length) { const id = st.deck.shift(); (C(id).kind === 'disaster' ? aside : st.hand).push(id); }
    st.deck.push(...aside); shuffle(st.deck);
  }
  const hand = $('hand-you'), toastEl = $('toast'), promptEl = $('prompt'), closeup = $('closeup'), choiceEl = $('choice');

  // ---- resources ------------------------------------------------------------------
  const reward = gid => G.goals[gid].reward;
  const famCount = f => st.won.filter(g => G.goals[g].family === f).length;
  const total = kind => {                                       // plain rewards + infrastructure sets (each family scores its set table)
    let n = st.won.filter(g => reward(g).kind === kind && !reward(g).set).reduce((a, g) => a + reward(g).n, 0);
    const fams = new Set(st.won.filter(g => G.goals[g].family && reward(g).kind === kind).map(g => G.goals[g].family));
    for (const f of fams) { const t = G.goals[st.won.find(g => G.goals[g].family === f)].reward.set; n += t[Math.min(famCount(f), t.length) - 1]; }
    return n; };
  const moneyCards = () => st.won.filter(g => reward(g).kind === 'money' && !reward(g).set && !st.spent.has(g));
  // Money = money mission cards you've won + 💰1 cards from the bank (st.cash), the launch consolation prize.
  const money = () => moneyCards().reduce((n, g) => n + reward(g).n, 0) + st.cash;
  const science = () => total('science');
  const vp = () => total('vp') - st.penalty;
  function pay(n) {                                            // spend money cards: least overpay, then fewest cards
    if (n <= 0) return 0;
    let best = null;
    const cards = [...moneyCards(), ...Array(st.cash).fill('CASH')], val = g => g === 'CASH' ? 1 : reward(g).n;
    const walk = (k, picked, sum) => {
      if (sum >= n) { if (!best || sum < best.sum || (sum === best.sum && picked.length < best.picked.length)) best = { picked: picked.slice(), sum }; return; }
      if (k >= cards.length) return;
      picked.push(cards[k]); walk(k + 1, picked, sum + val(cards[k])); picked.pop(); walk(k + 1, picked, sum);
    };
    walk(0, [], 0);
    best.picked.forEach(g => g === 'CASH' ? st.cash-- : st.spent.add(g));
    st.cash += best.sum - n;                                   // change comes back from the bank as 💰1 cards
    return best.sum - n;
  }
  const ICON = { vp: '★', money: '$', science: '⚛' };
  const CASH_HTML = n => G.cashHtml.replace('</div></div>', `</div>${n > 1 ? `<div class="mb-name">× ${n}</div>` : ''}</div>`);
  const rewardHtml = gid => { const g = G.goals[gid], r = reward(gid);
    return st.spent.has(gid) ? g.back.replace('card mback', 'card mback spent') : g.back; };   // won missions are flipped: the back is the resource

  // ---- helpers ------------------------------------------------------------------------
  let tt; const toast = msg => { toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('on'), 3200); };
  const prompt = msg => { promptEl.textContent = msg || idlePrompt(); promptEl.classList.add('on'); };
  const idlePrompt = () => innerWidth < 600 ? `Turn ${st.turn} · tap anything glowing, then End turn.`
    : `Turn ${st.turn} · Launch, Mission Control, buy from the market, or pay $1 to clear the rightmost market card and go first. End turn draws your next card.`;
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
  function choice(cardHtml, text, buttons) {                   // a modal: optional big card, text, buttons [{label, fn, main}]
    choiceEl.querySelector('.ch-card').innerHTML = cardHtml || '';
    choiceEl.querySelector('.ch-text').innerHTML = text;
    const box = choiceEl.querySelector('.ch-btns'); box.innerHTML = '';
    for (const b of buttons) { const el = document.createElement('button'); el.textContent = b.label; if (b.main) el.className = 'main';
      el.onclick = () => { choiceEl.hidden = true; b.fn && b.fn(); }; box.appendChild(el); }
    choiceEl.querySelector('.ch-card').style.setProperty('--cuz', Math.min(2.4, innerHeight * 0.42 / (66 * MM), innerWidth * 0.7 / (47 * MM)).toFixed(2));
    choiceEl.hidden = false;
  }
  function reach(from, n) {                                    // spaces within n crossings (1 dv each)
    const d = { [from]: 0 }, q = [from], par = {};
    while (q.length) { const s = q.shift(); if (d[s] >= n) continue; for (const t of adj[s] || []) if (!(t in d)) { d[t] = d[s] + 1; par[t] = s; q.push(t); } }
    Object.defineProperty(d, 'par', { value: par });
    return d;
  }
  const pendingCard = () => st.pending == null ? null : C(st.hand[st.pending]);
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
  const flying = m => m.active && !m.home && !m.done;
  const spendable = m => flying(m) && m.tokens.length > 0;
  const eligible = m => { const c = pendingCard(); if (!c || !flying(m)) return false;
    if (c.kind === 'equipment') return spendable(m);
    return !m.paid && mass(m.tokens) >= c.T - 1e-9 && (m.space !== 'earth' || lightsOnEarth(c)); };
  const reason = m => { const c = pendingCard(); if (!m.active) return 'That mission slot is empty. Launch first.';
    if (m.home) return `Mission ${ROMAN[m.i]} is home; it's recovered at the end of the turn.`;
    if (c.kind === 'equipment') return `Mission ${ROMAN[m.i]} has no cargo tokens left to turn into equipment.`;
    if (m.paid) return `Mission ${ROMAN[m.i]} already has a rocket waiting to fire.`;
    if (mass(m.tokens) < c.T) return `Mission ${ROMAN[m.i]} has ${mass(m.tokens)}t of cargo; ${c.name} costs ${c.T}t.`;
    return `${c.name} can't light on Earth. It's an upper stage.`; };
  const padTokens = () => { const pads = st.upgrades.map(C).filter(u => u.sub === 'pad');
    return pads.length ? pads.reduce((a, b) => mass(b.tokens.split('')) > mass(a.tokens.split('')) ? b : a).tokens : G.launch; };
  const bonus = k => st.upgrades.map(C).reduce((n, u) => n + (u[k] || 0), 0);
  const drawSize = () => 1 + bonus('draw');
  const launchesLeft = () => 1 + bonus('launch') - st.used.launch, mcLeft = () => 1 + bonus('mc') - st.used.mc;
  const owns = name => st.upgrades.some(u => C(u).name === name);
  const fixFor = d => Object.values(G.cards).find(u => u.kind === 'improvement' && u.fixes === d.id);
  const rightmost = arr => { for (let i = arr.length - 1; i >= 0; i--) if (arr[i]) return i; return -1; };
  const priceAt = (id, i) => ({ money: (C(id).price.money || 0) + (G.marketSurcharge[i] || 0), science: C(id).price.science || 0 });

  // ---- view -----------------------------------------------------------------
  function buildHand() {
    const n = st.hand.length, squeeze = Math.min(1, 5 / Math.max(n, 1)), spread = n > 6 ? 264 / n : 44;
    hand.innerHTML = st.hand.map((id, k) => { const o = k - (n - 1) / 2;
      return `<div class="hc${C(id).kind === 'equipment' ? ' eqc' : ''}" data-k="${k}" style="--cx:${(o * 22 * squeeze).toFixed(1)};--cy:${(Math.abs(o) * 3).toFixed(1)};--cr:${(o * 7 * squeeze).toFixed(1)};--ox:${(o * spread).toFixed(1)};--oy:${(Math.abs(o) * 2).toFixed(1)};--or:${(o * 2.5).toFixed(1)};z-index:${k + 1}"><div class="flip"><div class="face back">${BACK}</div><div class="face front">${C(id).html}</div></div></div>`; }).join('');
  }
  function syncHand() {
    void hand.offsetWidth;                                     // let a freshly built hand flip, not jump
    hand.classList.toggle('open', st.handOpen);
    hand.querySelectorAll('.hc').forEach((el, k) => el.classList.toggle('sel', st.sel === k));
  }
  function can() {
    const idle = st.mode === 'idle';
    return {
      launch: idle && launchesLeft() > 0 && !st.noLaunch && st.missions.some(m => !m.active),
      mc: idle && (mcLeft() > 0 || st.freeMC > 0 || st.extraMC > 0) && st.missions.some(spendable),
    };
  }
  function render() {
    const c = can(), idle = st.mode === 'idle';
    for (const k of ['launch', 'mc']) {
      const el = $('act-' + k), more = k === 'mc' && (st.freeMC > 0 || st.extraMC > 0);
      el.classList.toggle('used', (k === 'launch' ? launchesLeft() <= 0 || st.noLaunch : mcLeft() <= 0 && !more));
      el.classList.toggle('can', c[k]);
      el.classList.toggle('free', k === 'mc' && st.freeMC > 0);
    }
    for (const m of st.missions) {
      const slot = $('mslot-' + m.i);
      slot.innerHTML = m.card ? C(m.card).html : '';
      slot.classList.toggle('fired', !!m.card && m.fired);
      slot.classList.toggle('can', idle && !!m.card && !m.fired && flying(m));
      const crew = m.crewed && m.active ? `<span class="crewchip${m.crew ? '' : ' no'}">${m.crew ? 'CREW ABOARD' : 'crew needs an eq slot'}</span>` : '';
      $('mcargo-' + m.i).innerHTML = m.tokens.map(t => tri(t, m.paid ? 'spent' : '')).join('') + crew
        + (st.load && st.load.m === m ? `<span class="eqchip">${st.load.n} slot${st.load.n > 1 ? 's' : ''} to fill</span>` : '')
        + (m.equip.length ? `<div class="minis">${m.equip.map(e => `<div class="mini" title="${C(e).name}">${C(e).html}</div>`).join('')}</div>` : '')
        + (m.cards.length > 1 ? `<div class="stackchip">+${m.cards.length - 1} spent stage${m.cards.length > 2 ? 's' : ''} below</div>` : '');
      $('mrest-' + m.i).innerHTML = m.active ? '' : G.badges[m.i];
      $('mcol-' + m.i).classList.toggle('target', (st.mode === 'mc-target' && eligible(m)) || (st.mode === 'launch-pick' && !m.active));
      let bt = $('btok-' + m.i);
      if (m.active) {
        if (!bt) { bt = document.createElement('div'); bt.id = 'btok-' + m.i; bt.className = 'btok'; bt.title = `Mission ${ROMAN[m.i]} (${G.badgeNames[m.i]})`; bt.innerHTML = G.badges[m.i]; $('boardlayer').appendChild(bt); }
        const p = G.spaces[m.space], off = st.missions.filter(o => o.active && o.space === m.space && o.i < m.i).length;
        bt.style.left = (p.x + off * 5) + 'mm'; bt.style.top = p.y + 'mm';
        bt.classList.toggle('can', idle && !!aeroPath(m));
      } else if (bt) bt.remove();
    }
    hand.classList.toggle('can', st.mode === 'mc-pick' || st.mode === 'load');
    hand.classList.toggle('loading', st.mode === 'load');
    $('donebtn').hidden = st.mode !== 'load';
    const md = $('deck-rockets');
    md.style.setProperty('--t', (st.main.length * 0.3).toFixed(2) + 'mm'); md.style.visibility = st.main.length ? '' : 'hidden';
    const mr = rightmost(st.market);
    st.market.forEach((id, i) => { const el = $('mk-' + i);
      if (el.dataset.id !== (id || '')) { el.innerHTML = id ? C(id).html : ''; el.dataset.id = id || ''; }
      const p = id && priceAt(id, i), afford = p && money() >= p.money && science() >= p.science;
      el.classList.toggle('can', idle && !!afford);
      el.classList.toggle('take', idle && i === mr && !afford && money() >= 1);
      $('mkp-' + i).innerHTML = id ? `${p.money ? '$' + p.money : ''}${p.money && p.science ? ' + ' : ''}${p.science ? '⚛' + p.science : ''}${!p.money && !p.science ? 'free' : ''}`
        + (G.marketSurcharge[i] ? ` <span class="sur">(+$${G.marketSurcharge[i]} new)</span>` : '') : ''; });
    renderGoals();
    const dy = $('deck-you');
    dy.innerHTML = st.deck.length ? `${BACK}<em>${st.deck.length}</em>` : '<span>YOUR DECK</span>';
    dy.title = `Your deck: ${st.deck.length} cards. You draw ${drawSize()} at the end of your turn.`;
    $('upg-you').querySelector('.upg-list').innerHTML = st.upgrades.map(u => `<div class="mini" title="${C(u).name}">${C(u).html}</div>`).join('');
    $('vp-you').textContent = `★ ${vp()} · $ ${money()} · ⚛ ${science()}`;
    const fp = $('fp-token'), at = st.firstPlayer ? G.fpYou : G.fpMiddle;
    fp.style.left = at[0] + 'mm'; fp.style.top = at[1] + 'mm'; fp.title = st.firstPlayer ? 'You hold the first player token' : 'First player token';
  }
  function renderGoals() {
    const fill = (el, gid) => { if (!el) return;
      if (el.dataset.gid !== (gid || '')) { el.innerHTML = gid ? G.goals[gid].html : ''; el.dataset.gid = gid || ''; } };
    st.goals.perm.forEach((gid, i) => fill($('goal-f' + i), gid));
    st.goals.row.forEach((gid, i) => fill($('goal-m' + i), gid));
    const gd = $('deck-missions'); gd.style.setProperty('--t', (st.goals.deck.length * 0.3).toFixed(2) + 'mm'); gd.style.visibility = st.goals.deck.length ? '' : 'hidden';
    const next = st.goals.deck[st.goals.deck.length - 1], top = gd.querySelector('.dtop');   // the top card's back shows what kind of mission comes next
    if (next && top.dataset.gid !== next) { top.innerHTML = G.goals[next].back; top.dataset.gid = next; }
    const cg = $('cgoals-you'), key = st.won.join() + '|' + [...st.spent].join() + '|' + st.cash;
    if (cg.dataset.k !== key) {
      cg.dataset.k = key;
      const shown = [...st.won.map(rewardHtml), ...(st.cash ? [CASH_HTML(st.cash)] : [])];
      cg.innerHTML = shown.length ? shown.map((h, k) => `<div class="slot cg" style="left:${3 + k * Math.min(15, 100 / shown.length)}mm;top:7mm">${h}</div>`).join('')
        : '<span class="cg-hint">goals you\'ve won<br>reward side up</span>';
    }
  }

  // ---- launch -----------------------------------------------------------------
  function startLaunch() {
    const free = st.missions.filter(m => !m.active);
    if (free.some(m => m.crewed) && free.some(m => !m.crewed)) {
      st.mode = 'launch-pick'; render(); camYou();
      return prompt('Launch: click a free slot. I–II are crewed (the crew takes the first equipment slot), III–IV uncrewed.');
    }
    launch(free[0]);
  }
  function launch(m) {
    const toks = padTokens().split('');
    Object.assign(m, blank(m.i), { active: true, space: 'earth', visited: ['earth'], arrived: st.turn, launchedTurn: st.turn });
    st.used.launch++; st.freeMC++; st.mode = 'anim';
    render(); camYou();
    setTimeout(() => flyTokens(toks, c => $('bowl-' + c), () => $('mcargo-' + m.i), () => {
      m.tokens = toks; st.mode = 'idle'; render();
      toast(`Mission ${ROMAN[m.i]} (${m.crewed ? 'crewed' : 'uncrewed'}) is on the pad with ${mass(m.tokens)}t of lift.`);
      startMC();
    }), 500);
  }

  // ---- mission control ----------------------------------------------------------
  function startMC() {
    st.mode = 'mc-pick'; st.handOpen = true; st.sel = null; syncHand(); render(); camYou();
    prompt(`Mission Control${st.freeMC ? ' (free)' : ''}: pick a rocket or equipment card from your hand, then click it again to confirm. Click the table to cancel.`);
  }
  function handClick(k) {
    if (st.mode === 'mc-pick') {
      if (st.sel !== k) { st.sel = k; syncHand(); return; }
      const c = C(st.hand[k]);
      if (c.kind === 'action') return toast('Action cards are played outside Mission Control: cancel, then click it twice.');
      if (c.kind === 'bundle') return toast('Bundles can\'t be played yet. Coming soon.');
      if (c.kind === 'engine' && !c.rows.length) return toast(`${c.name} is a fixed-function card; it can't be flown yet.`);
      st.pending = k;
      const ok = st.missions.filter(eligible);
      if (!ok.length) { const m = st.missions.find(m => m.active) || st.missions[0]; toast(reason(m)); st.pending = null; return; }
      if (ok.length === 1) return place(ok[0]);
      st.mode = 'mc-target'; st.handOpen = false; syncHand(); render();
      return prompt(`Choose the glowing mission for ${c.name}${c.kind === 'equipment' ? ' (uses 1 equipment slot)' : ` (costs ${c.T}t)`}.`);
    }
    if (st.mode === 'load') {
      if (C(st.hand[k]).kind !== 'equipment') return toast('Only equipment cards can fill these slots.');
      if (st.sel !== k) { st.sel = k; return syncHand(); }
      return loadCard(k);
    }
    if (st.mode !== 'idle') return;
    if (!st.handOpen) { st.handOpen = true; st.sel = null; return syncHand(); }
    if (st.sel === k) return C(st.hand[k]).kind === 'action' ? playAction(k) : toast('Play rockets and equipment with Mission Control.');
    st.sel = k; syncHand();
  }
  function useMC() { if (st.freeMC > 0) st.freeMC--; else if (mcLeft() > 0) st.used.mc++; else st.extraMC--; }
  function place(m) {
    const k = st.pending, id = st.hand[k], c = C(id);
    useMC();
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
    render();
    fly(c.html, hand, $('mslot-' + m.i), () => {
      m.cards.push(id); m.card = id; m.fired = false; m.paid = true; render();
      prompt(`Click ${c.name} on Mission ${ROMAN[m.i]} to fire it.`);
    });
  }
  function openCloseup(m) {
    const c = C(m.card);
    st.mode = 'row'; st.firing = m;
    const box = closeup.querySelector('.cu-card');
    box.innerHTML = c.html;
    box.style.setProperty('--cuz', Math.min(3.6, innerHeight * 0.78 / (66 * MM), innerWidth * 0.9 / (47 * MM)).toFixed(2));
    box.querySelectorAll('table.strip tr').forEach((tr, r) => { tr.classList.add('pick'); tr.dataset.r = r; });
    closeup.hidden = false; render();
    prompt(`${c.name}: pick a row. Its tokens stay aboard; its Δv is how far you can move.`);
  }
  function pickRow(r) {
    const m = st.firing, c = C(m.card), row = c.rows[r];
    const had = mass(m.tokens), spare = had - c.T;
    closeup.hidden = true;
    const old = m.tokens.slice(), fresh = row.eq ? [] : tokensFor(row.cargo);
    const slots = (row.eq || 0) + (c.carry || 0);
    m.tokens = []; m.paid = false; m.fired = true; st.mode = 'anim'; render();
    toast(`Paying ${c.T}t${spare > 0 ? ` (${spare}t left over, discarded)` : ''}…`);
    flyTokens(old, () => $('mcargo-' + m.i), t => $('bowl-' + t), () =>
      setTimeout(() => flyTokens(fresh, t => $('bowl-' + t), () => $('mcargo-' + m.i), () => {
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
  // Equipment slots are never kept: fill them now or lose them. On a crewed mission the crew takes the first one.
  const equipInHand = () => st.hand.some(id => C(id).kind === 'equipment');
  function startLoad(m, n, then) {
    if (n > 0 && m.crewed && !m.crew) { m.crew = true; n--; render(); toast(`The crew boards Mission ${ROMAN[m.i]} (1 equipment slot).`); }
    if (n <= 0) return then && then();
    if (!equipInHand()) { setTimeout(() => toast(`No equipment in your hand: ${n} slot${n > 1 ? 's' : ''} lost.`), m.crewed ? 1400 : 0); return then && then(); }
    st.mode = 'load'; st.load = { m, n, then }; st.handOpen = true; st.sel = null;
    syncHand(); render(); camYou();
    prompt(`Load up to ${n} equipment card${n > 1 ? 's' : ''} onto Mission ${ROMAN[m.i]}: click one, then again to load it. Done when finished; unfilled slots are lost.`);
  }
  function loadCard(k) {
    const L = st.load, id = st.hand[k], c = C(id);
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
    if (L.then) L.then(); else prompt();
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
    m.space = sid; clearReach(); st.mode = 'idle'; st.move = null;
    if (sid === 'earth' && from !== 'earth') m.home = true;
    render();
    setTimeout(camYou, 1600);
    const sp = G.spaces[sid];
    if (m.home) toast(`Mission ${ROMAN[m.i]} is home. It's recovered at the end of your turn, after the draw.`);
    else if (sp.stop === 'none') toast(`Mission ${ROMAN[m.i]} can't stop here. Fire another stage before you end your turn, or it fails (a goal here still pays first).`);
    else toast(`Mission ${ROMAN[m.i]} reached ${sp.label || 'its new position'}.`);
    prompt();
  }
  // ---- aerobraking: with Atmospheric Return aboard, blue (and Mars red) crossings are free going down ----
  const hasHeatShield = m => m.equip.some(e => C(e).name === 'ATMOSPHERIC RETURN');
  function aeroPath(m) {
    if (!flying(m) || !hasHeatShield(m) || G.spaces[m.space].kind === 'surface') return null;
    const par = { [m.space]: null }, q = [m.space];
    while (q.length) { const s = q.shift();
      if (G.spaces[s].kind === 'surface') { const path = []; for (let t = s; t; t = par[t]) path.unshift(t); return path; }
      for (const t of aadj[s] || []) if (!(t in par)) { par[t] = s; q.push(t); } }
    return null;
  }
  function aerobrake(m, then) {
    const path = aeroPath(m); if (!path) return;
    for (const s of path) if (!m.visited.includes(s)) m.visited.push(s);
    m.space = path[path.length - 1]; m.arrived = st.turn; st.mode = 'anim';
    if (m.space === 'earth') m.home = true;
    render();
    toast(`Mission ${ROMAN[m.i]} aerobrakes: heat shield, then parachutes…`);
    setTimeout(() => { st.mode = 'idle'; render(); then ? then() : prompt(); }, 1600);
  }
  function cancel() {
    if (st.mode === 'move') { clearReach(); toast('Stayed in place.'); }
    closeup.hidden = true; st.mode = 'idle'; st.pending = null; st.firing = null; st.move = null;
    st.handOpen = false; st.sel = null; syncHand(); render(); prompt();
  }

  // ---- market and goal rows: buy, or take the rightmost instead of launching -----------
  function marketClick(i) {
    const id = st.market[i]; if (!id) return;
    const c = C(id), p = priceAt(id, i), afford = money() >= p.money && science() >= p.science;
    const canToken = i === rightmost(st.market) && money() >= 1;   // pay $1: discard it and take the first player token
    const lack = science() < p.science ? `It needs ⚛${p.science} science (you have ${science()}).` : `It costs $${p.money} (you have $${money()}).`;
    const btns = [];
    if (afford) btns.push({ label: `Buy for ${p.money ? '$' + p.money : 'free'}${p.science ? ` (needs ⚛${p.science})` : ''}`, main: true, fn: () => buy(i) });
    if (canToken) btns.push({ label: `Pay $1: discard it and take the first player token${st.firstPlayer ? ' (you have it)' : ''}`, main: !afford, fn: () => takeToken(i) });
    if (!btns.length) return toast(`${c.name}: ${lack}${i === rightmost(st.market) ? ' With $1 you could discard it and take the first player token.' : ''}`);
    btns.push({ label: 'Cancel' });
    choice(c.html, `${c.name}${afford ? '' : ` · ${lack}`}<br><small>${c.kind === 'improvement' ? 'Improvements stay in front of you, on your Space Center.' : 'Bought cards go to the bottom of your deck.'}</small>`, btns);
  }
  function buy(i) {
    const id = st.market[i], c = C(id), p = priceAt(id, i), lost = pay(p.money);
    st.market.splice(i, 1); st.market.unshift(st.main.pop() || null);
    st.mode = 'anim'; render();
    const to = c.kind === 'improvement' ? $('upg-you') : $('deck-you');
    fly(c.html, $('mk-' + i), to, () => {
      if (c.kind === 'improvement') st.upgrades.push(id); else st.deck.push(id);
      st.mode = 'idle'; render(); prompt();
      toast(`${c.name} ${c.kind === 'improvement' ? 'is on your Space Center' : 'goes to the bottom of your deck'}${lost ? ` (💰${lost} change from the bank)` : ''}.`);
    });
  }
  function takeToken(i) {                                      // pay $1, the rightmost market card is discarded, you go first next round
    const id = st.market[i], lost = pay(1);
    st.market.splice(i, 1); st.market.unshift(st.main.pop() || null); st.firstPlayer = true;
    st.mode = 'anim'; render();
    fly(C(id).html, $('mk-' + i), $('deck-rockets'), () => { st.mode = 'idle'; render(); prompt();
      toast(`${C(id).name} is discarded. You hold the first player token: you go first next round.${lost ? ` (💰${lost} change from the bank)` : ''}`); });
  }
  function goalClick(i) {
    toast(`Missions are claimed at the end of your turn, after the draw, by a mission that meets them.${i < G.goalDvSurcharge ? ' This one is new: its destination is 1 Δv farther.' : ''}`);
  }

  // ---- action cards ---------------------------------------------------------------------
  function playAction(k) {
    const id = st.hand[k], a = C(id);
    if (a.effect === 'backup') return toast('Keep Backup Systems: you\'ll be offered it when you draw a disaster.');
    st.hand.splice(k, 1); st.deck.push(id); st.sel = null; st.handOpen = false; buildHand(); syncHand();
    if (a.effect === 'draw2') { toast('Overtime: drawing 2 cards.'); st.mode = 'anim'; render(); return drawCards(2, () => { st.mode = 'idle'; render(); prompt(); }); }
    if (a.effect === 'audit') {                                   // look at your top 3, then keep the order or shuffle
      const top = st.deck.slice(0, 3); render();
      const dis = top.filter(t => C(t).kind === 'disaster').length;
      return choice('', `<b>Self Audit:</b> your next ${top.length} card${top.length === 1 ? '' : 's'}${dis ? ` (${dis} disaster${dis > 1 ? 's' : ''}!)` : ''}.<div class="peekrow">${top.map(t => `<div class="peek">${C(t).html}</div>`).join('')}</div>`,
        [{ label: 'Shuffle my deck', main: dis > 0, fn: () => { shuffle(st.deck); render(); toast('Deck shuffled.'); } },
         { label: 'Keep this order', main: !dis, fn: () => toast('Deck order kept.') }]);
    }
    if (a.effect === 'extra_mc') { st.extraMC++; render(); return toast('Extra Shift: one more Mission Control this turn.'); }
    render(); toast(`${a.name}: there are no opponents in this prototype yet, so it has no effect. It goes to the bottom of your deck.`);
  }

  // ---- drawing and disasters ----------------------------------------------------------------
  function drawCards(n, done) {
    if (n <= 0) return done();
    if (!st.deck.length) { toast('Your deck is empty.'); return done(); }
    const id = st.deck.shift(); render();
    if (C(id).kind === 'disaster') return disaster(id, () => drawCards(n - 1, done));
    fly(BACK, $('deck-you'), hand, () => { st.hand.push(id); buildHand(); st.handOpen = true; st.sel = st.hand.length - 1; syncHand(); render();
      toast(`You draw ${C(id).name}.`); setTimeout(() => drawCards(n - 1, done), 700); });
  }
  function lose(m, why) {
    const cards = [...m.cards, ...m.equip], toks = m.tokens.slice();
    if (m.crew) st.penalty += 2;
    st.deck.push(...cards);
    Object.assign(m, blank(m.i));
    flyTokens(toks, () => $('mrest-' + m.i), t => $('bowl-' + t), null);
    return `Mission ${ROMAN[m.i]} is lost (${why})${cards.length ? '; its cards go to the bottom of your deck' : ''}.`;
  }
  function disaster(id, next) {
    const d = C(id), fix = d.recurring && fixFor(d);
    cam(G.focusYou);
    const finish = msg => { shuffle(st.deck); render(); choice(d.html, msg + '<br><small>Your deck is shuffled.</small>', [{ label: 'OK', main: true, fn: next }]); };
    if (fix && owns(fix.name)) { st.removed.push(id); return finish(`${d.name}! But your ${fix.name} fixed it for good: the card is removed from your deck.`); }
    const backup = st.hand.findIndex(h => C(h).effect === 'backup');
    const apply = () => {
      const out = [];
      const hit = m => { if (m && m.active && !m.done) { const crewed = m.crew; out.push(lose(m, d.name.toLowerCase())); if (crewed) out.push('The crew is lost: −2★.'); } };
      if (d.effect === 'lose_hand' || d.also === 'lose_hand') { st.deck.push(...st.hand); out.push(st.hand.length ? `Your hand (${st.hand.length}) goes back into your deck.` : 'Your hand was empty.'); st.hand = []; buildHand(); }
      if (d.effect === 'pad') { st.noLaunchNext = true; out.push('No Launch on your next turn.'); }
      if (d.effect === 'accident') { const m = st.missions[d.slot - 1];
        if (m.active && (!d.launched || m.launchedTurn === st.turn)) hit(m);
        else out.push(`Slot ${ROMAN[d.slot - 1]} ${m.active ? 'didn\'t launch this turn' : 'is empty'}: no harm done.`); }
      if (d.effect === 'farthest_uncrewed') {
        const dist = reach('earth', 99), ms = st.missions.filter(m => m.active && !m.crewed && !m.done);
        const m = ms.sort((a, b) => (dist[b.space] || 0) - (dist[a.space] || 0))[0];
        if (m) hit(m); else out.push('You have no uncrewed mission in flight: no harm done.');
      }
      if (d.effect === 'lose_infra') {
        const g = [...st.won].reverse().find(g => G.goals[g].family === d.family);
        if (g) { st.won.splice(st.won.lastIndexOf(g), 1); st.goals.deck.unshift(g); out.push(`You lose a ${d.family.toLowerCase()} card (to the bottom of the contract deck).`, ...kingOfTheHill()); }
        else out.push(`You have no ${d.family.toLowerCase()}: no harm done.`);
      }
      if (d.effect === 'lose_money') { const mc = moneyCards().sort((a, b) => reward(a).n - reward(b).n)[0];
        if (st.cash) { st.cash--; out.push('You lose a 💰1 card.'); }
        else if (mc) { st.spent.add(mc); out.push(`You lose a $${reward(mc).n} money card.`); } else out.push('You have no money to lose.'); }
      if (d.recurring) { st.deck.push(id); out.push(`It stays in your deck until you buy ${fixFor(d).name}.`); }
      else { st.removed.push(id); out.push('A one-shot: it leaves the game.'); }
      finish(`<b>${d.name}!</b> ${out.join(' ')}`);
    };
    if (backup >= 0) return choice(d.html, `<b>${d.name}!</b> ${d.text}<br>Play Backup Systems to ignore it?`, [
      { label: 'Play Backup Systems', main: true, fn: () => { const b = st.hand.splice(backup, 1)[0]; st.deck.push(b, id); buildHand(); render();
        choice(d.html, `Backup Systems! ${d.name} is ignored and goes to the bottom of your deck.`, [{ label: 'OK', main: true, fn: next }]); } },
      { label: 'Take the hit', fn: apply }]);
    apply();
  }

  // ---- goals ------------------------------------------------------------------
  const deepN = sid => { const r = /^ds(\d+)$/.exec(sid); return r ? +r[1] : 0; };
  function effCheck(gid, rowIdx) {                             // new contracts (first 3 in the row) need +1 Δv: one step farther
    const c = Object.assign({}, G.goals[gid].check || {});
    if (rowIdx == null || rowIdx >= G.goalDvSurcharge || !G.goals[gid].check) return c;
    if (c.at && c.at.length === 1 && /^a\d$/.test(c.at[0])) { const n = +c.at[0].slice(1) + 1; c.at = [n <= 8 ? 'a' + n : 'leo']; }
    if (c.deep) c.deep += 1;
    return c;
  }
  function meets(m, c) {
    if (!c || !Object.keys(c).length || !m.active || m.done) return false;
    const names = m.equip.map(e => C(e).name).concat(m.crew ? ['CREW CAPSULE'] : []);
    return (!c.at || c.at.includes(m.space)) && (!c.deep || deepN(m.space) >= c.deep)
      && (!c.visited || c.visited.every(v => m.visited.includes(v)))
      && (!c.equip || c.equip.every(n => names.includes(n)))
      && (!c.without || !c.without.some(n => n === 'CREW CAPSULE' ? m.crewed : names.includes(n)))
      && (!c.equipCount || m.equip.length >= c.equipCount) && (!c.cargo || mass(m.tokens) >= c.cargo)
      && (!c.turns || st.turn - m.arrived >= c.turns);
  }
  // Launched this turn but met no goal: the rightmost mission card is discarded and you take a 💰1 card.
  function consolation(done) {
    const i = rightmost(st.goals.row); cam(G.focusGoals);
    if (i < 0) { st.cash++; render(); toast('No mission met a goal: take a 💰1 card from the bank.'); return setTimeout(done, 900); }
    const gid = st.goals.row[i], from = $('goal-m' + i);
    st.goals.row.splice(i, 1); st.goals.row.unshift(st.goals.deck.pop() || null); from.innerHTML = ''; from.dataset.gid = '';
    fly(G.goals[gid].html, from, $('deck-missions'), () => { render();
      fly(CASH_HTML(1), $('bank'), $('cgoals-you'), () => { st.cash++; render();
        toast(`You launched but met no goal: ${G.goals[gid].name} (rightmost) is discarded and you take a 💰1 card.`); setTimeout(done, 900); }); });
  }
  function prizes(done) {                                       // step 4: every open goal a surviving mission meets pays out
    const claims = [], used = new Set();
    st.goals.perm.forEach((gid, i) => { if (!gid) return; const m = st.missions.find(m => meets(m, effCheck(gid, null)));
      if (m) claims.push({ gid, m, from: $('goal-f' + i), perm: i }); });
    st.goals.row.forEach((gid, i) => { if (!gid) return; const m = st.missions.find(m => !used.has(m.i + G.goals[gid].name) && meets(m, effCheck(gid, i)));
      if (m) { used.add(m.i + G.goals[gid].name); claims.push({ gid, m, from: $('goal-m' + i), row: true }); } });
    if (!claims.length) return st.used.launch ? consolation(done) : done();
    cam(G.focusGoals);
    let k = 0;
    const one = () => {
      if (k >= claims.length) { st.goals.row = st.goals.row.filter(Boolean); while (st.goals.row.length < G.goalRowN) st.goals.row.unshift(st.goals.deck.pop() || null); render(); return setTimeout(done, 600); }
      const h = claims[k++], g = G.goals[h.gid];
      if (h.perm != null) st.goals.perm[h.perm] = null; else st.goals.row[st.goals.row.indexOf(h.gid)] = null;
      h.m.claimed = true;
      if (g.check && g.check.cargo) { const toks = h.m.tokens.slice(); h.m.tokens = []; flyTokens(toks, () => $('mcargo-' + h.m.i), t => $('bowl-' + t), null); }
      h.from.innerHTML = ''; h.from.dataset.gid = ''; render();
      fly(rewardHtml(h.gid), h.from, $('cgoals-you'), () => { st.won.push(h.gid); render();
        let msg = `Mission ${ROMAN[h.m.i]}: ${g.name}! ` + (g.reward.set ? `Your ${g.family.toLowerCase()} set: ${famCount(g.family)} card${famCount(g.family) > 1 ? 's' : ''}.` : `+${ICON[g.reward.kind]}${g.reward.n}`);
        const risk = g.family && famCount(g.family) === 1 && Object.keys(G.cards).find(k => G.cards[k].family === g.family);
        if (risk && !st.deck.includes(risk) && !st.removed.includes(risk)) { st.deck.push(risk); shuffle(st.deck); msg += ` New risk: ${C(risk).name} joins your deck.`; }
        toast(msg); setTimeout(one, 900); });
    };
    one();
  }
  function kingOfTheHill() {                                    // e.g. Largest Space Station: held while you have the most of a family
    const out = [];
    G.goalPerm.forEach((gid, i) => { const k = G.goals[gid].king; if (!k) return;
      const n = famCount(k.family), held = st.won.includes(gid);
      if (n > 0 && !held) { st.won.push(gid); st.goals.perm[i] = null; out.push(`You hold ${G.goals[gid].name} (+${G.goals[gid].reward.n}★).`); }
      if (n === 0 && held) { st.won.splice(st.won.indexOf(gid), 1); st.goals.perm[i] = gid; out.push(`${G.goals[gid].name} goes back: you have no ${k.family.toLowerCase()} left.`); }
    });
    render(); return out;
  }
  function clearMissions() {                                     // step 5: completed missions go home to your deck; park or fail
    const msgs = [];
    for (const m of st.missions) {
      if (!m.active) continue;
      if (m.home || m.claimed) {
        const cards = [...m.cards, ...m.equip], toks = m.tokens.slice();
        st.deck.push(...cards); Object.assign(m, blank(m.i));
        flyTokens(toks, () => $('mrest-' + m.i), t => $('bowl-' + t), null);
        msgs.push(`Mission ${ROMAN[m.i]} is complete; ${cards.length} card${cards.length === 1 ? '' : 's'} to the bottom of your deck.`);
      } else if (G.spaces[m.space].stop === 'none') {
        const crewed = m.crew; msgs.push(lose(m, 'it couldn\'t stop mid-flight')); if (crewed) msgs.push('The crew is lost: −2★.');
      }
    }
    return msgs;
  }
  function endTurn() {
    if (st.mode === 'anim' || !choiceEl.hidden) return;
    if (st.mode !== 'idle') cancel();
    const falling = st.missions.filter(m => flying(m) && G.spaces[m.space].stop === 'none' && aeroPath(m));
    if (falling.length) {                                       // a mid-climb crew with a heat shield falls home safely
      const m = falling[0]; toast(`Mission ${ROMAN[m.i]} can't stay up there; it falls back under its heat shield.`);
      return setTimeout(() => aerobrake(m, endTurn), 900);
    }
    st.mode = 'anim'; render(); camYou();
    prompt(`End of turn ${st.turn}: drawing ${drawSize()} card${drawSize() > 1 ? 's' : ''}…`);
    setTimeout(() => drawCards(drawSize(), () => prizes(() => {
      const msgs = clearMissions().concat(kingOfTheHill());
      st.used = { launch: 0, mc: 0 }; st.freeMC = 0; st.extraMC = 0; st.turn++;
      st.noLaunch = st.noLaunchNext; st.noLaunchNext = false;
      st.missions.forEach(m => { m.claimed = false; });
      st.mode = 'idle'; render(); camYou(); prompt();
      toast([...msgs, `Turn ${st.turn}.${st.noLaunch ? ' No Launch this turn.' : ''}`].join(' '));
    })), 500);
  }

  const why = k => ({
    launch: st.noLaunch ? 'A disaster grounded your pad: no Launch this turn.' : launchesLeft() <= 0 ? 'You already launched (or took a rightmost card) this turn.' : 'All four mission slots are in use.',
    mc: (mcLeft() <= 0 && !st.freeMC && !st.extraMC) ? 'Mission Control is used for this turn.'
      : st.missions.some(m => m.active) ? 'Your missions have no cargo tokens left to spend.'
      : 'Mission Control spends a mission\'s cargo, and you have no mission in flight. Launch one first (Launch includes a free Mission Control).',
  })[k];

  // ---- input (called from the table's pointer handler) -------------------------
  window.game = {
    _st: st,                                                   // read-only peek for debugging/tests
    _render: () => render(),                                   // tests: redraw after poking _st
    tap(target) {
      const t = target.closest ? target : target.parentElement;
      if (st.mode === 'anim' || !choiceEl.hidden) return true;
      if (st.mode === 'launch-pick') {
        const col = t.closest('.mcol'); const m = col && st.missions[+col.dataset.i];
        if (m && !m.active) { launch(m); return true; }
        st.mode = 'idle'; render(); prompt(); return true;
      }
      const bt = t.closest('.btok.can');
      if (bt && st.mode === 'idle') { aerobrake(st.missions[+bt.id.slice(5)]); return true; }
      const act = t.closest('[data-act]');
      if (act) { const k = act.dataset.act; if (st.mode !== 'idle') cancel(); if (can()[k]) ({ launch: startLaunch, mc: startMC })[k](); else toast(why(k)); return true; }
      if (st.mode === 'idle') {
        const mk = t.closest('.mkslot'); if (mk) { marketClick(+mk.id.slice(3)); return true; }
        const gs = t.closest('.gslot');
        if (gs && gs.id.startsWith('goal-m')) { goalClick(+gs.id.slice(6)); return true; }
        if (gs) { toast('Permanent goals pay victory points. They are claimed at the end of your turn, after the draw.'); return true; }
        if (t.closest('#deck-you')) { toast(`Your deck: ${st.deck.length} cards (${st.deck.filter(d => C(d).kind === 'disaster').length} disasters). You draw ${drawSize()} at the end of your turn.`); return true; }
      }
      const hc = t.closest('#hand-you .hc');
      if (hc) { handClick(+hc.dataset.k); return true; }
      const hl = t.closest('.hl');
      if (hl && st.mode === 'move') { moveTo(hl.dataset.s); return true; }
      const col = t.closest('.mcol');
      if (col) {
        const m = st.missions[+col.dataset.i];
        if (st.mode === 'mc-target') { eligible(m) ? place(m) : toast(reason(m)); return true; }
        if (st.mode === 'idle' && t.closest('.mslot') && m.card) { m.fired || !flying(m) ? toast('This stage has fired. Place the next one with Mission Control.') : openCloseup(m); return true; }
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
  addEventListener('keydown', e => { if (e.key !== 'Escape' || !choiceEl.hidden) return; if (st.mode === 'load') finishLoad(); else if (st.mode !== 'idle' && st.mode !== 'anim') cancel(); });
  $('donebtn').addEventListener('click', finishLoad);

  buildHand(); syncHand(); render(); prompt();
  if (innerWidth < 700 && !location.hash) setTimeout(camYou, 300);   // phones: start on your Space Center
})();
'''

if __name__ == "__main__":
    main()
