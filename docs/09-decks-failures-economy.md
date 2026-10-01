# 09 — Personal decks, failures and the economy (v1 draft)

Status: **draft, Oct 2026**, from Alex's playtest notes. Items marked **DIRECTION (Alex)** are what Alex asked for; items marked *proposal* are Claude's suggestions awaiting a yes/no; **OPEN** items need a call before anything is built. Card physics (docs/01) is unchanged. This revises the Research action and the goal rewards in `docs/07`, and answers docs/06's "Economy: money in or out?" (in) and the event/failure deck item.

## 1. Your own deck — DIRECTION (Alex)

- Each player has **their own deck**, with a printed spot for it on the Space Center board.
- **Draw from the top, put cards back on the bottom.** No discard pile and no regular shuffle: the deck is a queue, so a card you used comes back around after the rest of your deck.
- **Starting hand: 3 cards.** Starting deck: ~16–20 cards, including the failure cards below.
- Cards you buy go into your deck. **OPEN:** to the bottom (you wait a full cycle for them), to the top (you draw it next turn), or straight into your hand?
- This replaces Research's "buy one card from the main deck / market / your discard" (docs/07). **OPEN:** is the per-turn draw the new Research action, and is buying a separate step (once per turn? as many as you can afford?)?

## 2. Failure cards — DIRECTION (Alex)

Failures are shuffled into the starting deck. Drawing one is a **disaster**:

1. Your hand goes back into your deck and the deck is shuffled.
2. You lose the rest of your turn.
3. You probably lose your missions in flight, unless a card protects you (see Redundancy).

Two kinds:

| Kind | Count | What happens to the card |
|---|---|---|
| **Teething failures** | 4–5 | Resolve, then the card is gone for good. The program gets more reliable just by flying. |
| **Category failures** | 4–5 | Shuffled back in with your hand. It keeps coming back until you buy the technology that fixes that category, which removes it. |

*Proposal, categories with their fixes* (real failure modes, each fixed by a real piece of engineering):

| Failure | Real case | Fixed by |
|---|---|---|
| Pogo oscillation | Gemini/Titan II, Apollo 6 | Pogo suppressor |
| Combustion instability | F-1 development | Baffled injector |
| Staging failure | many early launches | Stage-separation testing |
| Guidance failure | Ariane 5 flight 501 | Redundant flight computer |
| Life-support / fire | Apollo 1, Apollo 13 | Crew-safety review (crewed missions only?) |

### Density warning (simulated, see below)

At the proposed density (about half the starting deck is failures), a player **loses ~8–9 of their first 20 turns, has a 3-card hand on only ~4 of them, and usually fails on turn 2.** The density hurts, but the bigger cost is that a failure also throws back your *whole hand*, so you never build up the cards a launch needs.

| Starting deck (good + teething + category) | Turns lost / 20 | Turns with a 3+ card hand | Median first failure |
|---|---|---|---|
| 8 + 4 + 4 (16) | 8.4 | 3.7 | turn 2 |
| 10 + 5 + 5 (20) | 8.7 | 3.6 | turn 2 |
| 8 + 4 + 4, categories fixed on turn 8 | 5.5 | 8.0 | turn 1 |
| 14 + 3 + 3 (20) | 5.2 | 8.0 | turn 2 |
| 16 + 2 + 2 (20) | 3.6 | 10.9 | turn 3 |

(Monte Carlo, 20,000 games; 1 draw per turn, a good card bought every 2nd successful turn and put on the bottom, failures at setup redrawn. Missions lost are not counted. It's an upper bound on the pain, since no Redundancy is modelled.)

**OPEN, ways to soften** (pick one or none):
- (a) Fewer failures: 4–6 in a 20-card deck.
- (b) A failure costs your turn, but you **keep your hand**; only your deck is shuffled.
- (c) A failure hits **one mission** (the one that's flying, or your choice), not your whole program. This is also closer to the real history: Apollo 1 didn't ground Gemini's results.
- (d) Leave it brutal on purpose. Early space programs *were* mostly failures (Vanguard), and the teething cards thin out fast.

**OPEN:** how this sits with docs/06's earlier idea of small failures (crews can recover) vs big failures (catastrophic, crewed losses freeze you). Do crewed missions get a different outcome from robotic ones?

## 3. Action cards — DIRECTION (Alex)

The main deck holds **actions** as well as rockets and equipment. Examples:

- **Redundancy:** play it when you draw a failure. You ignore the failure this turn. The failure card is **not** removed: it goes back into the deck (*proposal:* to the bottom).
- **Meddling with an opponent's deck:** e.g. look at their top 3 and reorder them, or put a card of yours on top of their deck.
- **Stealing a card** from another player.

*Proposal, flavour names from history* (no real engine names, per CLAUDE.md, but historical events are fine): Operation Paperclip (take a card from an opponent's hand), Espionage (look at an opponent's top 3, reorder them), Budget Cut (an opponent loses one money card), Backup Systems (Redundancy).

**OPEN:** how are actions played? (Free, or with a Mission Control tap?) Is a played action card bottom-decked like any other card, or spent and gone?

## 4. Goal cards pay out — DIRECTION (Alex)

Completing a goal and flipping it shows a reward on the back. One of three:

| Reward | Icon | Use |
|---|---|---|
| **Victory points** | star | Win the game. |
| **Science** | atom | A **threshold**: kept, never spent. A market card needs "at least N science". |
| **Money** | money bag | **Spent:** turn the card over / discard it to pay. |

Market cards get a price, e.g. **"3 science (not spent) + 2 money (spent)".**

This replaces the **pad upgrades and tech unlocks on goal backs** from docs/07 ("the most important upgrades live on goal cards"). **OPEN:** do upgrades (Heavy pad, etc.) become cards you buy from the market, or do some goal backs still carry them?

**OPEN:** does one goal pay a single icon, or a mix (e.g. 2 money + 1 science)? Mixed rewards would let FIRSTs be worth more than contracts. The existing colours hint at a natural split: MILITARY and COMMERCIAL pay money, SCIENCE pays science, FIRSTs pay VP.

## 5. Clearing stale cards — DIRECTION (Alex), mechanism *proposal*

Alex wants a way to get rid of market and goal cards that nobody takes.

*Proposal: a conveyor.* Market and goal rows fill from one end. At the end of each round the **oldest card drops off** and everything slides along, with a new card coming in. Stale cards leave on their own, and the row already reads as "a window of opportunity" (docs/05). Optional: the older a card is, the cheaper it gets (1 money less in the last slot).

Alternatives: (b) an action card that wipes the row ("New Administration"); (c) a player may spend 1 money to discard a market card. The conveyor needs no decisions at the table, which fits "mechanical simplicity".

## What this changes elsewhere (once decided)

- `docs/07`: the Research action, goal rewards, components (personal deck spot, money/science/VP icons).
- `data/cards.json`: new `failures` and `actions` sections; a cost (science, money) on every buyable card.
- `data/objectives.json`: a `reward` field per goal.
- `src/build_kit.py`: failure and action card layouts, goal backs with reward icons, price on market cards.
- `src/build_table.py`: deck spot on each Space Center, draw/bottom-deck, failure resolution, buying.
