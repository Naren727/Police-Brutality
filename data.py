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
