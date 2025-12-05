#!/usr/bin/env python
# coding: utf-8
#This code subsets the main second-stage dataset to the key covariates, saves a Stata file for the climate second stage, and converts a set of age-specific region fixed effect Excel files to Stata format for later use.

import pandas as pd
import numpy as np
import scipy.stats  # retained for compatibility with original environment
import warnings

warnings.filterwarnings("ignore")

# ======================================================================
# Paths
# ======================================================================

base_dta_dir = (
    "/Users/hannahkamen/Downloads/"
    "population-migration-master/estimation/1_main_specification/acs5yr0610/dta"
)

second_stage_path = f"{base_dta_dir}/second_stage_dataset.dta"
second_stage_out_path = f"{base_dta_dir}/second_stage_dataset_cl.dta"

fe_excel_template = f"{base_dta_dir}/regionfe_bpl_28_age{{age}}.xlsx"
fe_dta_template = f"{base_dta_dir}/regionfe_bpl_28_age{{age}}.dta"

# ======================================================================
# 1. Subset second-stage dataset to needed variables
# ======================================================================

data = pd.read_stata(second_stage_path)

# Wave fixed bin variables:
# wa_fbin158–wa_fbin222, then wa_fbin1–wa_fbin101
wa_bins_158_222 = [f"wa_fbin{i}" for i in range(158, 223)]
wa_bins_1_101 = [f"wa_fbin{i}" for i in range(1, 102)]

# Core climate, amenity, and demographic controls
core_vars = [
    "msa",
    "regionfe",
    "statefip",
    "lnrho",
    "metarea",
    "hot",
    "cold",
    "avgtemp",
    "precip",
    "dewpt",
    "relhum",
    "sun",
    "lnsea",
    "lnsea2",
    "lnlake",
    "lnlake2",
    "lnslope",
    "lnden",
    "lnhsgrad",
    "lncoll",
    "lngrad",
    "lnage",
    "lnhisp",
    "lnblack",
    "lnprec",
    "lndewpt",
    "lnrelhum",
    "lnsun",
    "lnavgtemp",
    "lnpop",
    "lnmanu",
    "lngvt",
    "lnpropt",
    "lnincome",
    "lnwhite",
    "lncrime",
]

keep_vars = wa_bins_158_222 + wa_bins_1_101 + core_vars

# Restrict to variables needed for the second-stage climate specification
data_lm = data[keep_vars]

# Export compact dataset for Stata
data_lm.to_stata(second_stage_out_path, write_index=False)

# ======================================================================
# 2. Convert region fixed effects Excel files to Stata format
# ======================================================================

# Files: regionfe_bpl_28_age2.xlsx through regionfe_bpl_28_age7.xlsx
for age in range(2, 8):
    fe_excel_path = fe_excel_template.format(age=age)
    fe_dta_path = fe_dta_template.format(age=age)

    fe_df = pd.read_excel(fe_excel_path)
    fe_df.to_stata(fe_dta_path, write_index=False)
