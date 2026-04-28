#!/usr/bin/env python3
"""
01_ocds_extraction_and_cleaning.py

Thesis Reproducibility Artifact - Component 1/3 (Data Provenance & Harmonization)
This script demonstrates the extraction workflow, cleaning logic, and entity-resolution proxy
for unifying both local raw JSON JSON-API data (MN-2019, MN-2024) and DIGIWHIST OCDS bulk
CSV exports (GE-2019) into a standardized Open Contracting Data Standard (OCDS) matrix.

Key methodological constraints executed here:
- Drops missing supplier IDs (< 2% error standard)
- Strict single award deduplication per tender logic: drop_duplicates(subset='tender_id', keep='first')
- Hard filtering constraint for local JSON inputs to strictly 'Шалгарсан' (Selected) statuses.
"""

import os
import json
import logging
import pandas as pd
import numpy as np

# Configure auditable reproducibility logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def safe_float(value):
    """Safely cast numeric/string currency mappings to generic floats."""
    if pd.isna(value) or value == "":
        return np.nan
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return np.nan

def normalize_supplier_name(name):
    """Standardizes supplier strings to mitigate 3-5% known residual entity resolution error."""
    if pd.isna(name):
        return None
    return str(name).strip().upper()

def process_local_json_api(tenders_path, bids_path, method_mapping_dict=None):
    """
    Parses native Mongolian JSON payload arrays into an OCDS compliant tabular DataFrame.
    """
    logging.info(f"Extracting local JSON structures from: {tenders_path}")
    
    # 1. Load generic Tender headers
    with open(tenders_path, "r", encoding="utf-8") as f:
        tenders_data = json.load(f)
        
    tenders_df = pd.DataFrame(tenders_data)
    
    if "tenderId" not in tenders_df.columns:
        raise ValueError("JSON file lacks required primary key 'tenderId'.")

    # Re-cast the local ID to standard OCDS format
    tenders_df = tenders_df.rename(columns={
        "tenderId": "ocid",
        "tenderYear": "date",
        "totalBudget": "tender_value_amount"
    })

    # 2. Extract Bid & Award statuses
    with open(bids_path, "r", encoding="utf-8") as f:
        # Note: Depending on file purity, json arrays may need preprocessing
        raw_bids = f.read().strip().replace('\n', '')
        if not raw_bids.startswith('{'): raw_bids = '{' + raw_bids
        if not raw_bids.endswith('}'): raw_bids = raw_bids + '}'
        bids_dict = json.loads(raw_bids)

    award_records = []
    
    # Flatten the distinct local "Шалгарсан" (Selected/Won) flag arrays logically
    for tender_id, bids in bids_dict.items():
        bid_count = len(bids)
        for b in bids:
            status = b.get("bidder_status") or b.get("wfmStatusCode")
            
            # CORE RULE: Isolate explicit winners natively (Methodology Sect 3.3)
            if status in ["Шалгарсан", "DISTINGUISHED_STATUS"]:
                award_records.append({
                    "ocid": tender_id,
                    "supplier_id": b.get("registerNumber") or b.get("supplierId"),
                    "supplier_name": b.get("supplierName") or b.get("bidder_name"),
                    "award_value_amount": safe_float(b.get("discountedAmount") or b.get("openedBidderPrice")),
                    "bids_count": bid_count,
                    "is_single_bidder": 1 if bid_count == 1 else 0
                })

    awards_df = pd.DataFrame(award_records)

    # Compile the final OCDS formatted frame
    unified = pd.merge(tenders_df, awards_df, on="ocid", how="inner")
    
    if method_mapping_dict:
        unified["tender_procurementMethod"] = unified["tenderTypeId"].map(method_mapping_dict)

    # Execute cleaning constraints (Methodology Sect 3.3)
    initial_len = len(unified)
    unified = unified.dropna(subset=["supplier_id"])
    dropped_missing = initial_len - len(unified)
    
    unified["supplier_name_norm"] = unified["supplier_name"].apply(normalize_supplier_name)
    
    # Strict deduplication (protects against multi-status or re-awards duplicating budget sizes)
    unified = unified.drop_duplicates(subset=["ocid"], keep="first")
    
    logging.info(f"Local JSON Output: Processed {len(unified)} valid awards. Dropped {dropped_missing} missing entities.")
    return unified

def process_digiwhist_ocds_csvs(input_dir):
    """
    Parses DIGIWHIST normalized CSV files, recreating the required OCDS table logic natively.
    """
    logging.info(f"Extracting OCDS-formatted DIGIWHIST structure from: {input_dir}")
    
    main_path = os.path.join(input_dir, "main.csv")
    awards_path = os.path.join(input_dir, "awards.csv")
    suppliers_path = os.path.join(input_dir, "awards_suppliers.csv")
    bids_path = os.path.join(input_dir, "bids_details.csv")

    main = pd.read_csv(main_path, usecols=["_link", "ocid", "buyer_id", "buyer_name", "tender_procurementMethod", "tender_value_amount"], low_memory=False)
    main = main.rename(columns={"_link": "_link_main"})

    awards = pd.read_csv(awards_path, usecols=["_link", "_link_main", "id", "value_amount"], low_memory=False)
    awards = awards.rename(columns={"_link": "award_link", "id": "award_id", "value_amount": "award_value_amount"})

    suppliers = pd.read_csv(suppliers_path, usecols=["_link_awards", "_link_main", "id", "name"], low_memory=False)
    suppliers = suppliers.rename(columns={"_link_awards": "award_link", "id": "supplier_id", "name": "supplier_name"})

    unified = pd.merge(awards, suppliers, on=["award_link", "_link_main"], how="left")
    unified = pd.merge(unified, main, on="_link_main", how="left")
    
    # Bids calculation logic (Lot Level)
    if os.path.exists(bids_path):
        bids = pd.read_csv(bids_path, usecols=["_link_main", "id", "relatedLots"], low_memory=False)
        bids_count = bids.dropna(subset=["_link_main", "id"]).groupby("_link_main")["id"].nunique().reset_index(name="bids_count")
        unified = pd.merge(unified, bids_count, on="_link_main", how="left")
    
    unified["is_single_bidder"] = (unified["bids_count"] == 1).astype(int)
    
    # Execute cleaning constraints (Methodology Sect 3.3)
    initial_len = len(unified)
    unified = unified.dropna(subset=["supplier_id"])
    dropped_missing = initial_len - len(unified)
    
    unified["supplier_name_norm"] = unified["supplier_name"].apply(normalize_supplier_name)
    unified = unified.drop_duplicates(subset=["ocid", "award_id"], keep="first")
    
    # Standardize column naming to strict unified OCDS crosswalk standard
    final_crosswalk_columns = [
        "ocid", "tender_procurementMethod", "buyer_name", "supplier_id", 
        "supplier_name_norm", "award_value_amount", "bids_count", "is_single_bidder"
    ]
    
    logging.info(f"DIGIWHIST Output: Processed {len(unified)} valid awards. Dropped {dropped_missing} missing entities.")
    return unified[[c for c in final_crosswalk_columns if c in unified.columns]]

if __name__ == "__main__":
    logging.info("Initialized 01_ocds_extraction_and_cleaning.py. Pipeline Ready.")
    # Example execution:
    # df_mn2024 = process_local_json_api("tenders.js", "bids.js")
    # df_ge2019 = process_digiwhist_ocds_csvs("georgia_export/")