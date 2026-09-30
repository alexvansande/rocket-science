#!/usr/bin/env python3
"""
Triskelion playtest harness — the RULES + MISSIONS engine.

Pipeline role (mirrors the card pipeline):
    data/cards.json ──> playtest.py ──> build/playtest-results.json ──> build_playtest_report.py ──> HTML

Two jobs:
  1. AUDIT — sanity-check the raw numbers in data/cards.json (ladder snapping,
             token<->mass agreement, ve<->Isp, dry+fuel==total, and every printed
             push-strip row recomputed from the rocket equation).
  2. PLAY  — fly reference missions on the board's dv budgets using the
             displacement (chain) model, and report whether each closes.

This module COMPUTES results into a plain dict and (a) prints a terminal report,
(b) writes build/playtest-results.json for the visualizer. It does no HTML.

Design model (see docs/01-physics-model.md):
    dv = ve * ln(total / (dry + cargo)),  ve = Isp * 9.81 / 1000  (km/s)
CHAIN staging (verified vs the Apollo cascade): each stage's cargo is the TOTAL
(wet) mass of the single stage directly above it; the top stage carries the
declared payload. Serial-stage dv adds; parallel boosters do NOT (entered
explicitly).

Run from src/:  python3 playtest.py
Exit code is nonzero if any data bug or hard invariant is violated (regression test).
"""

import json
import math
import os
import sys

import regen_strips  # side-effect-free import; expected_strip() audits for stale strips

G0 = 9.81
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cards.json")
OUT_JSON = os.path.join(HERE, "..", "build", "playtest-results.json")

# Token ladder + the deliberate super-heavy overflows (Super Heavy / Nova 3840,
# Sea Dragon 16000) — they print as "N × ⬛" and never park, so they're by design.
MASS_LADDER = [10, 20, 30, 40, 80, 120, 160, 320, 480, 640, 1280, 1920, 2560, 3840, 16000]
TOKEN_VALUE = {"Y": 10, "O": 40, "R": 160, "K": 640}
EQUIP_T = 2.5  # an equipment card is sub-grid, ~2.5t; counts as cargo unless carried free

with open(DATA) as f:
    DATAJSON = json.load(f)
ENGINES = {e["name"]: e for e in DATAJSON["engines"]}
EQUIP = {q["name"]: q for q in DATAJSON["equipment"]}

# Fixed sub-grid dv tables (equipment-count -> dv), from each card's fixed_text.
SUBGRID_DV = {
    "MARS ASCENT VEHICLE": {0: 6, 1: 4, 2: 3, 3: 2, 4: 1},
    "HYPERGOLIC UPPER":    {0: 6, 1: 3, 2: 1},
}

# ---- core physics -------------------------------------------------------------
def ve_of(eng):
    return eng["isp_s"] * G0 / 1000.0

def dv_raw(eng, cargo_t):
    total, dry = eng["total_mass_t"], eng["dry_mass_t"]
    if cargo_t > (total - dry) + 1e-9:
        return None  # nowhere to put that much cargo
    return ve_of(eng) * math.log(total / (dry + cargo_t))

def dv_round(eng, cargo_t):
    r = dv_raw(eng, cargo_t)
    return None if r is None else round(r)

def tokens_for_mass(mass_t):
    rem, out = mass_t, []
    for letter in ("K", "R", "O", "Y"):
        while rem >= TOKEN_VALUE[letter]:
            out.append(letter); rem -= TOKEN_VALUE[letter]
    if rem > 0:
        out.append("Y")
    return "".join(out)

def mass_of_tokens(tok):
    return sum(TOKEN_VALUE[t] for t in tok)

# =============================================================================
# BOARD dv BUDGETS  (docs/04-board-and-trajectories.md)
# =============================================================================
SEG = {
    "surface->LEO": 9,
    "LEO->escape": 3,
    "escape->lunar_orbit": 1,
    "lunar_orbit->lunar_surface": 2,     # propulsive (Moon: no aerobrake)
    "lunar_surface->lunar_orbit": 2,
    "lunar_orbit->TEI": 1,               # then free aerobrake home w/ Atmospheric Return
    "escape->mars_orbit": {"slow": 3, "medium": 4, "fast": 5},
    "mars_orbit->mars_surface_prop": 3,
    "mars_orbit->mars_surface_aero": 1,  # requires Atmospheric Return
    "mars_surface->mars_orbit": 4,
}

# =============================================================================
# PART 1 — NUMBERS AUDIT  -> dict
# =============================================================================
def run_audit():
    problems, dry_drift, warnings, strip_rows = [], [], [], 0
    for name, e in ENGINES.items():
        total = e.get("total_mass_t", 0)
        dry = e.get("dry_mass_t", 0)
        fuel = e.get("fuel_mass_t", None)

        if fuel is not None and abs((dry + fuel) - total) > 0.01:
            problems.append({"card": name, "field": "mass",
                             "msg": f"dry({dry})+fuel({fuel}) != total({total})"})
        if total not in MASS_LADDER:
            warnings.append({"card": name, "msg": f"total {total}t not on the mass ladder"})
        # Dry-mass floor (docs/01): dry >= total/16, rounded up. K2 is the documented
        # exemption — dry 20 < 30 props up the First Orbit knife-edge (K2+capsule = 9).
        if dry + 1e-9 < total / 16 and name != "KEROLOX BOOSTER":
            warnings.append({"card": name,
                             "msg": f"dry {dry}t below the total/16 floor ({total / 16:g}t)"})
        # Refuel cleanliness (docs/01): for R-class-and-up cards (total >= 320), the
        # refuel cost (fuel = total - dry) must lay out in at most TWO token colours
        # with no sub-token remainder — round dry until it does (tested at dry-change
        # time against the missions; K2 is exempt, pinned by First Orbit).
        if total >= 320 and fuel is not None and name != "KEROLOX BOOSTER":
            rem, colors = fuel, 0
            for v in (640, 160, 40, 10):
                if rem >= v:
                    colors += 1
                    rem %= v
            if colors > 2 or rem > 0:
                warnings.append({"card": name,
                                 "msg": f"refuel {fuel}t needs >2 token colours — round dry "
                                        f"per the docs/01 refuel-cleanliness rule"})
        if "exhaust_velocity_kms" in e and abs(ve_of(e) - e["exhaust_velocity_kms"]) > 0.05:
            warnings.append({"card": name,
                             "msg": f"stored ve {e['exhaust_velocity_kms']} != Isp-derived {ve_of(e):.3f}"})

        tok = e.get("total_tokens")
        if tok and abs(mass_of_tokens(tok) - total) > 0.01:
            problems.append({"card": name, "field": "total_tokens",
                             "msg": f"total_tokens '{tok}' shows {mass_of_tokens(tok)}t but total is "
                                    f"{total}t (should be '{tokens_for_mass(total)}')"})

        dtok = e.get("dry_tokens")
        if dtok:
            if abs(mass_of_tokens(dtok) - dry) > 0.01:
                dry_drift.append({"card": name, "shown": mass_of_tokens(dtok), "actual": dry})

        bad = []
        for row in e.get("strip", []) or []:
            strip_rows += 1
            dvc = dv_round(e, row["cargo_t"])
            if dvc is None:
                bad.append(f"cargo {row['cargo_t']}t exceeds fuel bay")
            elif dvc != row["dv"]:
                bad.append(f"cargo {row['cargo_t']}t: printed {row['dv']} != recomputed {dvc}")
        if bad:
            problems.append({"card": name, "field": "strip", "msg": "; ".join(bad)})

        # Staleness: the printed strip must be EXACTLY what regen_strips would produce
        # (catches missing/extra rows, which the per-row recompute above cannot see).
        expected = regen_strips.expected_strip(e)
        if (e.get("strip") or []) != expected:
            problems.append({"card": name, "field": "strip",
                             "msg": "strip is stale — differs from regen_strips output "
                                    "(run src/regen_strips.py)"})

        if e.get("kind") == "stage" and not (e.get("strip") or []):
            warnings.append({"card": name, "msg": "kind='stage' but empty strip"})

    return {
        "engines_checked": len(ENGINES),
        "strip_rows_checked": strip_rows,
        "problems": problems,
        "warnings": warnings,
        "dry_token_drift": dry_drift,
        "clean": len(problems) == 0,
    }

# =============================================================================
# PART 2 — MISSION MODEL  -> dict
# =============================================================================
class Burn:
    def __init__(self, engine_name, cargo_t, leg, note="", equip_carried=0,
                 fixed_dv=None, parallel_dv=None):
        self.engine_name = engine_name
        self.cargo_t = cargo_t
        self.leg = leg
        self.note = note
        self.equip_carried = equip_carried
        self.fixed_dv = fixed_dv
        self.parallel_dv = parallel_dv

    def mode(self):
        if self.parallel_dv is not None:
            return "parallel"
        if self.engine_name in SUBGRID_DV:
            return "subgrid"
        if self.fixed_dv is not None:
            return "fixed"
        return "serial"

    def dv(self):
        if self.parallel_dv is not None:
            return self.parallel_dv
        if self.fixed_dv is not None:
            return self.fixed_dv
        if self.engine_name in SUBGRID_DV:
            return SUBGRID_DV[self.engine_name][self.equip_carried]
        return dv_round(ENGINES[self.engine_name], self.cargo_t)

    def to_dict(self, ground_start, is_first):
        e = ENGINES.get(self.engine_name)
        dv = self.dv()
        mode = self.mode()
        ign_warn = bool(ground_start and is_first and mode == "serial"
                        and e and e.get("ignition") in ("space", "mars-surface"))
        return {
            "engine": self.engine_name,
            "fuel_type": (e.get("fuel_type") if e else None),
            "tech_label": (e.get("tech_label") if e else None),
            "cargo_t": (None if mode in ("parallel", "subgrid", "fixed") else self.cargo_t),
            "dv": dv,
            "leg": self.leg,
            "note": self.note,
            "mode": mode,
            "ignition": e.get("ignition") if e else None,
            "infeasible": dv is None,
            "ignition_warning": ign_warn,
        }

class Mission:
    def __init__(self, title, required_dv, crew=False, transit_months=0, must="pass",
                 ground_start=True, finding_if_short=None, finding_if_closes=None):
        self.title = title
        self.required_dv = required_dv
        self.crew = crew
        self.transit_months = transit_months
        self.must = must          # "pass" | "fail" | "info"
        self.ground_start = ground_start
        self.finding_if_short = finding_if_short
        self.finding_if_closes = finding_if_closes
        self.burns = []
        self.notes = []

    def add(self, *a, **k):
        self.burns.append(Burn(*a, **k)); return self

    def note(self, s):
        self.notes.append(s); return self

    def evaluate(self):
        burns, total, feasible = [], 0, True
        for i, b in enumerate(self.burns):
            bd = b.to_dict(self.ground_start, i == 0)
            burns.append(bd)
            if bd["infeasible"]:
                feasible = False
            else:
                total += bd["dv"]
        closes = feasible and (total >= self.required_dv)

        # verdict + hard-failure / finding classification
        problem = None
        finding = None
        if self.must == "fail":
            verdict = "correctly-short" if not closes else "INVARIANT-BROKEN"
            if closes:
                problem = f"invariant broken: '{self.title}' was expected to fall short but closed"
        elif self.must == "info":
            verdict = "closes" if closes else "falls-short"
        else:  # pass
            verdict = "PASS" if closes else "FAIL"
            if not closes:
                problem = f"regression: '{self.title}' should close but is {total} < {self.required_dv}"
        if not closes and self.finding_if_short:
            finding = self.finding_if_short.format(total=total, req=self.required_dv)
        if closes and self.finding_if_closes:
            finding = self.finding_if_closes.format(total=total, req=self.required_dv)

        return {
            "title": self.title,
            "required_dv": self.required_dv,
            "total_dv": total,
            "closes": closes,
            "feasible": feasible,
            "must": self.must,
            "verdict": verdict,
            "crew": self.crew,
            "transit_months": self.transit_months,
            "consumable_cards": (math.ceil(self.transit_months / 4) if self.crew and self.transit_months else 0),
            "ground_start": self.ground_start,
            "burns": burns,
            "notes": list(self.notes),
            "margin": total - self.required_dv,
        }, problem, finding

def T(name):
    return ENGINES[name]["total_mass_t"]

# =============================================================================
# SCENARIOS  -> list[Mission]  + the refuel analysis
# =============================================================================
def build_missions():
    M = []

    # 1. Apollo 11 — Apollo cards only, land + return.
    m = Mission("Apollo 11 — land on the Moon and return (Apollo cards only)",
                required_dv=(SEG["surface->LEO"] + SEG["LEO->escape"] + SEG["escape->lunar_orbit"]
                             + SEG["lunar_orbit->lunar_surface"] + SEG["lunar_surface->lunar_orbit"]
                             + SEG["lunar_orbit->TEI"]),
                crew=True, transit_months=2)
    m.add("HEAVY KEROLOX BOOSTER", T("HEAVY HYDROLOX CORE"), "surface → +4")
    m.add("HEAVY HYDROLOX CORE",   T("HEAVY HYDROLOX UPPER"), "+4 → LEO (9)")
    m.add("HEAVY HYDROLOX UPPER",  T("HYPERGOLIC TRANSFER STAGE"), "LEO → Earth Escape (TLI)")
    m.add("HYPERGOLIC TRANSFER STAGE", T("LIGHT DESCENT ENGINE"), "LOI + reserve TEI",
          equip_carried=2, note="carries Crew Capsule + Atmospheric Return free")
    m.add("LIGHT DESCENT ENGINE", EQUIP_T, "Lunar Orbit → Surface", note="carries Light Ascent (2.5t)")
    m.add("LIGHT ASCENT ENGINE", EQUIP_T, "Surface → Lunar Orbit", fixed_dv=2,
          note="equipment card, printed 2 dv lifting crew")
    m.note("TEI from the Transfer Stage's reserved dv; aerobrake home free (Atmospheric Return).")
    M.append(m)

    # 1b. Nova lunar landing — DIRECT ASCENT (land the CSM itself, no separate LM).
    m = Mission("Nova lunar landing — direct ascent (land the CSM, no LM)",
                required_dv=(SEG["surface->LEO"] + SEG["LEO->escape"] + SEG["escape->lunar_orbit"]
                             + SEG["lunar_orbit->lunar_surface"] + SEG["lunar_surface->lunar_orbit"]
                             + SEG["lunar_orbit->TEI"]),
                crew=True, transit_months=2)
    m.add("SUPER HEAVY KEROLOX BOOSTER", T("HEAVY HYDROLOX CORE"), "surface → +4")
    m.add("HEAVY HYDROLOX CORE",  T("HEAVY HYDROLOX UPPER"), "+4 → LEO")
    m.add("HEAVY HYDROLOX UPPER", T("HYPERGOLIC TRANSFER STAGE"), "LEO → Earth Escape")
    m.add("HYPERGOLIC TRANSFER STAGE", 0, "LOI + land + ascend + TEI (the CSM IS the lander)",
          equip_carried=2, note="40t CSM flies itself down and back — no separate Lunar Module")
    m.note("What we land: the whole 40t CSM, directly (Nova's design purpose). 4 stages, no LM. "
           "BUT the booster carries only a 480t core here, so Saturn (K3) flies the identical mission "
           "— Nova's extra lift is wasted unless you load a heavier core. Possible model flag: the "
           "board's flat 2-dv land/ascend doesn't penalise landing a heavy vehicle, so direct ascent "
           "is 'too cheap' vs the history that forced Apollo into Lunar-Orbit-Rendezvous.")
    M.append(m)

    # 2. Hubble to LEO on the Shuttle stack.
    HUBBLE_T = 25
    m = Mission("Deploy Hubble to LEO on the Shuttle stack", required_dv=SEG["surface->LEO"])
    m.add("HEAVY SOLID BOOSTER", 0, "liftoff (2 SRBs, parallel)", parallel_dv=1,
          note="2x Heavy Solid Booster fire together; parallel dv does not add")
    m.add("HYDROLOX DROP TANK", T("ORBITER") + HUBBLE_T, "ascent to near-orbit",
          note=f"carries Orbiter (80t) + {HUBBLE_T}t payload")
    m.add("ORBITER", HUBBLE_T, "OMS circularization", note="burns its own reserve")
    m.note("Orbiter re-enters on its built-in heat shield (free aerobrake). Hubble stays in LEO.")
    M.append(m)

    # 2b. SLS Block 1 / Artemis I — the Drop Tank under a NON-Orbiter hydrolox engine.
    # Encodes the ruling that the tank pairs with ANY hydrolox engine riding directly
    # above it (here H1 — whose heritage is literally the DCSS/ICPS). No new card needed.
    ORION_T = 10
    m = Mission("SLS Block 1 (Artemis I) — 2 SRBs + Drop Tank + ICPS (H1), Orion to lunar orbit",
                required_dv=(SEG["surface->LEO"] + SEG["LEO->escape"] + SEG["escape->lunar_orbit"]),
                crew=True, transit_months=1)
    m.add("HEAVY SOLID BOOSTER", 0, "liftoff (2 SRBs, parallel)", parallel_dv=1,
          note="2x Heavy Solid Booster fire together; parallel dv does not add")
    m.add("HYDROLOX DROP TANK", T("HYDROLOX UPPER") + ORION_T, "core-stage burn to orbit",
          note=f"the ICPS (H1) above burns the tank's fuel; carries H1 (30t) + Orion ({ORION_T}t)")
    m.add("HYDROLOX UPPER", ORION_T, "ICPS sends Orion translunar", note="Orion = 10t (1 yellow)")
    m.note("The Shuttle tank reused as the SLS core: same Drop Tank card, but the hydrolox "
           "engine riding it is the small H1 upper (DCSS/ICPS heritage) instead of the Orbiter. "
           "Closes with margin — the tank-pairs-with-any-hydrolox-engine ruling makes SLS "
           "buildable from existing cards.")
    M.append(m)

    # 3a. Starship to Mars — expendable, no refuel.
    m = Mission("Starship to Mars — expendable, NO orbital refuel", required_dv=SEG["surface->LEO"])
    m.add("SUPER HEAVY", T("STARSHIP"), "surface → +2 (booster staging)")
    m.add("STARSHIP", 120, "Starship climbs to LEO", note="120t payload")
    m.note("Reaches LEO but arrives EMPTY — zero dv left for trans-Mars injection.")
    M.append(m)

    # 3b. Starship to Mars — refueled in LEO, aerobrake descent (descent is free).
    m = Mission("Starship to Mars — refueled in LEO, aerobrake descent",
                required_dv=SEG["LEO->escape"] + SEG["escape->mars_orbit"]["slow"],
                crew=True, transit_months=8, ground_start=False)
    m.add("STARSHIP", 120, "LEO → Mars orbit", note="topped off to full fuel in LEO; 120t payload")
    m.note("Mars-orbit → surface is a FREE aerobrake with Atmospheric Return (not counted in the "
           "propulsive budget), so the stack only has to fund the 6 dv out to Mars orbit.")
    M.append(m)

    # 4. Moon sample-return on a non-Apollo stack.
    m = Mission("Moon sample-return on a Kerolox/Hydrolox stack (no Apollo heritage)",
                required_dv=(SEG["surface->LEO"] + SEG["LEO->escape"] + SEG["escape->lunar_orbit"]
                             + SEG["lunar_orbit->lunar_surface"] + SEG["lunar_surface->lunar_orbit"]
                             + SEG["lunar_orbit->TEI"]))
    m.add("HEAVY KEROLOX BOOSTER", T("HEAVY HYDROLOX CORE"), "surface → +4")
    m.add("HEAVY HYDROLOX CORE",   T("HYPERGOLIC TRANSFER STAGE"), "+4 → LEO")
    m.add("HYPERGOLIC TRANSFER STAGE", T("LIGHT DESCENT ENGINE"), "TLI + LOI + TEI reserve",
          equip_carried=2, note="carries Sample Container + Atmospheric Return free")
    m.add("LIGHT DESCENT ENGINE", EQUIP_T, "land (robotic)", note="carries Light Ascent")
    m.add("LIGHT ASCENT ENGINE", EQUIP_T, "ascend with samples", fixed_dv=2)
    m.note("Uncrewed: no consumables. A generic (non-tuned) stack still closes a land-and-return.")
    M.append(m)

    # 5a. First Orbit — the R-7 / Atlas stack (K2) with a sub-grid capsule.
    m = Mission("First Orbit — R-7 / Atlas (K2) + crew capsule (Sputnik · Gagarin · Glenn)",
                required_dv=SEG["surface->LEO"])
    m.add("KEROLOX BOOSTER", EQUIP_T, "stage-and-a-half to orbit",
          note="carries a sub-grid crew capsule (~2.5t), NOT a 10t cargo token")
    m.note("R-7 and Atlas both orbited a tiny capsule (Vostok 4.7t, Mercury 1.4t). As an "
           "equipment-scale payload, K2 makes 9 dv. Orbit is a tier-2 (R-7) feat — one unlock "
           "above the K1 suborbital start. Nobody orbits on their first rocket.")
    M.append(m)

    # 5b. K1 alone — the suborbital ceiling (Redstone / V-2).
    m = Mission("Level-1 K1 (Atlas sustainer) alone — suborbital ceiling", must="info",
                required_dv=SEG["surface->LEO"])
    m.add("KEROLOX SUSTAINER", EQUIP_T, "max climb with a capsule")
    m.note("K1 tops out ~7 dv: a suborbital hop (Redstone/Shepard) or a ballistic missile "
           "(V-2 — 'bomb London'), never orbit. Falling short of 9 here is CORRECT, not a bug.")
    M.append(m)

    # 5c. The commercial path — grow WITHOUT military contracts (telecom / GPS / tourism).
    m = Mission("Commercial launch — Falcon-9-class (K2) puts a satellite in LEO (private path)",
                required_dv=SEG["surface->LEO"])
    m.add("KEROLOX BOOSTER", EQUIP_T, "payload to orbit",
          note="1 equipment: comsat / GPS sat / smallsat / tourist capsule")
    m.note("The private growth path needs no military contracts: telecom, GPS, and tourism. K2 "
           "(Falcon 9 / R-7 / Atlas) lofts ~1 equipment-scale payload to LEO — enough for the "
           "bread-and-butter commercial market. NOTE: K2 orbits ~2.5-5t, the R-7/Soyuz end of its "
           "heritage; real Falcon 9 lifts ~22t, so heavy or GEO commercial needs an upper stage or K3.")
    M.append(m)

    # 5d. The honest two-stage Falcon 9 / Soyuz — first stage + the new Kerolox Upper (Ku).
    m = Mission("Falcon 9 — 20t commercial payload to LEO (K2 + Kerolox Upper, 2 stages)",
                required_dv=SEG["surface->LEO"])
    m.add("KEROLOX BOOSTER", T("KEROLOX UPPER"), "9-Merlin first stage lifts the upper")
    m.add("KEROLOX UPPER", 20, "Merlin Vacuum → orbital insertion", note="20t payload (2 yellow)")
    m.note("The real Falcon 9, staged: K2 (9 Merlins) does liftoff, the single Merlin Vacuum (Ku) does "
           "orbital insertion → ~20t to LEO. K2 ALONE only orbits a sub-token capsule (Sputnik/Glenn "
           "stage-and-a-half); real tonnage needs the upper. Same way Soyuz = K2 + Blok-I.")
    M.append(m)

    # 6a. Saturn V → crewed Mars LANDING + RETURN — the real invariant: must fail.
    m = Mission("Single Saturn V → crewed Mars landing + return (invariant: must FAIL)",
                required_dv=(SEG["LEO->escape"] + 2 * SEG["escape->mars_orbit"]["slow"]
                             + SEG["LEO->escape"]),
                must="fail", ground_start=False)
    m.add("HEAVY HYDROLOX UPPER", T("HYPERGOLIC TRANSFER STAGE"), "TLI from LEO")
    m.add("HYPERGOLIC TRANSFER STAGE", 10, "outbound + capture + return", equip_carried=2,
          note="CSM carries 10t mission payload; must also fund descent, ascent, and the way home")
    m.note("Round trip ≈ 12 dv plus a lander, ascent stage, and 8 months of food for the crew. "
           "Saturn V cannot. THIS is the real 'Saturn V can't reach Mars'.")
    M.append(m)

    # 6b. Saturn V → Mars ORBIT one-way, uncrewed — historically honest, KEEP.
    m = Mission("Single Saturn V → Mars ORBIT, one-way, uncrewed (historically true — KEEP)",
                required_dv=SEG["LEO->escape"] + SEG["escape->mars_orbit"]["slow"],
                must="info", ground_start=False)
    m.add("HEAVY HYDROLOX UPPER", T("HYPERGOLIC TRANSFER STAGE"), "TLI from LEO")
    m.add("HYPERGOLIC TRANSFER STAGE", 0, "injection toward Mars (probe / one-way)", equip_carried=2,
          note="a probe or a stripped, one-way capsule — no return, no crew consumables")
    m.note("INTENDED: 1970s hardware DID reach Mars (Viking). A stripped one-way shot to Mars orbit "
           "is a true fact, so the board is allowed to permit it. The line that must hold is "
           "crewed landing+return (6a), not reaching Mars at all.")
    M.append(m)

    # 7. The "For All Mankind" one-way crewed Mars LANDING on chemical tech — mad but possible.
    m = Mission("One-way crewed Mars landing — chemical tech, NO return (a suicide shot)",
                required_dv=(SEG["surface->LEO"] + SEG["LEO->escape"]
                             + SEG["escape->mars_orbit"]["slow"]),  # descent = free aerobrake
                crew=True, transit_months=8)
    m.add("HEAVY KEROLOX BOOSTER", T("HEAVY HYDROLOX CORE"), "surface → +4")
    m.add("HEAVY HYDROLOX CORE",   T("HEAVY HYDROLOX UPPER"), "+4 → LEO")
    m.add("HEAVY HYDROLOX UPPER",  T("HYPERGOLIC TRANSFER STAGE"), "LEO → Earth Escape (TMI)")
    m.add("HYPERGOLIC TRANSFER STAGE", 2 * EQUIP_T, "Mars injection + capture", equip_carried=2,
          note="Crew Capsule + Atmospheric Return ride free; +2 Consumables (8 mo food) as cargo")
    m.note("Aerobrake to the surface is free (Atmospheric Return). No ascent stage, no return "
           "propellant — they land ALIVE and STRANDED, food barely lasting. Physically possible, so "
           "the game permits it: the For All Mankind one-way gambit. Surviving needs a later rescue.")
    M.append(m)

    # 8. Level-1 only — an EQUIPMENT (sub-token) payload CAN orbit (K1 + H1).
    m = Mission("Level-1 only — 1 equipment to ORBIT (Kerolox Sustainer + Hydrolox Upper)",
                required_dv=SEG["surface->LEO"])
    m.add("KEROLOX SUSTAINER", T("HYDROLOX UPPER"), "first-stage climb")
    m.add("HYDROLOX UPPER", EQUIP_T, "upper to orbit", note="1 equipment (~2.5t) — a capsule/satellite")
    m.note("Level-1 CAN reach orbit — but only with a sub-token (equipment) payload, not a 10t token. "
           "This is the Gagarin/equipment-row lesson: the high-dv regime lives below the token floor.")
    M.append(m)

    # 9. Level-1 only — heavy load to a DV7 military contract (ICBM-class throw).
    m = Mission("Military contract — deliver 10t to DV7, level-1 only (K1 + H1)",
                required_dv=7)
    m.add("KEROLOX SUSTAINER", T("HYDROLOX UPPER"), "first-stage climb")
    m.add("HYDROLOX UPPER", 10, "throw the payload", note="10t (1 yellow) — 'don't ask questions'")
    m.note("ICBM-class throw: level-1 tech lobs a 10t payload to ~8 dv (≥ the DV7 contract). A 20t "
           "load would fall short — heavy military lift needs teching up.")
    M.append(m)

    # ===== CREWED MARS RETURN — three architectures ==========================
    # Propulsive leg budgets (aerobrake descents are FREE with Atmospheric Return).
    LEO_TO_MARS = SEG["LEO->escape"] + SEG["escape->mars_orbit"]["slow"]   # 6
    MARS_ASCENT = SEG["mars_surface->mars_orbit"]                         # 4
    MARS_TO_EARTH = SEG["escape->mars_orbit"]["slow"]                     # 3 (Earth aerobrake free)

    # --- A) Expendable, many stages, NUCLEAR (the 1969 NASA / Apollo-era plan) ---
    m = Mission("[Mars A · nuclear] NERVA trans-Mars push of the crewed lander stack",
                required_dv=LEO_TO_MARS, crew=True, transit_months=8, ground_start=False)
    m.add("NUCLEAR ENGINE", 20, "LEO → Mars orbit", note="NERVA pushes a ~20t lander/ascent stack")
    m.note("Apollo-era Mars = Saturn V launches + NERVA (nuclear) deep-space stages, all expendable. "
           "One NERVA pushes ~20t to Mars orbit. The full lander+ascent+return+food stack is heavier, "
           "so the real plan CLUSTERS several NERVA modules assembled over multiple Saturn launches. "
           "Pure CHEMICAL can't do this leg at useful payload — that is WHY NERVA was funded.")
    M.append(m)
    m = Mission("[Mars A · nuclear] return — MAV ascent + NERVA, Mars surface → Earth",
                required_dv=MARS_ASCENT + MARS_TO_EARTH, crew=True, transit_months=8, ground_start=False)
    m.add("MARS ASCENT VEHICLE", 1, "Mars surface → orbit", equip_carried=1,
          note="MAV lifts the crew (1 equipment) to Mars orbit — 4 dv")
    m.add("NUCLEAR ENGINE", EQUIP_T, "Mars orbit → Earth", note="a second NERVA stage, sent fueled")
    m.note("Return needs its own pre-fuelled NERVA (no ISRU here). Verdict 'closes' = the return leg "
           "is feasible; the architecture's real cost is the launch count to assemble it all in LEO.")
    M.append(m)

    # --- B) Land a Starship, refuel in LEO, ISRU-refuel on Mars, fly home ------
    m = Mission("[Mars B · Starship+ISRU] outbound, LEO → Mars surface (crew + refinery)",
                required_dv=LEO_TO_MARS, crew=True, transit_months=8, ground_start=False)
    m.add("STARSHIP", 30, "LEO → Mars orbit", equip_carried=4,
          note="refuelled full in LEO; carries crew + Methalox Refinery + power + 30t supplies")
    m.note("Aerobrake to the surface free. Outbound needs ~15 LEO tanker flights to fill the ship "
           "(see the refuel analysis). On the surface, the Methalox Refinery + power make return propellant.")
    M.append(m)
    m = Mission("[Mars B · Starship+ISRU] return, Mars surface → Earth (ISRU-fuelled)",
                required_dv=MARS_ASCENT + MARS_TO_EARTH, crew=True, transit_months=8, ground_start=False)
    m.add("STARSHIP", EQUIP_T, "Mars surface → Mars orbit → Earth", equip_carried=4,
          note="topped off by ISRU on Mars; crew only, Earth aerobrake free")
    m.note("ISRU is the cheat code: you don't haul return propellant from Earth, you make it on Mars. "
           "One Starship does the whole round trip, refuelled twice (LEO tankers, then Mars ISRU).")
    M.append(m)

    # --- C) NO ISRU — pre-position a fuelled return vehicle, crew flies light ---
    m = Mission("[Mars C · split] CARGO: pre-position a fuelled return vehicle on Mars (uncrewed)",
                required_dv=LEO_TO_MARS, ground_start=False)
    m.add("STARSHIP", T("MARS ASCENT VEHICLE"), "deliver the MAV to Mars surface",
          note="refuelled in LEO; carries the fuelled MAV (20t) as cargo, aerobrakes it down")
    m.note("Sent on an earlier window, uncrewed. The MAV waits on the surface, already fuelled — no "
           "in-situ production needed.")
    M.append(m)
    m = Mission("[Mars C · split] CREW: fly out light (return vehicle already waiting)",
                required_dv=LEO_TO_MARS, crew=True, transit_months=8, ground_start=False)
    m.add("STARSHIP", 30, "LEO → Mars surface", equip_carried=4,
          note="crew + supplies only — carries NO return propellant, so it flies lighter")
    m.note("Because the return ride is pre-positioned, the crew vehicle doesn't haul ascent/return mass.")
    M.append(m)
    m = Mission("[Mars C · split] RETURN: cached MAV ascent + return stage to Earth",
                required_dv=MARS_ASCENT + MARS_TO_EARTH, crew=True, transit_months=8, ground_start=False)
    m.add("MARS ASCENT VEHICLE", 1, "Mars surface → orbit", equip_carried=1,
          note="the pre-positioned MAV lifts the crew (1 equipment) — 4 dv")
    m.add("HYPERGOLIC TRANSFER STAGE", EQUIP_T, "Mars orbit → Earth", equip_carried=2,
          note="a pre-positioned hypergolic return stage; Earth aerobrake free")
    m.note("Mars Direct / split-mission, no ISRU: the answer to 'can we do it without making fuel on "
           "Mars?' — yes, by sending the return vehicle ahead on a cheaper uncrewed window.")
    M.append(m)

    # 10. A 1970s uncrewed Mars probe — Viking-class, deliver 1 instrument to the surface.
    m = Mission("1970s Mars probe (Viking-class) — deliver 1 equipment to the Martian surface",
                required_dv=SEG["surface->LEO"] + LEO_TO_MARS)  # aerobrake descent free
    m.add("HEAVY KEROLOX BOOSTER", T("HEAVY HYDROLOX CORE"), "surface → +4")
    m.add("HEAVY HYDROLOX CORE",   T("HEAVY HYDROLOX UPPER"), "+4 → LEO")
    m.add("HEAVY HYDROLOX UPPER",  T("HYPERGOLIC TRANSFER STAGE"), "LEO → Earth Escape")
    m.add("HYPERGOLIC TRANSFER STAGE", EQUIP_T, "Earth Escape → Mars (injection)", equip_carried=2,
          note="1 science instrument; capsule/heat shield ride free, aerobrake to surface")
    m.note("70s chemical tech lands a light robotic payload on Mars — no nuclear, no refuel. NOTE: "
           "modeled on a Saturn-class stack because the deck lacks a Titan-class hypergolic booster; "
           "the real Viking flew on the smaller Titan IIIE-Centaur, so this over-states the rocket "
           "needed. The point stands: the uncrewed probe path is wide open — it's CREWED Mars that's hard.")
    M.append(m)

    return M

def analysis_refuel():
    """Refuel one Starship in LEO, per the rules: park an EXPENDED Starship (no reuse),
    then fly tankers until you've delivered its full propellant load (total - dry).
    Tanker deliverable is read off the Starship push-strip — the cargo it can ferry to
    LEO while still making the dv to get there (Super Heavy supplies the rest)."""
    ss, sh = ENGINES["STARSHIP"], ENGINES["SUPER HEAVY"]
    target = ss["total_mass_t"] - ss["dry_mass_t"]          # full propellant to replace
    sh_dv = dv_round(sh, ss["total_mass_t"])                # Super Heavy lifting a full Starship
    need = SEG["surface->LEO"] - sh_dv                      # Starship must add this to reach LEO

    def max_strip_cargo(dvreq):
        return max((r["cargo_t"] for r in ss["strip"] if r["dv"] >= dvreq), default=0)

    dump = max_strip_cargo(need)        # tanker spends everything to just reach LEO
    rendez = max_strip_cargo(need + 1)  # tanker keeps 1 dv for rendezvous/circularization
    flights_dump = math.ceil(target / dump) if dump else None
    flights_rendez = math.ceil(target / rendez) if rendez else None
    return {
        "super_heavy_dv": sh_dv, "starship_need_dv": need, "target_refuel_t": target,
        "dump_deliverable_t": dump, "flights_dump": flights_dump,
        "rendezvous_deliverable_t": rendez, "flights_rendezvous": flights_rendez,
    }, None

# =============================================================================
# ORCHESTRATION
# =============================================================================
def compute():
    audit = run_audit()
    missions, problems, findings = [], [], []
    for m in build_missions():
        result, prob, fnd = m.evaluate()
        missions.append(result)
        if prob:
            problems.append(prob)
        if fnd:
            findings.append(fnd)
    refuel, rfind = analysis_refuel()
    if rfind:
        findings.append(rfind)
    problems += [f"{p['card']}: {p['msg']}" for p in audit["problems"]]
    return {
        "game": DATAJSON.get("game", "Triskelion"),
        "model": "displacement (chain) — dv = ve·ln(total/(dry+cargo))",
        "audit": audit,
        "missions": missions,
        "analysis": {"refuel": refuel},
        "findings": findings,
        "problems": problems,
        "ok": len(problems) == 0,
    }

# ---- terminal rendering -------------------------------------------------------
def _tty():
    return sys.stdout.isatty()
def col(s, code):
    return f"\033[{code}m{s}\033[0m" if _tty() else str(s)
def render_terminal(R):
    B = lambda s: col(s, "1")
    P, F, W = col("PASS", "32"), col("FAIL", "31"), col("WARN", "33")
    bar = B("=" * 78)
    print(bar); print(B("  NUMBERS AUDIT")); print(bar)
    a = R["audit"]
    for p in a["problems"]:
        print(f"  {F} {p['card']}: {p['msg']}")
    for w in a["warnings"]:
        print(f"  {W} {w['card']}: {w['msg']}")
    if a["clean"]:
        print(f"  {P} all engine numbers consistent "
              f"({a['engines_checked']} engines, {a['strip_rows_checked']} strip rows recomputed)")
    if a["dry_token_drift"]:
        print(col(f"  note: {len(a['dry_token_drift'])} cards round dry mass to nearest tokens "
                  f"(expected — dry mass is a sub-ladder dial).", "2"))
    print()
    print(bar); print(B("  MISSION PLAYTHROUGHS")); print(bar)
    for m in R["missions"]:
        print(B(f"  MISSION: {m['title']}"))
        for b in m["burns"]:
            if b["ignition_warning"]:
                print(f"      {W} first stage {b['engine']} ignition='{b['ignition']}' — cannot light at sea level")
            mark = {"parallel": "∥", "subgrid": "·", "fixed": "·", "serial": " "}[b["mode"]]
            cargo = f"cargo {b['cargo_t']:>5.0f}t" if b["cargo_t"] is not None else " " * 11
            dv = "—" if b["dv"] is None else f"{b['dv']:>2}"
            print(f"      {mark} {b['engine']:<24} {cargo}  → {dv} dv   "
                  + col(f"{b['leg']}" + (f"  ({b['note']})" if b['note'] else ""), "2"))
        sign = "≥" if m["closes"] else "<"
        crew = (col(f"   | crew: {m['transit_months']}mo → {m['consumable_cards']} Consumables card(s)", "2")
                if m["crew"] else "")
        print("      " + "-" * 60)
        print(f"      TOTAL {m['total_dv']} dv {sign} required {m['required_dv']} dv{crew}")
        for n in m["notes"]:
            print(col(f"      note: {n}", "2"))
        vmap = {"PASS": P, "FAIL": F, "correctly-short": P, "INVARIANT-BROKEN": F,
                "closes": "closes", "falls-short": "falls short"}
        print(f"      VERDICT: {vmap.get(m['verdict'], m['verdict'])}")
        print()
    rf = R["analysis"]["refuel"]
    print(B("  ANALYSIS: Starship LEO refueling"))
    print(f"      Park an EXPENDED Starship in LEO, then refill its {rf['target_refuel_t']:.0f}t "
          f"propellant load (total − dry).")
    print(f"      Super Heavy gives {rf['super_heavy_dv']} dv lifting a full Starship; each tanker "
          f"Starship must add {rf['starship_need_dv']} dv to reach LEO.")
    print(f"      Tanker dumps everything to just reach LEO → {rf['dump_deliverable_t']}t/flight "
          f"→ {col(rf['flights_dump'], '1')} flights.")
    print(f"      Tanker reserves 1 dv for rendezvous/dock → {rf['rendezvous_deliverable_t']}t/flight "
          f"→ {col(rf['flights_rendezvous'], '1')} flights.")
    print(col("      (SpaceX floats ~15 — lands in this band once rendezvous margin is counted.)", "2"))
    print()
    print(bar); print(B("  SUMMARY"))
    if R["findings"]:
        print(col("  DESIGN FINDINGS (judgment calls — not bugs):", "33"))
        for fnd in R["findings"]:
            print(f"        • {fnd}")
        print()
    if R["problems"]:
        print(f"  {F}  {len(R['problems'])} hard issue(s):")
        for p in R["problems"]:
            print(f"        - {p}")
    else:
        print(f"  {P}  numbers audit clean and all hard invariants hold.")
    print(bar)

def main():
    R = compute()
    render_terminal(R)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(R, f, indent=2)
    print(col(f"\n  wrote {os.path.relpath(OUT_JSON, HERE)}", "2"))
    sys.exit(0 if R["ok"] else 1)

if __name__ == "__main__":
    main()
