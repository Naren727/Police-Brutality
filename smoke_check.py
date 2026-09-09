"""Smoke-check the data pipeline without needing a running Streamlit app.

Run with: .venv/Scripts/python smoke_check.py
"""
from data import load_killings, load_income, load_poverty, load_race, build_state_join, headline_stats

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

stats = headline_stats()
assert set(stats) == {"total", "states", "male_pct", "median_age", "mental_illness_pct"}
assert stats["total"] == len(killings)
assert 45 <= stats["states"] <= 55
assert 90 <= stats["male_pct"] <= 100
assert 20 <= stats["median_age"] <= 60
assert 0 <= stats["mental_illness_pct"] <= 100

print("All data smoke checks passed.")
print(state_df.head())

import plotly.graph_objects as go
import charts

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
for fig in figs:
    assert isinstance(fig, go.Figure)

print(f"All {len(figs)} chart smoke checks passed.")
