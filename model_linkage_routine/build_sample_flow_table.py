#!/usr/bin/env python
# coding: utf_8

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
    Build full path to a Stata file in the estimation directory.
    """
    return os.path.join(EST_DIR, name)


def main():
    # read projection data for age group two and skilled group
    df = pd.read_stata(dta_path("projection_data_age2_1_wbmk_v2.dta"))

    # attach state names and abbreviations
    sl = pd.read_excel(os.path.join(BASE_DIR, "statelookup2.xlsx"))
    df_m = df.merge(sl, on="statefip", how="inner")

    # build state level summary of extreme hot and cold exposure
    temp_state = (
        df_m.groupby(["state", "abbrev"], as_index=False)[["fexthot_28", "fextcold"]]
        .agg({"fexthot_28": "max", "fextcold": "min"})
    )

    temp_state.to_excel(os.path.join(BASE_DIR, "temp_changes.xlsx"), index=False)

    # read state level population counts and education shares
    state_split = pd.read_excel(
        os.path.join(BASE_DIR, "state_pop_educ_shares.xlsx")
    )
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

    # identify one representative decision maker id for each origin state
    chosen = (
        df_m.loc[df_m["chosen"] == 1, ["id", "state"]]
        .drop_duplicates()
        .rename(columns={"state": "origin_state"})
    )

    # attach origin state to every choice observation
    df_with_origin = df_m.merge(chosen, on="id", how="inner")

    # sum choice shares by origin state and destination state
    flows = (
        df_with_origin.groupby(["origin_state", "state"], as_index=False)["share"]
        .sum()
        .rename(columns={"state": "moving_to"})
    )

    # attach origin state population and unskilled age two share
    flows = flows.merge(
        state_split[["state", "unskl_2", "state_pop"]],
        left_on="origin_state",
        right_on="state",
        how="left",
    )

    flows = flows.rename(columns={"state": "origin_state_check"})

    # compute approximate number of unskilled age two workers in each origin state
    flows["unskilled_pop_age2_origin"] = flows["unskl_2"] * flows["state_pop"]

    # restrict to flows that originate from Texas and write test file
    texas_flows = flows[flows["origin_state"] == "texas"].copy()

    texas_flows.to_csv(
        os.path.join(BASE_DIR, "texas_out_unskl2.csv"), index=False
    )


if __name__ == "__main__":
    main()
