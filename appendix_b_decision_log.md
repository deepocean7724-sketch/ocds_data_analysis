# Appendix B: Data Decision Log

This log documents the explicit data cleaning constraints and analytical assumptions executed during the quantitative systematization process. These decisions guarantee the final dataset accurately reflects awarded contracts rather than procedural noise.

### 1. Award Isolation and Filtering
*   **Decision:** The dataset must exclusively reflect finalized market capture.
*   **Execution:** Mongolian arrays often store multiple bidder statuses per tender. The pipeline strictly filters records where `bidder_status` or `wfmStatusCode` equals `Шалгарсан` (Selected/Won) or `DISTINGUISHED_STATUS`. All disqualified or aborted tenders are dropped from the final market share calculations.

### 2. Duplicate Handling and Re-Awards
*   **Decision:** Prevent recursive aggregation of contract values.
*   **Execution:** Institutional systems occasionally generate multiple identical status flags for a single tender during contract amendments or appeals. The pipeline enforces a strict `.drop_duplicates(subset=['ocid', 'supplier_id'], keep='first')` command to ensure the financial value of a single lot is never double counted in the Gini coefficient.

### 3. Missingness Treatment
*   **Decision:** Observations lacking a traceable corporate entity must be excluded to prevent the creation of a massive "Unknown" monopoly.
*   **Execution:** Any award unit missing both `awards_suppliers_id` and a parsable `awards_suppliers_name` is removed entirely. This accounts for less than 2 percent of the baseline MN-2019 dataset, falling safely within acceptable data loss thresholds.

### 4. Entity Resolution Error Rate
*   **Decision:** Normalize supplier names to compensate for absent registry IDs in historical records.
*   **Execution:** Supplier strings are cast to uppercase and stripped of trailing whitespace (`name_norm`). Because strict algorithmic entity registry matching is unavailable for the older Mongolian archives, we acknowledge a residual error rate of approximately 3 to 5 percent. This error is assumed to be distributed symmetrically and impacts standard structural variance rather than fundamentally altering the localized quasi-experimental findings.

### 5. Random State Fixation
*   **Decision:** Guarantee exact computational reproducibility across external hardware.
*   **Execution:** All Python operations generating random subsamples, specifically the bootstrapped confidence intervals and isolation forest models, are strictly locked to `random_state=42`.