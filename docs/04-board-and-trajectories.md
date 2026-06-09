# 04 — Board, Dv Map, and Trajectories

The physical board is Alex's responsibility (designed separately from the card kit). This doc records the conventions the cards assume.

## Spiral form (current — "Earth to Mars" dual loop)

The current board (`files/board art/earth to mars.pdf`) is a **dual loop**: an Earth spiral and a Mars spiral, joined through a shared central **Deep Space Trajectory** ladder.

- **Earth spiral** (right): Earth → Kármán Line → Low Earth Orbit → Geostationary Orbit, spiraling outward. Innermost turns (Kármán → surface) are the free-aerobrake re-entry zone (blue).
- **Moon stopover** (top): a small loop off Earth Escape — Earth Escape → Lunar Orbit → Moon. Lunar orbit sits essentially at Earth Escape energy (physically honest, not a simplification). No aerobrake anywhere on it — airless, so heatshields are dead weight here.
- **Mars spiral** (left): Mars → Mars Orbit, with Phobos and Deimos as nodes on the orbit ring.
- **Deep Space Trajectory ladder** (center): a linear dv ruler (+1, +2, …) bridging the two loops. **Effectively infinite — as long as we need.** This is the abstraction layer for *any* destination: Venus, Jupiter, Pluto, an asteroid, become "deliver this equipment to +N deltav" missions without drawing a dedicated map for each.

### Three crossing types (board legend)

Every boundary on the board is one of three crossing types:

- **Gray bar — burn to cross, either direction.** Costs dv. The default.
- **Blue dashed — down for free if you have heatshields.** Aerobrake descent; requires an Atmospheric Return card. Earth re-entry and Mars descent only.
- **Green — skip a turn to cross.** Trades a *turn* (and the consumables/time it costs) instead of dv. Used on the slow trajectories.

(The red/orange hatched segment on the inner Mars spiral is **purely aesthetic** — no special rule.)

## Dv budgets

| From → To | Dv |
|---|---|
| Earth surface → LEO | 9 |
| LEO → Earth Escape | 3 |
| Earth Escape → Lunar Orbit | 1 (essentially the same node) |
| Lunar Orbit → Lunar Surface | 2 |
| Lunar Surface → Lunar Orbit | 2 |
| Earth Escape → Mars Orbit | 3 (slow) / 4 (medium) / 5 (fast) — see "Three ways to Mars" |
| LEO → Mars Orbit (cheap, slow route) | 6 (= 3 to Earth Escape + 3 slow transit) |
| Mars Orbit → Mars Surface | 3 (propulsive) or 1 (with Atmospheric Return) |
| Mars Surface → Mars Orbit | 4 |
| Lunar Orbit → Mars Orbit | 4 |

## Three ways to Mars (the central tradeoff)

The deep-space ladder gives players a **spectrum of trajectories to Mars**, trading dv against time. The mechanic is the source of truth; the fast/medium/slow framing is just its consequence.

**The rule.** Costs are paid on the **intervals between** squares, not on the squares themselves.

- **Leaving Earth Escape always costs 1 dv** (the departure burn — paid no matter how you travel).
- **Interval 1:** 1 dv  **OR**  skip a turn + 4 consumables
- **Interval 2:** 1 dv  **OR**  skip a turn + 2 consumables
- **Intervals 3 & 4:** 1 dv **AND** skip a turn **AND** 1 consumable (no choice — these are forced)

So intervals 1 and 2 are the dials. Burn through them (pay dv) for the fast trip; coast them (skip a turn, eat consumables) for the slow trip. Intervals 3 and 4 always cost all three.

**Resulting spectrum** (crewed):

| Route | Choice on intervals 1 & 2 | Dv | Turns | Months |
|---|---|---|---|---|
| **Fast** | burn both | 5 | 3 | 3 |
| **Medium** | burn one, coast one | 4 | 4 | 4–6 |
| **Slow** | coast both | 3 | 5 | 8 |

**Uncrewed craft pay no consumables.** For a probe, "skip a turn" is purely a tempo cost — it exists only so the player who spent the dv to go fast actually arrives first.

## Clustering, bundling, and the "park" rule

Two different things people conflate — keep them separate:

- **Repeat a launch ×N (bundling):** N launches delivering a payload to a node is identical to one launch of N× the payload — *if the node can be parked on*. So a player may **declare "run this launch ×N" as a single action** rather than taking N repetitive turns (refuelling a Starship is ~15 launches — nobody wants 15 turns). This is normal and expected. It only works at a **parkable node** (a *circle*): you can accumulate payload there across turns, then combine and continue. This is real — orbital assembly, depot refuelling.
- **Cluster N rockets into one vehicle:** strapping boosters together is NOT free — it needs the pad, tower, hold-downs, and integration redesigned. So it's **capped: you may use up to 4× the same card in one vehicle; beyond that you need a bigger purpose-built rocket** (a new card). "Just build crazy bigger rockets" is the honest path — see **Sea Dragon** (`docs/02`), which is what a 6-Heavy-Kerolox strap-on *would* be if you welded it into one hull and sea-launched it.

  **Clustering is now carded — Rocket Bundle cards** (on the rocket pages, red ROCKETS back). A ×N bundle clips onto one rocket and flies it as **N identical rockets: it carries N× its cargo at the same dv**, and the stage beneath must lift N× its total mass. (The math: N rockets have N× wet, N× dry, N× cargo — the N cancels in `ve·ln(N·total/(N·dry + N·cargo))`, so dv is unchanged and only the cargo scales.) The set is a triangle — bigger classes bundle less freely: **Black (K) ×2 only; Red (R) ×2/×4; Orange (O) ×2/×4; Yellow (Y) ×2/×3/×4** (8 cards). Black caps at ×2 because a ×3–×4 super-heavy is already Sea-Dragon/Nova territory. You match the bundle's colour to the rocket's weight-class band. `tower_search.py` **respects these carded multipliers** — it reads `ALLOWED_MULTS` from `data["bundles"]` (keyed by the rocket's leading token) instead of free 1–4× clustering. The carded cap is what tames the absurd ceiling: with black capped at ×2, the theoretical dv ceiling falls from 33 dv / 110,000 t (free clustering) to **30 dv / 55,000 t**, and the cheapest crewed Mars-return rises from ~3,850 t to ~5,210 t (no ×3 on the heavy stages).

**Why the asymmetry — you cannot park on the way up.** At a parkable node you can serialise across turns (deliver, park, deliver more, combine). But **liftoff is atomic**: you can't lift two red tokens to "DV1 over the ocean," leave them hovering, and add two more next turn before igniting the upper stage. The entire first-stage lift must close in one launch — which is the whole reason the Shuttle fires *both* SRBs together. So the first stage is the one place parallel boosters genuinely matter; everywhere parkable, parallel is just bundling.

**The board enforces this through node typing.** The recursive booster-pyramid ("16 boosters → 32 black at DV2 → 8 boosters → …") is only legal if the intermediate ascent rungs are parkable. Mark the low ascent rungs **non-parkable** (*triangle* / mid-action — can't end a turn there) and the pyramid is blocked on the climb to orbit: you must use real first stages. Past LEO, *circle* nodes let you accumulate freely. No new rule needed — just type the nodes.

### Do we need hard anti-bundle first-stage rules? — No (decided, parked)

We considered extra first-stage rules (e.g. a stricter cluster cap, or **bundle cards** you must own to cluster, with the **black-token/SUPER class capped at 2×** instead of 4×). The tower brute-force (`src/tower_search.py`) settled it:

- **The math already self-limits the absurd towers.** The max-dv ceiling is a joke stack of bundled Sea Dragons — **~109,500 t of rocket to deliver a 10 t payload for 33 dv** (six Sea Dragons buy ~5 dv). Nobody builds that; you'd do multiple launches and assemble in orbit. Applying a 2× black cap only drops the (already absurd) ceiling from 33 dv / 110,000 t to 30 dv / 55,000 t — it changes nothing real.
- **The 2× black cap is NOT a balance fix; it's a play-style lever.** It does bite *practical* stacks (cheapest Mars round-trip 3,250 t → 4,690 t, +44%), by nerfing the efficient big first stage and nudging players toward multi-launch + orbital assembly.
- **The real lever is cost/money** (not yet built). Once a launch costs money scaled to mass/complexity, the giant towers are economically dead and orbital assembly wins on its own.

**Decision:** keep the plain 4× cluster cap; **no bundle cards, no anti-bundle rules for now.** Revisit the bundle-card idea (as deck-building texture, not balance) when the economy lands. The 2× black cap stays available as a dial if heavy first stages ever feel too cheap.

## Time is relative

Game time is **not a global clock**. A turn might represent months on a slow Hohmann coast or mere minutes on a launch. So-called "simultaneous" missions are not really simultaneous — each craft runs on its own trajectory time. Time enters the rules for exactly **two** things:

1. **Who got there first** — race tempo. The skip-a-turn mechanic exists so a player who pays dv to go fast actually arrives ahead of a slow coaster.
2. **How much food a crew needs to carry** — consumables tonnage.

Nothing else tracks absolute time. This is what lets the deep-space ladder stay abstract.

## Consumables and the time cost

- **1 Consumables card = 4 consumable units = 4 months of food for a crew of 3–4.** One unit (one 90° rotation) burned per month of mission time.
- Sized from NASA's ISS figure of ~4 kg/person/day. A 2.5t equipment card (the equipment-mass ceiling) holds ~4 months for 3–4 crew with margin for waste, packaging, and redundancy (raw number supports ~5).
- This is why the slow Mars route bites: 8 months = two full Consumables cards of tonnage the player must find room for, for the *whole* crew. An uncrewed probe ignores all of this.
- Refineries advance 1 step per month; Mars windows price off months (~7–8-month Hohmann).

## Mars descent

- Mars Orbit → Mars Surface: 3 dv propulsive, or **1 dv with Atmospheric Return** (aerobrake saves 2 dv).

## Aerobraking (free dv on descent)

- Requires **Atmospheric Return** equipment card (Mb3)
- Earth descent: LEO → surface = free (atmosphere does the braking)
- Mars descent: Mars Orbit → surface = saves 2-3 dv
- Lunar descent: no atmosphere, no aerobrake; must use Landing Gear (Mb2) + propulsion

## Free-return trajectories

The board geometry already encodes free returns. A craft that reaches Earth Escape without burning at Lunar Insertion can coast back to Earth and aerobrake home for 0 extra Dv. This is the Soviet Zond profile and Apollo 13's emergency return. **No special rule needed** — it's just a property of the map.

## Hydrolox boil-off rule

Liquid hydrogen boils off slowly. The rule (provisional):
- Transit losses are negligible (<5t even on Hohmann, below token grid)
- **Surface storage**: hydrolox tanks held on a surface >4 months lose 1 token per 4 months
- Methalox never boils off (storable at lower cryogenic temperatures)

This makes methalox strategically valuable for long-duration Mars surface missions and for ISRU production.

## Mars windows

Hohmann transfer windows open every ~26 months. Currently not enforced as a mechanic (would need a physical dial component). Open thread.

## Earth gravity loss

Listed dvs are *ideal* (the rocket-equation values). Real Earth-launch gravity losses are ~1.5 km/s, which are absorbed into the 9-dv LEO budget. Players don't track this separately — the board's printed budgets already reflect the historical real-flight requirement.
