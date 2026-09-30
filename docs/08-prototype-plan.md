# 08 — Digital Prototype Plan

Status: **draft for discussion, Sep 2026.** Goal: a playable version of the rules in `docs/07`, in the browser, on the GitHub Pages site. The point is to playtest the *loop* fast, not to make a finished video game.

## Principles

- **Same data, no second copy.** The prototype reads `data/cards.json`, `data/objectives.json` and `data/board.json` directly. Change a card mass, rerun, and the prototype changes.
- **No framework, no build step.** Plain JavaScript modules + SVG, served as static files. That matches the Python side (stdlib only) and keeps it hackable.
- **Rules engine separate from the screen.** `engine.js` is pure: `state + action → new state`, plus `legalActions(state)`. The UI only draws state and sends actions. That makes rules testable without a browser, and lets a later "rules card" swap engine behaviour, Fluxx-style.
- **The strip is the physics.** The engine only looks up printed strip rows; it never computes `ln`. Whatever the printed card says is what happens. That's also what players do at the table.
- **Reference missions are the tests.** Apollo 11, the Shuttle, Starship to Mars etc. are scripted as action sequences and replayed on every push. If a card change breaks Apollo, CI fails, just like `playtest.py` does today.

## Layout

```
site/play/index.html     the game page
site/play/engine.js      rules: state, legal actions, apply
site/play/ui.js          board (Alex's art, site/board.webp, with tokens placed from board.json), player boards, hand, cards
site/play/tests/         reference missions as action scripts (node --test)
data/board.json          spaces, links, crossing types, parking, positions on the image
```

CI copies `data/*.json` into the site. Card faces reuse the kit's renderer: `build_kit.py` also exports each card's HTML so the prototype shows the real cards, not look-alikes.

## Milestones

### M1 — Mission sandbox (one player, no turn limits)

**Progress (Sep 2026):** the table layout (`build/table.html`) is now playable for Blue: Research, Launch (+ free Mission Control), Mission Control, firing a placed rocket by picking a strip row, moving the token over reachable spaces, End turn with park-or-fail. Not yet: equipment and bundles in play, separation/splitting, aerobraking, consumables, unspent-Δv re-fire, goals.

Every card in hand, unlimited taps. Launch, pick a row, pay stages with cargo tokens, split, aerobrake, park or fail, eat consumables on the Mars route.

- **Done when:** Apollo 11, the Shuttle and Starship-to-Mars can be flown by clicking, and the same flights pass as scripted tests.
- **Needs from Alex:** answers to the board questions in `data/board.json` → `open_questions`. Nothing else, so **M1 can start now.**
- **Why first:** it tests the board + card physics loop on its own, which is the part most likely to surprise us.

### M2 — The Space Center turn

The player board with its three printed actions (Research, Launch, Mission Control), each used once. Launch places 4 red tokens + a free Mission Control. Hidden hand.

- **Needs:** starting hand, market size N, how many copies of each card.

### M3 — Goals

All FIRSTs face-up, 5-card market row, automatic claiming, flip for the reward.

- **Needs:** goal requirements in machine-readable form (today `objectives.json` has only a text `requires`), and **the reward sides, which don't exist yet.** Pad upgrades are the obvious first rewards.

### M4 — A real game at one table

2–4 players hot-seat, with a "pass the device" screen that hides hands. End condition, save/restore (so a game survives a page reload), and a log export for playtest notes.

- **Needs:** endgame trigger, player count.

### Later

Online multiplayer (needs a small server), event/failure deck, factions, Mars launch windows.

## Content gaps, by milestone

| Gap | Blocks | Placeholder so we can keep going |
|---|---|---|
| Board open questions (rocket icons, hatched bars, Mars descent) | M1 | Hatched = burn; rocket icon = nothing; Mars descent 1 burn + 3 free with heatshield |
| Starting hand, market N, card copies | M2 | K1, K2, H1, Crew Capsule, Atmospheric Return; N = 4; 2 copies of tier-1, 1 of the rest |
| Goal requirements as data | M3 | Hand-write them for the 16 main goals |
| Goal reward sides | M3 | Pad upgrades + the three improvements above |
| Endgame | M4 | First to N VP |

## Decisions for Alex

1. Plain JS, no framework, no build step: OK?
2. Hot-seat first, online later: OK?
3. Start M1 now, with the placeholders above for the board questions?
