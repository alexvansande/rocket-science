# 09 — Personal decks, failures and the economy (v1 draft)

Status: **draft, Oct 2026**, from Alex's playtest notes. **DECIDED** = Alex's call. *Proposal* = Claude's suggestion awaiting a yes/no. **OPEN** = needs a call before it's built. Card physics (docs/01) is unchanged. This revises Research, Launch's Crew Capsule rule, the mission areas and the goal rewards in `docs/07`, and answers docs/06's "Economy: money in or out?" (in) and the event/failure deck item.

## 1. Your own deck — DECIDED

- Each player has **their own deck**, with a printed spot for it on the Space Center board.
- **Draw from the top; every card you use goes to the bottom.** No discard pile and no regular shuffle: the deck is a queue. (Disasters shuffle it, see 3.)
- **Starting hand: 3 cards.** Starting deck: ~16–20 cards, including the failure cards.
- **Bought cards go to the bottom of your deck.** You wait for them to come round.
- **The Research action is gone.** You **draw 1 card** automatically at the **end** of your turn (see Turn order). Cards you buy later can raise your draw size.
- That leaves two tapped actions: **Launch** and **Mission Control**. **Buy as much as you can afford** each turn (for now).
- Draw-size upgrades are **Space Center improvements** (section 4b): once bought they stay in front of you, not in your deck.

## 2. Mission slots: 2 crewed, 2 uncrewed — DECIDED

The Space Center has **4 mission slots: 2 crewed, 2 uncrewed.** A crewed mission is one you launch into a crewed slot, so you no longer declare a Crew Capsule at launch (that docs/07 exception goes away).

- **Losing a crewed mission costs victory points.**
- Crewed goals need a mission flown from a crewed slot. Robotic goals need an uncrewed slot. That replaces the `without: Crew Capsule` / `equipCount` goal checks.

**The crew takes one equipment slot — DECIDED.** A crewed mission must have room for the crew: the first equipment slot it gets is the crew's. (Equipment slots are used immediately or lost, docs/07, so the crew simply fills one when slots appear.) A crewed mission that ends without an equipment slot has no room for a crew. K2's `1 eq` row still orbits a crew (First Orbit), and the mass stays honest.
- Fallback if this plays badly: keep a separate generic payload card (today's Crew Capsule) that must ride a crewed mission.
- **OPEN:** the **Crew Capsule card (C1)** then has no job. Retire it, or turn it into something else (e.g. a crewed-only upgrade)? C2 Crew Habitat, Consumables and C3 Greenhouse stay as they are.

## 3. Disaster cards — DECIDED (mechanics), counts OPEN

Failure cards are shuffled into the starting deck. **Each disaster card has its own effect.** All of them **shuffle your deck.** Examples:

- "If there's a mission in slot 1, it has an accident." (A slot number, so the effect needs no dice and is easy to read.)
- "Lose your hand." (Your hand goes into your deck before the shuffle.)
- Others to design: lose your turn, a mission on a burn loses a stage, a mission parked on the Moon/Mars is stranded …

Two lifetimes (from the first round of notes, still assumed):

| Kind | What happens to the card |
|---|---|
| **Teething failures** | Resolve, then the card is gone for good. The program gets more reliable just by flying. |
| **Category failures** | Stay in the deck until you buy the tech that fixes that category, which removes it. |

*Proposal, categories with their fixes* (real failure modes, each fixed by a real piece of engineering):

| Failure | Real case | Fixed by |
|---|---|---|
| Pogo oscillation | Gemini/Titan II, Apollo 6 | Pogo suppressor |
| Combustion instability | F-1 development | Baffled injector |
| Staging failure | many early launches | Stage-separation testing |
| Guidance failure | Ariane 5 flight 501 | Redundant flight computer |
| Cabin fire / life support | Apollo 1, Apollo 13 | Crew-safety review (hits crewed slots only) |

*Proposal:* slot-targeted disasters are the natural way to make crewed flight riskier. "Slot 1 or 2" = the crewed slots, so a disaster there also costs VP.

### Turn order — DECIDED (Alex, Oct 2026)

1. **Play:** Launch, move spacecraft, play actions, buy. Cards you fly **pile up on the mission slot**; nothing is removed mid-turn, spent stages included.
2. **Draw 1 card.**
3. **Disaster?** Follow its instructions, against your missions as they stand right now.
4. **Otherwise, collect prizes:** claim the goals your missions met this turn.
5. **Clear completed missions:** their cards go to the bottom of your deck, tokens to the bowls, badge home.

Why: the risk sits on what you just flew. Apollo reaches the Moon, then you flip the card. Drawing at the start of the turn had disasters finding empty slots (short missions are launched, scored and recovered within one turn) and "below orbit" could never be true then (park-or-fail).

Consequences:
- **Goals are claimed at end of turn**, not the moment they're met. (The table prototype claims immediately today; that changes.)
- **A long mission locks its cards up.** A Mars expedition keeps every stage it flew on its slot for many turns, out of your deck. That's the real cost of a big program, and it falls out of the rule.
- *Proposal:* park-or-fail is checked in step 5 too. A mission not at a stop is lost; its cards go to the bottom.
- *Proposal:* a disaster drawn in step 3 still lets you collect prizes from missions it didn't hit. (Alex's list reads "if it's not, then pick up prizes"; **OPEN:** does any disaster cost you the whole turn's prizes, or only the hit mission's?)
- With the draw at the end of your turn, "this turn" effects become "your next turn" (e.g. "No Launch on your next turn").

### Density warning (simulated)

With the first-round rule (every failure throws back your whole hand) and about half the starting deck as failures, a player **loses ~8–9 of their first 20 turns** and has a 3-card hand on only ~4 of them. Per-card effects fix most of this: only the "lose your hand" cards cause it. Keep those few.

| Starting deck (good + teething + category), every failure loses the hand | Turns lost / 20 | Turns with a 3+ card hand | Median first failure |
|---|---|---|---|
| 8 + 4 + 4 (16) | 8.4 | 3.7 | turn 2 |
| 10 + 5 + 5 (20) | 8.7 | 3.6 | turn 2 |
| 8 + 4 + 4, categories fixed on turn 8 | 5.5 | 8.0 | turn 1 |
| 14 + 3 + 3 (20) | 5.2 | 8.0 | turn 2 |
| 16 + 2 + 2 (20) | 3.6 | 10.9 | turn 3 |

(Monte Carlo, 20,000 games; 1 draw per turn, a good card bought every 2nd successful turn and put on the bottom, failures at setup redrawn. It's the worst case: every failure counted as "lose hand + lose turn", no Redundancy.) Re-run once the disaster cards have effects.

## 4. Action cards — DECIDED

The main deck holds **actions** as well as rockets and equipment. Played actions **go to the bottom of your deck**, like every other card.

- **Redundancy:** play it when you draw a disaster; you ignore it this turn. The disaster card is not removed (*proposal:* it goes to the bottom).
- **Meddling with an opponent's deck:** e.g. look at their top 3 and reorder them.
- **Stealing a card** from another player.

*Proposal, flavour names from history* (no real engine names, per CLAUDE.md, but historical events are fine): Backup Systems (Redundancy), Operation Paperclip (take a card from an opponent's hand), Espionage (look at an opponent's top 3, reorder them), Budget Cut (an opponent loses 1 money).

Playing an action is **free** (for now) — DECIDED.

## 4b. Space Center improvements — DECIDED (Alex, Oct 2026)

A card type in the rocket deck. Buy it, **put it down in front of you**, and it changes your rules for the rest of the game (the Fluxx idea from docs/07). Never in your deck, so never drawn or lost.

Prototype set (names and prices are placeholders):

| Improvement | Effect | Price |
|---|---|---|
| Flight Operations Team (×2) | Draw 1 more card at the end of each turn. | $3 + ⚛2 |
| Second Launch Complex | One more Launch each turn (each with its free Mission Control). | $3 + ⚛2 |
| Expanded Mission Control | One more Mission Control each turn. | $2 + ⚛2 |
| Orbital / Heavy / Super Pad | Launch places 4 red / 4 black / 6 black. | $2+⚛1 / $3+⚛3 / $4+⚛6 |
| The 5 disaster fixes | Remove that disaster for good, the next time it's drawn. | $1 each |

*Proposal for more:* Tracking Network (keep 1 equipment slot instead of losing it), Astronaut Corps (a crewed mission lost costs −1★, not −2), Propellant Depot (park spare cargo tokens in LEO).

## 4c. Space infrastructure goals — DECIDED (direction), card list *proposal*

A kind of **transient** goal card (it comes and goes through the contract row). Complete it and keep it; one alone is worth little, **sets pay escalating rewards** (e.g. one = nothing, two = 3★, three = 8★).

- **Transient — DECIDED (Alex).**
- **No money sets — DECIDED (Alex: income every turn is upkeep to remember).** And a one-off money payout can't work either: money only exists as cards you discard, so a set can't hand out "$2" without a token. *Proposal:* infrastructure pays **VP or science** only. Science is a threshold you count, so a growing set simply counts for more.
- **Disasters target infrastructure — DECIDED (Alex).** A lost infrastructure card goes to the bottom of the contract deck, and your set shrinks.

*Proposal, families* (each card = one delivery):

| Family | One card's delivery | Set pays | 1 / 2 / 3 / 4 cards |
|---|---|---|---|
| Space Station | a module: Crew Habitat or 20t to LEO | ★ | 0 / 3 / 8 / 15 |
| Moon Base | Crew Habitat or 20t to the Moon's surface | ★ | 0 / 3 / 8 / 15 |
| Mars Base | Crew Habitat or 20t to Mars' surface | ★ | 1 / 4 / 10 / 18 |
| Satellite Network | 1 eq to LEO or GEO | ⚛ | 0 / 1 / 3 / 6 |
| Deep Space Network | Large Antenna at escape or beyond | ⚛ | 1 / 3 / 6 / 10 |

*Proposal, disasters that hit infrastructure* (recurring, each with a fix):

| Disaster | Real case | Effect | Fixed by |
|---|---|---|---|
| Orbital debris | Kessler syndrome, Iridium–Cosmos 2009 | Lose 1 Satellite Network card. | Debris Tracking |
| Station fire | Mir, 1997 | Lose 1 Space Station card. | Fire Suppression |
| Dust storm | Opportunity, 2018 | Lose 1 Mars Base card. | Dust-Proof Power |

**Infrastructure replaces the MOST bases — DECIDED (Alex, Oct 2026).** Largest Lunar Base and Largest Martian Base are gone; the Moon Base and Mars Base families cover them. Space station sets cover Largest Space Station's ground too, but Alex wants **at least one king-of-the-hill card**, so:

- **Largest Space Station stays as king of the hill**, now countable: it's held by whoever has the **most Space Station cards** (a tie leaves it with the holder). Lose your last station and it goes back. International Station is unchanged (it needs other players).
- **Infrastructure disasters join your deck when you build** (*proposal, in the prototype*): Station Fire, Orbital Debris and Dust Storm aren't in the starting deck. Each is shuffled into your deck when you win your first card of its family, so owning infrastructure brings its own risk and the starting deck doesn't get heavier. Each has a fix (Fire Suppression, Debris Tracking, Dust-Proof Power, $1 + ⚛1). A lost card goes to the bottom of the contract deck.
- Infrastructure cards: 4 copies of each family in the contract deck (`objectives.json` → `type: INFRASTRUCTURE`, `family`, `reward.set`).

### Income from other players' actions — DIRECTION (Alex), OPEN

Some cards could pay you when another player does something (instead of income every turn). Mechanism and cards to be designed later.

## 5. Goals pay out; market cards have a price — DECIDED

Completing a goal and flipping it shows a reward on the back. **Each goal pays one type: usually 1–3 money bags, or science, or victory points.**

**Permanent goals pay VP; transient goals pay resources — DECIDED.** Permanent goals (FIRST, MOST, RESCUE, ENDURANCE) are face-up all game and pay victory points. Transient contracts come and go through the row and pay money or science.

| Reward | Icon | Use |
|---|---|---|
| **Victory points** | star | Win the game. |
| **Science** | atom | A **threshold**: kept, never spent. |
| **Money** | money bag | **Spent:** discard the goal card to pay. Mostly 1 bag, a few 2, rarely 3. |

Market cards get a price, e.g. **"3 science (not spent) + 2 money (spent)".**

**Upgrades move to the market — DECIDED.** Pad upgrades and other big tech are market cards like everything else. The strong ones are held back by price: they need more science or money.

*Proposal, which goal pays what:* MILITARY and COMMERCIAL pay money, SCIENCE pays science, FIRSTs pay VP.

## 6. The rows: a price gradient, and scrapping stale cards

### Price gradient — DECIDED (to try)

New cards enter the market and the temporary-goal row on the **left**. When a card is taken, the cards to its left **slide right** to fill the gap and a new card comes in on the left. So fresh cards cost a premium and get cheaper as they age:

| Row | Slot 1 (newest) | Slot 2 | Slot 3 | Rest |
|---|---|---|---|---|
| Market | +2 money | +1 money | — | printed price |
| Temporary goals | +1 Δv | +1 Δv | +1 Δv | as printed |

FIRST goals aren't in the row (they're all face-up from the start), so no surcharge on them.

**+1 Δv = the destination is one step farther — DECIDED.** One more ascent space for a MILITARY "DVn" throw (DV7 becomes DV8), one more rung for an "escape +N" goal. Physically it's **flying now instead of waiting for the best launch window**: a fresh contract is wanted now, and now costs extra Δv. Wait for the card to age, and the window opens.
- **OPEN:** goals with no Δv to raise (land on the Moon, station for N turns): no surcharge, or 1 money instead?

### Clearing the rightmost cards, and the first player token — DECIDED (Alex, Oct 2026)

Replaces the earlier "take the rightmost card of either row instead of launching". Two ways to clear stale cards:

1. **Launched but met no goal? — DECIDED (Alex, Oct 2026, replaces "instead of launching").** At the end of your turn, if you launched and none of your missions met a goal, discard the **rightmost mission card** and take a **💰1 card**. Launching is never wasted, and stale missions leave the row. (Earlier versions: take the rightmost card instead of launching, as the card's reward or as a sideways $1. All dropped.)
2. **Pay $1 to remove the rightmost market card and take the first player token.** The card is discarded. Not instead of anything: it's a purchase, any time on your turn.

**First player:** when everyone has played, the next round starts with whoever holds the token.

- **No free VP — DECIDED.** FIRST, MOST, RESCUE and ENDURANCE are **permanent goals**, all face-up from the start, never in the temporary row. The row holds only transient contracts (commercial, military, science), which pay money or science. 

### Card backs and frames — DECIDED (Alex, Oct 2026)

- **Mission cards** have their own frame (a thick dark rounded border) and a **resource back**: 💰 (money, green), ⚛ (science, purple) or 🛰 (infrastructure, brown, with the set table), plus the amount. Win a mission, flip it, and it *is* that resource. The top of the mission deck shows its back, so everyone knows what kind of mission comes next. (Permanent goals get a ★ back.) The 💰1 bank cards use the same money back.
- **Tech, action, improvement and disaster cards** share the red rocket back. Disasters must: a different back would let you see them coming in your deck.
- Kit: `build_kit.py` `mission_back_html()` / `mission_back_page()` print each sheet's backs slot by slot, rows mirrored for duplex.

### Money: mission cards + 💰1 cards — DECIDED (Alex, Oct 2026)

**The objectives deck is now called the mission deck.** Money comes from money mission cards you've won (spent by discarding them) and from **💰1 cards**, a bank supply used for the launch consolation. Pay with any mix; overpaying loses the extra. Budget overrun / Budget Cut take a 💰1 card first.

**Money missions pay 💰2 or more — DECIDED (Alex):** otherwise the 💰1 consolation is as good as flying a mission. Prototype values: Comsat 2, Special Delivery 2, Unnamed Payload 2, GPS 3, TV Broadcast 3, Orbital Tourist 3, Intercontinental Express 3, Maximum Throw 3.

## 7. First card draft — *proposal*, all numbers to playtest

### Disaster cards (10 in the starting deck)

Every disaster shuffles your deck. "Accident" = the mission is lost (tokens to the bowls, cards to the bottom of your deck, badge home). A **crewed** mission lost costs **−2 VP** (*proposal*). Recurring cards are deliberately milder than one-shots, since you'll see them again.

| # | Name (real case) | Kind | Effect | Removed by |
|---|---|---|---|---|
| 1 | Kaputnik (Vanguard TV-3) | one-shot | Lose your hand. | gone after use |
| 2 | Pad explosion (Nedelin) | one-shot | No Launch on your next turn. Lose your hand. | gone after use |
| 3 | Range safety destruct | one-shot | Accident: the mission in slot 3. | gone after use |
| 4 | Metric mix-up (Mars Climate Orbiter) | one-shot | Accident: your uncrewed mission farthest from Earth. | gone after use |
| 5 | Budget overrun | one-shot | Lose 1 money. | gone after use |
| 6 | Pogo oscillation (Apollo 6) | recurring | Accident: the mission in slot 1, if it launched this turn. | Pogo suppressor |
| 7 | Combustion instability (F-1) | recurring | No Launch on your next turn. | Baffled injector |
| 8 | Staging failure | recurring | Accident: the mission in slot 4, if it launched this turn. | Stage-separation testing |
| 9 | Guidance failure (Ariane 501) | recurring | Accident: the mission in slot 3, if it launched this turn. | Redundant flight computer |
| 10 | Cabin fire (Apollo 1) | recurring | Accident: the mission in slot 2. | Crew-safety review |

Slots 1–2 are crewed, 3–4 uncrewed. Pogo, staging and guidance failures only hit **a mission launched this turn**: launches are the risky part, a satellite parked for ten turns isn't. Cabin fire hits a crewed mission wherever it is. The slot numbers mean you choose your risk: an empty slot can't have an accident.

The 5 fixes are market cards. *Proposal:* once bought, a fix sits on your Space Center (like draw upgrades) and you **remove that disaster from your deck the next time it's drawn** (no deck search). Cheap: 1 money each, so early money has an obvious use.

### Action cards (main deck)

| Name | Effect |
|---|---|
| Backup Systems | Play when you draw a disaster: ignore it. The disaster goes to the bottom of your deck. |
| Operation Paperclip | Take a random card from an opponent's hand. It's yours now. |
| Espionage | Look at an opponent's top 3 cards and put them back in any order. |
| Press Leak | Put an opponent's top card on the bottom of their deck. |
| Budget Cut | An opponent loses 1 money. |
| Overtime | Draw 2 cards. |
| Self Audit (Alex, Oct 2026) | Look at the top 3 cards of your deck. You may shuffle your deck. |
| Extra Shift | One more Mission Control this turn. (The Shuttle's third burn, docs/07.) |

### Goal rewards (existing 28 goals)

The reward amount = the goal's current `vp` value, so nothing needs re-balancing to start:

| Goals | Pay |
|---|---|
| FIRST, MOST, RESCUE, ENDURANCE (12) — permanent | VP |
| SCIENCE (4) + FLYBY (4) — transient | science |
| COMMERCIAL (4) + MILITARY (4) — transient | money, 💰2–3 (see section 6) |

**The transient deck is multiplied — DECIDED (Alex, Oct 2026).** The 16 transient goals (4 each commercial, military, science, flyby) are printed **3 times each = 48 cards**, so money and science keep coming. `objectives.json`: `"transient": true, "copies": 3`; the old `filler` flag is gone. The kit prints them on their own MISSIONS sheets (12 permanent + 48 transient = 60 goal cards, 4 sheets); the table prototype gives each copy its own id.

### Prices

*Proposal, by tech tier:* tier 1 = 1 money; tier 2 = 2 money + 2 science; tier 3 = 3 money + 4 science; tier 4 and paper rockets = 4 money + 6 science. Pad upgrades: Heavy = 3 money + 3 science, Super = 4 + 6.

## Goal card layout — DECIDED (Alex, Oct 2026)

Top row = the **price**: what you must get where, in tokens/chips and board names ("YY → LEO", "CREW → MOON → EARTH"). Bottom row = the **prize** (★, $ or ⚛). Everything between is explanation and flavour. Rewards now live in `objectives.json` → `reward`. Space names: docs/04.

## In the web prototype (Oct 2026)

`build/table.html` (Blue's seat) now plays these rules: your own deck with draw at end of turn, the 5-step turn order, disasters (all 10) with Backup Systems, crewed/uncrewed slots, buying with money/science and the price gradient, +1 Δv on new contracts, the 💰1 consolation (launched but met no goal: discard the rightmost mission), paying $1 to discard the rightmost market card and take the first player token, permanent goals (VP) face-up and the ×3 transient deck, Space Center improvements (fixes, pads, +1 draw, second Launch, extra Mission Control). Data: `data/cards.json` → `disasters`, `actions`, `improvements`, `starting_deck`, and a `price` on every card.

Placeholders chosen for the prototype (all to playtest, none decided):
- **Starting deck:** 2× Kerolox Sustainer, 2× Light Solid Booster, Solid Kick Motor, Atmospheric Return, 2× Science Package, Backup Systems, Overtime + the 10 disasters (20 cards).
- **Prices:** by tech tier as in section 7; actions $1–2; improvements as in section 4b. Exception: **Hydrolox Upper costs $2 + ⚛2** (tier 2), not $1 — DECIDED (Alex), so K1 + Hydrolox Upper can't reach orbit from the basic pad early. Hydrolox upper stages came after the first orbits.
- **Main deck copies:** Backup Systems ×3, Overtime ×2, Self Audit ×2 ($1), Extra Shift ×2, other actions ×1. The Crew Capsule card is out of the decks.
- **Opponent actions** (Paperclip, Espionage, Press Leak, Budget Cut) do nothing yet: no opponents are simulated.
- **"Completed" mission** = it claimed a goal this turn, or it's back on Earth. A disaster costs only the prizes of the mission it hits.
- **Goals with no Δv to raise** (orbit, GEO, return trips) get no surcharge.
- A lost crewed mission costs −2★ only if the crew had boarded.

## What this changes elsewhere

- `docs/07`: drop Research and the Crew Capsule declaration; 4 slots become 2 crewed + 2 uncrewed; goal rewards and buying.
- `data/cards.json`: new `failures` and `actions` sections; a cost (science, money) on every buyable card; pad upgrades as cards.
- `data/objectives.json`: a `reward` field per goal; crewed/uncrewed instead of the capsule checks.
- `src/build_kit.py`: disaster and action card layouts, goal backs with reward icons, price on market cards.
- `src/build_table.py`: deck spot, crewed/uncrewed slots, automatic draw, bottom-decking, disaster resolution, buying.
