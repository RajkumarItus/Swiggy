# Swiggy Financial Forecasts

This folder contains a small Python script to generate 3-year forward financial forecasts for Swiggy (Bundl Technologies / Swiggy Limited) using simple scenario-driven assumptions.

Files created:
- `scripts/forecast.py` - main script; reads `data/historical.json` and writes forecasts to `outputs/`.
- `data/historical.json` - simple historical consolidated inputs for FY22–FY24 (numbers in ₹ million).
- `requirements.txt` - minimal Python dependencies.

Usage:

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the forecast generator:

```bash
python scripts/forecast.py --outdir outputs --scenarios all
```

This will write `outputs/swiggy_forecasts.csv` and `outputs/swiggy_forecasts.xlsx` with three scenarios (conservative, base, optimistic).

Customize the assumptions in `scripts/forecast.py` (the `SCENARIOS` dict and `NET_MARGIN_ADJUSTMENT`) or edit the historical inputs in `data/historical.json`.

Notes:
- The model is illustrative and intended as a starting point. For a full financial model you can expand the script into a three-statement model (P&L, balance sheet, cash flow), add CAPEX, working capital, interest, and taxes.
