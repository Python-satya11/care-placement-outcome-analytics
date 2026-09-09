# Care Transition Efficiency & Placement Outcome Analytics

Streamlit dashboard analyzing the CBP→HHS→sponsor pipeline for unaccompanied children. Computes 5 KPIs — Transfer Efficiency, Discharge Effectiveness, Pipeline Throughput, Backlog Accumulation Rate, and Outcome Stability — with a Sankey flow view, bottleneck detection, date filters, and threshold-based alerts to surface hidden delays.

## Problem Statement

While aggregate counts of children in custody are publicly monitored, process efficiency metrics are largely absent. Key unanswered questions include:

- How efficiently are children transferred from CBP to HHS?
- Are discharges keeping pace with inflows?
- When and where do care backlogs accumulate?
- Are placement outcomes improving or deteriorating over time?

Without structured transition analytics, system bottlenecks remain hidden. This project models the system as a **care pipeline** — CBP custody → HHS care → Sponsor placement — and derives process-efficiency metrics from the daily flow between stages, rather than relying on static custody counts alone.

## Key Performance Indicators

| KPI | Description | Value |
|---|---|---|
| Transfer Efficiency Ratio | Measures CBP → HHS speed | **0.69** |
| Discharge Effectiveness Index | Placement success | **0.02** |
| Pipeline Throughput | Overall system movement | **1.85** |
| Backlog Accumulation Rate | Delay severity | **-44.7 / day** |
| Outcome Stability Score | Consistency of placements | **0.44** |

> These values are computed over the full cleaned dataset. Re-run `streamlit_app.py` or the analysis notebook to recompute them for a custom date range.

## Screenshots

**Month-over-Month Discharge Trend**

![Month-over-month discharge trend](Month-over-month%20discharge%20.png)

**Backlog & Delay Identification**

![Backlog and delay identification](Backlog%20&%20Delay%20Identification.png)
<!-- Add this screenshot to assets/backlog_delay_identification.png -->

## Streamlit Web Application

### Core Modules
- Care Pipeline Flow Visualization (Sankey diagram)
- Transfer & Discharge Efficiency Panels
- Bottleneck Detection Charts
- Outcome Trend Analysis

### User Capabilities
- Date range selection
- Ratio-based metric toggles
- Threshold-based alerts (visual, color-coded)

### Run it locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Publish it on Streamlit Community Cloud

To deploy this app on [Streamlit Community Cloud](https://streamlit.io/cloud), your repository needs at minimum:

| File | Purpose |
|---|---|
| `streamlit_app.py` | The main application script Streamlit runs |
| `requirements.txt` | Tells the platform which Python packages to install |

Steps:
1. Push this repository to GitHub (public or connected private repo).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select this repository and branch, and set the main file path to `streamlit_app.py`.
4. Click **Deploy**.

## Repository Structure

```
care-transition-efficiency-dashboard/
├── streamlit_app.py            # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies for deployment
├── data_dictionary.md          # Column-level description of the dataset
├── README.md                   # Project overview (this file)
├── notebooks/
│   └── analysis.ipynb          # Exploratory analysis & KPI derivation notebook
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program_cleaned.csv
└── assets/
    ├── month_over_month_discharge.png
    └── backlog_delay_identification.png
```

## Dataset

| Column | Description |
|---|---|
| Date | Reporting date |
| Children apprehended and placed in CBP custody | Daily intake volume |
| Children in CBP custody | Active CBP care load |
| Children transferred out of CBP custody | Flow into the HHS system |
| Children in HHS Care | Active HHS care load |
| Children discharged from HHS Care | Successful sponsor placements |

See [`data_dictionary`](data_dictionary.md) for full column definitions and data-cleaning notes.

## Methodology

**Care Pipeline Modelling** — represent the system as a flow pipeline with defined stages (CBP custody → HHS care → Sponsor placement) and track daily movement between them.

**Transition Efficiency Metrics**
- Transfer Efficiency Ratio = Transfers ÷ CBP Custody
- Discharge Effectiveness = Discharges ÷ HHS Care
- Pipeline Throughput Rate = Total Exits ÷ Total Entries

**Backlog & Delay Identification** — compare inflow vs. successful exits, identify sustained imbalance periods, and detect accumulation of unresolved cases.

**Temporal & Pattern Analysis** — weekday vs. weekend transition speed, month-over-month placement trends, and prolonged stagnation periods.

**Outcome Stability Analysis** — variability in discharge performance, consistency of placement outcomes, and sudden drops in reunification success.

## Author

**Satyaranjan Jena**
MCA
[LinkedIn](https://www.linkedin.com/in/satyaranjan-jena09/)
