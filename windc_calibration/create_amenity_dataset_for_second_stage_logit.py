#!/usr/bin/env python
# coding: 

#this code combines Albouy et al. amenity data with an MSA 2013 to PUMA 2000 crosswalk, creates virtual MSAs for small non metropolitan states (Wyoming, South Dakota, Montana), and then constructs MSA level amenity variables. It does this by aggregating Albouy variables by PUMA and state, merging with the crosswalk, computing inverse distances to seas and lakes, weighting all amenity variables by each PUMA share of MSA population, and finally aggregating to the MSA level. The resulting weighted Albouy dataset is written to a Stata file for use in decomposition of the fixed effect that is produces by the logit stage

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/hannahkamen/Documents/population-migration2"
DTA_DIR = os.path.join(BASE_DIR, "dta")


def dta_path(name: str) -> str:
    """
    Build full path to a Stata dataset in the dta directory.
    """
    return os.path.join(DTA_DIR, name)


def main():
    """
    Construct metropolitan amenity measures from Albouy data using PUMA to MSA weights.

    Steps
    1 read PUMA to MSA crosswalk and Albouy amenity data
    2 define virtual MSAs for selected non metropolitan states by assigning new PumaID codes
    3 aggregate Albouy data by PumaID and state
    4 attach MSA information from the crosswalk
    5 construct inverse distance measures to sea and lake
    6 weight amenity variables by the share of each PUMA in the MSA population
    7 aggregate weighted variables to the MSA level and export to Stata
    """

    # step 1 read crosswalk and Albouy data
    puma_lkup = pd.read_stata(dta_path("msa2013_puma2000.dta"))
    albuoy = pd.read_stata(dta_path("albouy_all.dta"))

    # keep relevant crosswalk fields
    puma_lkup = puma_lkup[
        ["met2013", "msaname_crosswalk", "statefip", "statename", "pctmsapop", "PumaID"]
    ]

    # step 2 create virtual MSAs for small non metropolitan states using new PumaID codes
    albuoy["PumaID"] = np.where(
        albuoy["msaname"].isin(["Non-metro, WY", "Casper, WY", "Cheyenne, WY"]),
        999,
        albuoy["PumaID"],
    )
    albuoy["PumaID"] = np.where(
        albuoy["msaname"].isin(
            ["Rapid City, SD", "Non-metro, SD", "Sioux Falls, SD"]
        ),
        1001,
        albuoy["PumaID"],
    )
    albuoy["PumaID"] = np.where(
        albuoy["msaname"].isin(
            ["Non-metro, MT", "Great Falls, MT", "Billings, MT", "Missoula, MT"]
        ),
        1002,
        albuoy["PumaID"],
    )

    # step 3 aggregate Albouy variables by PumaID and state
    albuoy_gr = albuoy.groupby(["PumaID", "statefip"], as_index=False).mean()

    # step 4 expand crosswalk with rows for virtual MSAs
    puma_lkup.loc[len(puma_lkup.index)] = [
        999,
        "WY Virtual MSA, WY",
        56,
        "Wyoming",
        100,
        999,
    ]
    puma_lkup.loc[len(puma_lkup.index)] = [
        1001,
        "SD Virtual MSA, SD",
        46,
        "South Dakota",
        100,
        1001,
    ]
    puma_lkup.loc[len(puma_lkup.index)] = [
        1002,
        "MT Virtual MSA, MT",
        30,
        "Montana",
        100,
        1002,
    ]

    puma_lkup["msaname_crosswalk_l"] = puma_lkup["msaname_crosswalk"].str.lower()

    # step 5 merge aggregated Albouy data with crosswalk
    albuoy_m = albuoy_gr.merge(
        puma_lkup, on=["PumaID", "statefip"], how="inner"
    )

    # handle distances of zero to avoid division by zero
    albuoy_m["mean_sea"] = np.where(albuoy_m["mean_sea"] < 1, 1, albuoy_m["mean_sea"])
    albuoy_m["mean_lake"] = np.where(
        albuoy_m["mean_lake"] < 1, 1, albuoy_m["mean_lake"]
    )

    # create inverse distance measures to sea and lake
    albuoy_m["sea"] = 1.0 / albuoy_m["mean_sea"]
    albuoy_m["sea2"] = albuoy_m["sea"] ** 2
    albuoy_m["lake"] = 1.0 / albuoy_m["mean_lake"]
    albuoy_m["lake2"] = albuoy_m["lake"] ** 2

    # compute PUMA share of MSA population
    albuoy_m["propmsapop"] = albuoy_m["pctmsapop"] / 100.0

    # step 6 weight numeric amenity variables by share of MSA population
    non_weight_cols = [
        "statefip",
        "PumaID",
        "msa",
        "msaname",
        "BootstrapMSA",
        "BootstrapState",
        "met2013",
        "msaname_crosswalk",
        "statename",
        "pctmsapop",
        "pctpumapop",
        "dup",
        "msaname_crosswalk_l",
        "propmsapop",
    ]

    for col in albuoy_m.columns:
        if col not in non_weight_cols:
            # attempt to weight numeric columns
            try:
                albuoy_m[col] = albuoy_m[col] * albuoy_m["propmsapop"]
            except Exception:
                pass

    # step 7 aggregate weighted variables to MSA level
    group_keys = ["statefip", "PumaID", "msaname_crosswalk", "met2013", "statename"]
    albuoy_m_gr = albuoy_m.groupby(group_keys, as_index=False).sum()

    # standardize metropolitan area name and export
    albuoy_m_gr = albuoy_m_gr.rename(columns={"msaname_crosswalk": "metarea"})
    albuoy_m_gr["metarea"] = albuoy_m_gr["metarea"].str.lower()

    out_path = dta_path("albuoy_all_weighted_v2.dta")
    albuoy_m_gr.to_stata(out_path, write_index=False)


if __name__ == "__main__":
    main()
