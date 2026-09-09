# Police-Brutality Streamlit Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the exploratory notebook into a hosted Streamlit dashboard with a genuine state-level join (killings vs. income/poverty/race), per `docs/superpowers/specs/2026-09-09-streamlit-dashboard-design.md`.

**Architecture:** Three modules — `data.py` (cached loaders + the new `build_state_join()`), `charts.py` (one themed-Plotly-figure function per chart), `app.py` (Streamlit page layout only, no data/chart logic). A `smoke_check.py` script provides automated verification since there's no traditional business logic to unit test.

**Tech Stack:** Streamlit, pandas, Plotly (`plotly.express` + `graph_objects`), `statsmodels` (required by Plotly's `trendline="ols"`).

## Global Constraints

- Restrained data-journalism palette only: background `#f7f5f2`, text `#2b2b2b`, primary `#3b5b7c` (muted steel blue), secondary `#a13d3d` (muted maroon) — no other colors except the fixed race palette and the `Blues`/`OrRd` choropleth scales, all specified in Task 2.
- Raw killings counts are never presented as rates — every place a count appears near income/poverty/race, the "not population-adjusted" caveat must be visible on the same page.
- CSVs are read with relative paths (`"PoliceKillingsUS.csv"`, etc.) — the app is run from the repo root, not with the original notebook's hardcoded absolute paths.
- No new external data sources — only the 4 CSVs already in the repo.

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.streamlit/config.toml`
- Create: `.gitignore`

**Interfaces:** none (no code yet).

- [ ] **Step 1: Create the virtual environment and requirements file**

```bash
python -m venv .venv
```

Create `requirements.txt`:

```
streamlit
pandas
plotly
statsmodels
```

Install:

```bash
.venv/Scripts/pip install -r requirements.txt
```

- [ ] **Step 2: Freeze exact versions**

```bash
.venv/Scripts/pip freeze > requirements.txt
```

- [ ] **Step 3: Add the Streamlit theme config**

Create `.streamlit/config.toml`:

```toml
[theme]
base = "light"
backgroundColor = "#f7f5f2"
secondaryBackgroundColor = "#eeece7"
textColor = "#2b2b2b"
primaryColor = "#3b5b7c"
font = "sans serif"
```

- [ ] **Step 4: Add .gitignore**

Create `.gitignore`:

```
.venv/
__pycache__/
*.pyc
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .streamlit/config.toml .gitignore
git commit -m "chore: scaffold Streamlit project (deps, theme, gitignore)"
```

---

### Task 2: Data layer (`data.py`) with smoke checks

**Files:**
- Create: `data.py`
- Create: `smoke_check.py`

**Interfaces:**
- Produces: `load_killings() -> pd.DataFrame`, `load_income() -> pd.DataFrame`, `load_poverty() -> pd.DataFrame`, `load_race() -> pd.DataFrame`, `build_state_join() -> pd.DataFrame` (columns: `State, killings_count, median_income, poverty_rate, share_white, share_black, share_native_american, share_asian, share_hispanic`) — all consumed by `app.py` (Task 4) and `charts.py` (Task 3).

- [ ] **Step 1: Write the smoke-check script first**

Create `smoke_check.py`:

```python
"""Smoke-check the data pipeline without needing a running Streamlit app.

Run with: .venv/Scripts/python smoke_check.py
"""
from data import load_killings, load_income, load_poverty, load_race, build_state_join

killings = load_killings()
assert len(killings) == 2535, f"expected 2535 killings rows, got {len(killings)}"
assert killings["race"].isnull().sum() == 0, "race should have no missing values after cleaning"
assert killings["age"].isnull().sum() == 0, "age should have no missing values after cleaning"
assert set(killings["race"].unique()) <= {"Asian", "Black", "White", "Other", "Hispanic", "Native"}

income = load_income()
assert len(income) > 0
assert income["Median Income"].isnull().sum() == 0

poverty = load_poverty()
assert len(poverty) > 0
assert poverty["poverty_rate"].isnull().sum() == 0

race = load_race()
assert len(race) > 0

state_df = build_state_join()
assert 45 <= len(state_df) <= 55, f"expected ~50 states+DC, got {len(state_df)}"
assert state_df["killings_count"].sum() == len(killings)

print("All data smoke checks passed.")
print(state_df.head())
```

- [ ] **Step 2: Run it to verify it fails**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: `ModuleNotFoundError: No module named 'data'` (or ImportError — `data.py` doesn't exist yet).

- [ ] **Step 3: Implement `data.py`**

Create `data.py`:

```python
"""Data loading and cleaning for the Police-Brutality dashboard.

The 3 auxiliary CSVs (income, poverty, race) are saved with old Mac-style
CR-only line endings -- they look corrupted in a plain text editor, but
pandas' C parser already handles this correctly, so no special
line-terminator handling is needed here.
"""
import numpy as np
import pandas as pd
import streamlit as st

RACE_CODES = {
    "A": "Asian",
    "B": "Black",
    "W": "White",
    "O": "Other",
    "H": "Hispanic",
    "N": "Native",
}

SHARE_COLUMNS = [
    "share_white",
    "share_black",
    "share_native_american",
    "share_asian",
    "share_hispanic",
]


@st.cache_data
def load_killings() -> pd.DataFrame:
    df = pd.read_csv("PoliceKillingsUS.csv", encoding="cp1252")
    df = df.drop(columns=["id", "name", "date"])
    df["flee"] = df["flee"].fillna("Not fleeing")
    df["armed"] = df["armed"].fillna("unarmed")
    df["age"] = df["age"].fillna(df["age"].median())
    df["race"] = df["race"].fillna("W").map(RACE_CODES)
    return df


@st.cache_data
def load_income() -> pd.DataFrame:
    df = pd.read_csv("MedianHouseholdIncome2015.csv", encoding="cp1252")
    df = df.rename(columns={"Geographic Area": "state"})
    df["Median Income"] = pd.to_numeric(
        df["Median Income"].astype(str).str.extract(r"(\d+)", expand=False)
    )
    df["Median Income"] = df["Median Income"].fillna(df["Median Income"].mean())
    return df


@st.cache_data
def load_poverty() -> pd.DataFrame:
    df = pd.read_csv("PercentagePeopleBelowPovertyLevel.csv", encoding="cp1252")
    df = df.rename(columns={"Geographic Area": "state"})
    df["poverty_rate"] = pd.to_numeric(
        df["poverty_rate"].replace(["-", "(X)"], np.nan), errors="coerce"
    )
    df["poverty_rate"] = df["poverty_rate"].fillna(df["poverty_rate"].mean())
    return df


@st.cache_data
def load_race() -> pd.DataFrame:
    df = pd.read_csv("ShareRaceByCity.csv", encoding="cp1252")
    df = df.rename(columns={"Geographic area": "state"})
    for col in SHARE_COLUMNS:
        df[col] = pd.to_numeric(df[col].replace(["-", "(X)"], np.nan), errors="coerce")
    df = df.dropna(subset=SHARE_COLUMNS)
    return df


@st.cache_data
def build_state_join() -> pd.DataFrame:
    """One row per state: killings count + mean income/poverty/race shares.

    Raw counts only -- no population data exists in this dataset, so this
    cannot be normalized into a per-capita rate. Income/poverty/race are
    simple unweighted averages across each state's cities.
    """
    killings = load_killings()
    income = load_income()
    poverty = load_poverty()
    race = load_race()

    counts = killings.groupby("state").size().rename("killings_count")
    mean_income = income.groupby("state")["Median Income"].mean().rename("median_income")
    mean_poverty = poverty.groupby("state")["poverty_rate"].mean().rename("poverty_rate")
    mean_race = race.groupby("state")[SHARE_COLUMNS].mean()

    joined = (
        counts.to_frame()
        .join(mean_income, how="left")
        .join(mean_poverty, how="left")
        .join(mean_race, how="left")
        .reset_index()
        .rename(columns={"state": "State"})
    )
    return joined
```

- [ ] **Step 4: Run the smoke check to verify it passes**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: `All data smoke checks passed.` followed by the state table's head.

- [ ] **Step 5: Commit**

```bash
git add data.py smoke_check.py
git commit -m "feat: add data loading/cleaning layer with the missing state-level join"
```

---

### Task 3: Chart layer (`charts.py`)

**Files:**
- Create: `charts.py`
- Modify: `smoke_check.py` (append chart smoke checks)

**Interfaces:**
- Consumes: dataframes from `data.py` (Task 2).
- Produces: `killings_by_race`, `killings_by_age`, `killings_by_gender`, `killings_by_armed`, `killings_by_mental_illness`, `killings_by_flee`, `manner_of_death_by_age`, `killings_by_threat_level`, `choropleth_killings_by_state`, `choropleth_income_by_state`, `choropleth_poverty_by_state`, `killings_vs_poverty_scatter`, `killings_vs_income_scatter` — each returns a `plotly.graph_objects.Figure`, consumed by `app.py` (Task 4).

- [ ] **Step 1: Implement `charts.py`**

Create `charts.py`:

```python
"""Themed Plotly chart builders for the Police-Brutality dashboard."""
import plotly.express as px
import plotly.graph_objects as go

PRIMARY = "#3b5b7c"
SECONDARY = "#a13d3d"

RACE_COLORS = {
    "White": "#8c9db5",
    "Black": "#3b5b7c",
    "Hispanic": "#a13d3d",
    "Asian": "#6b8f71",
    "Native": "#c08a4e",
    "Other": "#9a9a9a",
}

CHART_LAYOUT = dict(
    paper_bgcolor="#f7f5f2",
    plot_bgcolor="#f7f5f2",
    font=dict(color="#2b2b2b", family="Helvetica, Arial, sans-serif"),
)


def killings_by_race(df):
    fig = px.histogram(
        df, x="race", color="race", color_discrete_map=RACE_COLORS,
        title="Police Killings by Race",
    )
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Race", yaxis_title="No. of Police Killings", showlegend=False)
    return fig


def killings_by_age(df):
    fig = px.strip(df, x="age", title="Police Killings by Age", color_discrete_sequence=[PRIMARY])
    fig.update_layout(**CHART_LAYOUT)
    return fig


def killings_by_gender(df):
    male = int((df["gender"] == "M").sum())
    female = int((df["gender"] == "F").sum())
    fig = px.pie(
        values=[male, female], names=["Male", "Female"],
        title="Police Killings by Gender",
        color_discrete_sequence=[PRIMARY, SECONDARY],
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig


def killings_by_armed(df):
    fig = px.histogram(df, x="armed", title="Victim Weaponry", color_discrete_sequence=[PRIMARY])
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Weaponry", yaxis_title="No. of Police Killings")
    return fig


def killings_by_mental_illness(df):
    present = int((df["signs_of_mental_illness"] == True).sum())
    absent = int((df["signs_of_mental_illness"] == False).sum())
    fig = px.pie(
        values=[present, absent], names=["Present", "Absent"],
        title="Signs of Mental Illness",
        color_discrete_sequence=[SECONDARY, PRIMARY],
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig


def killings_by_flee(df):
    fig = px.histogram(df, x="flee", title="Did the Victim Attempt to Flee?", color_discrete_sequence=[PRIMARY])
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Flee Status", yaxis_title="No. of Police Killings")
    return fig


def manner_of_death_by_age(df):
    fig = px.box(df, x="manner_of_death", y="age", title="Manner of Death by Age", color_discrete_sequence=[PRIMARY])
    fig.update_layout(**CHART_LAYOUT)
    return fig


def killings_by_threat_level(df):
    fig = px.histogram(df, x="threat_level", title="Officer Threat Level", color_discrete_sequence=[PRIMARY])
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Threat Level", yaxis_title="No. of Police Killings")
    return fig


def choropleth_killings_by_state(state_counts: dict):
    fig = go.Figure(data=go.Choropleth(
        locations=list(state_counts.keys()), locationmode="USA-states",
        z=list(state_counts.values()), colorscale="Blues",
    ))
    fig.update_layout(**CHART_LAYOUT, geo=dict(scope="usa"), title="Police Killings by State")
    return fig


def choropleth_income_by_state(income_df):
    fig = go.Figure(data=go.Choropleth(
        locations=income_df["state"], locationmode="USA-states",
        z=income_df["Median Income"], colorscale="Blues",
    ))
    fig.update_layout(**CHART_LAYOUT, geo=dict(scope="usa"), title="Median Household Income by State")
    return fig


def choropleth_poverty_by_state(poverty_df):
    fig = go.Figure(data=go.Choropleth(
        locations=poverty_df["state"], locationmode="USA-states",
        z=poverty_df["poverty_rate"], colorscale="OrRd",
    ))
    fig.update_layout(**CHART_LAYOUT, geo=dict(scope="usa"), title="Poverty Rate by State")
    return fig


def killings_vs_poverty_scatter(state_df):
    fig = px.scatter(
        state_df, x="poverty_rate", y="killings_count", trendline="ols",
        hover_name="State", color_discrete_sequence=[PRIMARY],
        title="Killings Count vs. Poverty Rate",
    )
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Avg. Poverty Rate (%)", yaxis_title="Killings Count")
    return fig


def killings_vs_income_scatter(state_df):
    fig = px.scatter(
        state_df, x="median_income", y="killings_count", trendline="ols",
        hover_name="State", color_discrete_sequence=[SECONDARY],
        title="Killings Count vs. Median Income",
    )
    fig.update_layout(**CHART_LAYOUT, xaxis_title="Avg. Median Income ($)", yaxis_title="Killings Count")
    return fig
```

- [ ] **Step 2: Append chart smoke checks**

Add to the end of `smoke_check.py`:

```python
import plotly.graph_objects as go
import charts

figs = [
    charts.killings_by_race(killings),
    charts.killings_by_age(killings),
    charts.killings_by_gender(killings),
    charts.killings_by_armed(killings),
    charts.killings_by_mental_illness(killings),
    charts.killings_by_flee(killings),
    charts.manner_of_death_by_age(killings),
    charts.killings_by_threat_level(killings),
    charts.choropleth_killings_by_state(killings["state"].value_counts().to_dict()),
    charts.choropleth_income_by_state(income),
    charts.choropleth_poverty_by_state(poverty),
    charts.killings_vs_poverty_scatter(state_df),
    charts.killings_vs_income_scatter(state_df),
]
for fig in figs:
    assert isinstance(fig, go.Figure)

print(f"All {len(figs)} chart smoke checks passed.")
```

- [ ] **Step 3: Run the smoke check**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: both the data-check output and `All 13 chart smoke checks passed.`. If it fails with `ImportError: trendline requires statsmodels`, confirm `statsmodels` is in `requirements.txt` and installed (Task 1).

- [ ] **Step 4: Commit**

```bash
git add charts.py smoke_check.py
git commit -m "feat: add themed chart builders for every dashboard visualization"
```

---

### Task 4: Streamlit app (`app.py`) and README update

**Files:**
- Create: `app.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: everything from `data.py` (Task 2) and `charts.py` (Task 3).

- [ ] **Step 1: Implement `app.py`**

Create `app.py`:

```python
"""Police-Brutality Streamlit dashboard entrypoint."""
import streamlit as st

import charts
from data import build_state_join, load_income, load_killings, load_poverty, load_race

st.set_page_config(page_title="US Police Shootings — Data Dashboard", layout="wide")

killings = load_killings()
income = load_income()
poverty = load_poverty()
race = load_race()
state_df = build_state_join()

st.title("US Police Shootings: A Data Dashboard")
st.markdown(
    """
This dashboard examines fatal police shootings in the United States, using a dataset of
recorded incidents alongside median household income, poverty rate, and racial composition
by state. The goal is to surface patterns that can inform both public understanding and
police department accountability.

Across the incidents in this dataset, victims were most often white, followed by Black and
Hispanic victims; the vast majority (95.8%) were male, and most were between 18 and 51 years
old. The states with the most recorded killings were California, Texas, and Florida.
"""
)

st.divider()
st.header("Victim demographics")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.killings_by_race(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_gender(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_mental_illness(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_threat_level(killings), use_container_width=True)
with col2:
    st.plotly_chart(charts.killings_by_age(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_armed(killings), use_container_width=True)
    st.plotly_chart(charts.killings_by_flee(killings), use_container_width=True)
    st.plotly_chart(charts.manner_of_death_by_age(killings), use_container_width=True)

st.divider()
st.header("Geographic view")
tab1, tab2, tab3 = st.tabs(["Killings by State", "Median Income", "Poverty Rate"])
with tab1:
    state_counts = killings["state"].value_counts().to_dict()
    st.plotly_chart(charts.choropleth_killings_by_state(state_counts), use_container_width=True)
with tab2:
    st.plotly_chart(charts.choropleth_income_by_state(income), use_container_width=True)
with tab3:
    st.plotly_chart(charts.choropleth_poverty_by_state(poverty), use_container_width=True)

st.divider()
st.header("State-level relationships")
st.markdown(
    """
The table below joins killings counts with average income, poverty rate, and racial
composition, aggregated to the state level. **These are raw counts, not per-capita
rates** — no population data exists in the source datasets, so a state's higher count
may simply reflect a larger population, not a higher underlying rate.
"""
)
st.dataframe(state_df, use_container_width=True)
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(charts.killings_vs_poverty_scatter(state_df), use_container_width=True)
with col4:
    st.plotly_chart(charts.killings_vs_income_scatter(state_df), use_container_width=True)

st.divider()
st.caption(
    "Methodology & limitations: this dataset is a fixed historical snapshot "
    "(from the original Kaggle \"US Police Shootings\" dataset) and is not live/current. "
    "Killings counts are not adjusted for state population, so they should not be read as "
    "rates. Income, poverty, and race figures are simple unweighted averages across each "
    "state's cities, not population-weighted state totals. Correlation shown in the "
    "scatter plots does not imply causation."
)
```

- [ ] **Step 2: Update README with run/deploy instructions**

Add to the end of `README.md`:

```markdown
## Running the dashboard

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt  # .venv/bin/pip on macOS/Linux
.venv/Scripts/streamlit run app.py              # .venv/bin/streamlit on macOS/Linux
```

## Deploying

This app is ready to deploy on [Streamlit Community Cloud](https://streamlit.io/cloud) —
point it at this repo with `app.py` as the entrypoint.
```

- [ ] **Step 3: Run the smoke check one final time**

```bash
.venv/Scripts/python smoke_check.py
```

Expected: both data and chart checks pass (confirms `app.py`'s imports are all valid, even though this doesn't execute `app.py` itself).

- [ ] **Step 4: Commit**

```bash
git add app.py README.md
git commit -m "feat: add the Streamlit dashboard page and run/deploy instructions"
```

---

### Task 5: Manual verification

**Files:** none (verification only)

- [ ] **Step 1: Start the app**

```bash
.venv/Scripts/streamlit run app.py
```

- [ ] **Step 2: Check every section in a browser**

Confirm: the overview paragraph renders, all 8 demographic charts render without error in the 2-column grid, all 3 choropleth tabs render, the state-level table shows ~51 rows with no obviously-wrong values (e.g. no negative income), both scatter plots render with a visible trend line, and the methodology caption is visible at the bottom. Confirm the page uses the off-white/charcoal/steel-blue palette, not Streamlit's default theme.

- [ ] **Step 3: Commit any fixups**

```bash
git add -A
git commit -m "fix: address issues found in manual verification"
```
