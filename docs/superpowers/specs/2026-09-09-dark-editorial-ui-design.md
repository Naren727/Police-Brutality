# Dark Editorial UI — Design Spec

## Purpose

The first dashboard build worked but landed on an off-white/steel-blue palette that reads too close to the Naikutty project's light warm theme, and several charts carry readability problems inherited from the original notebook (rainbow bars, two-slice pies, alphabetical category ordering). This spec replaces the visual layer with a dark editorial treatment ("Dossier") — validated after comparing three directions side by side in a browser — and fixes the chart-level problems while it's in there.

Scope is the presentation layer only. The data pipeline (`data.py`) and the state-level join built in the previous spec are unchanged apart from one added function.

## Canvas, type, and ink

| Role | Value |
|---|---|
| Page plane | `#0d0d0d` |
| Panel / chart surface | `#1a1a19` |
| Panel border | `rgba(255,255,255,0.08)` |
| Gridline | `#2c2c2a` |
| Primary ink | `#ffffff` |
| Secondary ink | `#c3c2b7` |
| Muted ink (axes, labels) | `#898781` |

Typefaces (Google Fonts, loaded via the injected stylesheet):
- **Instrument Serif** — the hero headline only. Large, editorial, with one italic accent phrase.
- **Inter** — body copy, chart text, table text.
- **JetBrains Mono** — section eyebrows, stat-tile labels, the methodology footer. Always uppercase with ~0.15em letter-spacing.

## Chart palette

Three hues, one per context. **Validated with the dataviz skill's `validate_palette.js` against the `#1a1a19` surface under `--pairs all`**: worst pair ΔE 20.9 normal-vision / 9.4 CVD, all three ≥3:1 contrast. (A first attempt using amber `#c98500` + red `#e66767` was rejected by the validator at ΔE 13.0, below the 15 normal-vision floor.)

| Hue | Hex | Used for |
|---|---|---|
| Blue | `#3987e5` | Every single-series chart (bars, histogram, box, scatter) and the killings choropleth ramp |
| Aqua-green | `#199e70` | Median income choropleth ramp |
| Orange | `#d95926` | Poverty rate choropleth ramp, and the editorial accent (hero italic, section numbers) |

Sequential choropleth ramps run **dark → luminous** so the low end recedes toward the surface:

- Blue: `#12233a` → `#2a5f9e` → `#5598e7`
- Aqua: `#0e2b22` → `#137a56` → `#3fc294`
- Orange: `#3a1a0e` → `#a8401c` → `#f07a45`

Reusing the poverty hue as the brand accent is deliberate — it keeps the interface and the data on one palette instead of introducing a decorative fourth color.

## Chart changes (beyond recoloring)

1. **Single-hue bars.** The current charts assign a different color per category, which only duplicates the x-axis label. All single-series bars become one blue.
2. **Sort by value, descending.** Categorical bars are currently alphabetical, which hides the ranking. `killings_by_race`, `killings_by_armed`, `killings_by_flee`, and `killings_by_threat_level` all sort by count.
3. **Both pie charts are removed.** Gender (95.8% / 4.2%) and mental illness (74.9% / 25.1%) are two-value splits — a two-slice pie is a well-known anti-pattern. They become HTML stat blocks: a large percentage, a caption, and a thin proportion bar.
4. **Age becomes a histogram** rather than a strip plot; it's a distribution.
5. **`killings_by_armed` becomes a horizontal top-10 bar.** The column has dozens of long category names that are unreadable on a vertical axis.
6. **Mark specs** from the dataviz skill: 4px rounded bar ends, scatter markers ≥8px with a 2px surface-colored ring, 2px trendlines in muted ink, recessive gridlines, direct value labels on the race bars (not on every chart).

## Page structure

- **Masthead** — mono kicker ("An investigation · US police use of force"), the hero headline in Instrument Serif with one orange italic phrase, and a deck paragraph.
- **KPI band** — four stat tiles (total incidents, states covered, % male, median age) separated by hairlines, values in tabular numerals, labels in mono. Computed from the real data via a new `headline_stats()` function, never hardcoded.
- **01 — Victim demographics** — the two stat splits (gender, mental illness) followed by the chart grid.
- **02 — Geography** — the three choropleths in tabs.
- **03 — State-level relationships** — the join explanation, the combined table, and the two scatter plots.
- **Methodology footer** — unchanged copy, restyled in muted mono.

Each numbered section renders as a mono eyebrow (`01 — VICTIM DEMOGRAPHICS`) followed by a hairline rule.

## Architecture

One new module keeps presentation out of the page file:

- **`theme.py`** *(new)* — owns *how it looks*: color constants, the registered Plotly template (`"dossier"`, set as the default so charts inherit surface/font/grid without repeating layout dicts), the injected CSS, and small render helpers (`masthead`, `section`, `kpi_band`, `stat_split`) that emit the custom HTML blocks.
- **`charts.py`** — rewritten against the template; every function still returns a `go.Figure`, so its contract with `app.py` is unchanged apart from the removed pie functions and the renamed age function.
- **`data.py`** — one addition, `headline_stats()`; all existing functions untouched.
- **`app.py`** — layout only, calling `theme` helpers and `charts` functions.
- **`.streamlit/config.toml`** — switched to a dark base so Streamlit's own chrome (tabs, table, scrollbars) matches.

## Testing

`smoke_check.py` is updated to match the new chart surface: it drops the two removed pie functions, adds the renamed `age_distribution`, and asserts `headline_stats()` returns the four expected keys with sane values (total equal to the killings row count, states between 45 and 55, male percentage between 90 and 100). Manual verification covers the rendered app: every section renders on the dark canvas, fonts load, the KPI band shows real computed numbers, bars are sorted and single-hued, and the three choropleths each use their own ramp.

## Explicitly out of scope

- No change to the data cleaning, the state join, or the methodology caveats — the "raw counts, not per-capita rates" warning stays exactly where it is.
- No new charts or data sources; this is a visual rebuild of what already exists, minus the two pies.
- No light-mode variant. The dark palette was selected and validated against the dark surface specifically; a light mode would need its own validated steps and isn't part of this work.

## Self-Review Notes

- No placeholders — every color, ramp, font, section, and file boundary is specified above.
- Consistency check: the removed pie charts are reflected in both the chart-changes section and the testing section; the added `headline_stats()` appears in both architecture and testing.
- Ambiguity resolved: the orange accent serves double duty (poverty ramp + brand accent) by explicit choice rather than accident; trendline and gridline colors are muted ink, not series colors, per the dataviz rule that text and chrome never wear series color.
