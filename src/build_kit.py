"""
Build the Triskelion complete kit HTML with silhouettes on every card.
"""

import json
import html as html_lib
from silhouettes import silhouette_for_engine, silhouette_for_equipment

CARDS_PATH = "../data/cards.json"

def load_cards(path=CARDS_PATH):
    """Load cards.json and apply the kit's render-time adjustments. Returns
    (data, sorted_engines). Importable with no side effects so other tools
    (e.g. build_playtest_report.py) can reuse the card renderers below."""
    with open(path) as f:
        data = json.load(f)

    data.setdefault("model", {})
    data["model"]["board_symbols"] = {
        "circle": "CIRCLE = stable. Craft may park here indefinitely.",
        "square": "SQUARE = waypoint. Craft may end turn but must move next.",
        "triangle": "TRIANGLE = mid-action. Craft cannot end turn here.",
    }
    data["model"]["card_format"] = {
        "page": "A4 (210mm x 297mm)",
        "grid": "4 cols x 4 rows = 16 cards per page",
        "card": "~47mm x 69mm",
        "illustration": "Hand-drawn SVG silhouettes embedded inline; active stage solid white, rest outline",
    }

    all_engines = sorted(data["engines"],
                         key=lambda e: (
                             {"KEROLOX": 1, "HYDROLOX": 2, "METHALOX": 3,
                              "SOLID": 4, "HYPERGOLIC": 5, "NUCLEAR": 6, "ION": 7}.get(
                                  e.get("fuel_type", "").upper(), 8),
                             e.get("precursor_tier") or 99,
                             e.get("total_mass_t", 0)))
    for e in all_engines:
        e["page"] = 1
    return data, all_engines

TOKEN_VALUE = {"Y": 10, "O": 40, "R": 160, "K": 640}
def tokens_for_mass(mass_t):
    if not mass_t or mass_t <= 0:
        return ""
    remaining, out = mass_t, []
    for letter in ("K", "R", "O", "Y"):
        v = TOKEN_VALUE[letter]
        while remaining >= v:
            out.append(letter)
            remaining -= v
    if remaining > 0:
        out.append("Y")
    return "".join(out)

def render_tokens(s, compact_at=5):
    """Render token glyphs. A run of >= compact_at identical tokens collapses to
    'N×<glyph>' so huge first stages (Super Heavy = 6×K, Sea Dragon = 25×K) stay
    legible instead of printing 25 squares."""
    if not s:
        return ""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        j = i
        while j < len(s) and s[j] == c:
            j += 1
        n = j - i
        if n >= compact_at:
            out.append(f'<span class="tk-mult">{n}×</span>'
                       f'<span class="t t-{c.lower()}">{c}</span>')
        else:
            out.extend(f'<span class="t t-{c.lower()}">{c}</span>' for _ in range(n))
        i = j
    return "".join(out)

FUEL_CLASS = {
    "KEROLOX": "f-ker", "HYDROLOX": "f-hyd", "METHALOX": "f-met",
    "HYPERGOLIC": "f-hyp", "SOLID": "f-sol", "ION": "f-ion",
    "NUCLEAR": "f-nuc", "": "f-other",
}
IGN_LABEL = {"earth": "GND", "space": "SPC", "both": "G+S", "mars-surface": "MARS"}

def weight_class(e):
    """Return weight-class CSS class based on the leading (largest) token of total mass.
    Y leading => LIGHT, O => MEDIUM, R => HEAVY, K => SUPER."""
    toks = e.get("total_tokens") or tokens_for_mass(e.get("total_mass_t", 0))
    if not toks:
        return "wc-medium"
    leading = toks[0]
    return {"K": "wc-super", "R": "wc-heavy", "O": "wc-medium", "Y": "wc-light"}.get(leading, "wc-medium")

def weight_class_label(e):
    """Human-readable weight class label for the card."""
    cls = weight_class(e)
    return {"wc-light": "LIGHT", "wc-medium": "MEDIUM",
            "wc-heavy": "HEAVY", "wc-super": "SUPER"}.get(cls, "MEDIUM")

def esc(s):
    return html_lib.escape(str(s)) if s is not None else ""


def engine_card_html(e):
    fuel = e.get("fuel_type") or ""
    wclass = weight_class(e)
    wlabel = weight_class_label(e)
    ign = IGN_LABEL.get(e.get("ignition", ""), "")
    total_t = e.get("total_mass_t", 0)
    dry_t = e.get("dry_mass_t", 0)
    fuel_t = max(0, total_t - dry_t)
    total_toks = e.get("total_tokens") or tokens_for_mass(total_t)
    dry_toks = e.get("dry_tokens") or tokens_for_mass(dry_t)
    fuel_toks = tokens_for_mass(fuel_t) if fuel_t > 0 else ""

    real_total = e.get("real_total_mass_t")
    real_note = ""
    if real_total and abs(real_total - total_t) > 0.5:
        real_note = f' <span class="real">~{esc(real_total)}t</span>'

    if e.get("kind") == "fixed" or not e.get("strip"):
        ft = e.get("fixed_text") or "Fixed-function card."
        body = f'<div class="fixed">{esc(ft)}</div>'
        if e.get("kind") == "engine_only":
            body += '<div class="eo-note">ENGINE ONLY (pairs w/ tank)</div>'
    else:
        # Split token rows from sub-token equipment rows. Always keep the equipment
        # tail (the high-dv marginal-payload rows) visible despite the 9-row cap.
        eq_rows = [r for r in e["strip"] if r.get("eq")]
        tok_rows = [r for r in e["strip"] if not r.get("eq")]
        shown = tok_rows[: max(0, 9 - len(eq_rows))] + eq_rows
        rows = []
        for r in shown:
            if r.get("eq"):
                n = r["eq"]
                pips = "".join('<span class="t t-eq">◆</span>' for _ in range(n))
                cargo_cell = f'<td class="ct">{pips}</td><td class="tt">{n} eq</td>'
            else:
                cargo_cell = (f'<td class="ct">{render_tokens(tokens_for_mass(r["cargo_t"]))}</td>'
                              f'<td class="tt">{esc(r["cargo_t"])}t</td>')
            rows.append(f'<tr>{cargo_cell}<td class="dv">{esc(r["dv"])}</td></tr>')
        body = '<table class="strip"><tbody>' + "".join(rows) + '</tbody></table>'

    # Equipment-carry note (renders below the strip if the engine carries equipment)
    eq_carry = e.get("equipment_carry", 0)
    eq_note = f'<div class="eq-carry">+ {eq_carry} equipment cards</div>' if eq_carry else ""

    silhouette = silhouette_for_engine(e["name"], e.get("page", 1))
    # On lighter backgrounds (yellow, orange) the white silhouette has poor
    # contrast — swap to dark fill / mid-gray outline. Dark backgrounds (red,
    # black) keep the default white-on-dark.
    if wclass in ("wc-light", "wc-medium"):
        silhouette = (silhouette
                      .replace('"white"', '"#1a1a1a"')
                      .replace('#bdbdbd', '#555'))

    tech_label = e.get("tech_label", "")
    tech_badge = f'<div class="tech-label">{esc(tech_label)}</div>' if tech_label else ""

    return f'''
<div class="card eng {wclass}">
  <div class="illus">{silhouette}{tech_badge}</div>
  <div class="content">
    <div class="title">{esc(e["name"])}</div>
    <div class="herit">{esc(e.get("heritage",""))}</div>
    <div class="tags"><span class="fuel">{esc(fuel)}</span><span class="ign">{esc(ign)}</span><span class="wc-tag">{wlabel}</span></div>
    <div class="isp">Isp {esc(e.get("isp_s",""))}s</div>
    <div class="mass"><span class="lbl">T:</span> {render_tokens(total_toks)} <span class="paren">({esc(total_t)}t){real_note}</span></div>
    <div class="mass fuel-row"><span class="lbl">F:</span> {render_tokens(fuel_toks)} <span class="paren">({esc(fuel_t)}t)</span></div>
    <div class="mass"><span class="lbl">D:</span> {render_tokens(dry_toks)} <span class="paren">({esc(dry_t)}t)</span></div>
    {body}
    {eq_note}
    <div class="req">{esc(e.get("requires",""))}</div>
  </div>
</div>'''


WC_BY_TOKEN = {"K": "wc-super", "R": "wc-heavy", "O": "wc-medium", "Y": "wc-light", "E": "wc-eq"}
WC_NAME = {"wc-super": "SUPER", "wc-heavy": "HEAVY", "wc-medium": "MEDIUM", "wc-light": "LIGHT",
           "wc-eq": "EQUIPMENT"}

def bundle_card_html(b):
    """A bundle multiplier card: clip onto one rocket (or sub-token craft) to fly it as
    N identical ones (carry N x cargo at the same dv). The big multiplier sits on the
    class colour ribbon. Rocket bundles live on the rocket pages; the blue EQUIPMENT
    bundles live on the equipment pages."""
    n = b["mult"]
    token = b["token"]
    wclass = WC_BY_TOKEN.get(token, "wc-medium")
    wlabel = WC_NAME[wclass]
    if token == "E":
        title = "EQUIPMENT BUNDLE"
        herit = "EQUIPMENT class &middot; clips to a sub-token craft (equipment-scale)"
        rule = (f'Fly <b>{n} identical craft</b> as one: this craft carries '
                f'<b>&times;{n} its equipment at the same dv</b>.')
        small = f"The stage beneath must lift {n}&times; the craft's mass."
    else:
        title = "ROCKET BUNDLE"
        herit = f"{wlabel} class &middot; clips to a {token}-class rocket"
        rule = (f'Fly <b>{n} identical rockets</b> as one: this {wlabel.lower()} rocket carries '
                f'<b>&times;{n} its cargo at the same dv</b>.')
        small = f"The stage beneath must lift {n}&times; this rocket's total mass."
    return f'''
<div class="card bundle {wclass}">
  <div class="illus"><div class="bundle-big">&times;{n}</div></div>
  <div class="content">
    <div class="title">{title}</div>
    <div class="herit">{herit}</div>
    <div class="bundle-rule">{rule}</div>
    <div class="bundle-rule small">{small}</div>
  </div>
</div>'''


def card_page(title, num, total, card_htmls):
    """Render one A4 sheet from a list of pre-built card HTML strings (engines, bundles, …)."""
    return f'''
<section class="page">
  <header><span class="ph-title">{esc(title)}</span><span class="ph-num">TRISKELION | p{num}/{total}</span></header>
  <div class="grid">{_grid_cards(card_htmls)}</div>
</section>'''


def equipment_card_html(eq):
    extra = "burner" if eq["name"] == "BURNER ENGINE" else ""
    extra += " consumables" if eq["name"] == "CONSUMABLES" else ""
    is_refinery = eq["name"] in ("HYDROLOX REFINERY", "METHALOX REFINERY")
    if is_refinery:
        extra += " refinery"
    silhouette = silhouette_for_equipment(eq["name"])
    rot_overlay = ""
    if eq["name"] == "CONSUMABLES":
        rot_overlay = (
            '<div class="rot-100">100%</div>'
            '<div class="rot-75">75%</div>'
            '<div class="rot-50">50%</div>'
            '<div class="rot-25">25%</div>'
        )
    elif is_refinery:
        # Counts UP — each rotation step fills a quarter of the next tank token
        rot_overlay = (
            '<div class="rot-100">&#9733; FULL</div>'
            '<div class="rot-75">3/4</div>'
            '<div class="rot-50">2/4</div>'
            '<div class="rot-25">1/4</div>'
        )
    tech_label = eq.get("tech_label", "")
    tech_badge = f'<div class="tech-label eq-badge">{esc(tech_label)}</div>' if tech_label else ""
    return f'''
<div class="card eq {extra}">
  <div class="illus">{silhouette}{rot_overlay}{tech_badge}</div>
  <div class="content">
    <div class="title">{esc(eq["name"])}</div>
    <div class="eq-label">EQUIPMENT</div>
    <div class="desc">{esc(eq.get("desc",""))}</div>
    <div class="eq-note">{esc(eq.get("note",""))}</div>
  </div>
</div>'''


def _grid_cards(card_htmls):
    """Join card HTML and pad the 4x4 grid with blank card outlines, so the last page
    of a deck still prints a full 16-slot sheet. Keeps cut lines and the duplex backs
    aligned (every front has a full grid behind it) and yields spare blank cards."""
    padded = list(card_htmls) + ['<div class="card blank"></div>'] * (PER_PAGE - len(card_htmls))
    return "\n".join(padded)


def back_page(label, cls):
    """A full sheet of identical card backs (printed on the even pages, behind each
    front sheet). label = ROCKETS (red) for the engine+equipment deck, MISSIONS (gold)
    for the objective deck. Same header + grid geometry as the fronts so they register."""
    one = f'<div class="card cback {cls}"><span>{esc(label)}</span></div>'
    cards = "\n".join([one] * PER_PAGE)
    return f'''
<section class="page back-page">
  <header><span class="ph-title">{esc(label)}</span><span class="ph-num">TRISKELION | card backs</span></header>
  <div class="grid">{cards}</div>
</section>'''


BACK_KIND = {"rockets": ("ROCKETS", "rockets"), "missions": ("MISSIONS", "missions")}

def mixed_back_page(kinds):
    """Backs for a MIXED front sheet (e.g. equipment + filler missions on one page).
    kinds = per-slot back kind in FRONT order ('rockets' | 'missions'). Each row of 4
    is horizontally REVERSED so the backs land behind their fronts under a long-edge
    duplex flip (uniform sheets never needed this; mixed ones do)."""
    kinds = list(kinds) + ["rockets"] * (PER_PAGE - len(kinds))
    cells = []
    for r in range(0, PER_PAGE, 4):
        for k in kinds[r:r + 4][::-1]:
            label, cls = BACK_KIND[k]
            cells.append(f'<div class="card cback {cls}"><span>{label}</span></div>')
    return f'''
<section class="page back-page">
  <header><span class="ph-title">CARD BACKS (mixed)</span><span class="ph-num">TRISKELION | card backs</span></header>
  <div class="grid">{"".join(cells)}</div>
</section>'''


OBJ_TYPE_COLOR = {
    "FIRST":      "#b8860b",
    "FLYBY":      "#5d2a91",
    "MOST":       "#1b3a6b",
    "RESCUE":     "#a83232",
    "ENDURANCE":  "#1b4332",
    # filler contract types (the 12 expendable space-fillers on the equipment sheet)
    "COMMERCIAL": "#0e7490",
    "MILITARY":   "#556b2f",
    "SCIENCE":    "#46237a",
}

OBJ_TYPE_ICON = {
    "FIRST":     '<svg viewBox="0 0 20 20"><polygon points="10,2 12,7 18,7 13,11 15,18 10,14 5,18 7,11 2,7 8,7" fill="#b8860b"/></svg>',
    "FLYBY":     '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="3" fill="#5d2a91"/><ellipse cx="10" cy="10" rx="9" ry="3" fill="none" stroke="#5d2a91" stroke-width="1.5" transform="rotate(-20 10 10)"/></svg>',
    "MOST":      '<svg viewBox="0 0 20 20"><rect x="3" y="13" width="4" height="5" fill="#1b3a6b"/><rect x="8" y="8" width="4" height="10" fill="#1b3a6b"/><rect x="13" y="3" width="4" height="15" fill="#1b3a6b"/></svg>',
    "RESCUE":    '<svg viewBox="0 0 20 20"><path d="M3 10 Q 10 2 17 10 Q 10 18 3 10 Z" fill="none" stroke="#a83232" stroke-width="2"/><circle cx="10" cy="10" r="3" fill="#a83232"/></svg>',
    "ENDURANCE": '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="7" fill="none" stroke="#1b4332" stroke-width="2"/><line x1="10" y1="10" x2="10" y2="5" stroke="#1b4332" stroke-width="2"/><line x1="10" y1="10" x2="14" y2="12" stroke="#1b4332" stroke-width="2"/></svg>',
    "COMMERCIAL": '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="8" fill="none" stroke="#0e7490" stroke-width="2"/><text x="10" y="14.2" font-size="11" font-weight="bold" text-anchor="middle" fill="#0e7490">$</text></svg>',
    "MILITARY":   '<svg viewBox="0 0 20 20"><path d="M10 2 L17 5 V10 Q17 16 10 18 Q3 16 3 10 V5 Z" fill="#556b2f"/></svg>',
    "SCIENCE":    '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="2" fill="#46237a"/><ellipse cx="10" cy="10" rx="8" ry="3" fill="none" stroke="#46237a" stroke-width="1.2"/><ellipse cx="10" cy="10" rx="8" ry="3" fill="none" stroke="#46237a" stroke-width="1.2" transform="rotate(60 10 10)"/><ellipse cx="10" cy="10" rx="8" ry="3" fill="none" stroke="#46237a" stroke-width="1.2" transform="rotate(120 10 10)"/></svg>',
}


def objective_card_html(o):
    color = OBJ_TYPE_COLOR.get(o["type"], "#444")
    icon = OBJ_TYPE_ICON.get(o["type"], "")
    vp_stars = ''.join('<span class="vp-star">&#9733;</span>' for _ in range(o["vp"]))
    note = f'<div class="obj-note">{esc(o.get("note",""))}</div>' if o.get("note") else ""
    return f'''
<div class="card obj" style="--accent: {color};">
  <div class="obj-head">
    <div class="obj-icon">{icon}</div>
    <div class="obj-type-label">{esc(o["type"])}</div>
    <div class="obj-vp">{vp_stars}</div>
  </div>
  <div class="obj-title">{esc(o["name"])}</div>
  <div class="obj-tagline">{esc(o["tagline"])}</div>
  <div class="obj-desc">{esc(o["desc"])}</div>
  <div class="obj-req">{esc(o["requires"])}</div>
  {note}
</div>'''


def objective_page(num, total, objs):
    cards = _grid_cards([objective_card_html(o) for o in objs])
    return f'''
<section class="page">
  <header><span class="ph-title">OBJECTIVE CARDS</span><span class="ph-num">TRISKELION | p{num}/{total}</span></header>
  <div class="grid">{cards}</div>
</section>'''


# NOTE: The embedded design-reference pages were removed — all of that content now
# lives in docs/*.md (the canonical design memory). The kit PDF is cards only.

CSS = '''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 9px; color: #1d1d1d; margin: 0; background: #ece9e0; }

.page { width: 210mm; height: 297mm; padding: 8mm; background: white; page-break-after: always; position: relative; margin: 0 auto 10px; }
.page:last-child { page-break-after: auto; }
@media print { body { background: white; } .page { margin: 0; box-shadow: none; } }

header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 0.4pt solid #222; padding-bottom: 2mm; margin-bottom: 3mm; font-size: 8.5pt; height: 7mm; }
.ph-title { font-weight: bold; letter-spacing: 0.4pt; }
.ph-num { color: #666; font-size: 7.5pt; }

.grid { display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, 1fr); gap: 2mm; height: calc(297mm - 16mm - 10mm); }

.card { background: white; border: 0.4pt solid #2a2a2a; display: flex; overflow: hidden; position: relative; }

/* Blank card outline — fills the unused slots on a deck's last page (spare blanks) */
.card.blank { background: #fff; }

/* Rocket-bundle multiplier cards (live on the rocket pages) — big ×N on the colour ribbon */
.card.bundle .bundle-big { font-size: 40pt; font-weight: 800; letter-spacing: -2pt; line-height: 1; }
.wc-super .bundle-big, .wc-heavy .bundle-big, .wc-eq .bundle-big { color: #fff; }
.wc-medium .bundle-big, .wc-light .bundle-big { color: #1a1a1a; }
.wc-eq .illus { background: #1b3a6b; }  /* E leading: equipment blue */
.card.bundle .bundle-rule { font-size: 7pt; line-height: 1.3; margin: 2mm 0 1mm; }
.card.bundle .bundle-rule.small { font-size: 5.8pt; color: #555; }

/* Card backs (even pages) — a full sheet of identical deck backs */
.card.cback { align-items: center; justify-content: center; text-align: center; }
.card.cback span { color: #fff; font-weight: 800; font-size: 17pt; letter-spacing: 1.5pt; text-transform: uppercase; }
.card.cback.rockets  { background: #b01818; border-color: #7d1010; }   /* red — engine + equipment deck */
.card.cback.missions { background: #b8860b; border-color: #8a6608; }   /* gold — objective deck */

.illus { width: 18mm; min-width: 18mm; padding: 1mm; display: flex; align-items: center; justify-content: center; position: relative; }
.illus svg { width: 100%; height: 100%; max-height: 62mm; }
/* Engine art stops above the tech badge so tall stacks' bells don't run under it */
.eng .illus { padding-bottom: 7.5mm; }
.tech-label {
  position: absolute;
  bottom: 1.5mm;
  left: 1.5mm;
  font-family: Helvetica, Arial, sans-serif;
  font-weight: bold;
  font-size: 9pt;
  color: white;
  letter-spacing: 0.3pt;
  padding: 0.5mm 1.2mm;
  background: rgba(0,0,0,0.35);
  border-radius: 1mm;
}
.wc-light .tech-label, .wc-medium .tech-label {
  /* On light backgrounds the dark badge needs more contrast */
  color: #1a1a1a;
  background: rgba(255,255,255,0.55);
}
.eq-badge {
  color: #1b3a6b;
  background: rgba(255,255,255,0.65);
  border: 0.4pt solid #1b3a6b;
}

/* Weight-class background on illustration column (matches the leading token of total mass) */
.wc-light  .illus { background: #e0a000; }  /* Y leading: yellow */
.wc-medium .illus { background: #d97600; }  /* O leading: orange */
.wc-heavy  .illus { background: #b01818; }  /* R leading: red */
.wc-super  .illus { background: #1a1a1a; }  /* K leading: black */

.content { flex: 1; padding: 1.5mm 2mm 1.5mm 2mm; overflow: hidden; font-size: 6.5pt; line-height: 1.2; }
.title { font-weight: bold; font-size: 7.5pt; letter-spacing: 0.1pt; line-height: 1.05; margin-bottom: 0.3mm; }
.herit { font-style: italic; font-size: 5.5pt; color: #666; margin-bottom: 0.8mm; line-height: 1.1; height: 6.5pt; overflow: hidden; }
.tags { display: flex; gap: 2.5mm; margin-bottom: 0.5mm; font-size: 5.5pt; align-items: baseline; }
.tags .fuel { font-weight: bold; color: #333; }
.tags .ign { color: #666; }
/* Weight-class tag on each card: small badge in the same color as the illustration column */
.tags .wc-tag {
  font-weight: bold; font-size: 5pt; letter-spacing: 0.4pt;
  color: white; padding: 0.5pt 1.5pt; border-radius: 1pt;
  margin-left: auto;
}
.wc-light  .wc-tag { background: #e0a000; color: #222; }
.wc-medium .wc-tag { background: #d97600; color: white; }
.wc-heavy  .wc-tag { background: #b01818; color: white; }
.wc-super  .wc-tag { background: #1a1a1a; color: white; }

.isp { font-size: 6pt; color: #444; margin-bottom: 0.3mm; }
.mass { font-size: 6pt; line-height: 1.5; }
.mass .lbl { color: #666; display: inline-block; width: 4mm; }
.fuel-row .lbl { color: #c45500; font-style: italic; }
.paren { color: #666; font-size: 5.5pt; }
.real { font-style: italic; color: #888; font-size: 5pt; }

.t { display: inline-block; width: 7pt; height: 7pt; line-height: 7pt; text-align: center; color: white; font-weight: bold; font-size: 5.5pt; border-radius: 1pt; margin-right: 0.3pt; vertical-align: -0.5pt; }
.t-y { background: #e0a000; color: #222; }
.t-o { background: #d97600; }
.t-r { background: #b01818; }
.t-k { background: #1a1a1a; }
.t-eq { background: #1b3a6b; color: #fff; font-size: 4.5pt; line-height: 7pt; }  /* sub-token equipment payload */
.tk-mult { font-weight: bold; font-size: 6pt; vertical-align: -0.5pt; margin-right: 0.3pt; }  /* "25×" before a token glyph */

table.strip { width: 100%; margin-top: 0.5mm; border-collapse: collapse; font-size: 6pt; }
table.strip td { padding: 0.2mm 1mm 0.2mm 0; vertical-align: middle; }
.ct { white-space: nowrap; }
.tt { color: #888; font-size: 5pt; }
.dv { font-weight: bold; text-align: right; font-size: 6.5pt; }

.fixed { font-weight: bold; font-size: 6.5pt; line-height: 1.3; margin-top: 0.5mm; }
.eo-note { font-style: italic; font-size: 5.5pt; color: #555; margin-top: 0.5mm; }
.eq-carry {
  font-size: 6pt; font-weight: bold; color: #1b3a6b;
  margin-top: 0.8mm; padding: 0.6mm 1.5mm;
  background: #e8eef5; border-left: 2pt solid #1b3a6b;
  letter-spacing: 0.2pt;
}

.req { position: absolute; bottom: 1mm; left: calc(18mm + 2mm); right: 2mm; font-style: italic; font-size: 4.5pt; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Equipment */
.eq .illus { background: #eef1f6; }
.eq.burner .illus { background: #f9eded; }
.eq.consumables .illus { background: #e8f0e3; }

/* Rotation indicators on CONSUMABLES and REFINERY cards. Placed within the
   illustration column so they don't collide with the title/desc text. As the
   card is rotated 90 deg at a time, the current state reads upright at top. */
.eq.consumables .illus, .eq.refinery .illus { position: relative; }
.rot-100, .rot-75, .rot-50, .rot-25 {
  position: absolute;
  font-size: 6pt; font-weight: bold; color: #1b3a6b; letter-spacing: 0.3pt;
}
.rot-100 { top: 0.5mm; left: 50%; transform: translateX(-50%); }
.rot-50  { bottom: 0.5mm; left: 50%; transform: translateX(-50%) rotate(180deg); }
.rot-75  { top: 50%; left: 0.5mm; transform-origin: left center;
           transform: rotate(-90deg) translateX(-50%); }
.rot-25  { top: 50%; right: 0.5mm; transform-origin: right center;
           transform: rotate(90deg) translateX(50%); }
.eq.refinery .illus { background: #e8eef5; }
.eq-label { font-weight: bold; font-size: 5.5pt; letter-spacing: 0.3pt; color: #1b3a6b; margin-bottom: 0.5mm; }
.burner .eq-label { color: #a83232; }
.desc { font-size: 6pt; line-height: 1.25; }
.eq-note { position: absolute; bottom: 1mm; left: calc(18mm + 2mm); right: 2mm; font-style: italic; font-size: 5pt; color: #666; line-height: 1.15; }

/* Reference pages */
.ref-body { font-size: 9pt; line-height: 1.45; }
.ref-body .intro { margin-bottom: 4mm; text-align: justify; }
.ref-body h2 { font-size: 10.5pt; margin: 4mm 0 1mm; letter-spacing: 0.3pt; }
.ref-body p { margin: 0 0 2mm; text-align: justify; }
.legend { border: 0.4pt solid #bbb; padding: 2mm 3mm; background: #faf9f5; margin: 1mm 0 3mm; font-size: 9pt; }
.legend p { margin: 0.3mm 0; }
.legend .sym { display: inline-block; width: 4mm; text-align: center; font-weight: bold; font-size: 12pt; }

/* Objective cards (page 4) */
.card.obj {
  background: white; border: 0.4pt solid #2a2a2a; border-top: 3pt solid var(--accent);
  padding: 1.8mm 2mm; overflow: hidden; position: relative; display: flex; flex-direction: column;
}
.obj-head { display: flex; align-items: center; gap: 1mm; margin-bottom: 1mm; }
.obj-icon { width: 5mm; height: 5mm; }
.obj-icon svg { width: 100%; height: 100%; display: block; }
.obj-type-label { font-size: 5pt; font-weight: bold; letter-spacing: 0.3pt; color: var(--accent); flex: 1; }
.obj-vp { font-size: 7pt; }
.vp-star { color: var(--accent); margin-left: 0.3pt; }
.obj-title { font-weight: bold; font-size: 9pt; letter-spacing: 0.2pt; line-height: 1.05; margin-bottom: 0.5mm; }
.obj-tagline { font-style: italic; font-size: 6pt; color: #888; margin-bottom: 1.5mm; line-height: 1.15; }
.obj-desc { font-size: 7pt; line-height: 1.3; margin-bottom: 1.5mm; flex: 1; }
.obj-req {
  font-size: 6pt; font-weight: bold; padding: 0.8mm 1mm; background: #f3f1e8;
  border-left: 2pt solid var(--accent); color: #333; line-height: 1.25;
}
.obj-note { font-size: 5.5pt; font-style: italic; color: #888; margin-top: 1mm; line-height: 1.2; }
'''

# Paginate each deck at 16 cards per A4 page (4x4 grid).
PER_PAGE = 16
def _npages(n):
    return (n + PER_PAGE - 1) // PER_PAGE


def main():
    data, page1_engines = load_cards()
    with open("../data/objectives.json") as f:
        objectives = json.load(f)

    bundles = data.get("bundles", [])
    rocket_bundles = [b for b in bundles if b["token"] != "E"]
    equip_bundles = [b for b in bundles if b["token"] == "E"]
    # The rocket deck = engine cards followed by the rocket-bundle multiplier cards.
    # The blue EQUIPMENT bundles (xN equipment) live on the equipment pages instead.
    engine_cards = [engine_card_html(e) for e in page1_engines] + [bundle_card_html(b) for b in rocket_bundles]
    equip_cards = [equipment_card_html(q) for q in data["equipment"]] + [bundle_card_html(b) for b in equip_bundles]

    # FILLER objectives (marked "filler": true — expendable space-fillers) ride in the
    # spare slots of the last equipment sheet instead of the main objectives page.
    filler_objs = [o for o in objectives if o.get("filler")]
    main_objs = [o for o in objectives if not o.get("filler")]

    n_engine_pages = _npages(len(engine_cards))
    n_equip_pages = _npages(len(equip_cards))
    n_obj_pages = _npages(len(main_objs))
    TOTAL_PAGES = n_engine_pages + n_equip_pages + n_obj_pages

    # Every front page is followed by its back page, so even pages = card backs.
    # Engine + equipment fronts get the red ROCKETS back; objectives get the gold MISSIONS back.
    pages = []
    pgnum = 0
    # Engines + rocket bundles (one red ROCKETS deck)
    for pi, i in enumerate(range(0, len(engine_cards), PER_PAGE)):
        pgnum += 1
        title = "ENGINE & BUNDLE CARDS" if n_engine_pages == 1 else f"ENGINE & BUNDLE CARDS (page {pi+1})"
        pages.append(card_page(title, pgnum, TOTAL_PAGES, engine_cards[i:i+PER_PAGE]))
        pages.append(back_page("ROCKETS", "rockets"))
    # Equipment (+ the blue equipment-bundle multipliers). The LAST sheet's spare
    # slots take the filler contract cards (gold MISSIONS backs -> mixed back sheet).
    equip_chunks = [equip_cards[i:i + PER_PAGE] for i in range(0, len(equip_cards), PER_PAGE)]
    for ci, chunk in enumerate(equip_chunks):
        pgnum += 1
        kinds = ["rockets"] * len(chunk)
        title = "EQUIPMENT CARDS"
        if ci == len(equip_chunks) - 1 and filler_objs:
            fill = [objective_card_html(o) for o in filler_objs][: PER_PAGE - len(chunk)]
            chunk = chunk + fill
            kinds += ["missions"] * len(fill)
            title = "EQUIPMENT + FILLER CONTRACTS"
        pages.append(card_page(title, pgnum, TOTAL_PAGES, chunk))
        pages.append(mixed_back_page(kinds) if "missions" in kinds else back_page("ROCKETS", "rockets"))
    # Objectives (the 16 main cards; fillers already placed above)
    for i in range(0, len(main_objs), PER_PAGE):
        pgnum += 1
        pages.append(objective_page(pgnum, TOTAL_PAGES, main_objs[i:i + PER_PAGE]))
        pages.append(back_page("MISSIONS", "missions"))

    pages_html = "\n".join(pages)
    data_json = json.dumps(data, indent=2)

    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Triskelion Game Kit (complete, with silhouettes)</title>
<style>{CSS}</style>
</head>
<body>

<!--
  Triskelion complete game kit, self-contained.
  All data needed to recompute every card is in the <script type="application/json"
  id="kit-data"> block below. Format: A4 pages, 16 cards per page (4x4 grid),
  cards ~47x69mm. Each card has a hand-drawn SVG silhouette in the left
  illustration column; the active stage is solid white, the rest of the rocket
  is a thin outline.
-->

<script type="application/json" id="kit-data">
{data_json}
</script>

{pages_html}

</body>
</html>
'''

    OUT_HTML = "../build/triskelion-kit.html"
    with open(OUT_HTML, "w") as f:
        f.write(doc)
    print(f"Wrote {OUT_HTML}")
    print(f"  Engines: {len(page1_engines)} + {len(rocket_bundles)} rocket bundles")
    print(f"  Equipment: {len(data['equipment'])} + {len(equip_bundles)} equipment bundles")
    print(f"  Data: {len(data_json)} bytes")


if __name__ == "__main__":
    main()
