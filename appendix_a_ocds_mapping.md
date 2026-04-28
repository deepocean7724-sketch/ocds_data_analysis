# Appendix A: OCDS Field Mapping Crosswalk

This table documents the theoretical mapping between the disparate local data structures (Mongolian electronic procurement archives and Open Data JSON APIs) and the unified Open Contracting Data Standard (OCDS). The DIGIWHIST Georgia 2019 dataset is already structurally aligned to OCDS, serving as the target schema for the harmonization pipeline.

| OCDS Core Field | Analytical Purpose | Mongolia 2019 (Archive) | Mongolia 2024 (JSON API) | Georgia 2019 (DIGIWHIST) |
| :--- | :--- | :--- | :--- | :--- |
| `ocid` | Unique tender identifier | `tender_id` | `tenderId` | `ocid` (via `_link_main`) |
| `date` | Temporal alignment | `year` / `publish_date` | `tenderYear` | `date` |
| `tender_procurementMethod` | Institutional assignment logic | `method` | `tenderTypeId` (Mapped) | `tender_procurementMethod` |
| `tender_value_amount` | RDD forcing variable (budget) | `budget` | `totalBudget` | `tender_value_amount` |
| `awards_id` | Unique award identifier | Generated incrementally | `invitationId` (sub-tender) | `award_id` |
| `awards_suppliers_id` | Entity resolution (hashing proxy) | `register_number` | `registerNumber` / `supplierId` | `supplier_id` |
| `awards_suppliers_name` | String matching fallback | `winner_name` | `supplierName` | `supplier_name` |
| `awards_value_amount` | Dependent variable for market share | `winning_bid_price` | `discountedAmount` / `openedBidderPrice` | `award_value_amount` |
| `awards_status` | Winner isolation filter | Explicit 'Won' text | `Шалгарсан` | System default (active) |
| `bids_count` | Competition level outcome metric | `bid_count` | Length of bid array | `bids_count` (lot level merge) |

**Mapping Notes:**
*   **Currency:** All `value_amount` metrics remain in local currency (MNT for Mongolia, GEL for Georgia). Cross national comparisons rely strictly on intra currency ratios (Gini, Concentration Ratios) to prevent exchange rate volatility from skewing structural concentration.
*   **Supplier ID Limitations:** The Mongolian datasets lack universal cryptographic hashing for early records. The pipeline relies heavily on `awards_suppliers_name` normalized strings where formal registry numbers are absent.