#!/usr/bin/env python3
"""
Tower search — brute-force the envelope of what the deck can stack.

Instead of asking "does THIS mission close?" (that's playtest.py), this asks
"what is the MOST dv any legal stack can deliver to a given payload?" — and which
cards show up in those optimal towers (so we can see what's strong or overpowered).

Method (per Alex): work bottom-up in the chain model.
  - A "stage" is a cluster of N identical cards (N limited to the Rocket Bundle
    multipliers carded for the rocket's weight class — see ALLOWED_MULTS).
  - A cluster of N cards of type E has wet mass N·total_E and lifts a cargo M with
        dv = round(ve_E · ln(N·total_E / (N·dry_E + M)))     (feasible while M < N·fuel_E)
  - The mass the NEXT stage down must lift is just N·total_E — INDEPENDENT of M.
    So the set of reachable masses is the fixed set {N·total_E}, and "max dv to
    deliver payload P with ≤ h stages" is a tiny dynamic program.

Run from src/:  python3 tower_search.py
Writes build/tower-search.json and prints a report.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, "..", "data", "cards.json")
OUT = os.path.join(HERE, "..", "build", "tower-search.json")
MAXH = 8                       # max tower height (stages) to explore
EQUIP_T = 2.5

with open(CARDS) as f:
    D = json.load(f)

# Engine-less tanks have no engine of their own — a hydrolox ENGINE must sit directly above
# them to burn their fuel (the Hydrolox Drop Tank is the Shuttle external tank). They're not
# banned; the DP only lets a tank be a stage when the card directly above it is a hydrolox
# engine. That keeps the tank honest (it can't be a god-tier standalone) while still usable.
ENGINELESS = {"HYDROLOX DROP TANK"}

# Self-propelled cargo stages PLUS engine-less tanks. A tank (Hydrolox Drop Tank) can be a
# stage only when a hydrolox ENGINE sits directly above it in the stack (the engine burns the
# tank's fuel) — so it's threaded through the DP, not banned.
ENGINES = [e for e in D["engines"]
           if e.get("kind") == "stage"
           and (e.get("total_mass_t", 0) - e.get("dry_mass_t", 0)) > 0]

def ve(e):
    return e["isp_s"] * 9.81 / 1000.0

# Cluster multipliers are NOT free 1–4× any more — a rocket can only be multiplied by a
# Rocket Bundle card that exists for its weight class. Read the allowed multipliers straight
# from data["bundles"], keyed by the leading token of the rocket's total mass (Y/O/R/K).
TOKEN_BANDS = [(640, "K"), (160, "R"), (40, "O"), (10, "Y")]
def leading_token(mass):
    for thr, tok in TOKEN_BANDS:
        if mass >= thr:
            return tok
    return "E"  # sub-token: equipment scale (Burner Engine)

ALLOWED_MULTS = {tok: {1} for tok in ("K", "R", "O", "Y", "E")}   # a single rocket is always legal
for _b in D.get("bundles", []):
    ALLOWED_MULTS.setdefault(_b["token"], {1}).add(_b["mult"])

# Every (engine, cluster-count) transition: lifts cargo M, then weighs N·total.
# Rebuildable so we can run the whole analysis with a card set (e.g. excluding the Nuclear
# Engine, or only the cards that flew). Cluster counts come from ALLOWED_MULTS, not range(1,4).
def build_trans(exclude=()):
    excl = set(exclude)
    trans = []
    for e in ENGINES:
        if e["name"] in excl:
            continue
        is_tank = e["name"] in ENGINELESS
        is_hyd_engine = (e.get("fuel_type", "").upper() == "HYDROLOX") and not is_tank
        mults = ALLOWED_MULTS.get(leading_token(e.get("total_mass_t", 0)), {1})
        for n in sorted(mults):
            trans.append({
                "name": e["name"], "n": n,
                "ve": ve(e), "wet": n * e["total_mass_t"], "dry": n * e["dry_mass_t"],
                "fuel": n * (e["total_mass_t"] - e["dry_mass_t"]),
                "ign": e.get("ignition", ""), "tech": e.get("tech_label", ""),
                "tank": is_tank, "hyd": is_hyd_engine,
            })

    return trans

TRANS = build_trans()

def stage_dv(t, cargo):
    if cargo >= t["fuel"]:                       # nowhere to put it
        return None
    return round(t["ve"] * math.log(t["wet"] / (t["dry"] + cargo)))

# Burner Engine — EQUIPMENT, not a stage. It ATTACHES to the cargo it pushes (no
# displacement bay), so it's bounded by the equipment-carry rule: a cargo token
# carries 1 equipment card per 10t (one orange = 4). Serial burns are therefore
# capacity-limited, and each burn must push <= its 40t cap (payload + the burners
# above it). For a 10t payload that means at most ONE burner (+1 dv) — no chains.
BURNER = next((q for q in D["equipment"] if q["name"] == "BURNER ENGINE"), None)

def burner_options(payload):
    """(bonus_dv, added_mass, pseudo_stages[top-first]) for strapping k serial
    Burners onto the payload."""
    opts = [(0, 0.0, [])]
    if not BURNER:
        return opts
    cap_cards = int(payload // 10)               # 1 equipment slot per 10t of cargo
    bt, cap = BURNER["mass_t"], BURNER["max_push_t"]
    for k in range(1, cap_cards + 1):
        if payload + (k - 1) * bt > cap:         # the deepest burner's push
            break
        stages = [{"card": BURNER["name"], "n": 1, "lifts_t": round(payload + i * bt, 1),
                   "wet_t": bt, "stage_dv": BURNER["burn_dv"], "ign": "space",
                   "tech": BURNER.get("tech_label", "Bn")} for i in range(k)]
        opts.append((k * BURNER["burn_dv"], k * bt, stages))
    return opts

def _stagedict(t, cargo, dv):
    return {"card": t["name"], "n": t["n"], "lifts_t": round(cargo, 1), "wet_t": round(t["wet"], 1),
            "stage_dv": dv, "ign": t["ign"], "tech": t["tech"]}

GROUND = {"earth", "both"}

# `above_hyd` = is the card DIRECTLY above this stage a hydrolox engine? (needed to legalise a tank)
_MAXDV = {}
def maxdv(m, h, above_hyd):
    """Max dv (and tower, top-first) for a LAUNCHABLE tower of <= h stages under payload m.
    The deepest (first-firing) stage MUST be ground-capable — a vacuum-only upper stage
    (Starship, hydrolox uppers, NERVA…) can't lift off the pad. Returns (dv, tower) or None."""
    if h <= 0:
        return None
    key = (m, h, above_hyd)
    if key in _MAXDV:
        return _MAXDV[key]
    best = None
    for t in TRANS:
        if t["tank"] and not above_hyd:          # a tank needs a hydrolox engine directly above
            continue
        dv = stage_dv(t, m)
        if not dv or dv <= 0:
            continue
        stage = _stagedict(t, m, dv)
        if t["ign"] in GROUND and (best is None or dv > best[0]):   # t IS the bottom
            best = (dv, [stage])
        if h > 1:                                                   # t rides a launchable sub-tower
            sub = maxdv(t["wet"], h - 1, t["hyd"])
            if sub is not None and (best is None or dv + sub[0] > best[0]):
                best = (dv + sub[0], [stage] + sub[1])
    _MAXDV[key] = best
    return best

def query(payload, h):
    """Max dv for the payload with <= h engine stages, trying each legal number of
    payload-attached Burners on top (they're equipment — they don't count as stages)."""
    best = (0, [])
    for bonus, addm, bstages in burner_options(payload):
        r = maxdv(payload + addm, h, False)      # the bare payload is not a hydrolox engine
        if r is not None and r[0] + bonus > best[0]:
            best = (r[0] + bonus, bstages + r[1])
    return best

def minmass_b(payload, d):
    """Cheapest launchable stack for the payload, trying each legal number of
    payload-attached Burners (their +1s reduce what the engines must deliver)."""
    best = (float("inf"), None)
    for bonus, addm, bstages in burner_options(payload):
        mass, tower = minmass(payload + addm, max(d - bonus, 0), False)
        if tower is not None and mass + addm < best[0]:
            best = (mass + addm, bstages + tower)
    return best

# Board mission dv totals — what the envelope numbers actually buy (docs/04).
MISSIONS = [
    ("Earth → LEO", 9),
    ("Moon: land + return (Apollo)", 18),
    ("Mars: one-way crewed landing", 15),
    ("Mars: land + return (crewed)", 23),
    ("Deep space: Voyager +8", 20),
]

_MM = {}
def minmass(m, d, above_hyd):
    """Cheapest LAUNCHABLE stack (min total stage wet-mass) to deliver >= d dv to a payload
    of mass m, with a GROUND-capable first stage (vacuum-only engines like NERVA can only ride
    above). A tank needs a hydrolox engine directly above it. Returns (total_mass, tower[top-first]).

    d is clamped to >= 0. d == 0 means "the dv goal is already met above; just need a ground
    first stage under mass m" — so even when a vacuum upper alone clears the dv, the search still
    explores adding a (lighter, overshooting) ground booster beneath it."""
    d = max(d, 0)
    key = (m, d, above_hyd)
    if key in _MM:
        return _MM[key]
    best = (float("inf"), None)
    for t in TRANS:
        if t["tank"] and not above_hyd:
            continue
        sdv = stage_dv(t, m)
        if not sdv or sdv <= 0:
            continue
        stage = _stagedict(t, m, sdv)
        if d == 0:                                # only need a ground first stage now
            if t["ign"] in GROUND and t["wet"] < best[0]:
                best = (t["wet"], [stage])
        else:
            if t["ign"] in GROUND and sdv >= d and t["wet"] < best[0]:   # t alone is the ground bottom
                best = (t["wet"], [stage])
            submass, subtower = minmass(t["wet"], d - sdv, t["hyd"])      # t rides a ground sub-tower
            if submass < float("inf") and t["wet"] + submass < best[0]:
                best = (t["wet"] + submass, [stage] + subtower)
    _MM[key] = best
    return best

# ---------------------------------------------------------------- report
def fmt_tower(tower):
    lines = []
    for s in reversed(tower):                   # bottom (launch) first
        nn = f"{s['n']}× " if s["n"] > 1 else ""
        lines.append(f"      {nn}{s['card']} [{s['tech']}] — lifts {s['lifts_t']}t → {s['stage_dv']} dv "
                     f"({s['ign']})")
    return "\n".join(lines)

def set_active_cards(exclude=()):
    """Rebuild the transition set (and clear the memo tables) for a card-exclusion run."""
    global TRANS, _MAXDV, _MM
    TRANS = build_trans(exclude)
    _MAXDV, _MM = {}, {}

MILESTONES = [
    {"dv": 9, "label": "Orbit (LEO)"},
    {"dv": 15, "label": "Moon / Mars landing (one-way)"},
    {"dv": 18, "label": "Apollo — Moon land + return"},
    {"dv": 20, "label": "Deep space (Voyager +8)"},
    {"dv": 23, "label": "Mars land + return"},
]
NEVER_FLEW = [e["name"] for e in ENGINES if not e.get("flown", True)]   # paper/test-only hardware

def compute_variant(payload):
    """Run the full analysis (envelope, max towers, cheapest mission stacks, Pareto frontier,
    card usage) against the CURRENT TRANS set. Returns a self-contained variant dict."""
    env, max_towers, seen = [], [], set()
    for h in range(1, MAXH + 1):
        dv, tower = query(payload, h)
        env.append(dv)
        if dv not in seen:
            seen.add(dv)
            max_towers.append({"height": h, "dv": dv, "stack": tower,
                               "liftoff_t": sum(s["wet_t"] for s in tower) + payload})
    ceiling = max_towers[-1]

    missions, usage = [], {}
    for label, need in MISSIONS:
        mass, tower = minmass_b(payload, need)
        if tower is None:
            continue
        for s in tower:
            usage[s["card"]] = usage.get(s["card"], 0) + 1
        missions.append({"label": label, "need_dv": need, "total_dv": sum(s["stage_dv"] for s in tower),
                         "stages": len(tower), "liftoff_t": mass + payload,
                         "ground_launchable": tower[-1]["ign"] in GROUND, "stack": tower})

    raw = []
    for dgoal in range(1, ceiling["dv"] + 1):
        mass, stack = minmass_b(payload, dgoal)
        if stack is None:
            continue
        raw.append({"dv": sum(s["stage_dv"] for s in stack), "liftoff_t": round(mass + payload),
                    "stages": len(stack), "stack": stack})
    best_at = {}
    for p in raw:
        if p["liftoff_t"] not in best_at or p["dv"] > best_at[p["liftoff_t"]]["dv"]:
            best_at[p["liftoff_t"]] = p
    pareto, best_dv = [], -1
    for mt in sorted(best_at):
        p = best_at[mt]
        if p["dv"] > best_dv:
            pareto.append(p)
            best_dv = p["dv"]
    pu = {}
    for p in pareto:
        for s in p["stack"]:
            pu[s["card"]] = pu.get(s["card"], 0) + 1
    single = {t["name"]: stage_dv(t, 10) for t in TRANS if t["n"] == 1 and stage_dv(t, 10)}
    if BURNER:
        single[BURNER["name"]] = BURNER["burn_dv"]
    most = [n for n, _ in sorted(pu.items(), key=lambda x: -x[1])[:3]]
    return {"envelope": env, "max_towers": max_towers, "ceiling": ceiling, "missions": missions,
            "pareto": pareto, "pareto_usage": pu, "card_single_dv": single, "usage": usage,
            "most_used": most}

def main():
    PAYLOAD = 10                                  # a 10t token = a spacecraft to deliver
    set_active_cards(())
    theo = compute_variant(PAYLOAD)               # theoretical — every card in the deck
    set_active_cards(NEVER_FLEW)
    hist = compute_variant(PAYLOAD)               # historical — only hardware that actually flew

    report = {"max_height": MAXH, "payload_t": PAYLOAD,
              "bundle_mults": {tok: sorted(m) for tok, m in ALLOWED_MULTS.items()},
              "milestones": MILESTONES, "never_flew": NEVER_FLEW,
              "variants": {"theoretical": theo, "historical": hist}}
    # back-compat: also surface the theoretical fields at top level for any older reader
    report.update({k: theo[k] for k in
                   ("envelope", "max_towers", "ceiling", "missions", "pareto", "pareto_usage",
                    "card_single_dv", "usage", "most_used")})

    for title, v in (("THEORETICAL (all cards)", theo), ("HISTORICAL (flew in reality)", hist)):
        print("=" * 78)
        print(f"  {title}: ceiling {v['ceiling']['dv']} dv @ ~{v['ceiling']['liftoff_t']:,}t · "
              f"{len(v['pareto'])} Pareto towers")
        top = sorted(v["pareto_usage"].items(), key=lambda x: -x[1])[:5]
        print("    most-used:  " + " · ".join(f"{n} {c}×" for n, c in top))
        for m in v["missions"]:
            print(f"    {m['label']:<34} {m['total_dv']:>2} dv  {m['stages']} stages  ~{m['liftoff_t']:,}t")
    print(f"\n  never flew (excluded from historical): {', '.join(NEVER_FLEW)}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  wrote {os.path.relpath(OUT, HERE)}")

if __name__ == "__main__":
    main()
