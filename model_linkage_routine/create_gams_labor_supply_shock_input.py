#!/usr/bin/env python
# coding: utf-8

##This script constructs state level labor supply shocks for GAMS from logit projection outputs. For each education group at age group two, it ##compares projected state shares to a benchmark, converts those differences into percent changes in state worker populations, aggregates across ##age group two, and then writes a GAMS ready CSV file containing the implied percent changes in skilled and unskilled worker shares by state.


import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/hannahkamen/Downloads"
EST_DIR = os.path.join(
    BASE_DIR,
    "population-migration-master",
    "estimation",
    "1_main_specification",
    "acs5yr0610",
    "dta",
)


def dta_path(name):
    """
    Build full path to a Stata dataset in the estimation directory.
    """
    return os.path.join(EST_DIR, name)


def build_state_skill_shocks(age_ids, educ_ids):
    """
    Construct state level percent changes in worker shares by education group.

    For each age group and education group:
    1 read logit projection output for the counterfactual
    2 read matching benchmark projection output
    3 aggregate shares by state for both files
    4 compute percent change relative to the benchmark
    5 weight the change across age groups and stack results
    """
    state_split = pd.read_excel(os.path.join(BASE_DIR, "state_pop_educ_shares.xlsx"))
    state_age_shares = pd.read_excel(os.path.join(BASE_DIR, "state_age_shares.xlsx"))
    msaid_state_lookup = pd.read_excel(os.path.join(BASE_DIR, "msaid_state_lookup.xlsx"))
    sl = pd.read_excel(os.path.join(BASE_DIR, "statelookup2.xlsx"))

    state_split = state_split[
        [
            "skl_2",
            "skl_3",
            "skl_4",
            "skl_5",
            "skl_6",
            "skl_7",
            "unskl_2",
            "unskl_3",
            "unskl_4",
            "unskl_5",
            "unskl_6",
            "unskl_7",
            "state",
            "state_pop",
        ]
    ]

    master = pd.DataFrame()

    for a in age_ids:
        for e in educ_ids:
            # read projection data for given age group and education group
            proj_file = f"projection_data_age{a}_{e}.dta"
            bmk_file = f"projection_data_age{a}_{e}_test.dta"

            tmp0 = pd.read_stata(dta_path(proj_file))
            bmk0 = pd.read_stata(dta_path(bmk_file))

            # attach state abbreviations
            tmp0 = tmp0.merge(sl, on="statefip", how="inner")

            # attach metro area and state information for benchmark file
            bmk0 = (
                bmk0.merge(msaid_state_lookup, on="msa", how="inner")
                .merge(sl, on="statefip", how="inner")
            )

            # aggregate projection and benchmark by state
            proj_state = (
                tmp0.groupby("state", as_index=False)[["fexthot_28", "fextcold", "share", "chosen"]]
                .agg({"fexthot_28": "max", "fextcold": "max", "share": "sum", "chosen": "sum"})
            )

            bmk_state = (
                bmk0.groupby("state", as_index=False)[["share", "chosen"]]
                .sum()
                .rename(columns={"share": "benchmark_pop"})
            )
            bmk_state = bmk_state[["state", "benchmark_pop"]]

            # merge benchmark into projection and compute percent change
            proj_state = proj_state.merge(bmk_state, on="state", how="inner")
            proj_state["pct_change"] = (
                proj_state["share"] - proj_state["benchmark_pop"]
            ) / proj_state["benchmark_pop"]

            # attach age shares and education identifier
            proj_state = proj_state.merge(state_age_shares, on="state", how="inner")
            proj_state["age_id"] = a
            proj_state["educ_id"] = e

            # current implementation treats this age group as the full working population
            # original intention was pct_change multiplied by the state age share
            proj_state["contribution_to_total_change"] = proj_state["pct_change"] * 1.0

            master = master.append(proj_state, ignore_index=True)

    # aggregate contributions from all age groups to obtain total change by state and education group
    master_gr = (
        master.groupby(["state", "educ_id"], as_index=False)["contribution_to_total_change"]
        .sum()
    )

    # convert educ_id to skill labels and attach abbreviations
    master_gr["educ_id"] = (
        master_gr["educ_id"].astype(str).str.replace("0", "unskl").str.replace("1", "skl")
    )
    master_gr = master_gr.merge(sl, on="state", how="inner")

    master_gr = master_gr.rename(
        columns={
            "abbrev": "r",
            "educ_id": "sk",
            "contribution_to_total_change": "skill_shr",
        }
    )

    master_gr = master_gr[["r", "sk", "skill_shr"]]

    return master_gr


def main():
    """
    Build age two skill shocks by state and export GAMS input file.
    """
    # restrict to age group two and two education groups in this routine
    age_ids = [2]
    educ_ids = [0, 1]

    master_gr = build_state_skill_shocks(age_ids=age_ids, educ_ids=educ_ids)

    # write GAMS shock file
    out_csv = os.path.join(BASE_DIR, "le0_shock_0.csv")
    master_gr.to_csv(out_csv, index=False)

    # write backup Excel file
    out_xlsx = os.path.join(BASE_DIR, "age_2_backup.xlsx")
    master_gr.to_excel(out_xlsx, index=False)


if __name__ == "__main__":
    main()
