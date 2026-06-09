#!/usr/bin/env python3
"""
Visualizer for the playtest harness.

Pipeline role:
    build/playtest-results.json  ──>  build_playtest_report.py  ──>  build/playtest-report.html

Reads the structured results emitted by playtest.py and renders a standalone,
self-contained HTML dashboard: numbers audit, every reference mission as a
dv-cascade bar against its required-dv marker, design findings, and the Starship
refuel analysis. No external assets, no dependencies.

Run from src/:
    python3 playtest.py            # produces build/playtest-results.json
    python3 build_playtest_report.py
"""

import html
import json
import math
import os

# Reuse the kit's card renderers so the report shows the SAME cards as the printed kit.
from build_kit import load_cards, engine_card_html, equipment_card_html, CSS as KIT_CSS

HERE = os.path.dirname(os.path.abspath(__file__))
IN_JSON = os.path.join(HERE, "..", "build", "playtest-results.json")
OUT_HTML = os.path.join(HERE, "..", "build", "playtest-report.html")

# Card lookup, keyed by name, for both engines and equipment (processed exactly as the kit does).
_KIT_DATA, _ = load_cards(os.path.join(HERE, "..", "data", "cards.json"))
ENGINE_BY_NAME = {e["name"]: e for e in _KIT_DATA["engines"]}
EQUIP_BY_NAME = {q["name"]: q for q in _KIT_DATA["equipment"]}

def render_used_cards(m):
    """Render the actual game cards a mission uses, side by side, exactly as the kit draws them."""
    seen, cards = set(), []
    for b in m["burns"]:
        name = b["engine"]
        if name in seen:
            continue
        seen.add(name)
        if name in ENGINE_BY_NAME:
            cards.append(engine_card_html(ENGINE_BY_NAME[name]))
        elif name in EQUIP_BY_NAME:
            cards.append(equipment_card_html(EQUIP_BY_NAME[name]))
    if not cards:
        return ""
    return f'<div class="kit-cards">{"".join(cards)}</div>'

FUEL_COLOR = {
    "KEROLOX": "#c9742e", "HYDROLOX": "#2e7dc9", "METHALOX": "#6a3fb5",
    "SOLID": "#9a9a3a", "HYPERGOLIC": "#c14b9a", "NUCLEAR": "#2ba36b",
    "ION": "#3ab0c9", None: "#888", "": "#888",
}
VERDICT = {  # verdict -> (label, css class)
    "PASS": ("PASS", "ok"),
    "FAIL": ("FAIL", "bad"),
    "correctly-short": ("CORRECTLY SHORT", "ok"),
    "INVARIANT-BROKEN": ("INVARIANT BROKEN", "bad"),
    "closes": ("CLOSES", "info"),
    "falls-short": ("FALLS SHORT", "warn"),
}

def esc(s):
    return html.escape(str(s)) if s is not None else ""

def mission_bar(m):
    """Stacked dv segments + a marker at required_dv."""
    scale = max(m["total_dv"], m["required_dv"], 1) * 1.04
    segs = []
    cum = 0
    for b in m["burns"]:
        if b["dv"] is None or b["dv"] <= 0:
            continue
        w = b["dv"] / scale * 100
        color = FUEL_COLOR.get(b["fuel_type"], "#888")
        if b["mode"] == "parallel":
            color = "#7a7a7a"
        label = f'{b["dv"]}' if w > 4 else ""
        segs.append(
            f'<div class="seg" style="width:{w:.2f}%;background:{color}" '
            f'title="{esc(b["engine"])}: {b["dv"]} dv — {esc(b["leg"])}">{label}</div>'
        )
        cum += b["dv"]
    req_pct = m["required_dv"] / scale * 100
    marker = (f'<div class="req-marker" style="left:{req_pct:.2f}%" '
              f'title="required {m["required_dv"]} dv"></div>')
    return f'<div class="bar">{"".join(segs)}{marker}</div>'

def mission_card(m):
    vlabel, vclass = VERDICT.get(m["verdict"], (m["verdict"], "info"))
    rows = []
    for b in m["burns"]:
        warn = ' <span class="ign">⚠ vac-ignite</span>' if b["ignition_warning"] else ""
        mode_mark = {"parallel": "∥", "subgrid": "·", "fixed": "·", "serial": ""}[b["mode"]]
        cargo = "—" if b["cargo_t"] is None else f'{b["cargo_t"]:.0f}t'
        dv = "—" if b["dv"] is None else b["dv"]
        dot = f'<span class="dot" style="background:{FUEL_COLOR.get(b["fuel_type"], "#888")}"></span>'
        tl = f' <span class="tl">{esc(b["tech_label"])}</span>' if b.get("tech_label") else ""
        bnote = f'<br><span class="bn">{esc(b["note"])}</span>' if b["note"] else ""
        rows.append(
            f'<tr><td class="eng">{dot}{mode_mark} {esc(b["engine"])}{tl}{warn}</td>'
            f'<td class="num">{cargo}</td><td class="num dv">{dv}</td>'
            f'<td class="leg">{esc(b["leg"])}{bnote}</td></tr>'
        )
    crew = ""
    if m["crew"]:
        crew = (f'<span class="chip crew">👨‍🚀 {m["transit_months"]} mo · '
                f'{m["consumable_cards"]} Consumables</span>')
    notes = "".join(f'<li>{esc(n)}</li>' for n in m["notes"])
    notes_html = f'<ul class="notes">{notes}</ul>' if notes else ""
    margin = m["margin"]
    margin_txt = (f'+{margin}' if margin >= 0 else f'{margin}')
    return f'''
<section class="mission {vclass}">
  <header>
    <h3>{esc(m["title"])}</h3>
    <span class="verdict {vclass}">{vlabel}</span>
  </header>
  <div class="meta">
    <span class="chip">{m["total_dv"]} dv delivered</span>
    <span class="chip req">needs {m["required_dv"]} dv</span>
    <span class="chip margin {'pos' if margin >= 0 else 'neg'}">{margin_txt} dv margin</span>
    {crew}
  </div>
  {mission_bar(m)}
  <table class="burns">
    <thead><tr><th>stage (bottom → top)</th><th>cargo</th><th>dv</th><th>leg</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  {notes_html}
  <div class="cards-label">cards used{'' if m["closes"] else ' <span class="short">— ✗ rocket falls short of the required dv</span>'}</div>
  {render_used_cards(m)}
</section>'''

def audit_section(a):
    if a["problems"]:
        items = "".join(
            f'<li><b>{esc(p["card"])}</b> <span class="field">{esc(p.get("field",""))}</span> — {esc(p["msg"])}</li>'
            for p in a["problems"])
        body = f'<ul class="problems">{items}</ul>'
        status = f'<span class="verdict bad">{len(a["problems"])} DATA BUG(S)</span>'
    else:
        body = ""
        status = '<span class="verdict ok">CLEAN</span>'
    warns = ""
    if a["warnings"]:
        w = "".join(f'<li>{esc(x["card"])}: {esc(x["msg"])}</li>' for x in a["warnings"])
        warns = f'<details><summary>{len(a["warnings"])} warning(s)</summary><ul>{w}</ul></details>'
    drift = ""
    if a["dry_token_drift"]:
        d = "".join(f'<li>{esc(x["card"])}: shows {x["shown"]}t for {x["actual"]}t dry</li>'
                    for x in a["dry_token_drift"])
        drift = (f'<details><summary>{len(a["dry_token_drift"])} cards round dry mass to tokens '
                 f'(expected — dry mass is a sub-ladder dial)</summary><ul>{d}</ul></details>')
    return f'''
<section class="panel audit">
  <header><h2>Numbers audit {status}</h2></header>
  <p class="sub">{a["engines_checked"]} engines · {a["strip_rows_checked"]} push-strip rows recomputed from the rocket equation.</p>
  {body}{warns}{drift}
</section>'''

def findings_section(findings):
    if not findings:
        return ""
    items = "".join(f'<li>{esc(f)}</li>' for f in findings)
    return f'''
<section class="panel findings">
  <header><h2>Design findings <span class="verdict warn">{len(findings)}</span></h2></header>
  <p class="sub">Surfaced by simulation — judgment calls, not bugs.</p>
  <ul>{items}</ul>
</section>'''

def refuel_section(rf):
    return f'''
<section class="panel">
  <header><h2>Analysis — Starship LEO refueling</h2></header>
  <p>Park an <b>expended</b> Starship in LEO (no reuse), then fly tankers until you have
     delivered its full propellant load <b>total − dry = {rf["target_refuel_t"]:.0f}t</b>.
     Super Heavy gives <b>{rf["super_heavy_dv"]} dv</b> lifting a full Starship, so each tanker
     must add <b>{rf["starship_need_dv"]} dv</b> to reach orbit.</p>
  <div class="refuel">
    <div class="rf-card"><span class="big">{rf["flights_dump"]}</span>
      tanker flights<br><small>dumping everything to just reach LEO ({rf["dump_deliverable_t"]}t/flight)</small></div>
    <div class="rf-card hl"><span class="big">{rf["flights_rendezvous"]}</span>
      tanker flights<br><small>keeping 1 dv for rendezvous/dock ({rf["rendezvous_deliverable_t"]}t/flight)</small></div>
  </div>
  <p class="sub">SpaceX has publicly floated ~15 — the result lands in this band once rendezvous margin is counted.</p>
</section>'''

TS_JSON = os.path.join(HERE, "..", "build", "tower-search.json")

def _stage_card(stage):
    """One tower stage = the real card, with a ×N · dv tag pinned to its visible spine."""
    name = stage["card"]
    if name in ENGINE_BY_NAME:
        inner = engine_card_html(ENGINE_BY_NAME[name])
    elif name in EQUIP_BY_NAME:
        inner = equipment_card_html(EQUIP_BY_NAME[name])
    else:
        return ""
    n = stage.get("n", 1)
    tag = (f'{"×"+str(n)+" · " if n > 1 else ""}{stage["stage_dv"]} dv')
    return f'<div class="tcard"><span class="stage-tag">{esc(tag)}</span>{inner}</div>'

def _tower(stack):
    # bottom (launch) first, left → right; cards overlap to show only their illustration spine
    return '<div class="tower">' + "".join(_stage_card(s) for s in reversed(stack)) + '</div>'

def _tblock(title, meta, stack, cls=""):
    return f'''<div class="tmission {cls}">
      <div class="tm-head"><b>{esc(title)}</b> <span class="tm-meta">{esc(meta)}</span></div>
      {_tower(stack)}
    </div>'''

def _dv_ruler(milestones, ceiling):
    marks = "".join(
        f'<div class="rmark" style="left:{m["dv"]/ceiling*100:.1f}%">'
        f'<span class="rdv">{m["dv"]}</span><span class="rlab">{esc(m["label"])}</span></div>'
        for m in milestones)
    return f'<div class="ruler"><div class="ruler-bar"></div>{marks}<span class="rend">{ceiling}</span></div>'

SERIES_COLOR = {"theoretical": "#2e6fb0", "historical": "#1c8a4d"}

def _scatter(series, milestones, ceiling):
    pts_all = [p["liftoff_t"] for s in series for p in s["pareto"]]
    if not pts_all:
        return ""
    W, H, mL, mR, mT, mB = 880, 360, 60, 18, 14, 44
    lx0, lx1 = math.log10(min(pts_all)) - 0.08, math.log10(max(pts_all)) + 0.08
    dvmax = max(ceiling, max(m["dv"] for m in milestones)) + 1
    def X(mass): return mL + (math.log10(mass) - lx0) / (lx1 - lx0) * (W - mL - mR)
    def Y(dv): return H - mB - dv / dvmax * (H - mT - mB)
    el = []
    for p10 in range(int(math.ceil(lx0)), int(math.floor(lx1)) + 1):
        x = X(10 ** p10)
        el.append(f'<line x1="{x:.1f}" y1="{mT}" x2="{x:.1f}" y2="{H-mB}" class="grid-v"/>')
        lbl = (f'{10**p10/1000:g}kt' if 10 ** p10 >= 1000 else f'{10**p10}t')
        el.append(f'<text x="{x:.1f}" y="{H-mB+14}" class="ax" text-anchor="middle">{lbl}</text>')
    for m in milestones:
        y = Y(m["dv"])
        el.append(f'<line x1="{mL}" y1="{y:.1f}" x2="{W-mR}" y2="{y:.1f}" class="ms-line"/>')
        el.append(f'<text x="{mL+4}" y="{y-3:.1f}" class="ms-label">{m["dv"]} — {esc(m["label"])}</text>')
    for s in series:
        par = s["pareto"]
        if not par:
            continue
        k = s["key"]
        pts = " ".join(f'{X(p["liftoff_t"]):.1f},{Y(p["dv"]):.1f}' for p in par)
        el.append(f'<polyline points="{pts}" class="frontier f-{k}"/>')
        for i, p in enumerate(par):
            el.append(f'<circle cx="{X(p["liftoff_t"]):.1f}" cy="{Y(p["dv"]):.1f}" r="4.2" class="sdot s-{k}" '
                      f'data-i="{i}" onmouseover="showTower(\'{k}\',{i})" onclick="showTower(\'{k}\',{i})"/>')
    el.append(f'<text x="6" y="11" class="ax-title">dv</text>')
    el.append(f'<text x="{W/2:.0f}" y="{H-2}" class="ax-title" text-anchor="middle">liftoff mass (log scale) →</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="scatter">{"".join(el)}</svg>'

def tower_search_section():
    if not os.path.exists(TS_JSON):
        return "", "{}"
    ts = json.load(open(TS_JSON))
    milestones = ts.get("milestones", [])
    variants = ts.get("variants") or {"theoretical": ts}
    theo = variants.get("theoretical", ts)
    hist = variants.get("historical")
    never_flew = set(ts.get("never_flew", []))
    SERIES = [{"key": "theoretical", "label": "Theoretical — every card", "data": theo}]
    if hist:
        SERIES.append({"key": "historical", "label": "Historical — flew in reality", "data": hist})
    ceiling = max((s["data"].get("ceiling", {}).get("dv", 0) for s in SERIES), default=1) or 1

    legend = "".join(
        f'<span class="leg-s"><i style="background:{SERIES_COLOR[s["key"]]}"></i>{esc(s["label"])}</span>'
        for s in SERIES)
    store, metas = "", {}
    for s in SERIES:
        par = s["data"].get("pareto", [])
        store += "".join(f'<template id="twhtml-{s["key"]}-{i}">{_tower(p["stack"])}</template>'
                         for i, p in enumerate(par))
        metas[s["key"]] = [{"dv": p["dv"], "stages": p["stages"], "liftoff_t": p["liftoff_t"]} for p in par]

    # Card usefulness — theoretical vs historical use counts side by side.
    stage_names = [e["name"] for e in _KIT_DATA["engines"] if e.get("kind") == "stage"]
    pu_t = theo.get("pareto_usage", {})
    pu_h = (hist or {}).get("pareto_usage", {})
    single = theo.get("card_single_dv", {})
    umax = max([1] + list(pu_t.values()))
    rows = ""
    for n in sorted(stage_names, key=lambda n: (-pu_t.get(n, 0), n)):
        flown = n not in never_flew
        nm = esc(n) + ("" if flown else ' <span class="nf">never flew</span>')
        hist_cell = (f'<td class="u-c">{pu_h.get(n,0)}×</td>' if flown else '<td class="u-c never">—</td>')
        rows += (f'<tr class="{"" if flown else "rnf"}"><td class="u-n">{nm}</td>'
                 f'<td class="u-bar"><span style="width:{pu_t.get(n,0)/umax*100:.0f}%"></span></td>'
                 f'<td class="u-c">{pu_t.get(n,0)}×</td>{hist_cell}'
                 f'<td class="u-d">{single.get(n,"—")}</td></tr>')

    # Mission cost — theoretical vs historical.
    hm = {m["label"]: m for m in (hist or {}).get("missions", [])}
    def mcell(m):
        return (f'{m["total_dv"]} dv · {m["stages"]} st · ~{m["liftoff_t"]:,}t') if m else "—"
    mrows = "".join(
        f'<tr><td>{esc(m["label"])}</td><td class="u-c">{m["need_dv"]}</td>'
        f'<td>{mcell(m)}</td><td>{mcell(hm.get(m["label"]))}</td></tr>'
        for m in theo.get("missions", []))
    tc, hc = theo.get("ceiling", {}), (hist or {}).get("ceiling", {})

    panels = f'''
  <section class="panel">
    <header><h2>The cost of dv — theoretical vs historical</h2></header>
    <p class="sub">Payload 10t, <b>log</b> mass axis. Each dot is the lightest launchable stack that reaches that dv —
       <b>hover any dot (either line)</b> to see its tower. The gap between the lines is exactly what the paper rockets
       (NERVA, Sea Dragon, Nova, the pressure-fed Super Hydrolox upper) buy you: at Mars-return the cheapest tower drops
       from ~9,600t (flown hardware) to ~3,850t.</p>
    <div class="scatter-legend">{legend}</div>
    {_dv_ruler(milestones, ceiling)}
    {_scatter([{"key": s["key"], "pareto": s["data"].get("pareto", [])} for s in SERIES], milestones, ceiling)}
    <div id="tower-detail" class="tower-detail"><div class="td-hint">hover a point on either curve to reveal its tower ↑</div></div>
    {store}
  </section>

  <section class="panel">
    <header><h2>Which cards are good? — uses across the cheapest towers</h2></header>
    <table class="urank"><thead><tr><th>card</th><th></th><th>theoretical</th><th>historical</th><th>1-card dv@10t</th></tr></thead>
      <tbody>{rows}</tbody></table>
    <p class="sub">The <b>Hydrolox Drop Tank</b> (Shuttle external tank) lands top-3 in <i>both</i> columns — the engine-less-tank
       trick (engines above drink from a dumb tank, hauling no dead engine mass) is genuinely efficient. Vindication for the
       ET, if not the orbiter bolted to its side. Rows marked <span class="nf">never flew</span> are theoretical-only.</p>
  </section>

  <section class="panel">
    <header><h2>Mission cost — theoretical vs historical</h2></header>
    <table class="mcmp"><thead><tr><th>board mission</th><th>needs</th><th>theoretical (every card)</th><th>historical (flown)</th></tr></thead>
      <tbody>{mrows}</tbody></table>
    <p class="sub">dv ceiling: theoretical <b>{tc.get("dv","?")} dv</b> @ ~{tc.get("liftoff_t",0):,}t (bundled Sea Dragons) ·
       historical <b>{hc.get("dv","?")} dv</b> @ ~{hc.get("liftoff_t",0):,}t. Flown hardware can't crack the deep-space ceiling
       without nuclear — which is the whole point of gating NERVA behind the public-outcry mechanic.</p>
  </section>'''
    return panels, json.dumps(metas)

CSS = '''
:root { --ok:#1c8a4d; --bad:#c02626; --warn:#b8860b; --info:#2e6fb0; --bg:#f4f2ec; --card:#fff; --ink:#1d1d1d; --dim:#777; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 -apple-system,Helvetica,Arial,sans-serif; }
.wrap { max-width:980px; margin:0 auto; padding:24px 18px 60px; }
.top { display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:8px; border-bottom:2px solid #2a2a2a; padding-bottom:12px; margin-bottom:18px; }
.top h1 { margin:0; font-size:22px; letter-spacing:.3px; }
.top .model { color:var(--dim); font-size:12px; }
.status { font-weight:700; padding:6px 14px; border-radius:20px; color:#fff; font-size:13px; }
.status.ok { background:var(--ok); } .status.bad { background:var(--bad); }
.scorebar { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px; }
.score { background:var(--card); border:1px solid #ddd; border-radius:8px; padding:10px 14px; min-width:90px; }
.score .n { font-size:22px; font-weight:700; } .score .l { font-size:11px; color:var(--dim); text-transform:uppercase; letter-spacing:.4px; }
.score.ok .n { color:var(--ok); } .score.bad .n { color:var(--bad); } .score.warn .n { color:var(--warn); }
.panel, .mission { background:var(--card); border:1px solid #e0ddd4; border-radius:10px; padding:16px 18px; margin-bottom:16px; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.panel header, .mission header { display:flex; justify-content:space-between; align-items:center; gap:10px; }
.panel h2 { margin:0 0 2px; font-size:16px; } .mission h3 { margin:0; font-size:15px; }
.sub { color:var(--dim); font-size:12px; margin:4px 0 10px; }
.verdict { font-weight:700; font-size:11px; padding:3px 10px; border-radius:14px; color:#fff; white-space:nowrap; }
.verdict.ok { background:var(--ok); } .verdict.bad { background:var(--bad); } .verdict.warn { background:var(--warn); } .verdict.info { background:var(--info); }
.mission.bad { border-left:4px solid var(--bad); } .mission.ok { border-left:4px solid var(--ok); }
.mission.warn { border-left:4px solid var(--warn); } .mission.info { border-left:4px solid var(--info); }
.meta { display:flex; gap:6px; flex-wrap:wrap; margin:10px 0; }
.chip { font-size:11px; background:#f0eee7; border:1px solid #e2dfd6; border-radius:12px; padding:2px 9px; color:#444; }
.chip.req { background:#eef3f9; } .chip.margin.pos { background:#e9f5ee; color:var(--ok); } .chip.margin.neg { background:#fbecec; color:var(--bad); }
.chip.crew { background:#f3eefa; }
.bar { position:relative; display:flex; height:26px; background:#efece4; border-radius:5px; overflow:hidden; margin:6px 0 12px; }
.seg { height:100%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:11px; font-weight:700; border-right:1px solid rgba(255,255,255,.5); }
.req-marker { position:absolute; top:-3px; bottom:-3px; width:2px; background:#111; }
.req-marker::after { content:"req"; position:absolute; top:-13px; left:-8px; font-size:9px; color:#111; }
table.burns { width:100%; border-collapse:collapse; font-size:12.5px; margin-top:4px; }
.burns th { text-align:left; color:var(--dim); font-weight:600; font-size:11px; border-bottom:1px solid #e6e3da; padding:3px 6px; }
.burns td { padding:4px 6px; border-bottom:1px solid #f1efe8; vertical-align:top; }
.burns .num { text-align:right; white-space:nowrap; } .burns .dv { font-weight:700; }
.burns .eng { white-space:nowrap; } .burns .leg { color:#555; }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; vertical-align:middle; }
.tl { font-size:10px; color:#fff; background:#555; border-radius:3px; padding:0 4px; }
.bn { color:var(--dim); font-size:11px; font-style:italic; }
.ign { color:var(--bad); font-size:10px; font-weight:700; }
ul.notes { margin:8px 0 0; padding-left:18px; color:#555; font-size:12px; }
.problems li { margin:4px 0; } .field { color:var(--dim); font-size:11px; }
.findings { border-left:4px solid var(--warn); background:#fffdf5; }
.findings ul { margin:6px 0 0; padding-left:18px; } .findings li { margin:6px 0; }
details { margin-top:8px; font-size:12px; color:#555; } summary { cursor:pointer; color:var(--info); }
.refuel { display:flex; gap:12px; margin:10px 0; }
.rf-card { flex:1; text-align:center; background:#f6f4ee; border:1px solid #e4e1d8; border-radius:8px; padding:12px; }
.rf-card.hl { background:#eef3f9; border-color:#cfe0f0; } .rf-card .big { display:block; font-size:30px; font-weight:800; }
.legend { display:flex; gap:12px; flex-wrap:wrap; font-size:11px; color:var(--dim); margin-bottom:18px; }
.legend span { display:inline-flex; align-items:center; gap:4px; }
footer { color:var(--dim); font-size:11px; text-align:center; margin-top:24px; }
/* The actual game cards, rendered by the kit's own code at kit size */
.cards-label { font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--dim); font-weight:700; margin:14px 0 6px; }
.cards-label .short { color:var(--bad); }
.kit-cards { display:flex; flex-wrap:wrap; gap:3mm; align-items:flex-start; }
.kit-cards .card { width:47mm; height:69mm; flex:0 0 auto; }
/* Tower view — cards overlap to show only their illustration spine; hover brings one forward */
.tg { font-size:14px; margin:18px 0 2px; padding-top:10px; border-top:1px solid #eee; }
.tmission { margin:14px 0 22px; }
.tmission.ceiling { background:#fbf3f3; border:1px dashed #d9b3b3; border-radius:8px; padding:6px 10px; }
.tm-head { font-size:13px; margin-bottom:2px; } .tm-meta { color:var(--dim); font-size:11px; margin-left:6px; }
.tower { display:flex; padding:7mm 2mm 3mm; align-items:flex-start; }
.tcard { position:relative; flex:0 0 47mm; width:47mm; transition:transform .14s ease; }
.tcard:not(:first-child) { margin-left:-29mm; }      /* leave the 18mm illustration column showing */
.tcard:hover { z-index:30; transform:translateY(-6mm); }
.tcard .card { width:47mm; height:69mm; box-shadow:1px 0 3px rgba(0,0,0,.18); }
.tcard:hover .card { box-shadow:0 10px 26px rgba(0,0,0,.38); }
.stage-tag { position:absolute; top:-4mm; left:0; z-index:6; background:#1d1d1d; color:#fff;
  font-size:8pt; font-weight:700; padding:0.4mm 1.6mm; border-radius:2px; white-space:nowrap; }
.urank { width:100%; border-collapse:collapse; font-size:12px; margin-top:6px; }
.urank th { text-align:left; color:var(--dim); font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:.3px; padding:2px 6px; }
.urank td { padding:1px 6px; } .u-n { white-space:nowrap; } .u-c { text-align:right; color:var(--dim); }
.u-d { text-align:right; color:var(--dim); width:90px; } .u-bar { width:55%; }
.u-bar span { display:inline-block; height:9px; background:var(--info); border-radius:3px; min-width:2px; }
/* Tabs */
.tabs { display:flex; gap:4px; margin-bottom:16px; border-bottom:2px solid #e0ddd4; }
.tab-btn { background:none; border:none; border-bottom:3px solid transparent; padding:8px 16px; font:600 14px inherit; color:var(--dim); cursor:pointer; margin-bottom:-2px; }
.tab-btn.active { color:var(--ink); border-bottom-color:var(--info); }
.tab-panel { display:none; } .tab-panel.active { display:block; }
/* scatter legend + series colors */
.scatter-legend { display:flex; gap:18px; font-size:12px; margin:2px 0 6px; }
.leg-s { display:inline-flex; align-items:center; gap:6px; color:#444; }
.leg-s i { width:14px; height:3px; border-radius:2px; display:inline-block; }
.scatter polyline.f-theoretical { stroke:#2e6fb0; } .scatter circle.s-theoretical { fill:#2e6fb0; }
.scatter polyline.f-historical { stroke:#1c8a4d; } .scatter circle.s-historical { fill:#1c8a4d; }
.td-head.td-theoretical { color:#2e6fb0; } .td-head.td-historical { color:#1c8a4d; }
/* never-flew rows + comparison tables */
.urank tr.rnf .u-n { color:#a08; } .nf { font-size:9px; color:#fff; background:#a06; border-radius:3px; padding:0 4px; vertical-align:middle; }
.u-c.never { color:#bbb; }
.mcmp { width:100%; border-collapse:collapse; font-size:12.5px; margin-top:6px; }
.mcmp th { text-align:left; color:var(--dim); font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:.3px; padding:4px 8px; border-bottom:1px solid #e6e3da; }
.mcmp td { padding:4px 8px; border-bottom:1px solid #f1efe8; } .mcmp td:nth-child(3) { color:#2e6fb0; } .mcmp td:nth-child(4) { color:#1c8a4d; }
/* dv ruler */
.ruler { position:relative; height:54px; margin:14px 4px 26px; }
.ruler-bar { position:absolute; top:8px; left:0; right:0; height:6px; border-radius:3px;
  background:linear-gradient(90deg,#cfe0f0,#9ac3e6,#6aa6d8,#3e7fb8); }
.rmark { position:absolute; top:0; transform:translateX(-50%); text-align:center; }
.rmark::after { content:""; position:absolute; top:6px; left:50%; width:2px; height:12px; background:#1d1d1d; transform:translateX(-50%); }
.rdv { display:block; font-weight:800; font-size:13px; }
.rlab { display:block; font-size:9.5px; color:var(--dim); margin-top:14px; white-space:nowrap; }
.rend { position:absolute; right:-2px; top:0; font-weight:800; font-size:13px; color:var(--dim); }
/* scatter */
.scatter { width:100%; height:auto; display:block; margin-top:4px; background:#fcfbf8; border:1px solid #eee; border-radius:6px; }
.scatter .grid-v { stroke:#eee; stroke-width:1; }
.scatter .ms-line { stroke:#c9a23a; stroke-width:1; stroke-dasharray:4 3; opacity:.7; }
.scatter .ms-label { fill:#a8821f; font-size:9.5px; font-weight:600; }
.scatter .frontier { fill:none; stroke:var(--info); stroke-width:2; }
.scatter .sdot { fill:var(--info); stroke:#fff; stroke-width:1.2; cursor:pointer; }
.scatter .sdot:hover { fill:var(--bad); r:6; }
.scatter .ax { fill:var(--dim); font-size:9.5px; } .scatter .ax-title { fill:#888; font-size:10px; font-weight:600; }
.tower-detail { min-height:80px; margin-top:6px; }
.td-hint { color:var(--dim); font-size:12px; font-style:italic; padding:20px 0; text-align:center; }
.td-head { font-weight:700; font-size:13px; margin:6px 0 2px; }
'''

def build(results):
    miss = results["missions"]
    n_pass = sum(1 for m in miss if m["verdict"] in ("PASS", "correctly-short"))
    n_bad = sum(1 for m in miss if m["verdict"] in ("FAIL", "INVARIANT-BROKEN"))
    n_prob = len(results["problems"])
    overall_ok = results["ok"]
    fuel_legend = "".join(
        f'<span><i class="dot" style="background:{c}"></i>{esc(name.title())}</span>'
        for name, c in FUEL_COLOR.items() if name)
    scores = f'''
<div class="scorebar">
  <div class="score ok"><div class="n">{n_pass}</div><div class="l">missions pass</div></div>
  <div class="score {'bad' if n_bad else ''}"><div class="n">{n_bad}</div><div class="l">missions fail</div></div>
  <div class="score warn"><div class="n">{len(results["findings"])}</div><div class="l">design findings</div></div>
  <div class="score {'bad' if n_prob else 'ok'}"><div class="n">{n_prob}</div><div class="l">data bugs</div></div>
</div>'''
    playtest_body = (audit_section(results["audit"])
                     + findings_section(results["findings"])
                     + "".join(mission_card(m) for m in miss)
                     + refuel_section(results["analysis"]["refuel"]))
    tower_body, pareto_meta = tower_search_section()
    pareto_meta = pareto_meta or "[]"
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(results["game"])} — Playtest Report</title>
<style>/* kit card styles first, report styles override page/body */
{KIT_CSS}
{CSS}</style></head>
<body><div class="wrap">
  <div class="top">
    <div><h1>{esc(results["game"])} — Automated Playtest</h1>
      <div class="model">model: {esc(results["model"])}</div></div>
    <span class="status {'ok' if overall_ok else 'bad'}">{'ALL CLEAR' if overall_ok else str(n_prob) + ' HARD ISSUE(S)'}</span>
  </div>
  {scores}
  <div class="legend">{fuel_legend}<span>∥ parallel · sub-grid</span></div>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab(event,'playtest')">Playtest missions</button>
    <button class="tab-btn" onclick="showTab(event,'towers')">Tower analysis</button>
  </div>
  <div id="tab-playtest" class="tab-panel active">{playtest_body}</div>
  <div id="tab-towers" class="tab-panel">{tower_body}</div>
  <footer>Generated by build_playtest_report.py — regenerate with
    <code>python3 playtest.py &amp;&amp; python3 tower_search.py &amp;&amp; python3 build_playtest_report.py</code></footer>
</div>
<script type="application/json" id="playtest-data">{json.dumps(results)}</script>
<script>
const PARETO = {pareto_meta};
function showTab(e, t) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + t).classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  e.target.classList.add('active');
}}
function showTower(v, i) {{
  const p = (PARETO[v] || [])[i], tpl = document.getElementById('twhtml-' + v + '-' + i),
        d = document.getElementById('tower-detail');
  if (!p || !tpl || !d) return;
  const label = v.charAt(0).toUpperCase() + v.slice(1);
  d.innerHTML = '<div class="td-head td-' + v + '">' + label + ' · ' + p.dv + ' dv · ' + p.stages +
                ' stages · liftoff ~' + p.liftoff_t.toLocaleString() + 't</div>';
  d.appendChild(tpl.content.cloneNode(true));
  document.querySelectorAll('.scatter .sdot').forEach(s => s.style.fill = '');
  const c = document.querySelector('.scatter .s-' + v + '[data-i="' + i + '"]');
  if (c) c.style.fill = 'var(--bad)';
}}
</script>
</body></html>'''

def main():
    if not os.path.exists(IN_JSON):
        raise SystemExit(f"missing {IN_JSON} — run `python3 playtest.py` first.")
    with open(IN_JSON) as f:
        results = json.load(f)
    os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
    with open(OUT_HTML, "w") as f:
        f.write(build(results))
    print(f"Wrote {os.path.relpath(OUT_HTML, HERE)}")

if __name__ == "__main__":
    main()
