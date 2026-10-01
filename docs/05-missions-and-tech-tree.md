# 05 — Missions and Tech Tree

## The unified loop

Three game loops fold into one motion:
1. **Mission objectives** score VPs
2. **Tech progression** unlocks higher-tier cards
3. **Deck building** gradually adds those cards to the player's hand

Each mission objective is tagged with the **tech labels** it awards on completion. Completing missions both scores VPs *and* advances the player's tech trees.

## Tech labels

Each card has a `tech_label` (visible bottom-left of the silhouette). See `docs/02-engine-deck.md` and `docs/03-equipment-deck.md` for the full catalog.

Format: letter(s) for family, number for tier within family. K3 = "tier 3 Kerolox card." C2 = "tier 2 Crew card." Etc.

## Mission types and the tech they award (sketch — playtest to refine)

| Mission type | Example | Awards |
|---|---|---|
| Heavy lift to LEO | "Put 4 red tokens in orbit" | K-progression |
| Crewed lunar flyby | Apollo 8 analog | Hp-progression, C-progression |
| Crewed lunar landing | Apollo 11 analog | Hp3, L-progression, C-progression |
| Mars sample return | unmanned | Sc3, R1 unlock |
| Mars crewed colony | crewed multi-mission | Hp3, C3, R2 |
| Deep-space flyby | Voyager analog | I-progression, Sc2, P-progression |
| LEO station construction | ISS analog | C2, multi-launch |
| Space telescope | Hubble / JWST analog | Sc1, P1 or P2 |

The "completes 2 of these to unlock tier 2" mechanic is the cleanest framing. Specifics TBD.

## Unlock conditions (printed on engine cards)

> **Superseded (Sep 2026)**: see `docs/07-rules-v0.md`. Goal cards are double-sided (goal on the front, upgrade reward on the back), and that is the unlock system. FIRSTs are all face-up from the start; other missions sit in a 5-card market row.

See `docs/02-engine-deck.md` for the per-card unlock chain. Summary:

**Internal progression** for K, H, S, Hp:
- Launch with tier N → unlock tier N+1

**Cross-family** for M, N, I, MAV:
- M1: launch N tons to orbit (any fuel)
- M2: launch M1
- M3: launch M2
- Hp3 (MAV): launch Hp2 (CSM)
- N1: launch RTG to deep space
- I1: complete deep-space mission

## Mission card mechanics

### Constant vs transient cards (current direction)

The objective deck splits into two kinds:

- **CONSTANT cards** — a small set of persistent milestones: the **FIRSTs** (claimed once, gone) and **MOSTs** (held until surpassed, scored at endgame). These are the marquee, history-defining goals (First Orbit, First Crew on Mars, Largest Station). Few in number, always relevant.
- **TRANSIENT cards** — a large pool of **contracts and missions** dealt to a **refreshing open-market row**. Each is a **window of opportunity**: launch this mission or grab this contract *now*, before the row refreshes and it's gone. Many of them are near-duplicates with small parameter changes, so the deck stays varied without bespoke design per card.

This gives the early/mid game a steady stream of opportunistic income and goals, against the backdrop of the few big constant milestones everyone is racing toward.

### Contract templates (transient)

Recurring contracts are parameterized — same shape, small variations — e.g.:
- **Military contract:** "Deliver 10 tons to DV7. Don't ask questions." / "Deliver 1 equipment to orbit. Don't ask questions." Pays money + experience. The ICBM-era income engine: 8 dv is intercontinental-throw class, exactly what level-1 cards reach. (No real city names — "unnamed payload.")
- **Commercial contract:** telecom / GPS / tourism — "Put a comsat in orbit," "Loft a tourist to LEO." The **private growth path** (see below).
- **Science / probe missions:** mostly inspired by real flights — Voyager 1 & 2, Mariner, Venera, Viking, Mars rovers, Mercury/Gemini — mapping onto the FLYBY and deep-space objective types (deliver an instrument to +N dv).

### Two growth paths: military and commercial

A player does **not** need military contracts to grow. There are two viable income engines:

- **Military:** ICBM-class throw (DV7-8) and defense payloads. Available earliest (level-1 cards do it).
- **Commercial:** telecom, GPS, space tourism. Requires reaching **orbit** with a light payload — which **K2 (Falcon 9 / R-7 / Atlas) + 1 equipment = 9 dv** delivers (validated in `src/playtest.py`, "Commercial launch"). K2 lofts ~1 equipment-scale payload (~2.5-5t) to LEO — enough for comsats, GPS, smallsats, a tourist capsule. Heavier or GEO commercial needs an upper stage or K3. (Caveat: K2 sits at the R-7/Soyuz end of its heritage; real Falcon 9 lifts ~22t, so the generic card under-represents the heaviest commercial lift — a tuning note, not a blocker.)

### Selection / scoring (still open)

How players draw, claim, and score remains open. Sketched:
1. **Open market**: face-up cards anyone can claim. First to complete wins.
2. **Personal mission**: each player has 2-3 secret objectives.
3. **Hybrid**: 1-2 personal + 3-4 open market.

Recommend hybrid, with the transient contract row as the shared open market and the constant FIRSTs as the racing spine.

## Filler contract cards (12, June 2026 — expendable)

The first batch of TRANSIENT contracts exists as 12 carded fillers occupying the spare slots of the second equipment sheet (gold MISSIONS backs via a mixed back sheet, so they shuffle into the mission deck when cut). Marked **`"filler": true`** in `data/objectives.json` — that flag is the "this is expendable" ink: **if a future layout needs the space, cut these first.** Three flavors, 4 each:

- **COMMERCIAL (teal, $ icon):** Comsat (1 eq to LEO), GPS Constellation (3 eq, one launch — the Equipment Bundle ×3 hook), TV Broadcast (1 eq to GEO), Orbital Tourist (capsule up and safely back).
- **MILITARY (olive, shield):** suborbital ballistic throws, "Don't ask questions" — 10t@DV5, 20t@DV6, 10t@DV7, 40t@DV8. No real place names; unnamed payloads.
- **SCIENCE (indigo, atom):** Weather Watch (TIROS — Science Package in LEO, 4 turns), Halley Armada (escape +2), Solar Probe (escape +4, needs Atmospheric Return as heat shield), Ice Moon Survey (escape +6, needs RTG).

## Machine-checkable goals (Sep 2026)

22 of the 28 goals carry a `check` in `objectives.json`, which the table prototype evaluates after every move, equipment load and end of turn. Fields (all optional, all must hold): `at` (space ids), `deep` (deep-space ladder rung ≥ N, i.e. "escape + N Dv"), `visited` (spaces the mission flew through earlier: "go there, then return"), `equip` (equipment names aboard), `without` (e.g. no Crew Capsule = robotic), `equipCount` (non-crew equipment: a Crew Capsule is not a comsat), `cargo` (tons of tokens aboard), `turns` (turns parked at `at`). Military "DVn" = ascent space aN (pays on delivery, even mid-climb). MOST / RESCUE / ENDURANCE goals have no check yet. When a goal is met the camera glides to the goal row; clicking the glowing card claims it (it moves to your Space Center's completed-goals spot, its stars are added, the market refills from the missions deck).

## VP-scoring conventions (current objective deck)

The 16-card objective deck has 5 categories (colors):
- **FIRSTS (gold)** — first to achieve milestone wins ALL points; others get 0
- **MOSTS (blue)** — player with the most of X at endgame wins
- **FLYBYS (purple)** — flyby objectives, any player can claim independently
- **RESCUE (red)** — opportunistic; complete when someone else's mission fails
- **ENDURANCE (green)** — long-duration objectives (station up X months, etc.)
- **International Station** — cooperative mechanic; multiple players contribute

## Endgame trigger

Open. Options:
- N total VPs reached by any player
- All FIRSTS claimed
- Fixed number of turns (e.g., 30 = simulates 30-year space program)
- Mars colony established (programmatic endgame)

## Faction asymmetry (open)

Open question: do players start with identical decks, or do factions (NASA, Soviet, SpaceX, ESA, CNSA) have different starting cards / different goal priorities?

Asymmetric factions deepen replay but make balancing harder. Symmetric is simpler to design but flatter. Recommend symmetric for first playtest cycles, add factions after core mechanics stabilize.
