# Data Dictionary

This document describes every column in the source dataset used by this project.

## Dataset Description

| Column | Description | Data Type | Notes |
|---|---|---|---|
| `Date` | Reporting date for the daily record | Date | Parsed as `Month DD, YYYY` (e.g. "December 11, 2025") |
| `Children apprehended and placed in CBP custody` | Daily intake volume — new children entering CBP custody that day | Numeric (int) | Renamed to `cbp_intake` in code |
| `Children in CBP custody` | Active CBP care load — total children currently held in CBP custody | Numeric (int) | Renamed to `cbp_custody` in code |
| `Children transferred out of CBP custody` | Flow into the HHS system — children moved from CBP to HHS that day | Numeric (int) | Renamed to `cbp_to_hhs_transfer` in code |
| `Children in HHS Care` | Active HHS care load — total children currently in HHS custody | Numeric (int) | Renamed to `hhs_care` in code |
| `Children discharged from HHS Care` | Successful sponsor placements — children released from HHS to a sponsor that day | Numeric (int) | Renamed to `hhs_discharge` in code |

## Pipeline Stages

The dataset represents three sequential stages a child moves through:

```
CBP Custody  -->  HHS Care  -->  Sponsor Placement
```

- **Stage 1 (CBP Custody):** `cbp_intake` flows in; `cbp_to_hhs_transfer` flows out.
- **Stage 2 (HHS Care):** `cbp_to_hhs_transfer` flows in; `hhs_discharge` flows out.
- **Stage 3 (Sponsor Placement):** the final, successful exit point of the pipeline.

## Data Cleaning Notes

- Rows with missing/null values are **dropped**, not filled — with a meaningful share of the dataset missing, forward-filling or imputing would fabricate data that was never reported.
- Numeric columns are stripped of thousands-separator commas (e.g. `"2,484"` → `2484`) before conversion to numeric type.
- `Date` values are parsed using the explicit format `%B %d, %Y` rather than automatic date inference, since automatic parsing produced incorrect/failed conversions on this dataset's format.
