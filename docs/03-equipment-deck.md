# 03 — Equipment Deck

16 equipment cards, sub-token mass (~2.5t each), carried by engine cards with `equipment_carry` capacity.

## Categories (with tech labels)

### Crew / Life Support (C-tier)
- **C1 — Crew Capsule**: Basic space for 4 people. Required for crewed missions.
- **C2 — Crew Habitat**: Long-stay module for 4 people. Place in orbit for a station; add cargo tokens to expand.
- **C3 — Greenhouse**: Produces 1 consumable per month. Surface only. Requires power.

### Power (P-tier)
- **P1 — Solar Array**: Power source for ion engines, greenhouses, ISRU refineries. Loses output past Mars and at lunar poles.
- **P2 — RTG (Radioisotope Thermoelectric Generator)**: Power source that works anywhere, including deep space and lunar poles. Heavier than Solar Array but immune to dust storms and night.

### Science (Sc-tier)
- **Sc1 — Science Package**: Instruments. Scores science objectives.
- **Sc2 — Large Antenna**: High-gain dish. Required for deep-space science missions to transmit data home.
- **Sc3 — Sample Container**: Holds material for sample-return missions. Must return to Earth.

### Mobility (Mb-tier)
- **Mb1 — Rover**: Surface mobility. Scores exploration objectives.
- **Mb2 — Landing Gear**: Enables controlled touchdown on a surface (no atmosphere needed). Replaces Atmospheric Return on airless bodies.
- **Mb3 — Atmospheric Return**: Heat shield + parachute. Enables atmospheric re-entry and soft splashdown. Aerobrake counts as free.

### Ascent (L-tier, paired with L1 lander engine)
- **L2 — Light Ascent Engine**: Tiny hypergolic ascent stage. 2 Dv lifting 1 equipment card (~2.5t). Single use.

### ISRU (R-tier)
- **R1 — Hydrolox Refinery**: Electrolyzes water ice into hydrogen + oxygen. Deploy on Moon or Mars surface. Rotate once per turn; on 4th rotation gain one free hydrolox tank token. Requires power.
- **R2 — Methalox Refinery**: Sabatier reactor. Combines CO2 + H2 into methane + oxygen. Deploy on Mars surface only. Rotate once per turn; on 4th rotation gain one free methalox tank token. Requires power. Stable propellant — no boil-off.

### Single-use / no tier
- **Cn — Consumables**: Holds 4 consumables (food for 4-person crew × 4 months). Rotate card 90° per consumable used.
- **Bn — Burner Engine**: Single 1-Dv burn for a craft ≤10t (1 yellow). Single use. Models Apollo SPS short burns, BepiColombo chemical insertion, cubesat kick motors.

## Equipment carry rules (engines that carry equipment for free)

| Engine | Carries |
|---|---|
| Hypergolic Upper (Hp1) | 2 equipment cards |
| Hypergolic Transfer Stage (Hp2) | 2 equipment cards |
| Ion Engine (I1) | 2 equipment cards |
| Orbiter (Sh1) | 4 equipment cards |
| Starship (M2) | 4 equipment cards |
| Nuclear Engine (N1) | 4 equipment cards |
| Mars Ascent Vehicle (Hp3) | 4 equipment cards |

Equipment carry capacity is separate from the propellant bay. Equipment rides along free, does NOT enter the rocket equation. Reflects real spacecraft adapters where instruments mount in cubbies separate from propellant tanks.

## Rotation indicators

Three cards have rotation tracker overlays:
- **Consumables**: counts DOWN. Each rotation = 1 consumable used. 100% / 75% / 50% / 25%
- **Hydrolox Refinery / Methalox Refinery**: counts UP. Each rotation = 1/4 of next tank token produced. 1/4 / 2/4 / 3/4 / FULL

## Dropped from earlier versions

These existed and were dropped:
- Heat Shield + Parachute → merged into Atmospheric Return (Mb3)
- Comms Satellite → dropped (no remaining role; Large Antenna covers deep-space comms)
- Spy Satellite, Deep-Space Probe → dropped (Science Package + Solar Array suffices)
- Lander Legs → duplicated Landing Gear, dropped
- Nuclear Reactor → renamed to RTG (more accurate name)
