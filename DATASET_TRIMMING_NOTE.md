# Dataset Trimming Note for GitHub Compatibility

To comply with GitHub’s file size limits, the `bidder_comment` and `tender_gov_url` columns were removed from the raw Mongolian datasets (`MN-2019_trimmed.csv` and `MN-2024_trimmed.csv`). 

**This action has no impact on the computational reproducibility of the thesis or the Python analysis pipeline, for the following reasons:**

1. **Extraction Logic:** The extraction script (`01_ocds_extraction_and_cleaning.py`) isolates winning entities using explicit categorical flags (e.g., `bidder_status` == "Шалгарсан"), rather than parsing qualitative comment text. 
2. **Standardized Schema:** Neither the URL nor the administrative comment text are mapped to the target Open Contracting Data Standard (OCDS) schema defined in `appendix_a_ocds_mapping.md`. 
3. **Quantitative Modeling:** The structural metrics engine and Fuzzy RDD calculations (`02_` and `03_` scripts) rely strictly on numeric bounds (budgets/award values), categorical predictors (procurement methods), and hashed entity IDs. The removed columns contained unstructured text and redundant URLs with no mathematical utilization in the thesis.
