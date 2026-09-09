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
