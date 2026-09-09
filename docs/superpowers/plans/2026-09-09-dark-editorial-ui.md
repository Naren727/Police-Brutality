# Dark Editorial UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the dashboard's light off-white presentation layer with the dark editorial "Dossier" treatment and fix the inherited chart readability problems, per `docs/superpowers/specs/2026-09-09-dark-editorial-ui-design.md`.

**Architecture:** A new `theme.py` owns everything visual — color constants, a registered Plotly template that every figure inherits, the injected stylesheet, and the HTML render helpers (masthead, KPI band, section headers, stat splits). `charts.py` is rewritten against that template, `data.py` gains one function, and `app.py` becomes pure layout.

**Tech Stack:** Streamlit, Plotly (`express` + `graph_objects` + `plotly.io` templates), pandas. No new dependencies.

## Global Constraints

- **Do not substitute chart colors.** `#3987e5` (blue), `#199e70` (aqua), `#d95926` (orange) were validated together with the dataviz skill's `validate_palette.js` against the `#1a1a19` surface under `--pairs all`. Changing any of them requires re-running that validator.
- Surfaces: page `#0d0d0d`, panels/charts `#1a1a19`, borders `rgba(255,255,255,0.08)`, grid `#2c2c2a`. Ink: `#ffffff` primary, `#c3c2b7` secondary, `#898781` muted.
- Gridlines, axes, trendlines and text never wear a series color — they use muted ink.
- Every categorical bar chart is single-hue and sorted by value descending.
- All KPI/stat figures are computed from the data, never hardcoded in the page copy.

---

### Task 1: `theme.py` and the dark Streamlit base

**Files:**
- Create: `theme.py`
- Modify: `.streamlit/config.toml`

**Interfaces:**
- Produces: constants `PAGE, SURFACE, BORDER, GRID, INK, INK_SECONDARY, INK_MUTED, BLUE, AQUA, ORANGE, ACCENT, RAMP_BLUE, RAMP_AQUA, RAMP_ORANGE, TEMPLATE`; functions `apply()`, `masthead(kicker, title_html, deck)`, `kpi_band(items)`, `section(number, label, title)`, `stat_split(value, label, pct, foot)`, `body(text_html)`, `methodology(text_html)` — consumed by `charts.py` (Task 3) and `app.py` (Task 4).

- [ ] **Step 1: Create `theme.py`**

```python
"""Dark editorial theme: colors, Plotly template, injected CSS, and layout helpers."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- Surfaces and ink -------------------------------------------------------
PAGE = "#0d0d0d"
SURFACE = "#1a1a19"
BORDER = "rgba(255,255,255,0.08)"
GRID = "#2c2c2a"
INK = "#ffffff"
INK_SECONDARY = "#c3c2b7"
INK_MUTED = "#898781"

# --- Data hues --------------------------------------------------------------
# Validated with the dataviz skill's validate_palette.js against the #1a1a19
# surface under --pairs all: worst pair dE 20.9 normal-vision / 9.4 CVD, all
# three >= 3:1 contrast. Re-run that validator before changing any of these.
BLUE = "#3987e5"
AQUA = "#199e70"
ORANGE = "#d95926"
ACCENT = ORANGE

# Sequential ramps run dark (near-surface) -> luminous.
RAMP_BLUE = [[0.0, "#12233a"], [0.5, "#2a5f9e"], [1.0, "#5598e7"]]
RAMP_AQUA = [[0.0, "#0e2b22"], [0.5, "#137a56"], [1.0, "#3fc294"]]
RAMP_ORANGE = [[0.0, "#3a1a0e"], [0.5, "#a8401c"], [1.0, "#f07a45"]]

TEMPLATE = "dossier"


def _register_template() -> None:
    pio.templates[TEMPLATE] = go.layout.Template(
        layout=dict(
            paper_bgcolor=SURFACE,
            plot_bgcolor=SURFACE,
            colorway=[BLUE, ORANGE, AQUA],
            font=dict(family="Inter, system-ui, sans-serif", color=INK_SECONDARY, size=12),
            title=dict(font=dict(color=INK, size=15), x=0, xanchor="left"),
            margin=dict(l=8, r=8, t=52, b=8),
            xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=INK_MUTED, size=11),
                       title=dict(font=dict(color=INK_MUTED, size=11))),
            yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=INK_MUTED, size=11),
                       title=dict(font=dict(color=INK_MUTED, size=11))),
            hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER,
                            font=dict(color=INK, family="Inter, system-ui, sans-serif")),
            legend=dict(font=dict(color=INK_SECONDARY)),
        )
    )
    pio.templates.default = TEMPLATE


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

.stApp { background: #0d0d0d; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppViewBlockContainer"], .block-container { max-width: 1180px; padding-top: 3.2rem; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

.kicker {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: #898781; display: flex; align-items: center; gap: 14px;
}
.kicker::after { content: ''; flex: 1; height: 1px; background: #2c2c2a; }
.hero-title {
  font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; color: #ffffff;
  font-size: clamp(38px, 6vw, 68px); line-height: 1.04; letter-spacing: -0.015em;
  margin: 20px 0 12px;
}
.hero-title em { font-style: italic; color: #d95926; }
.deck { font-size: 16px; line-height: 1.65; color: #c3c2b7; max-width: 64ch; margin-bottom: 30px; }

.kpi-band {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #2c2c2a;
  border-top: 1px solid #2c2c2a; border-bottom: 1px solid #2c2c2a; margin: 4px 0 34px;
}
.kpi { background: #0d0d0d; padding: 18px 16px 20px; }
.kpi .v { font-size: 34px; font-weight: 600; color: #ffffff; letter-spacing: -0.02em;
          font-variant-numeric: tabular-nums; line-height: 1; }
.kpi .l { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.14em;
          text-transform: uppercase; color: #898781; margin-top: 8px; }

.section-head { margin: 34px 0 18px; }
.section-head .eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: #898781; display: flex; align-items: center; gap: 14px;
}
.section-head .eyebrow .num { color: #d95926; }
.section-head .eyebrow::after { content: ''; flex: 1; height: 1px; background: #2c2c2a; }
.section-head h2 {
  font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; color: #ffffff;
  font-size: 32px; letter-spacing: -0.01em; margin: 12px 0 0;
}

.stat-split {
  border: 1px solid rgba(255,255,255,0.08); background: #1a1a19; border-radius: 8px;
  padding: 22px 24px 24px;
}
.stat-split .v { font-size: 44px; font-weight: 600; color: #ffffff; letter-spacing: -0.02em;
                 font-variant-numeric: tabular-nums; line-height: 1; }
.stat-split .l { font-size: 14px; color: #c3c2b7; margin-top: 10px; }
.stat-split .track { height: 6px; border-radius: 3px; background: #2c2c2a; margin-top: 18px; overflow: hidden; }
.stat-split .fill { height: 100%; border-radius: 3px; background: #3987e5; }
.stat-split .foot { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.12em;
                    text-transform: uppercase; color: #898781; margin-top: 12px; }

[data-testid="stPlotlyChart"] {
  border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; background: #1a1a19; padding: 6px;
}

[data-testid="stTabs"] button {
  font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
  letter-spacing: 0.12em; text-transform: uppercase; color: #898781 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] { color: #ffffff !important; }

[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; }

.body-copy { font-size: 15px; line-height: 1.7; color: #c3c2b7; max-width: 72ch; margin-bottom: 18px; }
.body-copy strong { color: #ffffff; font-weight: 600; }

.method {
  font-family: 'JetBrains Mono', monospace; font-size: 10.5px; line-height: 1.9;
  letter-spacing: 0.04em; color: #898781; border-top: 1px solid #2c2c2a;
  padding-top: 18px; margin-top: 40px;
}
</style>
"""


def apply() -> None:
    """Register the Plotly template and inject the stylesheet. Call once, first."""
    _register_template()
    st.markdown(_CSS, unsafe_allow_html=True)


def masthead(kicker: str, title_html: str, deck: str) -> None:
    st.markdown(
        f'<div class="kicker">{kicker}</div>'
        f'<h1 class="hero-title">{title_html}</h1>'
        f'<p class="deck">{deck}</p>',
        unsafe_allow_html=True,
    )


def kpi_band(items) -> None:
    """items: sequence of (value, label) pairs, already formatted as strings."""
    cells = "".join(
        f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div></div>'
        for value, label in items
    )
    st.markdown(f'<div class="kpi-band">{cells}</div>', unsafe_allow_html=True)


def section(number: str, label: str, title: str) -> None:
    st.markdown(
        f'<div class="section-head">'
        f'<div class="eyebrow"><span class="num">{number}</span> {label}</div>'
        f"<h2>{title}</h2>"
        f"</div>",
        unsafe_allow_html=True,
    )


def stat_split(value: str, label: str, pct: float, foot: str) -> None:
    st.markdown(
        f'<div class="stat-split">'
        f'<div class="v">{value}</div>'
        f'<div class="l">{label}</div>'
        f'<div class="track"><div class="fill" style="width:{pct:.1f}%"></div></div>'
        f'<div class="foot">{foot}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def body(text_html: str) -> None:
    st.markdown(f'<div class="body-copy">{text_html}</div>', unsafe_allow_html=True)


def methodology(text_html: str) -> None:
    st.markdown(f'<div class="method">{text_html}</div>', unsafe_allow_html=True)
```

- [ ] **Step 2: Switch the Streamlit base theme to dark**

Replace the contents of `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
backgroundColor = "#0d0d0d"
secondaryBackgroundColor = "#1a1a19"
textColor = "#ffffff"
primaryColor = "#d95926"
font = "sans serif"
```

- [ ] **Step 3: Verify the module imports and registers the template**

```bash
.venv/Scripts/python -c "import theme; theme._register_template(); import plotly.io as pio; print(pio.templates.default)"
```

Expected: prints `dossier`.

- [ ] **Step 4: Commit**

```bash
git add theme.py .streamlit/config.toml
git commit -m "feat: add dark editorial theme module and switch Streamlit to a dark base"
```

---

### Task 2: `headline_stats()` in `data.py`

**Files:**
- Modify: `data.py`
- Modify: `smoke_check.py`

**Interfaces:**
- Produces: `headline_stats() -> dict` with keys `total` (int), `states` (int), `male_pct` (float), `median_age` (float), `mental_illness_pct` (float) — consumed by `app.py` (Task 4).

- [ ] **Step 1: Add the failing assertion to `smoke_check.py`**

Insert immediately after the existing `state_df` assertions (before the `print("All data smoke checks passed.")` line), and add `headline_stats` to the import at the top of the file:

```python
stats = headline_stats()
assert set(stats) == {"total", "states", "male_pct", "median_age", "mental_illness_pct"}
assert stats["total"] == len(killings)
assert 45 <= stats["states"] <= 55
assert 90 <= stats["male_pct"] <= 100
assert 20 <= stats["median_age"] <= 60
assert 0 <= stats["mental_illness_pct"] <= 100
```

Change the import line to:

```python
from data import load_killings, load_income, load_poverty, load_race, build_state_join, headline_stats
```

- [ ] **Step 2: Run it to verify it fails**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: `ImportError: cannot import name 'headline_stats' from 'data'`.

- [ ] **Step 3: Implement `headline_stats()`**

Append to `data.py`:

```python
@st.cache_data
def headline_stats() -> dict:
    """Top-line figures for the masthead KPI band, computed from the data."""
    df = load_killings()
    return {
        "total": int(len(df)),
        "states": int(df["state"].nunique()),
        "male_pct": float((df["gender"] == "M").mean() * 100),
        "median_age": float(df["age"].median()),
        "mental_illness_pct": float((df["signs_of_mental_illness"] == True).mean() * 100),
    }
```

- [ ] **Step 4: Run the smoke check to verify it passes**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: data checks pass (the chart checks at the bottom of the file still reference the old chart functions and will be updated in Task 3 — if they fail here, that is expected and Task 3 fixes them).

- [ ] **Step 5: Commit**

```bash
git add data.py smoke_check.py
git commit -m "feat: add headline_stats for the masthead KPI band"
```

---

### Task 3: Rewrite `charts.py` against the theme

**Files:**
- Modify: `charts.py` (full rewrite)
- Modify: `smoke_check.py` (chart list)

**Interfaces:**
- Consumes: constants from `theme.py` (Task 1), dataframes from `data.py`.
- Produces: `killings_by_race`, `age_distribution`, `killings_by_armed`, `killings_by_flee`, `killings_by_threat_level`, `manner_of_death_by_age`, `choropleth_killings_by_state`, `choropleth_income_by_state`, `choropleth_poverty_by_state`, `killings_vs_poverty_scatter`, `killings_vs_income_scatter` — 11 functions, each returning a `go.Figure`, consumed by `app.py` (Task 4). **`killings_by_gender` and `killings_by_mental_illness` are deleted** (replaced by `theme.stat_split`).

- [ ] **Step 1: Replace the contents of `charts.py`**

```python
"""Chart builders for the dashboard. Every figure inherits the 'dossier' template."""
import plotly.express as px
import plotly.graph_objects as go

from theme import (BLUE, GRID, INK_MUTED, INK_SECONDARY, RAMP_AQUA, RAMP_BLUE,
                   RAMP_ORANGE, SURFACE)


def _counts(df, column, top_n=None):
    """Value counts as a two-column frame, already sorted descending."""
    counts = df[column].value_counts()
    if top_n is not None:
        counts = counts.head(top_n)
    counts = counts.reset_index()
    counts.columns = [column, "count"]
    return counts


def _bar_marks(fig):
    """Shared bar spec: one hue, 4px rounded ends, no legend."""
    fig.update_traces(marker_color=BLUE, marker_cornerradius=4)
    fig.update_layout(showlegend=False, bargap=0.35)
    return fig


def killings_by_race(df):
    counts = _counts(df, "race")
    fig = px.bar(counts, x="race", y="count", title="Victims by race", text="count")
    fig.update_traces(textposition="outside", cliponaxis=False,
                      textfont=dict(color=INK_SECONDARY, size=11))
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return _bar_marks(fig)


def age_distribution(df):
    fig = px.histogram(df, x="age", nbins=40, title="Age distribution")
    fig.update_layout(xaxis_title="Age", yaxis_title="Victims")
    return _bar_marks(fig)


def killings_by_armed(df, top_n=10):
    counts = _counts(df, "armed", top_n=top_n).sort_values("count")
    fig = px.bar(counts, x="count", y="armed", orientation="h",
                 title=f"What victims were armed with (top {top_n})")
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return _bar_marks(fig)


def killings_by_flee(df):
    counts = _counts(df, "flee")
    fig = px.bar(counts, x="flee", y="count", title="Did the victim attempt to flee?")
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return _bar_marks(fig)


def killings_by_threat_level(df):
    counts = _counts(df, "threat_level")
    fig = px.bar(counts, x="threat_level", y="count",
                 title="Threat level recorded by the officer")
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return _bar_marks(fig)


def manner_of_death_by_age(df):
    fig = px.box(df, x="manner_of_death", y="age", title="Manner of death by age")
    fig.update_traces(marker_color=BLUE, line_color=BLUE,
                      fillcolor="rgba(57,135,229,0.18)")
    fig.update_layout(xaxis_title=None, yaxis_title="Age", showlegend=False)
    return fig


def _choropleth(locations, z, title, colorscale):
    fig = go.Figure(
        go.Choropleth(
            locations=locations, locationmode="USA-states", z=z, colorscale=colorscale,
            marker_line_color=SURFACE, marker_line_width=0.6,
            colorbar=dict(thickness=10, outlinewidth=0, len=0.7,
                          tickfont=dict(color=INK_MUTED, size=10)),
        )
    )
    fig.update_layout(
        title=title, height=430, margin=dict(l=8, r=8, t=52, b=8),
        geo=dict(scope="usa", bgcolor=SURFACE, lakecolor=SURFACE,
                 landcolor="#232322", subunitcolor=GRID, coastlinecolor=GRID),
    )
    return fig


def choropleth_killings_by_state(state_counts: dict):
    return _choropleth(list(state_counts.keys()), list(state_counts.values()),
                       "Recorded killings by state", RAMP_BLUE)


def choropleth_income_by_state(income_df):
    grouped = income_df.groupby("state")["Median Income"].mean().reset_index()
    return _choropleth(grouped["state"], grouped["Median Income"],
                       "Average median household income by state", RAMP_AQUA)


def choropleth_poverty_by_state(poverty_df):
    grouped = poverty_df.groupby("state")["poverty_rate"].mean().reset_index()
    return _choropleth(grouped["state"], grouped["poverty_rate"],
                       "Average poverty rate by state", RAMP_ORANGE)


def _scatter(state_df, x, title, x_title):
    fig = px.scatter(state_df, x=x, y="killings_count", trendline="ols",
                     hover_name="State", title=title)
    fig.update_traces(selector=dict(mode="markers"),
                      marker=dict(size=10, color=BLUE, line=dict(width=2, color=SURFACE)))
    for trace in fig.data:
        if trace.mode == "lines":
            trace.line.color = INK_MUTED
            trace.line.width = 2
    fig.update_layout(xaxis_title=x_title, yaxis_title="Recorded killings", showlegend=False)
    return fig


def killings_vs_poverty_scatter(state_df):
    return _scatter(state_df, "poverty_rate", "Killings vs. poverty rate",
                    "Avg. poverty rate (%)")


def killings_vs_income_scatter(state_df):
    return _scatter(state_df, "median_income", "Killings vs. median income",
                    "Avg. median income ($)")
```

- [ ] **Step 2: Update the chart list in `smoke_check.py`**

Replace the `figs = [...]` block with:

```python
figs = [
    charts.killings_by_race(killings),
    charts.age_distribution(killings),
    charts.killings_by_armed(killings),
    charts.killings_by_flee(killings),
    charts.killings_by_threat_level(killings),
    charts.manner_of_death_by_age(killings),
    charts.choropleth_killings_by_state(killings["state"].value_counts().to_dict()),
    charts.choropleth_income_by_state(income),
    charts.choropleth_poverty_by_state(poverty),
    charts.killings_vs_poverty_scatter(state_df),
    charts.killings_vs_income_scatter(state_df),
]
```

- [ ] **Step 3: Run the smoke check**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: data checks pass, then `All 11 chart smoke checks passed.` If `marker_cornerradius` raises on this Plotly version, drop that one property from `_bar_marks` and re-run.

- [ ] **Step 4: Commit**

```bash
git add charts.py smoke_check.py
git commit -m "feat: rewrite charts for the dark theme, sorted single-hue bars, no pies"
```

---

### Task 4: Rewrite `app.py` as the editorial layout

**Files:**
- Modify: `app.py` (full rewrite)

**Interfaces:**
- Consumes: `theme` helpers (Task 1), `headline_stats` (Task 2), all 11 chart functions (Task 3).

- [ ] **Step 1: Replace the contents of `app.py`**

```python
"""US Police Shootings — dark editorial dashboard."""
import streamlit as st

import charts
import theme
from data import (build_state_join, headline_stats, load_income, load_killings,
                  load_poverty)

st.set_page_config(page_title="Fatal Force — US Police Shootings", layout="wide")
theme.apply()

killings = load_killings()
income = load_income()
poverty = load_poverty()
state_df = build_state_join()
stats = headline_stats()

theme.masthead(
    "An investigation &middot; US police use of force",
    "Fatal police shootings<br/>in <em>America</em>",
    f"{stats['total']:,} recorded incidents, set against median household income, poverty "
    "rate and racial composition in every state &mdash; and what those three do, and do "
    "not, explain.",
)

theme.kpi_band([
    (f"{stats['total']:,}", "Recorded incidents"),
    (f"{stats['states']}", "States covered"),
    (f"{stats['male_pct']:.1f}%", "Male victims"),
    (f"{stats['median_age']:.0f}", "Median age"),
])

theme.section("01", "Demographics", "Who was killed")

split1, split2 = st.columns(2)
with split1:
    theme.stat_split(
        f"{stats['male_pct']:.1f}%", "of victims were male", stats["male_pct"],
        f"{100 - stats['male_pct']:.1f}% female",
    )
with split2:
    theme.stat_split(
        f"{stats['mental_illness_pct']:.1f}%", "showed signs of mental illness",
        stats["mental_illness_pct"],
        f"{100 - stats['mental_illness_pct']:.1f}% showed none",
    )

left, right = st.columns(2)
with left:
    st.plotly_chart(charts.killings_by_race(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_flee(killings), use_container_width=True)
    st.plotly_chart(charts.manner_of_death_by_age(killings), use_container_width=True)
with right:
    st.plotly_chart(charts.age_distribution(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_armed(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_threat_level(killings), use_container_width=True)

theme.section("02", "Geography", "Where it happened")

tab_killings, tab_income, tab_poverty = st.tabs(["Killings", "Median income", "Poverty rate"])
with tab_killings:
    st.plotly_chart(
        charts.choropleth_killings_by_state(killings["state"].value_counts().to_dict()),
        use_container_width=True,
    )
with tab_income:
    st.plotly_chart(charts.choropleth_income_by_state(income), use_container_width=True)
with tab_poverty:
    st.plotly_chart(charts.choropleth_poverty_by_state(poverty), use_container_width=True)

theme.section("03", "Correlation", "What the states have in common")

theme.body(
    "The table joins killings counts with average income, poverty rate and racial "
    "composition, aggregated to the state level. <strong>These are raw counts, not "
    "per-capita rates</strong> &mdash; no population data exists in the source datasets, so "
    "a state's higher count may simply reflect a larger population, not a higher "
    "underlying rate."
)
st.dataframe(state_df, use_container_width=True)

scatter1, scatter2 = st.columns(2)
with scatter1:
    st.plotly_chart(charts.killings_vs_poverty_scatter(state_df), use_container_width=True)
with scatter2:
    st.plotly_chart(charts.killings_vs_income_scatter(state_df), use_container_width=True)

theme.methodology(
    "Methodology &amp; limitations &mdash; this dataset is a fixed historical snapshot from "
    "the original Kaggle &ldquo;US Police Shootings&rdquo; dataset and is not live or current. "
    "Killings counts are not adjusted for state population and must not be read as rates. "
    "Income, poverty and race figures are unweighted averages across each state&rsquo;s "
    "cities, not population-weighted state totals. Correlation shown in the scatter plots "
    "does not imply causation."
)
```

- [ ] **Step 2: Run the smoke check one final time**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: all data and chart checks pass (this confirms every symbol `app.py` imports still exists).

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: rebuild the dashboard layout as a dark editorial page"
```

---

### Task 5: Manual verification

**Files:** none (verification only)

- [ ] **Step 1: Run the app**

```bash
.venv/Scripts/streamlit run app.py
```

- [ ] **Step 2: Check the page in a browser**

Confirm: the page is near-black with the serif masthead and the orange italic word; the KPI band shows four computed figures with hairline dividers; the two stat splits render with proportion bars in place of the old pies; every bar chart is a single blue and sorted largest-first; the armed chart is horizontal; the three choropleth tabs each use a different ramp (blue / aqua / orange) on a dark map; both scatters show blue markers with a muted trendline; the table and methodology footer are styled. Check the browser console for errors.

- [ ] **Step 3: Commit any fixups**

```bash
git add -A
git commit -m "fix: address issues found in manual verification"
```
