# Rocket Science / Triskelion

A board game that teaches rocket physics through interplanetary mission planning. 3-6 players. Each turn you build, deploy, and launch craft from a card-based catalog of real(ish) rocket stages, racing to complete historical and future mission objectives.

Designer: Alex Van de Sande.

**Site:** https://alexvansande.github.io/rocket-science/ — the card kit and playtest report, rebuilt from `data/` on every push to `main` (`.github/workflows/pages.yml`, landing page in `site/`). The playable prototype will live there too.

## Repo layout

```
data/         # cards.json, objectives.json — the game's source of truth
src/          # Python build scripts (HTML+PDF generation, SVG silhouettes)
docs/         # Design documentation (you are here)
site/         # Landing page for GitHub Pages (built outputs are added by CI)
build/        # Generated PDFs and HTML output (git-ignore in production)
```

## The pipeline

The project is split into four decoupled pieces, each reading the one before it:

```
                         ┌─ build_kit.py ─────────────► build/triskelion-kit.html/.pdf   (the cards)
data/cards.json ─────────┤
data/objectives.json     └─ playtest.py ──► build/playtest-results.json
                                                   └─ build_playtest_report.py ──► build/playtest-report.html
```

1. **`data/cards.json` + `data/objectives.json`** — the source of truth (all card numbers).
2. **`src/build_kit.py`** — renders the printable card layout (HTML, then PDF).
3. **`src/playtest.py`** — the rules+missions engine: audits the numbers and flies reference missions, emitting `build/playtest-results.json`.
4. **`src/build_playtest_report.py`** — visualizes those results as an HTML dashboard.

## Quickstart

```bash
cd src/

# Cards
python3 build_kit.py        # -> build/triskelion-kit.html (cards only)
# then render the PDF with either:
python3 -c "from weasyprint import HTML; HTML('../build/triskelion-kit.html').write_pdf('../build/triskelion-kit.pdf')"
# or headless Chrome (if WeasyPrint isn't installed):
# "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
#   --print-to-pdf=../build/triskelion-kit.pdf ../build/triskelion-kit.html

# Strips (only if card masses/Isps changed): regenerate the displacement-model strips
python3 regen_strips.py     # rewrites data/cards.json strips (token rows + equipment tail)

# Playtest + visual report
python3 playtest.py             # audits numbers, flies missions -> build/playtest-results.json (+ terminal report)
python3 tower_search.py         # brute-forces the dv envelope + cheapest mission stacks -> build/tower-search.json
python3 build_playtest_report.py  # -> build/playtest-report.html (missions + browsable tower stacks)
```

The kit PDF is **cards only** — engine, equipment, and objective pages. All design/rules text lives in `docs/*.md` (the canonical design memory). `playtest.py` exits nonzero if any card number is broken or a hard invariant fails, so it doubles as a regression test. Run it after editing any mass, Isp, or strip.

## Design docs (read in order)

1. **`docs/01-physics-model.md`** — The displacement model (the rocket equation we use, and why we don't use the additive model).
2. **`docs/02-engine-deck.md`** — Engine families, tech progression, unlock conditions.
3. **`docs/03-equipment-deck.md`** — Equipment cards and their roles.
4. **`docs/04-board-and-trajectories.md`** — Dv map, aerobraking, free-return trajectories.
5. **`docs/05-missions-and-tech-tree.md`** — Mission objectives, tech-label system, unlock mechanic.
6. **`docs/06-status-and-open-threads.md`** — What's done, what's pending, what's been tried and rejected.

## Current version

v0.3-playtest (June 2026). Apollo 11 mission verified end-to-end. Shuttle mission verified. Starship Mars architecture playable. Mars Ascent Vehicle added. Tech-label system (K1/H2/Hp3 etc) now visible on cards.

## Open threads

See `docs/06-status-and-open-threads.md`. Big-ticket items: event/failure deck, mission flow / market draft for objectives, faction asymmetry, Mars window dial physical component.
