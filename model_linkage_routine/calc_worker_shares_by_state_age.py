#!/usr/bin/env python
# coding: utf_8

#this code takes state level age shares and total state population, converts them into working age population counts, then normalizes those counts to obtain the share of the working population in each age group for every state. It then merges on state identifiers from a lookup file and writes a Stata dataset that serves as a lookup for state age shares in later steps of the model.

import os
import warnings
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


def main():
    """
    Construct state level working age shares by age group and write a lookup file.
    """

    # read state to abbreviation lookup
    sl = pd.read_excel(os.path.join(BASE_DIR, "statelookup2.xlsx"))

    # read state age shares with total state population
    state_age_shares = pd.read_excel(
        os.path.join(BASE_DIR, "state_age_shares.xlsx")
    )

    # convert age shares into working age counts by multiplying by total state population
    for col in ["2", "3", "4", "5", "6", "7"]:
        state_age_shares[col] = state_age_shares[col] * state_age_shares["state_pop"]

    # compute total working age population as the sum of age groups two through seven
    state_age_shares["working_pop"] = state_age_shares[
        ["2", "3", "4", "5", "6", "7"]
    ].sum(axis=1)

    # convert counts back into shares of the working age population
    for col in ["2", "3", "4", "5", "6", "7"]:
        state_age_shares[col] = state_age_shares[col] / state_age_shares["working_pop"]

    # prepare lookup table with state identifiers and working age shares by age group
    cols_keep = ["state", "2", "3", "4", "5", "6", "7", "working_pop"]
    state_age_shares_lkup = state_age_shares[cols_keep].merge(
        sl, on="state", how="inner"
    )

    state_age_shares_lkup = state_age_shares_lkup.rename(
        columns={
            "2": "age2_",
            "3": "age3_",
            "4": "age4_",
            "5": "age5_",
            "6": "age6_",
            "7": "age7_",
        }
    )

    # ensure statefip is numeric for later merges
    state_age_shares_lkup["statefip"] = state_age_shares_lkup["statefip"].astype(
        float
    )

    # write Stata lookup file for use in the migration and GAMS routines
    out_path = dta_path("state_age_shares_lkup.dta")
    state_age_shares_lkup.to_stata(out_path, write_index=False)


if __name__ == "__main__":
    main()
