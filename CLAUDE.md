# CLAUDE.md — instructions for Claude Code sessions

This is a board-game design project. The goal is to make rocket engineering accessible for kids through interplanetary mission planning gameplay.

## Read this first

**Before changing anything, read `docs/01-physics-model.md` and `docs/06-status-and-open-threads.md`** (and `docs/07-rules-v0.md` for the turn loop, `docs/10-pacing.md` for what the game's phases and resources are for). They contain hard-won decisions that past Claude sessions repeatedly burned hours rediscovering. In particular:

1. **The rocket equation is the displacement model**: `dv = ve × ln(total / (dry + cargo))`. NOT the additive model. If you find yourself thinking "but shouldn't we add cargo to the launch mass?" — refer back to `docs/01-physics-model.md`. The answer is documented.

2. **Strip rows round to nearest integer.** Not floor, not ceiling. Ceiling was tried and overcompensated.

3. **Heritage cards represent the WHOLE STAGE AS FLOWN**, not individual engines. Saturn V's S-IC = one Heavy Kerolox Booster card despite having 5 F-1 engines internally. The Shuttle's two SRBs = two Heavy Solid Booster cards because they were physically separate stages.

4. **Apollo 11 should be ACHIEVABLE on a single Saturn V**, not require clustering. If playtest shows shortfall, nudge individual card masses by a few tons rather than introducing clustering rules.

5. **Saturn V should NOT reach Mars** — this is by design. Verifies the deck honors real physics.

## Code conventions

- Python 3, no fancy frameworks. WeasyPrint for HTML→PDF, pdf2image for verification.
- All data in `data/*.json`. All source in `src/*.py`. All docs in `docs/*.md`. Built output in `build/`.
- The build script (`src/build_kit.py`) reads from `../data/`. Run it from `src/`.
- Strip regeneration: `src/regen_strips.py` reads `../data/cards.json`, recomputes strips per the displacement model, writes back.
- Card silhouettes: `src/silhouettes.py`. Add new silhouettes by adding a function and registering it in `silhouette_for_engine()` or `silhouette_for_equipment()`.

## Design intent

- **Physical honesty over game balance.** Real Isps, real masses (snapped to base-4 token ladder).
- **Glance-readable cards.** Token visualization, no fractional rocket-equation lookup at the table.
- **Tech-tree progression** is the deck-building loop. Cards have `tech_label` (K1, H2, Hp3, etc.) visible bottom-left of silhouette.
- **The user (Alex) is the designer and playtester.** Don't decide anything significant alone — ask. The user prefers blunt correction over flattery and dislikes AI-typical filler.

## What NOT to do

- Don't propose clustering as a fix when Apollo is short by 1 dv. Tune the card masses instead.
- Don't reintroduce dropped cards (see `docs/02-engine-deck.md` for the list of permanently-dropped cards).
- Don't name generic precursor cards after real specific engines (no "Merlin" or "Falcon"). Use generic names with historical footnotes.
- Don't switch back to the additive rocket equation. Refer to `docs/01-physics-model.md` if tempted.
- Don't over-engineer. The user values mechanical simplicity highly.

## File ownership

- `src/build_kit.py` and `src/silhouettes.py`: rendering code. Edit freely.
- `src/regen_strips.py`: strip math. Edit if the displacement model needs adjusting (it shouldn't).
- `data/cards.json` and `data/objectives.json`: source of truth. Edit via scripts, not by hand if possible.
- `docs/*.md`: design memory. Update when decisions change.
- `build/*.pdf` and `build/*.html`: generated, don't commit (see `.gitignore`).
- `files/board art/`: Alex's art working folder (board PDFs/SVGs, AI files, historical kit exports). **READ-ONLY — never modify, delete, or write into it.** Read it for reference (the current board is `files/board art/earth to mars.pdf`), but treat it as Alex's exclusive domain.
- `src/playtest.py`: the rules+missions engine. Run from `src/` (`python3 playtest.py`). Audits card numbers (recomputes every strip row) and flies reference missions (Apollo, Shuttle/Hubble, Starship-to-Mars, level-1-only, Saturn-V invariant) against the board dv budgets. Emits `build/playtest-results.json` and prints a terminal report; exits nonzero on any data bug or broken invariant. Run it after changing any card mass, Isp, or strip.
- `src/build_playtest_report.py`: visualizer. Reads `build/playtest-results.json` → `build/playtest-report.html` (standalone dashboard with dv-cascade bars; renders the real cards per mission by importing `build_kit`). Keep it presentation-only; all rules logic stays in `playtest.py`.
- `data/board.json` + `site/board.webp`: the board as data (spaces, links, crossing types, parking, x/y on the image), transcribed from the board PDF, and Alex's board art rendered small for the web. **Always show Alex's art, never a generated redraw** (tried, rejected). The prototype overlays tokens on the image using the JSON positions. Plan: `docs/08-prototype-plan.md`.
- `src/build_table.py`: the table layout (`build/table.html`, on the site): the whole game set up at real size in mm (A2 board, 47x66 cards, 4 seats rotated to face their edges). No game logic yet: pan, zoom (wheel / pinch / slider), a soft CSS tilt (rotateX 18°), a lamp-glow background painted on the viewport (not a giant element: GPU layer limits clip it), and hands that flip on click / pull a card forward / 'activate' (placeholder toast until the engine exists). Decks are real CSS 3D boxes (card back on top at n×0.3mm, striped card-edge sides; `#tilt`/`#table` are preserve-3d and zoom uses scale3d so depth scales). `#view=x,y,zoom` in the URL (table mm) opens a given view — useful for screenshots/sharing. Reuses the kit's card renderers. **Playable for Blue (you):** `GAME_JS` in `build_table.py` is a small state machine following `docs/09` (your own deck: draw at END of turn, used cards to the bottom; disasters resolve against your missions, then goals pay out, then completed missions return their cards; buy from the market with money/science; launched but met no goal → discard the rightmost mission card, take a 💰1 card (`st.cash`); pay $1 to discard the rightmost market card and take the first player token; slots I–II crewed, the crew takes the first equipment slot; Launch = pick a slot + your pad's tokens + a free Mission Control; Mission Control = pick card → confirm → pick an eligible mission (can pay T, lights on Earth if on the pad); click the placed rocket → close-up → pick a row → old tokens spent/discarded, row tokens placed → reachable spaces (BFS over `board.json` links, 1 Δv per crossing) glow → click to move; End turn loses missions not at a stop). Needs Python ≥ 3.12 (nested f-string quotes): `python3.12 build_table.py`. Game data (card ids, printed strip rows, board positions in mm) is embedded as `#game-data`. Gotcha: `#tilt`/`#table` are `pointer-events:none` because Chrome hit-tests preserve-3d parent planes in front of their children.
- `src/tower_search.py`: brute-force the dv envelope. DP over the chain model (each stage = a cluster of 1-4 identical cards; resulting mass `N×total` is independent of cargo, so reachable masses are a small fixed set). Maps the max-dv tower per payload and which cards appear in optimal stacks — surfaces overpowered/dominated cards. Excludes engine-less tanks (Drop Tank). Writes `build/tower-search.json`. Note: assumes ALL cards unlocked, so it's the late-game ceiling, not early-game progression.
