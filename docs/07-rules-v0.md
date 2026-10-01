# 07 — Rules v0 (the playable loop)

Status: **draft, Sep 2026.** Items marked **DECIDED** are Alex's calls. Items marked *proposal* are Claude's suggestions awaiting a yes/no. The card physics (docs/01) is unchanged. This doc is the turn loop wrapped around it.

## Components

- **Main board:** Earth / Moon / Mars spirals + deep-space ladder (docs/04).
- **4 player boards ("Space Center")** — DECIDED. Each has the three actions printed on it (Research, Launch, Mission Control), 4 mission areas (each holds one rocket card + its cargo tokens), a spot for completed goals, and 4 mission tokens.
- **Main deck:** rockets, equipment and bundle cards. **N cards lie face-up beside it** as an open market — DECIDED.
- **Goals deck.** Goal cards are **double-sided** (*direction, Alex*): the goal on one side, the reward you gain for completing it on the other. The most important upgrades live on goal cards, not in the main deck.
- **Cargo tokens:** small triangular wooden tokens in four colours on the base-4 mass ladder. K = 640t, R = 160t, O = 40t, Y = 10t.

## Goals setup — DECIDED

- **All FIRST goals are face-up from the start** and stay available until claimed.
- **Other missions:** a row of 5 face-up cards, with the rest of the goals deck beside it. Refill the row as cards are taken.

## Turn: tap each action once — DECIDED

On your turn you may use **each action on your Space Center once**. There are three (**Build was dropped, Sep 2026**, as unnecessary for now; upgrades come from goal rewards instead):

| Action | Effect |
|---|---|
| **Research** | **Buy one card** into your hand: blind from the top of the main deck, one of the N face-up market cards, or from your own discard pile. Refill the market after taking from it. **No hand limit for now.** |
| **Launch** | Put a mission token on **Earth**. Place **4 red cargo tokens** (640t) in that mission's area. Then take a **free Mission Control** on it, immediately. |
| **Mission Control** (Move) | Spend a mission's cargo tokens to place a rocket card from your hand on its area. Then follow the card. |

Later cards and goal rewards can add actions or change these rules (the Fluxx idea: your rules are what's in front of you).

**Hand = rockets and equipment (hidden). Table = your Space Center (public).** Nobody knows what you can fly until you do.

## Launch — DECIDED

1. Put a mission token on Earth.
2. Place **4 red cargo tokens** in that mission's area. That's the launch pad's lift: **640t**.
3. Take a free Mission Control on this mission right away. Its rocket must be able to light on Earth (GND or G+S badge).
4. **Crew Capsule must be declared now.** If the mission is crewed, put the Crew Capsule card aboard at launch. It's the one thing you can't add later.

The first stage is bought with the pad's tokens exactly like any later stage is bought with cargo, so **launching and staging are the same move.**

**No precommitment.** Apart from the Crew Capsule, you don't declare upper stages or equipment. The tokens are generic mass; which hardware they turn out to be is decided when you spend them. You may launch hoping to draw the right cards before you need them.

## Mission Control (Move) — DECIDED

1. **Spend** cargo tokens from the mission's area to pay a rocket's **T: cost**, and place that rocket card from your hand on the mission's area.
2. **Leftover tokens are discarded**, or passed to another of your missions on the same space (**separation**, see Splitting). Never kept loose: the cargo *was* the next stage. Paying at least T means nobody needs to make change, and the rule can only waste capacity, never beat the rocket equation. *Future idea:* a "redundancy" card that turns discarded excess into safety.
3. **The rocket card says: "Move spacecraft, keep remaining tokens."** Pick a row on its strip. Move the mission token up to that many spaces, then put the row's cargo tokens on the mission's area.

Why this is the physics: a card's total mass already includes its cargo bay (displacement model, docs/01). Paying T and then putting down the row's cargo *is* the model, turned into a board action.

**Worked example: a Falcon 9-style launch, basic turn**

| Action | Pay | Row | Result |
|---|---|---|---|
| Launch | none | 4 red placed | on Earth |
| free Mission Control: Kerolox Booster (K2) | RRR (480t); 1 red discarded | 120t → OOO | Δv 4 |
| Mission Control: Kerolox Upper (Ku) | OOO (120t) | 20t → YY | Δv 4 + 5 = **9, LEO**, 20t of payload aboard |

**Unspent Δv — decided earlier, needs re-checking against this flow.** A stage that still has Δv left stays with the mission and can fire again on a later turn (Apollo's CSM: into lunar orbit, park, home next turn). *Open:* with "move up to N spaces", how is the unspent Δv tracked, and does firing it again cost a Mission Control?

## Equipment — DECIDED

Equipment cards work **exactly like rockets**: they come from your hand and ride aboard a mission. The difference is what they give. A rocket turns cargo into more movement; equipment gives **special actions** (land on an airless surface, aerobrake, make propellant on Mars, keep a crew fed) and sometimes **special prizes** (goal requirements such as Science Package + RTG at escape +6).

Like rockets, equipment is **not precommitted** (except the Crew Capsule, which is declared at launch). You play it from your hand onto a mission later, paying for it with capacity already aboard. That capacity comes from:
- **Cargo tokens, by mass — DECIDED.** One yellow (10t) buys 4 equipment cards (each ~2.5t), an orange 16, and so on. Spend the tokens like paying for a rocket.
- A stage's `+ N equipment cards` slots.
- A strip row whose cargo is `N eq`, below one yellow. *Proposal:* there are no tokens that small, so **choosing an `N eq` row means placing those equipment cards from your hand right then.** This is the same exception as the Crew Capsule, and it needs no new components. It's usually the capsule riding those rows anyway (K2 + capsule = First Orbit).

**Equipment in play (prototype, Sep 2026).** Mission Control works on any mission in flight that has cargo tokens *or* free equipment slots. Equipment uses a free slot first; otherwise the smallest token is broken into slots by mass (Y = 4), and **unused slots stay aboard** (unlike a rocket, which absorbs all the cargo). Stages with `+ N equipment cards` add N slots when they fire. *Open:* the Crew Capsule was decided to be declared at launch; the prototype currently lets you add it later like any equipment — keep the exception or drop it?

## Splitting a mission — DECIDED

You may **split a mission whenever you want**. Take another of your mission tokens, put it on the same space, and divide the stages, cargo tokens and equipment between the two mission areas. Each part then moves and parks on its own (each must end your turn at a parking spot). Example: the LM separates in lunar orbit and lands while the CSM waits in orbit. You have 4 mission tokens, so at most 4 missions or mission parts in flight.

## Bundle cards: doubling a rocket — DECIDED

A **×2 / ×3 / ×4 bundle card** is played together with a rocket from your hand and flies it as N identical rockets. You pay N × T, carry N × the row's cargo, and the Δv stays the same. (The rocket equation: N rockets carrying N loads have the same mass ratio as one.) This is how parallel boosters work at the table. The cards already exist (docs/04); the printed set limits the multiplier by weight class (black ×2 only; red and orange ×2/×4; yellow ×2/×3/×4).

**Worked example: the Shuttle, no special numbers needed**

| Step | Pay | Row | Result |
|---|---|---|---|
| Launch, then Heavy Solid Booster + ×2 bundle | 2 × K = 1,280t (a Heavy pad's tokens) | 320t (RR) each → **640t aboard (K)** | Δv 1 |
| Mission Control: Drop Tank (burned by the orbiter's engines) | K | 80t (OO) | Δv 1 + 7 = 8 |
| Mission Control: Orbiter | OO | 30t (YYY: the 25t payload bay) | Δv 8 + 1 = **9, LEO** |

Three burns, as decided below. Two SRBs cost 1,280t, more than the basic pad's 640t, so the Shuttle needs a **Heavy** pad. This replaces the hand-entered `parallel_dv=1` in `playtest.py`.

## Park or fail — DECIDED

If a mission does not **end your turn at a parking spot**, it fails.

- Board symbols (from the kit's `board_symbols`): **● circle** = park any number of turns; **■/◆ square** = waypoint, may end a turn but must move next turn (Earth Escape); **▲ triangle** = may not end a turn. Per space in `data/board.json` → `stop`.
- *Proposal:* the unmarked deep-space and Mars-route spaces count as parking (coasting). The climb from Earth to LEO is never a parking spot.
- A basic turn (Launch with its free Mission Control, plus the regular Mission Control) is two burns: enough for K2 alone, Falcon 9, K1+H1, Saturn V to LEO on the S-II, Starship, Sea Dragon, and SLS.
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

## Launch pads = tokens at launch — DECIDED (upgrade tiers are a proposal)

The pad is simply **how many cargo tokens Launch puts down**. The basic printed Launch gives **4 red = 640t**, which buys any single first stage up to 640t. Pad upgrades (mostly goal rewards) give more:

| Pad | Launch places | Buys | Real-world echo |
|---|---|---|---|
| **Basic** (printed) | 4 red = 640t | K1, K2, M1, S2, one S3 | Baikonur, Canaveral LC-14 |
| **Heavy** | 4 black = 2,560t | K3 Saturn, Shuttle (2 × SRB = 1,280t) | LC-39 |
| **Super** | 6 black = 3,840t | Nova, Super Heavy | Starbase |
| **Sea launch** | 25 black | Sea Dragon | Truax's ocean pad |

No separate mass-limit rule is needed: you simply can't pay for a first stage you don't have tokens for.

## Goal rewards — *direction*

- Goal cards are double-sided: complete the goal, flip it, and gain the upgrade printed on the back.
- This makes "missions award tech" (docs/05) *the* unlock system, and replaces docs/02's "launch tier N → unlock N+1".
- *Proposal, to avoid runaway leaders:* FIRST goals give distinctive but not essential upgrades. The market-row contracts give **common** upgrades (duplicates exist), so everyone keeps progressing.

## Open questions

1. **Setup and end:** player count, starting hand, size N of the face-up market, endgame trigger.
2. **Hand limit:** none for now; revisit after playtesting.
3. **Proposals awaiting a yes/no:** parking spots, aerobraking costs no tap, launch-pad tiers, placing equipment cards when choosing an `N eq` row, FIRST vs contract rewards, and the time follow-ups.

## Answered (Sep 2026)

- Build action dropped. Three actions: Research (buy one card), Launch (token on Earth + 4 red + free Mission Control), Mission Control (spend tokens to place a rocket; leftovers discarded or separated).
- Rocket cards say "Move spacecraft, keep remaining tokens".
- Launch pads are the number of tokens Launch places.

- Rockets and equipment fly from hand; the Space Center is public.
- Research: blind, open market, or own discard pile; the basic card gives one take.
- No precommitment except the Crew Capsule, which is declared at launch.
- Equipment works like rockets but gives special actions and prizes.
- Missions split whenever you want.
- Parallel boosters are bundle cards (×2/×3/×4).
- Turns are not time; they only matter for consumables on the Mars route.
- No hand limit for now.
- One yellow token buys 4 equipment cards (by mass). Burner Engine archived.
