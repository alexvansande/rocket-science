# 02 — Engine Deck

24 engine cards, organized as heritage + two-precursor tech tree.

## Heritage + two-precursor model

Each fuel family has a **heritage top card** representing a famous historical stage AS FLOWN (Saturn V S-IC, Saturn V S-II, Starship booster, Shuttle SRB, Apollo CSM). Below each heritage card sit **two precursors**, sized roughly 4× and 16× less powerful.

Where a smaller heritage card naturally sits at the right rung (Saturn V S-IVB at one-quarter of S-II), use it. Where no historical hardware fits, use a **generic-named card** with a historical footnote — never use names like "Merlin" or "Falcon" because that would make Saturn V depend on a 2010-era engine (anachronism). The footnote lists the real hardware that inspired the card.

**Falcon 9, Atlas V, etc. are OPERATIONAL/COMMERCIAL, not HERITAGE.** They serve as inspiration for generic cards (e.g., Kerolox Booster's footnote mentions Falcon 9 / R-7 / Atlas V), but the cards don't bear their names. This keeps the deck era-neutral.

## Tech labels

Every engine card has a tech_label visible bottom-left of the silhouette:

| Label | Engine | Mass | Heritage |
|---|---|---|---|
| **K1** | Kerolox Sustainer | 160t | Atlas-Mercury class (generic) |
| **K2** | Kerolox Booster | 480t | R-7 / Soyuz / Falcon 9 / Atlas V first stage (generic) |
| **Ku** | Kerolox Upper | 120t | Falcon 9 2nd stage (Merlin Vacuum) / Soyuz Blok-I |
| **K3** | Heavy Kerolox Booster | 2560t | Saturn V S-IC (5× F-1) |
| **K4** | Nova | 3,840t (6×⬛) | NASA Nova C8 (1959-62), 8× F-1 direct-ascent |
| **K4** | Sea Dragon | 16,000t (25×⬛) | Truax/Aerojet Sea Dragon (1962), sea-launched |
| **H1** | Hydrolox Upper | 30t | Centaur / DCSS / Ariane upper (generic) |
| **H2** | Heavy Hydrolox Upper | 120t | Saturn V S-IVB (single J-2) |
| **H3** | Heavy Hydrolox Core | 480t | Saturn V S-II (5× J-2) |
| **H4** | Super Hydrolox Upper | 2560t (4×⬛) | Sea Dragon 2nd stage (generic pressure-fed) |
| **M1** | Methalox Booster | 320t | Vulcan / New Glenn / Zhuque-2 (generic) |
| **M2** | Starship | 1920t | Starship upper (6 Raptor) |
| **M3** | Super Heavy | 3840t | Starship booster (33 Raptor) |
| **Hp1** | Hypergolic Upper | 10t | Aestus / AJ10 / RCS quads (generic) |
| **Hp2** | Hypergolic Transfer Stage | 40t | Apollo CSM / Briz-M |
| **Hp3** | Mars Ascent Vehicle | 20t | NASA DRA 5.0 MAV (methalox, but heritage of CSM) |
| **S1** | Solid Kick Motor | 40t | Star-48 apogee motor |
| **S2** | Light Solid Booster | 160t | Atlas / Delta strap-ons (generic) |
| **S3** | Heavy Solid Booster | 640t | Shuttle SRB / Ariane 5 / SLS |
| **N1** | Nuclear Engine | 80t | NERVA (US) / RD-0410 (USSR) |
| **I1** | Ion Engine | 20t | Hall thruster (Soviet SPT) |
| **L1** | Light Descent Engine | 10t | Apollo LM descent stage |
| **Sh1** | Orbiter | 80t | Space Shuttle orbiter (3× SSME) |
| **Sh1** | Hydrolox Drop Tank | 640t | Space Shuttle external tank |

## Ignition tags

Each engine has an `ignition` field showing where it can ignite (vocabulary normalized June 2026 — `earth` / `both` / `space` / `mars-surface`, nothing else):
- `earth` / `both` — can light at sea level (most boosters, methalox engines, solid boosters). `both` also restarts in vacuum.
- `space` — vacuum-only; cannot ignite in atmosphere (most upper stages, NERVA, ion, in-space hypergolics)
- `mars-surface` — designed to ignite from Mars surface (currently just the MAV)

Card badges: GND / G+S / SPC / MARS (rendered by `IGN_LABEL` in `build_kit.py`).

**Implicit rule:** an engine's first stage must be tagged for the launch surface. This is enforced by the data, not by a hard rule — the card's tag tells the player where it lights.

**The tag also encodes "can this be a first stage" — including thrust-to-weight, not just ignition altitude.** The displacement model tracks *ideal Δv only*; it has no concept of thrust-to-weight (see `docs/01`). So a high-mass-ratio upper stage like **Starship** would *look* like a single-stage-to-orbit on its strip (Starship + 80t ≈ 9 dv). In reality it can't: fully fuelled, Starship's T/W ≈ 0.9 — it can't leave the pad, which is the whole reason Super Heavy exists. We model that limit by tagging Starship **`space`** (it must ride a booster off Earth), even though its Raptors *do* fire at sea level. So `space` reads as "**upper stage — not an Earth first stage**," whether the reason is vacuum-only ignition (NERVA, hydrolox uppers) or thrust-to-weight (Starship).
- **Exception, by physics:** Starship *can* lift off from **Mars/the Moon** (low gravity → T/W > 1) — the Mars-return architecture needs this. The `space` tag is about *Earth* liftoff; surface launches from low-gravity bodies are allowed (the playtest models Starship's Mars ascent directly).

## Unlock mechanic (provisional — superseded)

> **Superseded (Sep 2026)** by `docs/07-rules-v0.md`: unlocks now come from **double-sided goal cards** (the reward is printed on the back) and **launch pads by mass**. The chain below is kept as history and as a source of reward ideas.

Each card prints a `Requires` line. Players start with TIER 1 cards only and unlock higher tiers through play.

**Internal progression** (Kerolox, Hydrolox, Solid, Hypergolic):
- Launch successfully with tier N → unlock tier N+1 cards
- K1 launch → K2; K2 launch → K3; same pattern for H, S, Hp

**Cross-family unlocks** for leap-tech families:
- **M1 (Methalox Booster)** unlocks when player launches N tons (TBD by playtest) to orbit using any fuel
- **Hp3 (Mars Ascent Vehicle)** unlocks after a successful Hp2 (CSM) launch
- **N1 (Nuclear Engine)** unlocks by launching an RTG to deep space
- **I1 (Ion Engine)** unlocks by completing any deep-space mission

**Fixed-function cards** (no progression):
- L1 (Light Descent) — lander, no precursor required
- Sh1 (Orbiter + Drop Tank) — the Shuttle pair. The Orbiter only flies on the tank; the tank pairs with **any** hydrolox engine (see below).

## Drop Tank pairing — any hydrolox engine (ruling, June 2026)

The **Hydrolox Drop Tank** has no engines of its own. The rule: **a HYDROLOX engine card riding directly above the tank burns the tank's fuel** — the tank's strip is the burn, the engine above legalizes it. It is NOT locked to the Orbiter:

- **Orbiter + Drop Tank** = the Space Shuttle (the original pairing).
- **2× Heavy Solid Booster + Drop Tank + Hydrolox Upper (H1)** = **SLS Block 1** — the Shuttle tank reused as the SLS core, with the H1 (whose heritage is literally the DCSS/ICPS) burning it and then sending Orion translunar. Verified in `src/playtest.py`: Orion-class 10t to lunar orbit, 14 vs 13 dv required. No new "tiny hydrolox engine" card was needed — H1 is it.

`tower_search.py` enforces the same rule (a tank is only a legal stage when a hydrolox engine sits directly above it), so the tank's strong showing in the tower analysis reflects the actual card rule.

## Special rules per family

**Solid engines (S1, S2, S3):** must spend full Dv in one turn. No partial burns, no take-back, no two-burn sequencing. This mirrors real physics: solid motors can't be throttled or shut off once lit.

**Ion engines (I1):** capped at 1 Dv per turn. Lifetime cap ~15 Dv total. Models the slow accumulation of an electric propulsion thruster.

**MAV (Hp3):** refuelable from Mars-surface Methalox Refinery. Aerobrake-descend from Mars orbit free with Atmospheric Return. Single ascent use.

## Sea Dragon (K4 + H4) and super-heavy first stages

There are **two K4 super-heavies** — peers at the top tier, two philosophies of "bigger than Saturn":

- **K4 Nova** (card name: "Super Heavy Kerolox Booster") — kerolox, **3,840t (6×⬛)**, Isp 263, the real NASA *direct-ascent* super-Saturn (8× F-1 vs Saturn's 5). Conventional clustered-engine land launch; unlocks normally (launch a K3). Pairs with a hydrolox upper for ~120-150t to LEO — "Saturn-plus." Dropped historically when Lunar-Orbit-Rendezvous made Saturn V sufficient — a mission-mode decision, not engineering. **Note:** the playtest shows Nova lifting a *Saturn-sized* core buys nothing over Saturn V (same 4 dv) — that's fine and intended. A big rocket only pays off when you load it heavier; letting players discover that for themselves is the lesson, not a bug.
- **K4 Sea Dragon** — the giant below.

**Sea Dragon** is the honest answer to "I want way *more* lift than even Nova" — a single monstrous purpose-built vehicle, not a pile of strapped boosters (the real Truax/Aerojet 1962 sea-launched "big dumb booster"). Two cards, a fixed pair:

- **K4 Sea Dragon** — kerolox first stage, **16,000t (= 25 black tokens)**, Isp 263, pressure-fed. Carries the H4 upper (2,560t) → 4 dv.
- **H4 Super Hydrolox Upper** — hydrolox upper, 2,560t, Isp 420. Carries ~550t payload → 5 dv.
- Stack: **9 dv → ~550t to LEO**, reproducing the real vehicle (≈4× Saturn V).
- Unlock: `Requires Sea launch` (a launch-*site* gate, TBD — not a tier unlock; ties to the stage-0 / launch-site open thread).

**Big first stages overflow the token grid, and that's fine.** Sea Dragon's first stage is 25 black tokens; on the card it prints compactly as **`25 × ⬛`** (and Super Heavy as `6 × ⬛`). Nobody ever *parks* a super-heavy first stage in orbit — black tokens only show up around DV3-4 — so the huge mass is just a number on the card; it never has to be laid out as physical tokens. (Rendering: `render_tokens()` in `build_kit.py` collapses any run of ≥5 identical tokens.)

**Clustering cap (the reason Sea Dragon exists as a card, not a strap-on):** you may use **up to 4× the same card** in one vehicle (4 black = 2,560t, the cargo-strip ceiling). Beyond 4, strapping isn't physically free — it needs a redesigned pad/tower/integration — so you must build a **bigger purpose-built rocket** (a new card) instead. See `docs/04` "Clustering, bundling, and the park rule."

## Staging the small launchers — Falcon 9 / Soyuz (K2 + Ku)

The kerolox family used to be all boosters (K1-K4) with no second stage — so K2 had to abstract a *whole* launcher into one card. That's now fixed with the **Kerolox Upper (Ku)** — the single Merlin Vacuum / Soyuz Blok-I class kerolox second stage. So the small launchers stage honestly, like Saturn V does:

- **Falcon 9 = K2 (9-Merlin first stage) + Ku (Merlin Vacuum)** → K2 lifts the upper (4 dv), Ku does orbital insertion (5 dv) → **~20-22t to LEO**.
- **Soyuz = K2 (stage-and-a-half) + Ku (Blok-I)** → same shape.
- The **first stage is the same card as Falcon 9's** — "if two cards are similar enough, keep them as one" (K2 = the 9-Merlin first stage *and* the R-7 core, generically).

**Why the R-7 is K2 + Ku, NOT three cards (boosters + core + Blok-I):** the 4 strap-on boosters and the central core are a **stage-and-a-half** — they all light on the pad and fire in *parallel*; the boosters drop at ~2 min while the core keeps burning. Parallel firing doesn't add dv serially (same rule as the Shuttle's 2 SRBs), so boosters+core collapse cleanly into **one** card (K2). The boosters were never a separate flown stage — they were expendable, dropped into the Kazakh steppe (and scavenged for scrap by locals), never recovered or reused. Only the Blok-I upper is a genuine *serial* second stage → the Ku card. (The Shuttle was split into separate SRB cards only because those are physically separate, reusable, *solid* hardware that maps to a generic card; the R-7's same-fuel strap-ons don't warrant that.)

## Suborbital vs orbital — the K1/K2 threshold

Reaching orbit (9 dv) is a tier-2 milestone, not a starting capability — and the deck already supports this correctly:

- **K1 Kerolox Sustainer** (Atlas sustainer class) alone ≈ 7 dv → **suborbital only**: a ballistic-missile lob ("bomb London", V-2) or a suborbital crewed hop (Redstone/Shepard).
- **K2 Kerolox Booster** is the **R-7 / Atlas** — the first orbital rocket. Carrying a crew capsule **as a sub-grid equipment card (~2.5t)**, not a 10t cargo token, K2 makes **9 dv → orbit**. This is Sputnik / Gagarin / Glenn.

The key modeling rule: **early crewed capsules are equipment-scale (Vostok 4.7t, Mercury 1.4t — below the 10t token grid)**, so they ride as equipment, not as a yellow token. Don't nudge K1 to force tier-1 orbit; *First Orbit* is meant to be earned by teching up to the R-7. See `docs/06` principle 10 and the "First Orbit" mission in `src/playtest.py`.

## Resizing history

Cards that have been resized during design — note for context:
- Hydrolox Upper: 120t → 30t (now Centaur-scale; the 120t S-IVB role is Heavy Hydrolox Upper)
- Hypergolic Upper: 30t → 10t (Aestus scale, was too close to CSM at 30t)
- Light Solid Booster: 80t → 160t (proper precursor to Heavy Solid Booster at 640t)
- Methalox Booster: 640t → 320t (Vulcan/New Glenn scale, was too close to Starship)
- Heavy Kerolox Booster: tuned to Saturn V S-IC (2560t, 5× F-1)
- Heavy Hydrolox Core: tuned to Saturn V S-II (480t, 5× J-2)
- Light Descent: reduced to real LM mass (10t, 1 yellow)
- Dry-mass floor pass (June 2026, `dry >= total/16` — see docs/01): Super Heavy dry 200→320, Starship 80→120, Sea Dragon 800→1120, Solid Kick 2→2.5. K2 exempt (First Orbit knife-edge). All flown cards also gained `real_total_mass_t` (historical mass, printed as ~Nt beside the in-game rounding).
- Refuel-cleanliness pass (June 2026, fuel ≤2 token colours for total ≥ 320 — see docs/01): Starship dry 120→160 (refuel KKRRR), Super Hydrolox Upper dry 200→160 (refuel KKKRRR, dv-6 row became a clean RRR). K2 dry 40 re-tested and re-rejected (breaks First Orbit / Commercial / Falcon 9).

## Dropped cards (do not re-add)

These existed in earlier versions and were dropped during the deck restructure. They are duplicates or have no role in the precursor model:
- Hydrolox Booster (320t Delta IV) — duplicates Heavy Hydrolox Upper at smaller scale
- Hydrolox Core (480t Ariane EPC) — duplicates Heavy Hydrolox Core (Saturn S-II)
- Solid Booster (640t generic) — duplicates Heavy Solid Booster
- Light Solid Engine (80t Vega) — duplicates Light Solid Booster after its resize
- ~~Kerolox Upper (120t Soyuz Blok-I)~~ — **RE-ADDED** as Ku (the precursor path needed it: it's the Falcon 9 / Soyuz second stage; see "Staging the small launchers" above)
- Hypergolic Booster (480t Proton) — Soviet 1st-stage hypergolic; dropped for now
- Methalox Upper (320t) — collapsed into Methalox Booster
- Light Ascent Engine (engine version) — moved to equipment deck

If a future session wants to re-add any of these, check whether the precursor path actually needs them first.
