#!/usr/bin/env python3
"""
Strip regeneration — the DISPLACEMENT model (docs/01-physics-model.md).

    dv = ve * ln(total_mass / (dry_mass + cargo)),   ve = Isp * 9.81 / 1000

NOT the additive model. (An earlier version of this file used the additive form
`ln((total+cargo)/(dry+cargo))` and referenced long-dropped cards — it would have
silently corrupted every strip. Do not reintroduce it. See CLAUDE.md and
docs/01.)

Each strip has two parts:
  1. TOKEN rows  — cargo at token-clean masses (10t..fuel), one row per integer
     dv (largest cargo kept per dv), with two-token gap-fill between flanking rows.
  2. EQUIPMENT rows — below the 10t token floor, the rocket carries only blue
     equipment cards (~2.5t each). We add rows for 3, 2, 1 equipment (7.5/5/2.5t),
     keep only those that unlock a NEW higher dv than the token rows, and dedupe by
     dv (largest cargo per dv). Minimum 1 equipment — a rocket always carries at
     least one payload card, never flies empty. These rows carry an "eq" field.

This is where Gagarin/Glenn live: K2 carrying a sub-token capsule makes 9 dv (orbit)
where K2 + a 10t token makes only 8.

Run from src/:  python3 regen_strips.py
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, "..", "data", "cards.json")

with open(CARDS) as f:
    d = json.load(f)

TOKENS = [10, 20, 30, 40, 80, 120, 160, 320, 480, 640, 1280, 1920, 2560]
EQUIP_T = 2.5  # one blue equipment card, sub-token

def ve(e):
    return e["isp_s"] * 9.81 / 1000.0

def dv_disp(e, cargo):
    """Displacement-model dv (continuous)."""
    return ve(e) * math.log(e["total_mass_t"] / (e["dry_mass_t"] + cargo))

def two_token_combos_in_range(low, high):
    s = set()
    for i, t1 in enumerate(TOKENS):
        for a in range(1, 10):
            for j, t2 in enumerate(TOKENS):
                if j <= i:
                    continue
                for b in range(1, 10):
                    v = a * t1 + b * t2
                    if low < v < high:
                        s.add(v)
    return sorted(s)

def token_rows(e):
    """Token-clean rows: largest cargo per integer dv, capped below fuel, gap-filled."""
    fuel = e["fuel_mass_t"]
    by_dv = {}
    for c in TOKENS:
        if c >= fuel:
            continue
        dv = round(dv_disp(e, c))
        if 0 < dv <= 15 and (dv not in by_dv or c > by_dv[dv]):
            by_dv[dv] = c
    dvs = sorted(by_dv)
    if len(dvs) >= 2:
        for tdv in range(dvs[0], dvs[-1] + 1):
            if tdv in by_dv:
                continue
            above = next((by_dv[x] for x in sorted(by_dv) if x > tdv), None)
            below = next((by_dv[x] for x in sorted(by_dv, reverse=True) if x < tdv), None)
            if above is None or below is None:
                continue
            best = None
            for c in two_token_combos_in_range(above, below):
                if c >= fuel:
                    continue
                if round(dv_disp(e, c)) == tdv and (best is None or c > best):
                    best = c
            if best is not None:
                by_dv[tdv] = best
    return sorted(({"cargo_t": c, "dv": dv} for dv, c in by_dv.items()),
                  key=lambda r: r["dv"])

def equipment_rows(e, base):
    """Sub-token rows for 3/2/1 equipment cards. Keep only NEW higher dv steps,
    largest cargo per dv. Minimum 1 equipment (never empty)."""
    max_dv = max((r["dv"] for r in base), default=0)
    best = {}  # dv -> (cargo, n_equipment)
    for n in (3, 2, 1):  # largest cargo first
        cargo = n * EQUIP_T
        if cargo >= e["fuel_mass_t"]:
            continue
        dv = round(dv_disp(e, cargo))
        if dv > max_dv and dv not in best:
            best[dv] = (cargo, n)
    return [{"cargo_t": c, "dv": dv, "eq": n}
            for dv, (c, n) in sorted(best.items())]

for e in d["engines"]:
    if e.get("kind") == "fixed":
        continue  # sub-grid cards (MAV, Hypergolic Upper, Ion) print their own dv table
    base = token_rows(e)
    e["strip"] = base + equipment_rows(e, base)

with open(CARDS, "w") as f:
    json.dump(d, f, indent=2)

# ---- verify -------------------------------------------------------------------
E = {e["name"]: e for e in d["engines"]}
def fmt(r):
    return (f"{r['eq']}eq" if "eq" in r else f"{r['cargo_t']:g}t") + f"/{r['dv']}"
def look(name, cargo):
    rows = [r for r in E[name]["strip"] if r["cargo_t"] >= cargo]
    return min(rows, key=lambda r: r["cargo_t"])["dv"] if rows else None

print("=== Regenerated strips (displacement model + equipment tail) ===\n")
for name in E:
    if E[name].get("kind") == "fixed":
        continue
    print(f"  {name:26} " + " ".join(fmt(r) for r in E[name]["strip"]))

print("\nKey checks:")
print(f"  First Orbit — K2 + 1 capsule (~2.5t): {look('KEROLOX BOOSTER', 2.5)} dv (need 9)")
print(f"  K1 suborbital ceiling (+capsule):     {look('KEROLOX SUSTAINER', 2.5)} dv (need 9 for orbit)")
print(f"  Apollo LM descent — Light Descent + Ascent eq: {look('LIGHT DESCENT ENGINE', 2.5)} dv (need 2)")
print(f"  CSM return regime — Transfer w/ 1 eq:  {look('HYPERGOLIC TRANSFER STAGE', 2.5)} dv")
