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
