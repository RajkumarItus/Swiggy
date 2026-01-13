#!/usr/bin/env python3
"""Swiggy financials forecast generator

This script loads historical consolidated numbers (FY22-FY24) from data/historical.json
and produces 3-year forward forecasts under three scenarios (conservative, base, optimistic).
Outputs a CSV and Excel file under outputs/.

Usage:
    python scripts/forecast.py [--outdir outputs] [--scenarios all|base|conservative|optimistic]

Requires: pandas, openpyxl
"""

from dataclasses import dataclass, asdict
import json
import argparse
from pathlib import Path
import pandas as pd

# Defaults
REPO_ROOT = Path(".")
DATA_FILE = REPO_ROOT / "data" / "historical.json"
OUT_DIR = REPO_ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Scenario:
    name: str
    growth: list  # year-over-year growth rates for FY25, FY26, FY27 (as decimals)
    ebitda_margin_path: list  # EBITDA margins for FY25, FY26, FY27 (as decimals)


SCENARIOS = {
    "conservative": Scenario("conservative", [0.15, 0.12, 0.10], [-0.08, -0.06, -0.04]),
    "base": Scenario("base", [0.25, 0.20, 0.15], [-0.05, -0.02, 0.01]),
    "optimistic": Scenario("optimistic", [0.35, 0.25, 0.20], [-0.02, 0.03, 0.06]),
}

# Simplified net margin adjustment: net_margin = ebitda_margin - adjustment
NET_MARGIN_ADJUSTMENT = 0.06  # -6 percentage points


def load_historical(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def project(historical: dict, scenario: Scenario):
    # Base year FY24 consolidated numbers
    base_rev = historical["FY24"]["consolidated_revenue_million"]
    base_net = historical["FY24"]["consolidated_net_loss_million"]
    base_assets = historical["FY24"]["total_assets_million"]

    rows = []
    prev_rev = base_rev
    assets = base_assets
    for i, (g, ebitda_m) in enumerate(zip(scenario.growth, scenario.ebitda_margin_path), start=1):
        year = f"FY{24 + i}"
        rev = round(prev_rev * (1 + g), 0)
        ebitda = round(rev * ebitda_m, 0)
        net_margin = ebitda_m - NET_MARGIN_ADJUSTMENT
        net = round(rev * net_margin, 0)
        # Simple assets proxy: assets grow at 0.8 * revenue growth
        assets = round(assets * (1 + 0.8 * g), 0)
        rows.append({
            "scenario": scenario.name,
            "year": year,
            "revenue_million": rev,
            "ebitda_million": ebitda,
            "net_million": net,
            "total_assets_million": assets,
        })
        prev_rev = rev
    return rows


def build_all(historical: dict, which: str = "all"):
    scenarios_to_run = SCENARIOS.keys() if which == "all" else [which]
    all_rows = []
    for name in scenarios_to_run:
        sc = SCENARIOS[name]
        all_rows.extend(project(historical, sc))
    return pd.DataFrame(all_rows)


def main():
    parser = argparse.ArgumentParser(description="Generate 3-year financial forecasts for Swiggy")
    parser.add_argument("--outdir", default=str(OUT_DIR), help="Output directory")
    parser.add_argument("--scenarios", default="all", help="Which scenarios to run: all/base/conservative/optimistic")
    args = parser.parse_args()

    hist = load_historical(DATA_FILE)
    df = build_all(hist, which=args.scenarios)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "swiggy_forecasts.csv"
    xlsx_path = outdir / "swiggy_forecasts.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    print(f"Wrote forecasts to: {csv_path} and {xlsx_path}")


if __name__ == "__main__":
    main()
