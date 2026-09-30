"""
Tabletop layout: the game as it sits on a real table, at real size (millimetres).

    data/*.json + site/board.webp ──> build_table.py ──> build/table.html

Static setup view: the printed board in the middle, a Space Center board at each of
the four seats, the shared decks / market rows / token bowls between them. Pan and
zoom only; no game logic. Cards are the real kit cards (build_kit renderer).
Run from src/:  python3 build_table.py
"""
import json
import shutil

from build_kit import (load_cards, engine_card_html, equipment_card_html,
                       objective_card_html, CSS as KIT_CSS)

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
SEAT_W, SEAT_H = 400, 290              # Space Center board (170 deep) + hand in front
PB_H = 170

PLAYERS = [  # seat, colour, rotation, centre
    ("bottom", "Blue",   "#2f6db5", 0,   (BOARD_X + BOARD_W / 2, 1081)),
    ("left",   "Green",  "#2f8f5b", 90,  (BOARD_X - 20 - SEAT_H / 2, BOARD_Y + BOARD_H / 2)),
    ("top",    "Purple", "#7a4bb0", 180, (BOARD_X + BOARD_W / 2, 152)),
    ("right",  "White",  "#e9e6df", 270, (BOARD_X + BOARD_W + 20 + SEAT_H / 2, BOARD_Y + BOARD_H / 2)),
]

TOKEN_COLORS = {"K": "#1c1c1c", "R": "#b3261e", "O": "#e07b00", "Y": "#f0b400"}


def at(x, y, w=None, h=None, extra=""):
    size = (f"width:{w}mm;" if w is not None else "") + (f"height:{h}mm;" if h is not None else "")
    return f'style="left:{x}mm;top:{y}mm;{size}{extra}"'


def card(html, x, y, rot=0):
    return f'<div class="slot" {at(x, y, CARD_W, CARD_H, f"transform:rotate({rot}deg);")}>{html}</div>'


def stack(kind, label, x, y, n=6):
    """A face-down deck: a card back with visible thickness."""
    return (f'<div class="slot stack {kind}" {at(x, y, CARD_W, CARD_H)} style="--n:{n}">'
            f'<div class="card cback {kind}"><span>{label}</span></div></div>')


def zone_label(text, x, y, w=None, align="left"):
    return f'<div class="zlabel" {at(x, y, w, None, f"text-align:{align};")}>{text}</div>'


def cargo(color, x, y, rot=0, size=12):
    """A triangular wooden cargo token."""
    c = TOKEN_COLORS[color]
    return (f'<svg class="tok" {at(x, y, size, size * 0.9, f"transform:rotate({rot}deg);")} viewBox="0 0 20 18">'
            f'<polygon points="10,1 19,17 1,17" fill="{c}" stroke="rgba(0,0,0,.35)" stroke-width="0.8" stroke-linejoin="round"/>'
            f'<polygon points="10,1 19,17 10,12" fill="rgba(255,255,255,.14)"/></svg>')


def rocket_token(color, x, y, size=13, rot=0):
    """A player's wooden mission token (rocket meeple)."""
    return (f'<svg class="tok meeple" {at(x, y, size * 0.62, size, f"transform:rotate({rot}deg);")} viewBox="0 0 16 26">'
            f'<path d="M8,1 C12,5 12.5,10 12,17 L15,22 L15,25 L11,23 L5,23 L1,25 L1,22 L4,17 C3.5,10 4,5 8,1 Z" '
            f'fill="{color}" stroke="rgba(0,0,0,.45)" stroke-width="0.9" stroke-linejoin="round"/>'
            f'<circle cx="8" cy="10" r="2" fill="rgba(255,255,255,.55)"/></svg>')


def bowl(color, label, cx, cy, r=30):
    import random
    rnd = random.Random(color)
    toks = "".join(cargo(color, cx - 6 + rnd.uniform(-r * 0.5, r * 0.5), cy - 5 + rnd.uniform(-r * 0.45, r * 0.45),
                         rnd.uniform(0, 360)) for _ in range(9))
    return (f'<div class="bowl" {at(cx - r, cy - r, 2 * r, 2 * r)}></div>{toks}'
            + zone_label(label, cx - r, cy + r + 3, 2 * r, "center"))


# ---- Space Center (player board) -----------------------------------------
ACTIONS = [
    ("RESEARCH", "Take 1 card: top of the deck, the market, or your own discard pile."),
    ("BUILD", "Play 1 improvement from your hand onto your Space Center."),
    ("LAUNCH", "Launch a rocket from your hand. Pick a row; fly N spaces from Earth; put its cargo in a mission area.<br><b>Basic pad: up to 480t.</b>"),
    ("MOVE", "Pay a rocket's T: cost with a mission's cargo. Pick a row; fly its &Delta;v; its cargo replaces the old."),
]
TAP = ('<svg viewBox="0 0 20 20" class="tap"><path d="M15 6 A7 7 0 1 0 17 11" fill="none" stroke="currentColor" '
       'stroke-width="2.2" stroke-linecap="round"/><polygon points="12,2 18,6 12,9" fill="currentColor"/></svg>')


def space_center(name, color, flying=None):
    """flying: {mission_index: [cargo colours]} for missions currently on the board."""
    flying = flying or {}
    acts = "".join(
        f'<div class="action" {at(8 + i * (CARD_W + 5), 22, CARD_W, CARD_H)}>'
        f'<div class="ahead">{TAP}<span>{t}</span></div><div class="atext">{txt}</div></div>'
        for i, (t, txt) in enumerate(ACTIONS))
    missions = ""
    for i in range(4):
        mx, my = 222 + (i % 2) * 87, 22 + (i // 2) * 72
        body = ""
        if i in flying:
            body = "".join(cargo(c, 20 + k * 13, 34, 0) for k, c in enumerate(flying[i]))
            body += '<div class="inflight">in flight</div>'
        else:
            body = rocket_token(color, 60, 34, 16)
        missions += (f'<div class="marea" {at(mx, my, 83, 68)}><div class="mname">MISSION {"I II III IV".split()[i]}</div>'
                     f'<div class="rest" {at(58, 32, 16, 20)}></div>{body}</div>')
    return f'''<div class="pboard" style="--pc:{color};">
  <div class="pb-title">SPACE CENTER <span>· {name}</span></div>
  {acts}
  <div class="improve" {at(8, 94, 4 * CARD_W + 15, 68)}>improvements are built here, or on top of an action</div>
  {missions}
</div>'''


def seat(seat_name, pname, color, rot, center, flying=None):
    cx, cy = center
    x, y = cx - SEAT_W / 2, cy - SEAT_H / 2
    fan = "".join(
        f'<div class="slot handcard" {at(SEAT_W / 2 - CARD_W / 2 + (k - 2) * 22, PB_H + 14 + abs(k - 2) * 3, CARD_W, CARD_H, f"transform:rotate({(k - 2) * 7}deg);")}>'
        f'<div class="card cback rockets"><span>ROCKETS</span></div></div>' for k in range(5))
    discard = (f'<div class="dslot" {at(SEAT_W + 8, 50, CARD_W, CARD_H)}><span>DISCARD</span></div>')
    return (f'<div class="seat" {at(x, y, SEAT_W, SEAT_H, f"transform:rotate({rot}deg);")}>'
            f'{space_center(pname, color, flying)}{discard}{fan}'
            f'<div class="zlabel handlabel" {at(0, PB_H + 14 + CARD_H + 16, SEAT_W, None, "text-align:center;")}>{pname} player’s hand</div></div>')


def board_pos(space_id):
    s = next(s for s in BOARD["spaces"] if s["id"] == space_id)
    return BOARD_X + s["x"] / 1000 * BOARD_W, BOARD_Y + s["y"] / 707 * BOARD_H


def main():
    parts = []
    # Main board
    parts.append(f'<img class="mainboard" src="board.webp" alt="Earth to Mars board" {at(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)}>')

    # Goals: FIRSTs (always open) + missions deck and 5-card market
    firsts = [o for o in OBJS if o["type"] == "FIRST"]
    fx = BOARD_X - 25
    parts.append(zone_label("FIRSTS · always open", fx, 305))
    for i, o in enumerate(firsts):
        parts.append(card(objective_card_html(o), fx + i * (CARD_W + GAP), 318))
    mx = fx + 6 * (CARD_W + GAP) + 24
    parts.append(zone_label("MISSIONS · deck + 5 open", mx, 305))
    parts.append(stack("missions", "MISSIONS", mx, 318, 10))
    for i, name in enumerate(["LARGEST SPACE STATION", "VENERA", "COMSAT", "WEATHER WATCH", "INTERCONTINENTAL EXPRESS"]):
        parts.append(card(objective_card_html(OBJ[name]), mx + (i + 1) * (CARD_W + GAP) - 2, 318))

    # Rockets & tech: main deck + open market
    ry = BOARD_Y + BOARD_H + 22
    parts.append(zone_label("ROCKETS &amp; TECH · deck + open market", BOARD_X, ry - 13))
    parts.append(stack("rockets", "ROCKETS", BOARD_X, ry, 14))
    market = [engine_card_html(ENG["KEROLOX SUSTAINER"]), engine_card_html(ENG["KEROLOX BOOSTER"]),
              engine_card_html(ENG["HYDROLOX UPPER"]), equipment_card_html(EQ["CREW CAPSULE"])]
    for i, h in enumerate(market):
        parts.append(card(h, BOARD_X + (i + 1) * (CARD_W + GAP), ry))

    # Cargo token bowls
    bx = BOARD_X + 5 * (CARD_W + GAP) + 45
    parts.append(zone_label("CARGO TOKENS", bx - 30, ry - 13))
    for i, (c, lbl) in enumerate([("K", "K · 640t"), ("R", "R · 160t"), ("O", "O · 40t"), ("Y", "Y · 10t")]):
        parts.append(bowl(c, lbl, bx + i * 70, ry + 30))

    # Seats. Example in-flight mission for Blue: 3 orange cargo aboard, token in LEO.
    for s, pname, color, rot, center in PLAYERS:
        flying = {0: ["O", "O", "O"]} if s == "bottom" else None
        parts.append(seat(s, pname, color, rot, center, flying))
    lx, ly = board_pos("leo")
    parts.append(rocket_token(PLAYERS[0][2], lx - 4, ly - 8, 14))

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
  <div id="table" style="width:{TABLE_W}mm;height:{TABLE_H}mm;">
    {"".join(parts)}
  </div>
</div>
<div class="hud">
  <span class="ttl">Rocket Science · table layout</span>
  <button id="zout" aria-label="Zoom out">&minus;</button><button id="zfit">Fit</button><button id="zin" aria-label="Zoom in">+</button>
</div>
<script>{PANZOOM_JS}</script>
</body>
</html>'''
    with open("../build/table.html", "w") as f:
        f.write(html)
    shutil.copy("../site/board.webp", "../build/board.webp")   # so build/table.html previews locally
    print(f"Wrote ../build/table.html ({len(html):,} bytes)")


TABLE_CSS = r'''
html, body { margin: 0; height: 100%; overflow: hidden; background: #2a1c12; font-size: 9px; }
#viewport { position: fixed; inset: 0; overflow: hidden; cursor: grab; touch-action: none; }
#viewport.drag { cursor: grabbing; }
#table {
  position: absolute; left: 0; top: 0; transform-origin: 0 0; will-change: transform;
  border-radius: 14mm;
  background:
    radial-gradient(ellipse at 50% 45%, rgba(255,220,170,.10), rgba(0,0,0,.28) 75%),
    repeating-linear-gradient(90deg, rgba(0,0,0,.05) 0 2mm, rgba(255,255,255,.025) 2mm 3.5mm, rgba(0,0,0,.035) 3.5mm 7mm),
    repeating-linear-gradient(90deg, #6b4428 0 41mm, #714a2c 41mm 83mm, #65402a 83mm 128mm);
  box-shadow: inset 0 0 0 4mm #4a2e1b, inset 0 0 18mm rgba(0,0,0,.45), 0 10px 40px rgba(0,0,0,.6);
}
#table > *, .seat > *, .pboard > *, .marea > * { position: absolute; }
.mainboard { border-radius: 2mm; box-shadow: 0 0.6mm 0 #cfc6b4, 0 1.2mm 0 #b9ae98, 0 3mm 8mm rgba(0,0,0,.55); background: #fff; }
.slot > .card { width: 100%; height: 100%; border-radius: 1.8mm; box-shadow: 0 1.2mm 3mm rgba(0,0,0,.45); }
.stack > .card { box-shadow:
    0.35mm 0.35mm 0 #e8e2d6, 0.7mm 0.7mm 0 #cfc7b8, 1.05mm 1.05mm 0 #e8e2d6, 1.4mm 1.4mm 0 #cfc7b8,
    1.75mm 1.75mm 0 #e8e2d6, 2.1mm 2.1mm 0 #bdb4a3, 3mm 3.5mm 6mm rgba(0,0,0,.5); }
.card.cback span { font-size: 13pt; }
.zlabel { color: rgba(255,236,200,.62); font: 700 3.3mm/1 Helvetica, Arial, sans-serif; letter-spacing: 0.5mm; text-transform: uppercase; white-space: nowrap; }
.tok { filter: drop-shadow(0 0.7mm 0.6mm rgba(0,0,0,.55)); }
.bowl { border-radius: 50%;
  background: radial-gradient(circle at 50% 45%, #3b2718 0 55%, #5a3b22 70%, #8a6038 86%, #4a2f1b 100%);
  box-shadow: 0 2mm 5mm rgba(0,0,0,.5), inset 0 2mm 5mm rgba(0,0,0,.6); }

.pboard { left: 0; top: 0; width: 400mm; height: 170mm; border-radius: 4mm;
  background: linear-gradient(#f7f2e7, #efe7d6); border: 2.2mm solid var(--pc);
  box-shadow: 0 0.6mm 0 #d8cdb6, 0 1.2mm 0 #c3b69c, 0 3mm 8mm rgba(0,0,0,.5); font-family: Helvetica, Arial, sans-serif; color: #1d1d1d; }
.pb-title { left: 8mm; top: 5mm; font-weight: 800; font-size: 5mm; letter-spacing: 0.6mm; }
.pb-title span { font-weight: 600; color: #6b6356; }
.action { background: #fff; border: 0.35mm solid #2a2a2a; border-radius: 1.8mm; overflow: hidden; }
.ahead { display: flex; align-items: center; gap: 1.5mm; background: #1d1d1d; color: #fff; padding: 2mm 2.5mm; font-weight: 800; font-size: 3.6mm; letter-spacing: 0.4mm; }
.tap { width: 4mm; height: 4mm; color: #f0b400; flex: none; }
.atext { padding: 2.5mm; font-size: 2.9mm; line-height: 1.35; color: #333; }
.improve { border: 0.4mm dashed #b3a78f; border-radius: 1.8mm; color: #a0947c; font-size: 2.8mm; display: flex; align-items: center; justify-content: center; text-align: center; padding: 4mm; }
.marea { border: 0.4mm solid #cbbd9f; border-radius: 1.8mm; background: rgba(255,255,255,.5); }
.mname { left: 3mm; top: 2.5mm; font-weight: 800; font-size: 3mm; letter-spacing: 0.4mm; color: #6b6356; }
.rest { border-radius: 50%; border: 0.4mm dashed #b3a78f; }
.marea .meeple { left: 59.7mm !important; top: 33.5mm !important; }
.inflight { left: 3mm; bottom: 3mm; font-size: 2.6mm; color: #8a7e66; font-style: italic; }
.dslot { border: 0.5mm dashed rgba(255,236,200,.45); border-radius: 1.8mm; display: flex; align-items: center; justify-content: center; }
.dslot span { color: rgba(255,236,200,.55); font: 700 3mm Helvetica, Arial, sans-serif; letter-spacing: 0.5mm; transform: rotate(-90deg); }
.handcard { transform-origin: 50% 120%; }
.handlabel { font-size: 2.8mm; }

.hud { position: fixed; right: 16px; bottom: 16px; display: flex; align-items: center; gap: 6px; font: 600 12px Helvetica, Arial, sans-serif; }
.hud .ttl { color: rgba(255,236,200,.7); margin-right: 8px; }
.hud button { font: 700 14px Helvetica, Arial, sans-serif; min-width: 34px; height: 34px; border-radius: 17px; border: 1px solid rgba(255,236,200,.35);
  background: rgba(30,20,12,.75); color: #f3e6cf; cursor: pointer; padding: 0 12px; }
.hud button:hover { background: rgba(60,40,24,.9); }
@media (max-width: 600px) { .hud .ttl { display: none; } }
'''

PANZOOM_JS = r'''
(() => {
  const vp = document.getElementById('viewport'), tb = document.getElementById('table');
  const MM = 96 / 25.4;
  const W = tb.offsetWidth, H = tb.offsetHeight;
  let s = 1, x = 0, y = 0;
  const MIN = 0.08, MAX = 4;
  const apply = () => { tb.style.transform = `translate(${x}px,${y}px) scale(${s})`; };
  const fit = () => {
    s = Math.min(innerWidth / W, innerHeight / H) * 0.96;
    x = (innerWidth - W * s) / 2; y = (innerHeight - H * s) / 2; apply();
  };
  const zoomAt = (f, cx, cy) => {
    const ns = Math.min(MAX, Math.max(MIN, s * f));
    x = cx - (cx - x) * ns / s; y = cy - (cy - y) * ns / s; s = ns; apply();
  };
  vp.addEventListener('wheel', e => {
    e.preventDefault();
    if (e.ctrlKey || e.deltaMode === 1 || Math.abs(e.deltaY) >= 40 && e.deltaX === 0) {
      zoomAt(Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)), e.clientX, e.clientY);
    } else { x -= e.deltaX; y -= e.deltaY; apply(); }
  }, { passive: false });
  const pts = new Map(); let last = null;
  vp.addEventListener('pointerdown', e => { vp.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); vp.classList.add('drag'); last = null; });
  vp.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    const prev = pts.get(e.pointerId); pts.set(e.pointerId, e);
    if (pts.size === 1) { x += e.clientX - prev.clientX; y += e.clientY - prev.clientY; apply(); }
    else if (pts.size === 2) {
      const [a, b] = [...pts.values()];
      const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      const mx = (a.clientX + b.clientX) / 2, my = (a.clientY + b.clientY) / 2;
      if (last) { x += mx - last.mx; y += my - last.my; zoomAt(d / last.d, mx, my); }
      last = { d, mx, my };
    }
  });
  const up = e => { pts.delete(e.pointerId); last = null; if (!pts.size) vp.classList.remove('drag'); };
  vp.addEventListener('pointerup', up); vp.addEventListener('pointercancel', up);
  document.getElementById('zin').onclick = () => zoomAt(1.3, innerWidth / 2, innerHeight / 2);
  document.getElementById('zout').onclick = () => zoomAt(1 / 1.3, innerWidth / 2, innerHeight / 2);
  document.getElementById('zfit').onclick = fit;
  addEventListener('resize', fit);
  fit();
})();
'''

if __name__ == "__main__":
    main()
