# 09 — Personal decks, failures and the economy (v1 draft)

Status: **draft, Oct 2026**, from Alex's playtest notes. **DECIDED** = Alex's call. *Proposal* = Claude's suggestion awaiting a yes/no. **OPEN** = needs a call before it's built. Card physics (docs/01) is unchanged. This revises Research, Launch's Crew Capsule rule, the mission areas and the goal rewards in `docs/07`, and answers docs/06's "Economy: money in or out?" (in) and the event/failure deck item.

## 1. Your own deck — DECIDED

- Each player has **their own deck**, with a printed spot for it on the Space Center board.
- **Draw from the top; every card you use goes to the bottom.** No discard pile and no regular shuffle: the deck is a queue. (Disasters shuffle it, see 3.)
- **Starting hand: 3 cards.** Starting deck: ~16–20 cards, including the failure cards.
- **Bought cards go to the bottom of your deck.** You wait for them to come round.
- **The Research action is gone.** You **draw 1 card** automatically at the **end** of your turn (see Turn order). Cards you buy later can raise your draw size.
- That leaves two tapped actions: **Launch** and **Mission Control**. **Buy as much as you can afford** each turn (for now).
- *Proposal:* draw-size upgrades sit **on your Space Center** once bought, not in your deck. A "+1 draw" card buried in your deck would only work on the turn you draw it.

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

## 5. Goals pay out; market cards have a price — DECIDED

Completing a goal and flipping it shows a reward on the back. **Each goal pays one type: usually 1–3 money bags, or science, or victory points.**

| Reward | Icon | Use |
|---|---|---|
| **Victory points** | star | Win the game. |
| **Science** | atom | A **threshold**: kept, never spent. |
| **Money** | money bag | **Spent.** *Proposal:* paid out as bag tokens (see 6). |

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

**OPEN, what "+1 Δv" means at the table.** Options:
- (a) *Claude's pick:* the goal's **destination is one step farther**: one more ascent space for a MILITARY "DVn" throw (DV7 becomes DV8), one more rung for an "escape +N" goal. Readable straight off the board, and it's the honest version (a fresh contract is a harder spec).
- (b) The mission must **burn 1 more Δv** than it needs to reach the goal. Hard to see at the table: a spacecraft's leftover Δv isn't tracked anywhere.
- Some goals have no Δv to raise (land on the Moon, station for N turns). For those: (a) gives no surcharge, or they pay 1 money instead.

### Scrapping the rightmost card — DECIDED (want), mechanism *proposal*

Alex wants the stale rightmost cards gone, but by a player's choice with a small payoff, not by a per-turn conveyor.

*Proposal: **Scrap**, once per turn, free.* Discard the rightmost card of **either** row:
- **market card → take 1 money** ("surplus sale");
- **goal card → take 1 science**? Too strong, since science is permanent. *Better:* **goal card → take 1 money** too ("cancelled contract, the agency pays a fee").

One rule for both rows, and it doubles as a trickle of income, so a player with a bad hand can still do something useful. If 1 money a turn is too generous, limit it to "only if you bought nothing this turn".

Other options considered:
- (b) **Take the rightmost market card for free, to the bottom of your deck.** The consolation *is* the card. Clears stale cards only if somebody wants them for free, which might not happen for really bad ones.
- (c) **Instead of your end-of-turn draw, take the rightmost market card.** You skip the disaster flip: safety is the consolation. Elegant, but a player could avoid disasters indefinitely by always taking it.

### Money needs tokens — *proposal*

If money is paid by discarding goal cards worth 1–3 bags, paying 2 with a 3-bag card means either losing 1 or making change. And scrapping needs a "1 money" to hand out. *Proposal:* **money-bag tokens.** Money goals pay out tokens; you keep the goal card in your completed pile like any other. VP and science goals stay as cards (science is just counted). Then Budget overrun / Budget Cut take a token.

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
| Extra Shift | One more Mission Control this turn. (The Shuttle's third burn, docs/07.) |

### Goal rewards (existing 28 goals)

The reward amount = the goal's current `vp` value, so nothing needs re-balancing to start:

| Goals | Pay |
|---|---|
| FIRST, MOST, RESCUE, ENDURANCE (12) | VP |
| FLYBY (4) + SCIENCE (4) | science |
| COMMERCIAL (4) + MILITARY (4) | money (1–2 bags) |

**Flag: money now comes only from the 8 commercial/military contracts, which are marked `filler` ("cut these first").** They're now the economy, so the flag should go, and the deck probably needs more money contracts (more copies of the military throws, which level-1 rockets can reach). Science has the same problem: only 8 cards pay it.

### Prices

*Proposal, by tech tier:* tier 1 = 1 money; tier 2 = 2 money + 2 science; tier 3 = 3 money + 4 science; tier 4 and paper rockets = 4 money + 6 science. Pad upgrades: Heavy = 3 money + 3 science, Super = 4 + 6.

## What this changes elsewhere

- `docs/07`: drop Research and the Crew Capsule declaration; 4 slots become 2 crewed + 2 uncrewed; goal rewards and buying.
- `data/cards.json`: new `failures` and `actions` sections; a cost (science, money) on every buyable card; pad upgrades as cards.
- `data/objectives.json`: a `reward` field per goal; crewed/uncrewed instead of the capsule checks.
- `src/build_kit.py`: disaster and action card layouts, goal backs with reward icons, price on market cards.
- `src/build_table.py`: deck spot, crewed/uncrewed slots, automatic draw, bottom-decking, disaster resolution, buying.
