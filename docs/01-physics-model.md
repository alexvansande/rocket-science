# 01 — The Physics Model (Displacement, not Additive)

## The one rule that matters

**Every engine card is a sealed delivery package with a fixed total mass.** The card has:
- `total_mass_t` — wet mass at ignition (locked, on the token ladder)
- `dry_mass_t` — empty-shell mass (locked)
- `fuel_mass_t` = total − dry — the payload bay's size (locked)

Inside the payload bay, the player chooses how much to fill with fuel vs cargo. The split is the only decision per engine.

**Formula:**
```
dv = ve × ln(total / (dry + cargo))
```
where `ve = Isp × 9.81 / 1000` (in km/s).

At `cargo = 0`, dv is maximized (full fuel load). At `cargo = total − dry`, dv = 0 (no fuel, doesn't move). Cargo cannot exceed `fuel_mass_t` — physically nowhere to put it.

## The model is IDEAL-Δv only (no thrust-to-weight, no sea-level Isp)

The strip computes the *ideal* rocket-equation Δv and nothing else. It does **not** model **thrust-to-weight** or the **sea-level vs vacuum Isp** drop. Consequences to accept (they're part of the ~10% abstraction, not bugs):
- A high-mass-ratio upper stage *looks* like an SSTO (Starship + 80t ≈ 9 dv) even though, fully fuelled, its T/W < 1 and it can't leave the pad.
- Landing/ascending a *heavy* vehicle looks as cheap as a light one (flat board dv), so e.g. a Saturn V can "direct-ascent" the heavy CSM in the model.

We don't model thrust — that would add real complexity for corner cases, and mechanical simplicity wins. Where a result is *too* wrong to permit, we lean on the **`ignition` tag** as the lever: Starship is tagged `space` so the rules forbid it as an Earth first stage (see `docs/02`). The numbers stay honest (the Δv is real); the rule just stops you using a lone upper stage where thrust would forbid it.

## THIS IS NOT THE ADDITIVE MODEL

Real-world mission planning uses:
```
dv = ve × ln((total + cargo) / (dry + cargo))    [NOT us]
```
where each stage carries the fully-fueled upper stack on top. Correct for designing rockets, requires recursive backward planning across the whole stack. A game cannot ask players to solve this every turn.

The displacement model is a forward lookup: pick a card, choose cargo, read dv. One question, one answer. Real cargo-to-rocket ratios are ~1:10, so the difference between the two models is roughly 10% — we trade that for the playability win.

**If a future Claude session tries to slip back into additive: refuse and re-read this section.** I have done it three times in past sessions and burned hours each time.

## The push strip

The strip is a pre-computed lookup table. For each token-clean cargo value within the payload bay, the strip lists the dv from the displacement formula rounded to the nearest integer.

Strip rows are capped at `cargo ≤ fuel_mass_t`. Stripe display caps at 9 rows on the card (more rows exist in JSON for engines with wide dv ranges).

**Lookup convention:** match cargo to the closest strip row. If cargo falls between two rows, compute `dv = round(ve × ln(total / (dry + cargo)))` directly using the card's printed Isp, dry, and total values.

## Strip generation algorithm (in `regen_strips.py`)

**Uses the displacement formula above.** (A past version of `regen_strips.py` used the *additive* form `ln((total+cargo)/(dry+cargo))` and referenced long-dropped cards — running it would have silently corrupted all 55+ strip rows. It has been rewritten to displacement and verified to reproduce the existing token rows exactly. Never reintroduce the additive form here.)

Token rows:
1. For each token-clean cargo value, compute `dv` and round to nearest integer.
2. Dedupe: keep heaviest cargo for each dv (eliminates useless rows).
3. Cap at `cargo < fuel_mass_t`.
4. If integer dvs are missing between min and max present rows, gap-fill with the largest 10t-grid cargo that rounds to the missing dv **and whose printed token layout uses at most TWO colours** (e.g. K RRR = 1,120t). **The ≤2-colour rule (June 2026):** rows needing 3+ colours (like the old `K RRR OOO YYY` = 1,270t on Heavy Kerolox) are forbidden — too many tokens to read at a glance, and the dv column gets pushed off the card. Cleanliness beats squeezing out the last few tons of cargo per row; the lookup convention (compute directly between rows) covers the gap.
5. Return empty list (not None) if no valid rows — this clears stale data when regenerating.

Equipment tail (below the 10t token floor):
6. Below one yellow token, the rocket carries only blue **equipment** cards (~2.5t each). Add rows for **3, 2, 1 equipment** (7.5/5/2.5t), computed with the same displacement formula.
7. Keep only equipment rows whose dv is **higher** than any token row, deduped by dv (largest cargo per dv). **Minimum 1 equipment** — a rocket always carries at least one payload card; it never flies empty.
8. These rows carry an `"eq": N` field and render as equipment pips, not tokens.

This is where the marginal missions live. **K2 (R-7) + a 10t token = 8 dv, but K2 + a sub-token capsule = 9 dv → orbit** (Gagarin/Glenn). The Apollo CSM's return burn and the LM's 2-dv landing both come from this regime. Light Descent, which had no token-scale rows at all, now prints `2eq→1, 1eq→2`.

## Refueling and dry-mass rounding

**The dry-mass FLOOR (June 2026): `dry >= total/16`, rounded up.** No stage may be lighter than 1/16 of its wet mass — both a realism guard (real stages run ~6%+ dry) and a token-cleanliness generator: when the total is 4 tokens of one colour, dry = total/16 is exactly **one token two rungs down** and max fuel is **3 big + 3 small** (Heavy Kerolox 2560 = 4K → dry 1R, fuel 3K 3R; Drop Tank 640 = 1K → dry 1O, fuel 3R 3O). For totals that aren't a power-of-4 multiple, the floor is the *minimum* — round dry up further if it buys cleaner refuel tokens (Super Heavy 3840 → dry 320 = RR, fuel 5K RR; Sea Dragon 16000 → dry 1120 = KRRR, fuel 23K R; Starship 1920 → dry 160 = R, fuel KKRRR; Super Hydrolox Upper 2560 → dry 160 = R, fuel KKKRRR). **Exemption: K2 stays at dry 20 (< its 30 floor)** — raising it even to 30 drops K2+capsule from 9 dv to 8 and kills First Orbit; at 40 it also breaks Commercial launch and Falcon 9 (verified three times now — do not retry). Intuition: dry mass is fuel you can't burn — mass still pushed at burnout — and the Gagarin burn runs the mass ratio down to dry+2.5t, so those 20t are exactly the margin that makes orbit. The card *prints* `D: O` as accepted display drift (the parenthetical shows the true 20t, same as the MAV's O-over-4t); the F refuel line stays the honest 460t = RROOOYY, since refuel must restore the real fuel load. Cards print the historical mass (`real_total_mass_t`, shown as *~Nt*) beside the in-game rounding.

**The refuel-cleanliness rule (June 2026, enforced by the audit):** for R-class-and-up cards (**total ≥ 320**), the refuel cost `F = total − dry` must lay out in **at most TWO token colours** with no sub-token remainder. Dry mass barely affects gameplay (it's a log argument), so spend it freely on this. Side benefit: a lighter/cleaner dry often turns ugly gap-fill strip rows back into pure ladder rows — dropping Super Hydrolox Upper's dry from 200 to 160 changed its dv-6 row from `440 = RROOO` to a clean `480 = RRR` automatically. Procedure when changing any dry: pick the clean value, run `regen_strips.py` + `playtest.py`, keep only if green.

To refuel a depleted stage in orbit, a tanker delivers **`fuel_mass_t = total − dry`** worth of matching tokens (the card's **F** row). Since `total` is token-clean and **`dry_mass_t` is just a tuning dial** (only Isp is sacred), round `dry` so the refuel cost lands on **few, large tokens** — a 9-token "3K 3R 3Y" refuel is fiddly at the table; "3K 3R 1O" is not. Rule of thumb: make `dry` a multiple of 40 (kills yellows in the refuel), ideally a multiple of 160 (kills oranges too). Always re-run `regen_strips.py` + `playtest.py` after — rounding `dry` nudges the dv rows.

Most cards are now rounded so the refuel cost has **no yellows** (Heavy Kerolox 160 → 3K 3R, Heavy Solid 80 → 3R 2O, Drop Tank 40 → 3R 3O, Methalox 40 → R 3O, etc.). **But dry mass is not infinitely free — some values are load-bearing and the playtest rejects rounding them.** Notably **K2 Kerolox Booster (dry 20) and K1 Kerolox Sustainer (dry 12) cannot be rounded up to 40** — they prop up the knife-edge *First Orbit* (K2 + capsule = exactly 9) and the suborbital ceiling. Small upper stages (Hypergolic Upper, Light Descent, Hydrolox Upper) also keep awkward dry masses because their totals are too small to round cleanly. **Always run `regen_strips.py` + `playtest.py` after any dry change** — the harness is the gate (`src/` has an optimizer pattern for this: try the clean value, keep it only if green).

## Equipment-carry rule

Blue EQUIPMENT cards are sub-token mass (~2.5t each). Some engine cards have dedicated compartments separate from the propellant bay that carry equipment for free. Printed on the card as `+ N equipment cards`.

Current values:
- **Hypergolic Transfer Stage, Hypergolic Upper, Ion Engine**: +2 equipment cards
- **Orbiter, Starship, Nuclear Engine, Mars Ascent Vehicle**: +4 equipment cards
- All others: 0 (or equipment carrying happens via cargo bay)

Equipment cargo does NOT enter the rocket equation. It rides along free.

## Sub-grid engines

Some engines are too small to interact with the 10t token grid. They carry equipment cards directly, with printed dv-per-equipment-cards rules:

- **Hypergolic Upper**: 0eq=6Dv, 1eq=3Dv, 2eq=1Dv. Single use.
- **Mars Ascent Vehicle**: 0eq=6Dv, 1eq=4Dv, 2eq=3Dv, 3eq=2Dv, 4eq=1Dv. Refuelable from Mars-surface Methalox Refinery.
- **Light Ascent Engine** (equipment, not engine): 2Dv lifting 1 equipment card. Single use.

## Reference build: Apollo 11

Use this to verify card calibration during playtest. Cards:
- Heavy Kerolox Booster (K3)
- Heavy Hydrolox Core (H3)
- Heavy Hydrolox Upper (H2)
- Hypergolic Transfer Stage (Hp2)
- Light Descent Engine (L1)
- Light Ascent Engine equipment (L2)
- Crew Capsule equipment (C1)
- Atmospheric Return equipment (Mb3)

**Cascade** (with current playtested cards):
1. Heavy Kerolox Booster carries 3 red (480t = Core mass) → 4 dv (surface → +4)
2. Heavy Hydrolox Core carries 3 orange (120t = Upper) → 5 dv (reaches LEO at 9)
3. Heavy Hydrolox Upper carries 1 orange (40t = CSM+LM) → 3 dv (reaches Lunar Insertion)
4. Hypergolic Transfer Stage carries 1 yellow (10t = LM) → 2 dv (LOI) + reserves 1 dv (TEI). Plus 2 equipment cards (Crew Capsule + Atmospheric Return).
5. Light Descent carries Light Ascent equipment to surface (2 dv). Light Ascent lifts crew back (2 dv printed).
6. CSM uses remaining 1 dv for TEI; Crew Capsule + Atmospheric Return aerobrakes home free.

Confirmed working in playtest (June 2026).

## Sanity check: single Saturn V and Mars (state this precisely)

The honest fact is **not** "a Saturn V can't reach Mars" — 1970s hardware *did* reach Mars (Viking, 1976). A stripped, one-way Saturn V shot *can* inject toward Mars orbit, and that is historically true: NASA could have flown a one-way probe — or, grimly, a one-way crewed suicide flyby. **If the board permits that, keep it — it's a true fact.**

What a single Saturn V **cannot** do is a **crewed Mars landing and return**. That mission has to carry, all at once: ~8 months of food for the crew (consumables tonnage), a descent stage, an ascent stage, and the propellant for the trip home (~12 dv round trip from LEO). The Apollo CSM (Hypergolic Transfer Stage) flown light has enough dv to *get there* but nowhere near enough to haul that payload and fund the return.

So the invariant the deck must honor is: **crewed Mars landing+return needs higher-Isp propellants (methalox, nuclear), LEO refueling, ISRU, or multi-mission architecture — not a single Saturn V.** Reaching Mars *orbit* one-way is allowed. (Verified by `src/playtest.py`: the round-trip mission correctly falls short; the one-way probe correctly closes.)
