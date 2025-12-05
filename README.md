# Labor Market, Relocation, and Climate Change

This repository contains code and analysis for my dissertation chapter entitled "Extreme Heat and U.S. Labor Relocation: Implications for Inequality"

Abstract: Global warming is projected to lead to relatively large shifts in climate amenities that have long been
tied to household utility in the US. Using a logit model representing worker location choice across cities in the us, I estimate worker population changes by educational attainment resulting from climate shocks and link these shifts to WiNDC, a general equilibrium model
of the US economy. I demonstrate how impacts to labor supply by worker type affect the wage gap between workers with and without a college degree
## Structure

- `logit_model_run_files/` – All stata .do files required for 1) processing and cleaning ACS micro-data, climate data, and other controls 2) running logit regression that determines migratory frictions and dis-preference for extreme heat by worker type 3) second stage fixed effects regression and 4) processing state-level labor supply shifts induced by climate shocks
-- `logit_data/` – micro_data inputs for logit_model
- `windc_calibration/` – python scripts that NAICS industry skill intensity input for WiNDC equilibrium model
- `model_linkage_routine/` – python scripts that 1) process demographic shifts in educational attainment by state implied by logit model and 2) process this data for re-input into WiNDC.
- `final_results/` – python scripts that process and visualize GAMS output for use in paper.
-  `climate_migration_results/` – python scripts that process and visualize population shifts 

logit stata routine adapted from Carbone, Lee, and Shen (2021) "U.S. HOUSEHOLD PREFERENCES FOR CLIMATE AMENITIES: DEMOGRAPHIC ANALYSIS AND ROBUSTNESS TESTING"
