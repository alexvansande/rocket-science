# 07 — Rules v0 (the playable loop)

Status: **draft, Sep 2026.** Items marked **DECIDED** are Alex's calls. Items marked *proposal* are Claude's suggestions awaiting a yes/no. The card physics (docs/01) is unchanged. This doc is the turn loop wrapped around it.

## Components

- **Main board:** Earth / Moon / Mars spirals + deep-space ladder (docs/04).
- **4 player boards ("Space Center")** — DECIDED. Each has the four starting actions printed on it, 4 mission areas, and 4 mission tokens.
- **Main deck:** rockets, equipment, bundle cards, and tech/Space Center improvements. **N cards lie face-up beside it** as an open market — DECIDED.
- **Goals deck.** Goal cards are **double-sided** (*direction, Alex*): the goal on one side, the reward you gain for completing it on the other. The most important upgrades live on goal cards, not in the main deck.
- **Cargo tokens:** small triangular wooden tokens in four colours on the base-4 mass ladder. K = 640t, R = 160t, O = 40t, Y = 10t.

## Goals setup — DECIDED

- **All FIRST goals are face-up from the start** and stay available until claimed.
- **Other missions:** a row of 5 face-up cards, with the rest of the goals deck beside it. Refill the row as cards are taken.

## Turn: tap each card once — DECIDED

On your turn you may activate (tap) **each card in front of you once**. The printed starting actions give a basic turn of:

| Action | Effect |
|---|---|
| **Research** | Take cards into your hand: **blind from the top of the main deck, one of the N face-up market cards, or from your own discard pile** — DECIDED. How many is set by your Research card: **the printed basic one gives a single take — DECIDED.** Upgrading Research (by building on top of it) gives more. Refill the market after taking from it. **No hand limit for now** — DECIDED (revisit after playtesting). |
| **Build** | Play a Space Center improvement from your hand, either beside your board or **on top of a printed starting action** (upgrading it). Rockets are not built: they fly straight from hand. |
| **Launch** | Launch a mission from Earth (below). |
| **Move** | Fire one more stage on a mission already in flight (below). |

Cards you build later can add taps, extra actions, or change these rules (the Fluxx idea: your rules are the cards in front of you).

## Launch

1. Pick a rocket **from your hand — DECIDED** that can light on Earth (GND or G+S badge). The pad must be able to lift it (see Launch pads). Your hand is your hidden fleet; nobody knows what you can fly until you launch.
2. Pick a row on its strip.
3. **Crew Capsule must be declared now — DECIDED.** If the mission is crewed, put the Crew Capsule card aboard at launch. It is the one thing you can't add later (you can't put people on a rocket that's already flying).
4. Put your mission token **N squares from Earth**, where N is the row's Δv.
5. Put the row's cargo tokens in that mission's area.
6. Discard the rocket card to your own discard pile.

**No precommitment — DECIDED.** Apart from the Crew Capsule, you don't declare the upper stages or equipment at launch. The cargo tokens are generic mass in space; you pay them for whatever rockets and equipment you play from your hand later. So you may launch without the right cards in hand, gambling that you'll draw them before you need them. (Physically honest: the tokens are the mass that went up. Which hardware that mass turns out to be is decided later.)

Split between hand and table: **hand = rockets and equipment (hidden); table = your Space Center (public rules).**

## Move

1. Play a rocket **from your hand** and pay its **T: cost** using the cargo tokens aboard that mission.
2. **Spend all of them — DECIDED.** Tokens beyond the stage's cost are discarded, never kept as leftovers. (Physics: the cargo *was* the next stage. Paying at least T means you never need to make change, and the rule can only waste capacity, never beat the rocket equation.) *Future idea, not designed yet:* a "redundancy" card that turns this discarded excess into safety.
3. Pick a row on the new rocket, move up to its Δv, and put that row's cargo tokens aboard.
4. **Unspent Δv — DECIDED.** A stage that still has Δv left **stays with the mission** and can fire again on a later turn from a parking spot. Example: Apollo's CSM fires into lunar orbit, parks, and fires again next turn to come home. A stage that has used all its Δv is discarded.

Why this is the physics: a card's total mass already includes its cargo bay (displacement model, docs/01). Paying T in tokens and then putting down the row's cargo *is* the model, turned into a board action.

## Equipment — DECIDED

Equipment cards work **exactly like rockets**: they come from your hand and ride aboard a mission. The difference is what they give. A rocket turns cargo into more movement; equipment gives **special actions** (land on an airless surface, aerobrake, make propellant on Mars, keep a crew fed) and sometimes **special prizes** (goal requirements such as Science Package + RTG at escape +6).

Like rockets, equipment is **not precommitted** (except the Crew Capsule, which is declared at launch). You play it from your hand onto a mission later, paying for it with capacity already aboard. That capacity comes from:
- **Cargo tokens, by mass — DECIDED.** One yellow (10t) buys 4 equipment cards (each ~2.5t), an orange 16, and so on. Spend the tokens like paying for a rocket.
- A stage's `+ N equipment cards` slots.
- A strip row whose cargo is `N eq`, below one yellow. *Proposal:* there are no tokens that small, so **choosing an `N eq` row means placing those equipment cards from your hand right then.** This is the same exception as the Crew Capsule, and it needs no new components. It's usually the capsule riding those rows anyway (K2 + capsule = First Orbit).

## Splitting a mission — DECIDED

You may **split a mission whenever you want**. Take another of your mission tokens, put it on the same space, and divide the stages, cargo tokens and equipment between the two mission areas. Each part then moves and parks on its own (each must end your turn at a parking spot). Example: the LM separates in lunar orbit and lands while the CSM waits in orbit. You have 4 mission tokens, so at most 4 missions or mission parts in flight.

## Bundle cards: doubling a rocket — DECIDED

A **×2 / ×3 / ×4 bundle card** is played together with a rocket from your hand and flies it as N identical rockets. You pay N × T, carry N × the row's cargo, and the Δv stays the same. (The rocket equation: N rockets carrying N loads have the same mass ratio as one.) This is how parallel boosters work at the table. The cards already exist (docs/04); the printed set limits the multiplier by weight class (black ×2 only; red and orange ×2/×4; yellow ×2/×3/×4).

**Worked example: the Shuttle, no special numbers needed**

| Step | Pay | Row | Result |
|---|---|---|---|
| Launch Heavy Solid Booster + ×2 bundle | none | 320t (RR) each → **640t aboard (K)** | Δv 1 |
| Move: Drop Tank (burned by the orbiter's engines) | K | 80t (OO) | Δv 1 + 7 = 8 |
| Move: Orbiter | OO | 30t (YYY: the 25t payload bay) | Δv 8 + 1 = **9, LEO** |

Three burns, as decided below. The launch mass is 2 × 640 = 1,280t, so the Shuttle needs the **Heavy** pad. This replaces the hand-entered `parallel_dv=1` in `playtest.py`.

## Park or fail — DECIDED

If a mission does not **end your turn at a parking spot**, it fails.

- *Proposal:* parking spots are every orbit and surface space, plus the deep-space ladder (coasting counts as parked). The climb from Earth to LEO is never a parking spot.
- A basic turn (1 Launch + 1 Move) is two burns: enough for K2 alone, Falcon 9, K1+H1, Saturn V to LEO on the S-II, Starship, Sea Dragon, and SLS.
- **The Shuttle needs 3 burns to reach orbit (SRBs → tank → orbital manoeuvring engines). That's fine, DECIDED.** Extra-action cards will allow it. So the Shuttle is a mid-game rocket in practice.

## Time — DECIDED

**A turn is not a fixed length of time.** It can be minutes (a launch) or months (a coast). Turns only matter for **consumables on the way to Mars** (the deep-space ladder's skip-a-turn crossings, docs/04) and for tempo (who arrives first). Nothing else counts months.

Follow-ups this creates (not yet decided):
- Refineries and the Greenhouse say "rotate once per turn", but docs/04 says "1 step per month". Per turn is the simple reading.
- ENDURANCE goals ("station up X months") need rewording in turns.

## Aerobraking — *proposal*

- Descending through a **blue dashed** crossing with Atmospheric Return aboard **costs no tap** and can happen any time during your turn. It ends at the surface.
- Earth: from LEO to the ground is free. This is how crewed missions come home.
- Mars: the atmosphere saves 2 of the 3 Δv. The final 1 Δv is still a real burn (a Move).
- Free-return trajectories need no rule. They are the same free descent.

## Launch pads by weight class — DECIDED (tiers are a proposal)

The Space Center's pad limits the total mass you can launch: the first-stage card's T, times the bundle multiplier if any. (Everything above it is cargo inside that total, by the displacement model.) Pad upgrades come mostly from goal rewards.

| Pad | Lifts up to | Unlocks | Real-world echo |
|---|---|---|---|
| **Basic** (printed) | 480t | K1, K2, M1, S2 | Baikonur, Canaveral LC-14 |
| **Heavy** | 2,560t | K3 Saturn, Shuttle (2 × SRB = 1,280t) | LC-39 |
| **Super** | 3,840t | Nova, Super Heavy | Starbase |
| **Sea launch** | any | Sea Dragon | Truax's ocean pad |

Gate by **mass**, not by the colour tag: every Earth booster is already red or black, so the colour would give only two tiers.

## Goal rewards — *direction*

- Goal cards are double-sided: complete the goal, flip it, and gain the upgrade printed on the back.
- This makes "missions award tech" (docs/05) *the* unlock system, and replaces docs/02's "launch tier N → unlock N+1".
- *Proposal, to avoid runaway leaders:* FIRST goals give distinctive but not essential upgrades. The market-row contracts give **common** upgrades (duplicates exist), so everyone keeps progressing.

## Open questions

1. **Setup and end:** player count, starting hand, size N of the face-up market, endgame trigger.
2. **Hand limit:** none for now; revisit after playtesting.
3. **Proposals awaiting a yes/no:** parking spots, aerobraking costs no tap, launch-pad tiers, placing equipment cards when choosing an `N eq` row, FIRST vs contract rewards, and the time follow-ups.

## Answered (Sep 2026)

- Rockets and equipment fly from hand; the Space Center is public.
- Research: blind, open market, or own discard pile; the basic card gives one take.
- No precommitment except the Crew Capsule, which is declared at launch.
- Equipment works like rockets but gives special actions and prizes.
- Missions split whenever you want.
- Parallel boosters are bundle cards (×2/×3/×4).
- Turns are not time; they only matter for consumables on the Mars route.
- No hand limit for now.
- One yellow token buys 4 equipment cards (by mass). Burner Engine archived.
