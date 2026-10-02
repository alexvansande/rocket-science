# 10 — Pacing: the four phases (design brief)

Status: **direction from Alex, Oct 2026.** This is the *why* behind resources and costs. Every number in docs/09 (prices, science thresholds, rewards) should be judged against this doc, not set on its own. Items marked *proposal* are Claude's; **OPEN** needs a call.

## What we're solving

Resources exist for **pacing** and for **multiple paths**, not for their own sake.

- **Start simple, add rules as you go.** The first turns are a tutorial: how a rocket works, what Δv is, then a two-stage rocket.
- **Every mission is achievable, but you build up to it.** It should feel like a puzzle you solve for yourself. **Solo should be playable**; other players help or get in your way.
- **No single dominant line.** "Buy the biggest rocket and launch it" must never be the answer.
- **History is the path.** Each engine family grows the way it really did, and the big turning points of the space age show up as phases.

## The four phases

| Phase | Theme | Ends when | What the player is learning / deciding |
|---|---|---|---|
| **1. Learning to fly** | V-2 → Sputnik → Gagarin | someone reaches **First Orbit** | The rules. One stage, then two. How Δv and staging work. Zero science. A tutorial level. |
| **2. The Moon race** | Mercury → Gemini → Apollo | **First Moon Landing** (Armstrong) | *How* to get there, not *whether*: one big rocket (direct ascent), rendezvous in Earth orbit, refuel in orbit, lunar orbit rendezvous (split the craft, one crew member waits in orbit)… Real architecture choices, several of which work. |
| **3. Infrastructure** | Shuttle, Mir, ISS, the post-Apollo decades | **cheap access to orbit** (the SpaceX moment: a reusable rocket) | What to build: a Moon base first, or straight for Mars? Stations, networks, reusability. Choices from phases 1–2 start to matter. Politics bites: budget cuts, a collapsing program, buying a ride on someone else's rocket (NASA on Soyuz), cooperation (an international station). Some engineering turns out wrong (the Shuttle). |
| **4. Mars** | Starship era | the **endgame** (OPEN: something like a big Mars base / city, not first footprint) | A race again, using the infrastructure you built. Where you invested science decides who gets there first. |

## What each resource is for

- **Science = how far along history you are.** It moves you through the phases and opens tech families along their historical lineages (the tech labels already are those lineages: K1 → K2 → K3, S1 → S2 → S3, H1 → H2 …). *Where* you invest science is a strategic choice: it decides your route to Mars.
- **Money = how much you can fly and keep running.** More money, more launches. It is also what politics attacks: budget cuts, no launches this turn, decommission your station because you can't pay its upkeep, cancel your expensive heavy rocket for a cheaper way to orbit. Reusable and refurbished rockets, and communication networks, are money decisions.
- **Launch cost is per rocket, not by mass — DECIDED (Alex).** Bigger isn't automatically pricier: Sea Dragon was huge *because* it was designed to be cheap. *Proposal:* each rocket card prints a **cost per flight**, set from history (cost to orbit), not from its tonnage: Saturn V expensive, Sea Dragon cheap for its size, reusable rockets cheap per flight, the Shuttle sold as cheap but expensive in practice (the "wrong engineering" lesson).

## How phases could add rules (*proposal*)

The game grows more complex as it goes, so rules can arrive with the phases instead of all at the start:

- **Era cards.** A phase ends when its milestone is claimed; flip the next era card. It adds rules and cards: e.g. crew and the Moon missions in phase 2; infrastructure, upkeep and political events in phase 3; Mars missions in phase 4.
- Phase 1 could run with very few rules (no disasters at all, or only the teething ones), so the first turns are pure "how does a rocket work".
- Political events (budget cuts, a program collapse, ride-sharing) live in the phase 3 deck.

## Opening fixes after the first playtest — DECIDED (Alex, Oct 2026)

Playtest: too few rockets, too many disasters, no money without rockets, and missions from every era mixed (a Mars Base on turn 1). Fixes:

- **Era-stacked decks.** Every card and mission has an `era` (1–4 = the phases above) in `data/*.json`. The market deck and the mission deck are each sorted by era, each era shuffled on its own, era 1 on top. Eras are set from history (first flight or design date).
- **Fewer disasters at the start.** Only the 5 one-shot teething failures start in your deck; the 5 recurring ones join it when **First Orbit** is claimed (the tutorial is over). Infrastructure disasters still join when you build.
- **More rockets.** Starting deck: 3× Kerolox Sustainer, 3× Light Solid Booster, Solid Kick Motor (the two-stage lesson), Atmospheric Return, 2× Science Package, Backup Systems, Overtime. Starting hand 5.
- **Easy early money and science.** New era-1 missions: **Test Flight** (10t → E3, 💰2, ×4: any starting rocket can do it) and **Sounding Rocket** (Science Package → E5, ⚛1, ×4: the first science). More Special Delivery (×5) and Intercontinental Express (×4, the K1 + Kick Motor two-stage lesson).

## How we'll check it

- **Pacing spec → solo bot → tune.** Write the target arc in turns, then a simple solo bot plays the real cards on the real board under the real rules, and we tune science and money until the bot hits the arc and different strategies finish close together. `src/science_ladder.py` is the seed of this.

## OPEN

1. **Endgame / win condition.** Something on Mars: a city or big base, not first human.
2. **Target arc.** Rough turns per phase, and total game length (solo and with 4).
3. **Phase transitions.** Era cards adding rules (proposal above), or something else? Does the whole table change phase together when the first player hits the milestone, or each player separately?
4. **Science mechanics.** Spend science to open tech (a tree by lineage) or unlock by milestones flown? How science separates the phases.
5. **Money mechanics.** Cost per flight on rocket cards: does that replace paying money to buy cards (cards then cost science only)? Upkeep for stations in phase 3?
6. **Which current rules are phase 1 and which come later** (disasters, crew slots, infrastructure, first player token…).
