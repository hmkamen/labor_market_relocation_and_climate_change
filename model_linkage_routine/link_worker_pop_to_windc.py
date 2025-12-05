#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import scipy.stats
import math
import warnings
import os
warnings.filterwarnings("ignore")


# ### This routine links worker population data projected by logit to gams equilibrium model input, and handles these steps:
# #### 1) read in logitprojection data
# #### 2) merge with population data for each group
# #### 3) converge age groups to total population
# #### 4) get update population shares
# #### 5) read into gams , run gams 
# #### 6) re-import gams results (housing prices, wages, and updates population shares (from logit)
# #### 7) prep gams results for incorporation into logit routine
# #### 8) re-run shares in stata
# #### 9) map out migration flows for top entry exit

# base paths
DOWNLOADS_DIR = "/Users/hannahkamen/Downloads"
ESTIMATION_DIR = os.path.join(
    DOWNLOADS_DIR,
    "population-migration-master",
    "estimation",
    "1_main_specification",
    "acs5yr0610",
)
DTA_DIR = os.path.join(ESTIMATION_DIR, "dta")

# helper to build paths
def dta_path(filename):
    return os.path.join(DTA_DIR, filename)


def main():
    # Step 1 read logit projection data and benchmark population shares

    state_age_shares = pd.read_excel(
        os.path.join(DOWNLOADS_DIR, "state_age_shares.xlsx")
    )

    # container for per state per education group changes
    master = pd.DataFrame()

    # age_id equals 2 in this script
    age_id = 2

    # educ_id equals 0 for unskilled and 1 for skilled
    for educ_id in [0, 1]:
        # read projection data for given age and education group
        proj_file = f"projection_data_age{age_id}_{educ_id}_wbmk_iter1.dta"
        proj_path = dta_path(proj_file)
        tmp0 = pd.read_stata(proj_path)

        # Step 2 merge projection data with state age information

        # group by state to get total probability mass in benchmark and iteration 1
        tmp = (
            tmp0.groupby("state", as_index=False)
            .agg({"fexthot_28": "max", "fextcold": "max", "share_it1": "sum", "share": "sum"})
        )

        # Step 3 compute percent change in shares for given age group and education group

        tmp["pct_change"] = (tmp["share_it1"] - tmp["share"]) / tmp["share"]

        # attach age shares and tag age and education identifiers
        tmp = tmp.merge(state_age_shares, on="state", how="inner")
        tmp["age_id"] = age_id
        tmp["educ_id"] = educ_id

        # current implementation gives age group two full weight in the total change
        # original plan used tmp["pct_change"] * tmp[str(age_id)] to weight by age share
        tmp["contribution_to_total_change"] = tmp["pct_change"] * 1.0

        master = master.append(tmp, ignore_index=True)

    # aggregate over age groups to get total percent change by state and education group
    master_gr = (
        master.groupby(["state", "educ_id"], as_index=False)[
            "contribution_to_total_change"
        ]
        .sum()
    )

    # Step 4 prepare GAMS shock input file with state level skill share changes

    # read state lookup for abbreviations
    sl = pd.read_excel(os.path.join(DOWNLOADS_DIR, "statelookup2.xlsx"))

    # map numeric educ_id to labels "unskl" and "skl"
    master_gr["educ_id"] = (
        master_gr["educ_id"].astype(str).str.replace("0", "unskl").str.replace("1", "skl")
    )

    # merge state abbreviation and rename columns for GAMS input
    master_gr = master_gr.merge(sl, on="state", how="inner")
    master_gr = master_gr.rename(
        columns={
            "abbrev": "r",
            "educ_id": "sk",
            "contribution_to_total_change": "skill_shr",
        }
    )

    master_gr = master_gr[["r", "sk", "skill_shr"]]

    # write shock file for GAMS
    gams_shock_path = os.path.join(DOWNLOADS_DIR, "le0_shock_0_it1.csv")
    master_gr.to_csv(gams_shock_path, index=False)

    # Step 5 run GAMS with updated worker supply
    # this step occurs outside this script
    # GAMS reads le0_shock_0_it1.csv, solves the equilibrium, and writes y_rpt.csv, phou_rpt.csv, npl_rpt.csv

    # Step 6 re import GAMS results and combine with population changes

    y_rpt = pd.read_csv(os.path.join(DOWNLOADS_DIR, "y_rpt.csv"))
    phou_rpt = pd.read_csv(os.path.join(DOWNLOADS_DIR, "phou_rpt.csv"))
    npl_rpt = pd.read_csv(os.path.join(DOWNLOADS_DIR, "npl_rpt.csv"))

    # read MSA data used in the second stage of the logit model
    msa = pd.read_stata(dta_path("second_stage_dataset_cl.dta"))

    # compute percent of state population in each MSA for logit input
    msa = msa[["statefip", "msa", "lnpop"]].copy()
    msa["msa_pop"] = np.exp(msa["lnpop"])
    msa_tot = msa.groupby("statefip", as_index=False)["msa_pop"].sum()
    msa_tot = msa_tot.rename(columns={"msa_pop": "msa_pop_total"})
    msa = msa.merge(msa_tot, on="statefip")
    msa["pct_state_total"] = msa["msa_pop"] / msa["msa_pop_total"]

    msa_pct_path = dta_path("msa_pop_pct.dta")
    msa.to_stata(msa_pct_path, write_index=False)

    # tidy GAMS outputs

    # labor price by region and skill
    npl_rpt = npl_rpt[["region", "skill", "value"]].rename(
        columns={"region": "abbrev", "value": "pl"}
    )

    # housing price index by region
    phou_rpt = phou_rpt[["pct", "region"]].rename(
        columns={"region": "ph", "pct": "abbrev"}
    )

    # read state education shares and population
    state_educ = pd.read_excel(os.path.join(DOWNLOADS_DIR, "state_educ_shares.xlsx"))
    state_educ = state_educ.merge(sl, on="state", how="inner")
    state_educ = state_educ[
        ["statefip", "skl", "unskl", "state", "abbrev", "state_pop"]
    ].copy()

    # merge housing prices, labor prices, and percent changes from master_gr
    r_df = (
        phou_rpt.merge(npl_rpt, on="abbrev")
        .merge(master_gr, left_on=["abbrev", "skill"], right_on=["r", "sk"])
        .merge(state_educ, on="abbrev")
    )

    # Step 7 prepare combined results for the logit routine

    # pivot percent changes in skill shares by state
    pop_changes = (
        r_df.pivot(index="state", columns="sk", values="skill_shr")
        .reset_index()
        .rename(columns={"skl": "skl_pct_delta", "unskl": "unskl_pct_delta"})
    )

    # pivot labor prices by state and skill
    pl_changes = (
        r_df.pivot(index="state", columns="sk", values="pl")
        .reset_index()
        .rename(columns={"skl": "pl_skl", "unskl": "pl_unskl"})
    )

    # keep one row per state and attach state level changes
    r_df_base = r_df[
        ["statefip", "abbrev", "state", "skill", "ph", "skl", "unskl", "state_pop"]
    ].drop_duplicates(subset="state")

    r_df_base = (
        r_df_base.merge(pop_changes, on="state").merge(pl_changes, on="state")
    )

    # compute new skill level counts and new total state population
    r_df_base["skilled_level_change"] = (
        r_df_base["skl"] * r_df_base["state_pop"]
        + r_df_base["skl"] * r_df_base["state_pop"] * r_df_base["skl_pct_delta"]
    )
    r_df_base["unskilled_level_change"] = (
        r_df_base["unskl"] * r_df_base["state_pop"]
        + r_df_base["unskl"] * r_df_base["state_pop"] * r_df_base["unskl_pct_delta"]
    )
    r_df_base["new_state_pop"] = (
        r_df_base["skilled_level_change"] + r_df_base["unskilled_level_change"]
    )

    # write state level data for logit estimation
    gams_dta_path = dta_path("gams_dta.dta")
    r_df_base.to_stata(gams_dta_path, write_index=False)

    # Step 8 re estimate logit shares in Stata
    # this step occurs outside this script
    # Stata reads msa_pop_pct.dta and gams_dta.dta and re runs the logit model to produce updated shares

    # Step 9 construct migration flow tables for top entry and exit states
    # this step is handled in a separate script that constructs state to state flows
    # for example the flow map script that reads updated shares and produces entrance files


if __name__ == "__main__":
    main()
