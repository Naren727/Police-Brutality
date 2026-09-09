# Police-Brutality Streamlit Dashboard — Design Spec

## Purpose

The repo currently contains one exploratory Jupyter notebook (`Police Brutality.ipynb`) plus a `.pbix` Power BI file — neither is hostable on the web, and despite the README's "joined against income + poverty by state" framing, no such join actually exists in the code: each of the 4 datasets (killings, income, poverty, race-by-city) is cleaned and charted independently. This spec turns the notebook's analysis into a hosted Streamlit dashboard, and adds the missing state-level join as a genuinely new piece of analysis.

## Data Notes (from direct inspection)

- `PoliceKillingsUS.csv`: 2,535 rows, columns `id, name, date, manner_of_death, armed, age, gender, race, city, state, signs_of_mental_illness, threat_level, flee, body_camera`. `state` is a 2-letter code.
- `MedianHouseholdIncome2015.csv` (29,322 rows) and `PercentagePeopleBelowPovertyLevel.csv` (29,329 rows): both use `Geographic Area` (capital A) as the state-code column, city-level granularity.
- `ShareRaceByCity.csv` (29,268 rows): uses `Geographic area` (lowercase a) for the same thing — an inconsistency to normalize away, not preserve.
- The 3 auxiliary CSVs are saved with old Mac-style CR-only line endings. This looks broken in a plain text editor, but `pandas.read_csv(..., encoding='cp1252')` already parses all rows correctly (verified: row counts above are post-parse) — no special line-terminator handling is needed in code, just a comment noting why the raw file looks odd if someone opens it directly.
- No population data exists anywhere in this dataset. The state-level join can only compare raw killings **counts** against income/poverty/race — not a per-capita rate. This limitation is surfaced to the viewer, not hidden.

## Architecture

Three focused modules instead of one monolithic script:

- **`data.py`** — pure data loading/cleaning functions, one per source (`load_killings`, `load_income`, `load_poverty`, `load_race`), each `@st.cache_data`-decorated. Preserves the original notebook's cleaning decisions (median age fill, `"unarmed"`/`"Not fleeing"` defaults for missing `armed`/`flee`, race-code-to-name mapping, `-`/`(X)` treated as missing in the Census-derived files) since those were reasonable choices already made once. Adds `build_state_join()`, which aggregates income/poverty/race to state level (`groupby('state').mean()`) and merges them with killings counts per state into one dataframe — this is the piece that didn't exist before.
- **`charts.py`** — one function per chart, each taking a dataframe and returning a themed Plotly figure. Centralizes the color palette so every chart is visually consistent instead of each notebook cell picking its own `color_discrete_sequence`.
- **`app.py`** — the Streamlit page itself: page config, section layout, calls into `data.py` and `charts.py`. No data manipulation or chart construction logic lives here.

## Visual Design — restrained data-journalism palette

- Background: soft off-white (`#f7f5f2`), text: charcoal (`#2b2b2b`) — set via `.streamlit/config.toml` theme, not injected CSS.
- Primary chart color: muted steel blue (`#3b5b7c`). Secondary/emphasis color (used sparingly, for the poverty-adjacent metric and mental-illness "present" slice): muted maroon (`#a13d3d`).
- Fixed race-category palette (replaces the notebook's arbitrary `bisque/aquamarine/pink` list): White `#8c9db5`, Black `#3b5b7c`, Hispanic `#a13d3d`, Asian `#6b8f71`, Native `#c08a4e`, Other `#9a9a9a`.
- Single-series histograms (armed, flee, threat level) use one muted blue bar color instead of a different color per bar — a rainbow bar chart reads as decorative, not serious.
- Choropleths: killings count and income use a monochromatic `Blues` scale; poverty rate uses `OrRd` (the one metric where "higher = more concerning" benefits from a warm scale) — replacing the original notebook's arbitrary `bluyl`/`twilight`/`icefire`.

## Page Structure

1. **Overview** — title, then the `Inference.md` narrative rewritten as 2-3 short paragraphs of prose (not a bullet dump) introducing what the dashboard covers and its main high-level findings.
2. **Victim demographics** — the existing 7 charts (race, age, gender, armed, mental illness, flee, threat level; manner-of-death vs. age box plot), laid out in a 2-column grid via `st.columns`, re-themed per above. Content/insights unchanged from the notebook — this section is a re-skin, not a redesign.
3. **Geographic view** — the 3 existing choropleths (killings by state, median income by state, poverty rate by state), in `st.tabs` so they don't stack endlessly.
4. **State-level relationships** *(new)* — a short paragraph explaining what's being joined and why (raw counts, not per-capita — see limitations), the combined state table (`st.dataframe`), and two scatter plots side by side: killings count vs. poverty rate, killings count vs. median income, each with an OLS trend line (`plotly.express` `trendline="ols"`, which needs `statsmodels` as a dependency).
5. **Methodology & limitations** — a visible closing note: no population data (so these are counts, not rates), the dataset is a fixed historical snapshot from the original Kaggle source (not live/current), and the state join uses simple unweighted city-level averages for income/poverty/race.

## Hosting

Streamlit Community Cloud (free, direct-from-GitHub deploy) — matches the original completeness-review recommendation. Total CSV size (~2.6MB combined) is small enough to commit directly; no Git LFS needed. Requires `requirements.txt` (`streamlit`, `pandas`, `plotly`, `statsmodels` for the trendline) and `app.py` as the entrypoint, both added by this plan.

## Explicitly out of scope

- The `.pbix` Power BI file is left untouched in the repo — not part of the web deliverable, not deleted.
- No new data sources (e.g. fetching real population figures to compute per-capita rates) — that would be a materially bigger scope than "make what's here hostable," and is called out as a known limitation instead.
- No authentication, database, or write-path — this is a read-only public dashboard over static CSVs.

## Testing

This is a data/viz project with no user-input business logic to unit test in the traditional sense (unlike Naikutty's form). Verification is: (1) a smoke-check script that calls every `data.py` function and asserts non-empty, expected-shape output (catches silent parsing regressions), and (2) manual verification of the running Streamlit app — every section renders, the state join table has a reasonable row count (~50 states + DC), and no chart errors out.

## Self-Review Notes

- No placeholders — palette, page structure, module boundaries, and the join methodology are all fully specified.
- Scope: one cohesive dashboard build; not decomposed further since all 4 sections share the same data layer and are meant to be viewed together.
- Ambiguity resolved: "join depth" is table + scatter with trendlines (not raw correlation coefficients, per your answer), tone is restrained/data-journalism (not matching Naikutty's playful branding, per your answer), and the missing per-capita normalization is explicitly surfaced as a limitation rather than worked around.
