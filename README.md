# The World in One Day — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Brengsek27/news-image-20261120-r3/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Brengsek27/news-image-20261120-r3/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One page, one day: 69 verified stories from Friday 20 November 2026 — 20 illustrated cards (a cyclone landfall, a missile over Riyadh, COP31's final day, Voyager crossing one light-day, Harden's 51) plus 49 briefs on a dotted locator map. Every story happened, or was first reported, that Friday; disputed claims are attributed, and a DATE CHECK box names the big stories that were actually Thursday's. Entered on make.fun: https://make.fun/bounty/news-image-20261120

## Run it
- `python3 render.py` — regenerates `entry.png` (1024×1024) and `layout.json`; the render is deterministic.
- `python3 verify.py` — validates the PNG, re-renders twice and compares byte for byte, audits the layout (69 stories, 20 illustrated cards, no text below 9.5px, no overlaps), and tests the copier against corrupted PNGs.
- `node main.ts` — validates `entry.png` and copies it to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
