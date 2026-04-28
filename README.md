# Public Procurement Analysis: Structural Concentration and Institutional Design

This repository contains the complete quantitative reproducibility package for the thesis evaluating structural supplier inequality and algorithmically managed procurement platforms (Mongolia 2019/2024 and Georgia 2019). The analysis integrates an extended Most Similar Systems Design (MSSD) with a fuzzy Regression Discontinuity Design (RDD).

## Repository Architecture

To verify the input-agnostic framework and the strict adherence to the Open Contracting Data Standard (OCDS), the analytical logic is compartmentalized into three primary Python execution engines:

*   `01_ocds_extraction_and_cleaning.py`: Harmonizes raw JSON payloads and DIGIWHIST CSV bulk exports into a singular OCDS compliant dataframe. Implements explicit missingness treatments and duplicate filtering logic (see Appendix B).
*   `02_universal_metrics_engine.py`: Accepts any OCDS mapped dataset and calculates the central measurement architecture (normalized Gini coefficients, Lorenz curves, Concentration Ratios, and "Professional Winners" dependencies) without altering core mathematical loops.
*   `03_statistical_modeling_and_figures.py`: Generates the quasi-causal and inferential tests. This includes the chi-square associational tests, the 200-iteration bootstrap subsampling (`random_state=42`), and the fuzzy RDD model utilizing the 100M/150M MNT legal procedure cutoffs via an R bridge.

## Installation and Requirements

The statistical pipeline heavily utilizes Python 3 along with specific econometrics packages ported from R. 

1. Ensure Python 3.10+ is installed.
2. Ensure an R environment is installed locally with the `rdrobust` package configured.
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt