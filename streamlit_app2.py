"""
Care Transition Efficiency & Placement Outcome Analytics
==========================================================
Run with:
    streamlit run streamlit_app2.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Care Transition Efficiency Analytics", layout="wide")
st.title("Care Transition Efficiency & Placement Outcome Analytics")

# ----------------------------------------------------------------------------
# LOAD DATA DIRECTLY FROM YOUR FILE
# ----------------------------------------------------------------------------
CSV_FILE = "HHS_Unaccompanied_Alien_Children_Program_cleaned.csv"

df = pd.read_csv(CSV_FILE)

# Strip any hidden whitespace from column headers to prevent mismatch errors
df.columns = df.columns.str.strip()

# Rename columns to short, easy-to-use names
df = df.rename(columns={
    "Date": "date",
    "Children apprehended and placed in CBP custody*": "cbp_intake",
    "Children in CBP custody": "cbp_custody",
    "Children transferred out of CBP custody": "cbp_to_hhs_transfer",
    "Children in HHS Care": "hhs_care",
    "Children discharged from HHS Care": "hhs_discharge"
})

# Thoroughly clean number columns (handles strings with commas, quotes, and spaces)
number_cols = ["cbp_intake", "cbp_custody", "cbp_to_hhs_transfer", "hhs_care", "hhs_discharge"]
for col in number_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace('"', "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Parse date strings like "December 21, 2025" and strip any time component
df["date"] = pd.to_datetime(df["date"], format="%B %d, %Y", errors="coerce")
df = df.dropna(subset=["date"])
df["date"] = pd.to_datetime(df["date"].dt.date)

df = df.sort_values("date").reset_index(drop=True)

# ----------------------------------------------------------------------------
# DERIVED METRICS
# ----------------------------------------------------------------------------
df["hhs_net_change"] = df["cbp_to_hhs_transfer"] - df["hhs_discharge"]
df["cbp_net_change"] = df["cbp_intake"] - df["cbp_to_hhs_transfer"]

df["transfer_efficiency_ratio"] = df["cbp_to_hhs_transfer"] / df["cbp_custody"]
df["discharge_effectiveness"] = df["hhs_discharge"] / df["hhs_care"]
df["pipeline_throughput_rate"] = df["hhs_discharge"] / df["cbp_intake"]

df["hhs_backlog_trend"] = df["hhs_net_change"].rolling(7, min_periods=1).mean()
df["cbp_backlog_trend"] = df["cbp_net_change"].rolling(7, min_periods=1).mean()

df["is_weekend"] = df["date"].dt.dayofweek.isin([5, 6])
df["year_month"] = df["date"].dt.to_period("M").astype(str)

# ----------------------------------------------------------------------------
# SIDEBAR: DATE RANGE FILTER
# ----------------------------------------------------------------------------
st.sidebar.header("Filters")

if df.empty:
    st.error("Dataframe is empty. Please check your CSV data structure and date formats.")
    st.stop()

min_date = df['date'].min().date()
max_date = df['date'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
fdf = df.loc[mask].copy()

st.sidebar.header("Show Metrics")
show_transfer = st.sidebar.checkbox("Transfer Efficiency Ratio", value=True)
show_discharge = st.sidebar.checkbox("Discharge Effectiveness", value=True)
show_throughput = st.sidebar.checkbox("Pipeline Throughput Rate", value=True)

st.sidebar.header("Alert Thresholds")
transfer_thresh = st.sidebar.slider("Transfer Efficiency cutoffs", 0.0, 2.0, (0.5, 0.9), 0.05)
discharge_thresh = st.sidebar.slider("Discharge Effectiveness cutoffs", 0.0, 2.0, (0.5, 0.9), 0.05)
throughput_thresh = st.sidebar.slider("Pipeline Throughput cutoffs", 0.0, 2.0, (0.7, 1.0), 0.05)
backlog_thresh = st.sidebar.slider("Backlog Accumulation Rate cutoffs (lower=better)", -200, 200, (-20, 20), 5)
stability_thresh = st.sidebar.slider("Outcome Stability Score cutoffs", 0.0, 1.0, (0.5, 0.8), 0.05)

def alert_color(value, thresh, higher_is_better=True):
    if pd.isna(value):
        return "⚪"
    low, high = thresh
    if higher_is_better:
        if value >= high:
            return "🟢"
        elif value >= low:
            return "🟡"
        return "🔴"
    else:
        if value <= low:
            return "🟢"
        elif value <= high:
            return "🟡"
        return "🔴"

# ----------------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------------
st.header("Key Performance Indicators")

transfer_eff = fdf["transfer_efficiency_ratio"].mean()
discharge_eff = fdf["discharge_effectiveness"].mean()
throughput = fdf["hhs_discharge"].sum() / fdf["cbp_intake"].sum()
backlog_rate = fdf["hhs_net_change"].mean()
mean_de, std_de = fdf["discharge_effectiveness"].mean(), fdf["discharge_effectiveness"].std()
stability_score = np.clip(1 - (std_de / mean_de), 0, 1) if mean_de and not pd.isna(mean_de) else np.nan

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(f"{alert_color(transfer_eff, transfer_thresh)} Transfer Efficiency Ratio", f"{transfer_eff:.2f}")
c2.metric(f"{alert_color(discharge_eff, discharge_thresh)} Discharge Effectiveness Index", f"{discharge_eff:.2f}")
c3.metric(f"{alert_color(throughput, throughput_thresh)} Pipeline Throughput", f"{throughput:.2f}")
c4.metric(f"{alert_color(backlog_rate, backlog_thresh, higher_is_better=False)} Backlog Accumulation Rate", f"{backlog_rate:+.1f}/day")
c5.metric(f"{alert_color(stability_score, stability_thresh)} Outcome Stability Score", f"{stability_score:.2f}")

st.divider()

# ----------------------------------------------------------------------------
# MODULE 1: CARE PIPELINE FLOW VISUALIZATION
# ----------------------------------------------------------------------------
st.header("1. Care Pipeline Flow Visualization")

total_intake = fdf["cbp_intake"].sum()
total_transfer = fdf["cbp_to_hhs_transfer"].sum()
total_discharge = fdf["hhs_discharge"].sum()
cbp_stuck = max(total_intake - total_transfer, 0)
hhs_stuck = max(total_transfer - total_discharge, 0)

sankey = go.Figure(go.Sankey(
    node=dict(
        label=["New CBP Intake", "CBP Custody", "HHS Care", "Sponsor Placement", "Remaining in CBP", "Remaining in HHS"],
        pad=20, thickness=20,
        color=["#3498db", "#2980b9", "#8e44ad", "#27ae60", "#e74c3c", "#e67e22"]
    ),
    link=dict(
        source=[0, 1, 2, 1, 2],
        target=[1, 2, 3, 4, 5],
        value=[total_intake, total_transfer, total_discharge, cbp_stuck, hhs_stuck]
    )
))
sankey.update_layout(height=400)
st.plotly_chart(sankey, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# MODULE 2: TRANSFER & DISCHARGE EFFICIENCY PANELS
# ----------------------------------------------------------------------------
st.header("2. Transfer & Discharge Efficiency Panels")

eff_fig = go.Figure()
if show_transfer:
    eff_fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["transfer_efficiency_ratio"], name="Transfer Efficiency Ratio"))
if show_discharge:
    eff_fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["discharge_effectiveness"], name="Discharge Effectiveness"))
if show_throughput:
    eff_fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["pipeline_throughput_rate"], name="Pipeline Throughput Rate"))
eff_fig.add_hline(y=1.0, line_dash="dash", line_color="gray")
eff_fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Ratio")
st.plotly_chart(eff_fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# MODULE 3: BOTTLENECK DETECTION CHARTS
# ----------------------------------------------------------------------------
st.header("3. Bottleneck Detection Charts")

backlog_fig = go.Figure()
backlog_fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["hhs_backlog_trend"], name="HHS Backlog Trend", fill="tozeroy"))
backlog_fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["cbp_backlog_trend"], name="CBP Backlog Trend"))
backlog_fig.add_hline(y=0, line_dash="dash", line_color="gray")
backlog_fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Net Change (7-day avg)")
st.plotly_chart(backlog_fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# MODULE 4: OUTCOME TREND ANALYSIS
# ----------------------------------------------------------------------------
st.header("4. Outcome Trend Analysis")

monthly = fdf.groupby("year_month")["discharge_effectiveness"].mean().reset_index()
trend_fig = px.line(monthly, x="year_month", y="discharge_effectiveness", markers=True,
                     labels={"year_month": "Month", "discharge_effectiveness": "Avg Discharge Effectiveness"})
trend_fig.update_layout(height=380)
st.plotly_chart(trend_fig, use_container_width=True)

with st.expander("View filtered data"):
    st.dataframe(fdf, use_container_width=True)