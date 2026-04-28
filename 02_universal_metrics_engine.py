#!/usr/bin/env python3
"""
02_universal_metrics_engine.py

Thesis Reproducibility Artifact - Component 2/3 (Input-Agnostic Measurement Architecture)
This module isolates all metric computation logic (Gini, Lorenz, Concentration Ratios,
Buyer Dependency, and Method-Level Competition). It is designed to accept any standardized
Open Contracting Data Standard (OCDS) pandas DataFrame.

Key methodological constraints executed here:
- Strict mathematical formulations for Gini (normalized indices bounded between 0 and 1).
- 4-way Sensitivity tests for 'Professional Winners' (e.g., 10 wins across 3 distinct buyers).
- Method-level competition slicing (Single-bidder rate and mean bidder counts).
"""

import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def calculate_gini(values):
    """
    Standard Lorenz-based Gini calculation logic retrieved from local project tests.
    Computes inequality of contract wealth distribution.
    """
    v = np.sort(np.asarray(values, dtype=float))
    v = v[np.isfinite(v)]
    n = len(v)
    if n == 0 or v.sum() <= 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2.0 * np.sum(idx * v) - (n + 1) * v.sum()) / (n * v.sum()))

def calculate_lorenz_curve(values):
    """
    Outputs the coordinates (cumulative supplier share, cumulative value share) 
    required to chart visual Lorenz inequality curves.
    """
    v = np.sort(np.asarray(values, dtype=float))
    v = v[v > 0]
    n = len(v)
    if n == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0])
    
    cumulative_value = np.cumsum(v)
    total_value = cumulative_value[-1]
    
    percentiles = np.insert(np.arange(1, n + 1) / n, 0, 0.0)
    shares = np.insert(cumulative_value / total_value, 0, 0.0)
    
    return percentiles, shares

def get_structural_concentration(df):
    """Calculates macro-level concentration metrics: Gini and top tier ratios."""
    supplier_totals = df.groupby("supplier_id")["award_value_amount"].sum()
    supplier_totals = supplier_totals[supplier_totals > 0].sort_values(ascending=False)
    
    total_market_value = supplier_totals.sum()
    gini_coeff = calculate_gini(supplier_totals.values)
    
    # CR-k logic (e.g., Top 1%, Top 5%)
    n_suppliers = len(supplier_totals)
    top_1_perc_count = max(1, int(0.01 * n_suppliers))
    top_5_perc_count = max(1, int(0.05 * n_suppliers))
    
    top_1_val = supplier_totals.iloc[:top_1_perc_count].sum()
    top_5_val = supplier_totals.iloc[:top_5_perc_count].sum()
    
    return {
        "gini_coefficient": gini_coeff,
        "active_suppliers": n_suppliers,
        "cr_top_1_pct_share": top_1_val / total_market_value if total_market_value else 0,
        "cr_top_5_pct_share": top_5_val / total_market_value if total_market_value else 0
    }

def evaluate_professional_winners(df):
    """
    Calculates institutional lock-in using the 'Professional Winners' multi-threshold logic.
    Returns the count of suppliers meeting various success and buyer-spread criteria.
    """
    # Group per supplier to count total distinct wins and unique buying entities
    supplier_stats = df.groupby("supplier_id").agg(
        total_wins=("ocid", "nunique"),
        unique_buyers=("buyer_name", "nunique")
    ).reset_index()

    thresholds = [
        {"desc": "5 Wins, 2+ Buyers", "w": 5, "b": 2},
        {"desc": "5 Wins, 3+ Buyers", "w": 5, "b": 3},
        {"desc": "10 Wins, 2+ Buyers", "w": 10, "b": 2},
        {"desc": "10 Wins, 3+ Buyers", "w": 10, "b": 3} # Baseline Metric
    ]
    
    results = {}
    for t in thresholds:
        mask = (supplier_stats["total_wins"] >= t["w"]) & (supplier_stats["unique_buyers"] >= t["b"])
        prof_count = mask.sum()
        results[t["desc"]] = prof_count
        
    return results

def compute_competition_outcomes_by_method(df):
    """
    Analyzes the association between method-mix and standard competitive outcomes 
    like the localized single-bidder rate.
    """
    method_stats = df.groupby("tender_procurementMethod").agg(
        total_awards=("ocid", "nunique"),
        single_bidder_awards=("is_single_bidder", "sum"),
        mean_bidders=("bids_count", "mean")
    ).reset_index()
    
    method_stats["single_bidder_rate"] = method_stats["single_bidder_awards"] / method_stats["total_awards"]
    
    return method_stats

def analyze_buyer_dependency(df):
    """
    Computes dyadic lock-in: What percentage of a specific buyer's total budget
    is captured exclusively by their absolute top supplier?
    """
    dyads = df.groupby(["buyer_name", "supplier_id"]).agg(
        dyad_value=("award_value_amount", "sum")
    ).reset_index()

    buyer_totals = df.groupby("buyer_name").agg(total_value=("award_value_amount", "sum")).reset_index()
    
    # Isolate the top supplier constraint per buyer
    idx = dyads.groupby("buyer_name")["dyad_value"].idxmax()
    top_dyads = dyads.loc[idx].rename(columns={"dyad_value": "top_1_supplier_value"})
    
    merged = pd.merge(buyer_totals, top_dyads, on="buyer_name", how="inner")
    merged["top_1_dependence_ratio"] = merged["top_1_supplier_value"] / merged["total_value"]
    
    # Provide the systemic median of top-1 buyer dependency
    median_dependence = merged["top_1_dependence_ratio"].median()
    
    return {
        "median_top_1_dependency": median_dependence,
        "buyers_analyzed": len(merged)
    }

def run_all_universal_metrics(df, dataset_name="Target Dataset"):
    """Wrapper function to execute and log the complete measurement architecture."""
    logging.info(f"Running Universal Metrics Engine for: {dataset_name}")
    
    structural = get_structural_concentration(df)
    prof_winners = evaluate_professional_winners(df)
    competition = compute_competition_outcomes_by_method(df)
    buyer_dep = analyze_buyer_dependency(df)
    
    report = {
        "dataset_name": dataset_name,
        "structural_metrics": structural,
        "professional_winners_sensitivity": prof_winners,
        "buyer_dependency": buyer_dep,
        "method_competition": competition.to_dict(orient="records")
    }
    
    return report

if __name__ == "__main__":
    logging.info("Initialized 02_universal_metrics_engine.py. Metrics Library Ready.")
    # Example execution:
    # import 01_ocds_extraction_and_cleaning as extractor
    # df = extractor.process_local_json_api("tenders.js", "bids.js")
    # report = run_all_universal_metrics(df, "MN-2024")
    # import pprint; pprint.pprint(report)