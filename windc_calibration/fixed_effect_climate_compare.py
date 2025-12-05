#!/usr/bin/env python
# coding: utf-

#This code links and compares msa fixed effects and climate data from the 2006-2010 acs data to fixed effects from the 2015-2019 data, harmonizes MSA definitions #(2000 #/ 2007 / 2019), computes absolute differences, and exports two Excel files: one for fixed effects and one for climate measures.

import pandas as pd
import numpy as np
import scipy.stats  # imported for completeness
import warnings

warnings.filterwarnings("ignore")

gams_python_path = "/Library/Frameworks/GAMS.framework/Resources/apifiles/Python/gams"

# =====================================================================
# Load crosswalks and identifier files
# =====================================================================

# MSA identifier data (contains msa and metarea codes)
msa = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/msa_identifier.dta"
)

# Crosswalk between 2019 MSAs and 2000 / 2007 MSA codes
msa_lookup = pd.read_excel(
    "/Users/hannahkamen/Downloads/msa_2019_lookup_adj.xlsx"
)

# =====================================================================
# Compare old and new climate variables (Albouy-style)
# =====================================================================

# Old climate file (ACS 06–10 heterogeneity)
albuoy_old = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/acs5yr0610/dta/climate_hetero.dta"
).copy()

# Harmonize metarea naming (replace "-" with "/" to match older lookup)
albuoy_old["metarea"] = albuoy_old["metarea"].str.replace("-", "/", regex=False)
albuoy_old["avgtemp_old"] = albuoy_old["avgtemp"]
albuoy_old["hot_old"] = albuoy_old["exthot_28"]
albuoy_old["cold_old"] = albuoy_old["extcold"]
albuoy_old = albuoy_old[["metarea", "hot_old", "cold_old", "avgtemp_old"]]

# New climate file
albuoy_new = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/albuoy_new.dta"
).copy()
albuoy_new["avgtemp_new"] = albuoy_new["avgtemp"]
albuoy_new["hot_new"] = albuoy_new["hot"]
albuoy_new["cold_new"] = albuoy_new["cold"]
albuoy_new = albuoy_new[["metarea", "hot_new", "cold_new", "avgtemp_new"]]

# Bridge old metarea (2007-style) to 2019 metarea, then to new climate metarea
albuoy_m = (
    albuoy_old
    .merge(
        msa_lookup,
        left_on="metarea",
        right_on="metarea_07_lookup",
        how="inner"
    )
    .merge(
        albuoy_new,
        left_on="metarea_19",
        right_on="metarea",
        how="inner"
    )
)

# Absolute differences between old and new climate variables
albuoy_m["abs_diff_hot"] = (albuoy_m["hot_new"] - albuoy_m["hot_old"]).abs()
albuoy_m["abs_diff_cold"] = (albuoy_m["cold_new"] - albuoy_m["cold_old"]).abs()
albuoy_m["abs_diff_avgtemp"] = (
    albuoy_m["avgtemp_new"] - albuoy_m["avgtemp_old"]
).abs()

albuoy_m.to_excel(
    "/Users/hannahkamen/Downloads/old_new_albuoy_compare.xlsx",
    index=False,
)

# =====================================================================
# Compare old and new region fixed effects by age group
# =====================================================================

# New fixed effects for age group 1
new_fe_age1 = pd.read_excel(
    "/Users/hannahkamen/Documents/population-migration2/dta/"
    "regionfe_bpl_28_age1_adj.xlsx"
)

# Link new FE to msa identifiers and 2019 lookup
new_fe = (
    msa.merge(new_fe_age1, on="msa", how="inner")
       .merge(msa_lookup, left_on="metarea", right_on="metarea_19", how="inner")
)

new_fe = new_fe.rename(columns={"regionfe": "regionfe_age1_new"})

# Add new fixed effects for age groups 2–4
for i in np.arange(2, 5, 1):
    df = pd.read_excel(
        f"/Users/hannahkamen/Documents/population-migration2/dta/"
        f"regionfe_bpl_28_age{i}_adj.xlsx"
    )
    df = df.rename(columns={"regionfe": f"regionfe_age{i}_new"})
    # Merge on msa to bring in additional age-specific FE columns
    new_fe = new_fe.merge(df[["msa", f"regionfe_age{i}_new"]], on="msa", how="inner")

# Keep only relevant columns from new FE
new_fe = new_fe[
    [
        "metarea",          # current metarea (2019 code via msa_identifier)
        "metarea_07_lookup",
        "regionfe_age1_new",
        "regionfe_age2_new",
        "regionfe_age3_new",
        "regionfe_age4_new",
    ]
]

# Old fixed effects
old_fe = pd.read_csv(
    "/Users/hannahkamen/Downloads/FE_acs0610.csv"
).copy()

old_fe = old_fe.rename(
    columns={
        "metarea": "metarea_07_lookup",
        "regionfe_age1": "regionfe_age1_old",
        "regionfe_age2": "regionfe_age2_old",
        "regionfe_age3": "regionfe_age3_old",
        "regionfe_age4": "regionfe_age4_old",
    }
)

old_fe = old_fe[
    [
        "metarea_07_lookup",
        "regionfe_age1_old",
        "regionfe_age2_old",
        "regionfe_age3_old",
        "regionfe_age4_old",
    ]
]

# Merge old FEs onto new FEs using 2007-style metarea lookup
old_new_fe = new_fe.merge(old_fe, on="metarea_07_lookup", how="inner")

# Attach new climate variables (already constructed above) by metarea
# Use albuoy_new, which is keyed by metarea (same code system as msa_identifier)
old_new_fe_m = old_new_fe.merge(
    albuoy_new,
    on="metarea",
    how="inner",
)

# Absolute differences in region fixed effects by age group
for i in np.arange(1, 5, 1):
    old_col = f"regionfe_age{i}_old"
    new_col = f"regionfe_age{i}_new"
    diff_col = f"fe_absdiff_{i}"
    old_new_fe_m[diff_col] = (old_new_fe_m[new_col] - old_new_fe_m[old_col]).abs()

# Export combined FE comparison table (old vs new FE plus new climate)
old_new_fe_m.to_excel(
    "/Users/hannahkamen/Downloads/fe_compare.xlsx",
    index=False,
)
