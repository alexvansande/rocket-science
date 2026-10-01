# 09 — Personal decks, failures and the economy (v1 draft)

Status: **draft, Oct 2026**, from Alex's playtest notes. **DECIDED** = Alex's call. *Proposal* = Claude's suggestion awaiting a yes/no. **OPEN** = needs a call before it's built. Card physics (docs/01) is unchanged. This revises Research, Launch's Crew Capsule rule, the mission areas and the goal rewards in `docs/07`, and answers docs/06's "Economy: money in or out?" (in) and the event/failure deck item.

## 1. Your own deck — DECIDED

- Each player has **their own deck**, with a printed spot for it on the Space Center board.
- **Draw from the top; every card you use goes to the bottom.** No discard pile and no regular shuffle: the deck is a queue. (Disasters shuffle it, see 3.)
- **Starting hand: 3 cards.** Starting deck: ~16–20 cards, including the failure cards.
- **Bought cards go to the bottom of your deck.** You wait for them to come round.
- **The Research action is gone.** Drawing is automatic at the start of your turn. Cards you buy later can raise your draw size. *Proposal:* the base draw is 1 card. **OPEN:** confirm.
- That leaves two tapped actions: **Launch** and **Mission Control**. Buying happens once per turn (*proposal*; **OPEN**).

## 2. Mission slots: 2 crewed, 2 uncrewed — DECIDED

The Space Center has **4 mission slots: 2 crewed, 2 uncrewed.** A crewed mission is one you launch into a crewed slot, so you no longer declare a Crew Capsule at launch (that docs/07 exception goes away).

- **Losing a crewed mission costs victory points.**
- Crewed goals need a mission flown from a crewed slot. Robotic goals need an uncrewed slot. That replaces the `without: Crew Capsule` / `equipCount` goal checks.

**OPEN, the capsule's mass.** The physics needs the crew to weigh something: K2 orbits *with a capsule* only because the capsule rides an equipment row (First Orbit, docs/06 principle 10), and Apollo's CSM is real mass. Options:
- (a) *Proposal:* a crewed slot **comes with a capsule printed on it, taking 1 equipment slot.** The first equipment space on any crewed mission is always the crew. No card needed, mass stays honest.
- (b) You still fly a Crew Capsule card on a crewed mission; the slot just says it must carry one.
- (c) The crew is weightless. Simplest, but K2 + nothing then orbits a "crew" for free, which breaks First Orbit's history lesson.

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

*Proposal, flavour names from history* (no real engine names, per CLAUDE.md, but historical events are fine): Backup Systems (Redundancy), Operation Paperclip (take a card from an opponent's hand), Espionage (look at an opponent's top 3, reorder them), Budget Cut (an opponent loses one money card).

**OPEN:** does playing an action need a tap (Mission Control), or is it free?

## 5. Goals pay out; market cards have a price — DECIDED

Completing a goal and flipping it shows a reward on the back. **Each goal pays one type: usually 1–3 money bags, or science, or victory points.**

| Reward | Icon | Use |
|---|---|---|
| **Victory points** | star | Win the game. |
| **Science** | atom | A **threshold**: kept, never spent. |
| **Money** | money bag | **Spent:** discard the goal card to pay. |

Market cards get a price, e.g. **"3 science (not spent) + 2 money (spent)".**

**Upgrades move to the market — DECIDED.** Pad upgrades and other big tech are market cards like everything else. The strong ones are held back by price: they need more science or money.

*Proposal, which goal pays what:* MILITARY and COMMERCIAL pay money, SCIENCE pays science, FIRSTs pay VP.

## 6. Clearing stale cards — DECIDED (want), mechanism *proposal*

*Proposal: a conveyor.* Market and goal rows fill from one end. At the end of each round the **oldest card drops off** and everything slides along, with a new card coming in. Stale cards leave on their own, and the row already reads as "a window of opportunity" (docs/05). Optional: the older a card is, the cheaper it gets.

Alternatives: (b) an action card that wipes the row ("New Administration"); (c) spend 1 money to discard a market card.

## What this changes elsewhere

- `docs/07`: drop Research and the Crew Capsule declaration; 4 slots become 2 crewed + 2 uncrewed; goal rewards and buying.
- `data/cards.json`: new `failures` and `actions` sections; a cost (science, money) on every buyable card; pad upgrades as cards.
- `data/objectives.json`: a `reward` field per goal; crewed/uncrewed instead of the capsule checks.
- `src/build_kit.py`: disaster and action card layouts, goal backs with reward icons, price on market cards.
- `src/build_table.py`: deck spot, crewed/uncrewed slots, automatic draw, bottom-decking, disaster resolution, buying.
