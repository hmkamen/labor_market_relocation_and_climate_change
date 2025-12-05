#!/usr/bin/env python
# this code builds the input migration flow datadframe separately for college educated and non-college educated workers
# the resulting output dataframe is used as an input into the flowmap visualization tool I create for the paper on https://www.flowmap.blue/

## state-to-state worker flows are constructed using the following routine:

## 1) how much each origin state’s probability of choosing state s changes in the post-climate-shock logit output, input variable (share_diff)
##2) how many many extra workers state s gains in total in that educational attainment group from the shock, this involves a weighting procedure by existing populations and educational attainment share in that group (final_change * state_pop * skill_share).

Then it allocates Florida’s extra population across origin states in proportion to the probability changes.

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# base directory for input and output files
BASE_DIR = "/Users/hannahkamen/Downloads"

# total population constant used for normalization
TOTAL_POP = 14412444.2


def path_in_base(name):
    # helper that builds full path inside the base directory
    return os.path.join(BASE_DIR, name)


def build_state_coords(sl):
    # read census files that contain centroids for geographic pairs
    map_files = [path_in_base("census_texas.csv"), path_in_base("census_ny.csv")]
    frames = [pd.read_csv(f) for f in map_files]
    map_dta = pd.concat(frames, ignore_index=True)

    # create centroid strings and clean labels
    map_dta["centroid2"] = map_dta["centroid1"] + "," + map_dta["centroid2"]
    map_dta["centroid1"] = map_dta["FULL1_NAME"] + "," + map_dta["FULL2_NAME"]
    map_dta["FULL1_NAME"] = map_dta["GEOID1"]
    map_dta["FULL2_NAME"] = map_dta["GEOID2"]

    # replace geo identifiers with cleaner ids from the input
    map_dta["GEOID1"] = map_dta["level_1"]
    map_dta["GEOID2"] = map_dta["Unnamed: 0"]
    map_dta = map_dta[
        ["GEOID1", "GEOID2", "FULL1_NAME", "FULL2_NAME", "centroid1", "centroid2"]
    ]

    # find one centroid for each state using abbreviation matches
    states = sl["abbrev"].dropna().unique()
    state_coords_list = []

    for s in states:
        subset = map_dta[map_dta["FULL2_NAME"].str.contains(s)]
        if not subset.empty:
            subset = subset.copy()
            subset["state"] = s
            state_coords_list.append(subset)

    state_coords = pd.concat(state_coords_list, ignore_index=True)
    state_coords = state_coords.drop_duplicates(subset="state")
    state_coords = state_coords[["state", "FULL2_NAME", "centroid2"]].copy()

    # parse centroid strings into numeric latitude and longitude
    state_coords["id"] = np.arange(len(state_coords))
    state_coords["name"] = state_coords["state"]
    state_coords["lat"] = state_coords["centroid2"].apply(
        lambda x: x.split(",")[1].replace(")", "").strip()
    )
    state_coords["lon"] = state_coords["centroid2"].apply(
        lambda x: x.split(",")[0].replace("(", "").replace("c", "").strip()
    )

    # keep only variables needed by the flow map input
    state_coords_lm = state_coords[["id", "name", "lat", "lon"]]
    state_coords_lm.to_csv(path_in_base("flowmap_location_lookup.csv"), index=False)

    return state_coords_lm


def prepare_flows(master_map):
    # identify origin state for each decision maker using chosen equal one rows
    chosen = (
        master_map.loc[master_map["chosen"] == 1, ["id", "state"]]
        .drop_duplicates()
        .rename(columns={"state": "origin_state"})
    )

    # attach origin state to every row for that id
    master_with_origin = master_map.merge(chosen, on="id", how="left")

    # sum shares by origin state and destination state
    flows = (
        master_with_origin.groupby(["origin_state", "state"], as_index=False)[
            ["share0", "shareb"]
        ]
        .sum()
    )

    # rename columns and compute change in shares
    flows = flows.rename(columns={"origin_state": "living_flag", "state": "moving_to"})
    flows["share_diff"] = flows["share0"] - flows["shareb"]

    return flows


def build_entrance_flows(
    flow_df,
    le0_subset,
    state_educ,
    state_to_abbrev,
    abbrev_to_id,
    skill_col,
    total_pop,
    out_file,
):
    # keep destination states where the shock implies positive net inflow
    pos_states = le0_subset.loc[le0_subset["final_change"] > 0, "state"].unique()
    flow_pos = flow_df.loc[
        flow_df["moving_to"].isin(pos_states) & (flow_df["share_diff"] > 0)
    ].copy()

    if flow_pos.empty:
        return pd.DataFrame(columns=["origin", "dest", "count"])

    # compute total change in shares by destination state
    totals = (
        flow_pos.groupby("moving_to", as_index=False)["share_diff"]
        .sum()
        .rename(columns={"share_diff": "share_diff_tot"})
    )

    flow_pos = flow_pos.merge(totals, on="moving_to", how="left")
    flow_pos["inflow_share"] = flow_pos["share_diff"] / flow_pos["share_diff_tot"]

    # attach state education shares and population
    entrance = flow_pos.merge(
        state_educ, left_on="moving_to", right_on="state", how="inner"
    )

    # attach shocks for matched state and education group
    entrance = entrance.merge(
        le0_subset[["state", "final_change"]], on="state", how="inner"
    )

    # compute implied population change for each origin and destination pair
    entrance["raw_pop_change_moving_to"] = (
        entrance["final_change"]
        * entrance["state_pop"]
        * entrance[skill_col]
        * entrance["inflow_share"]
    )

    # map state names to abbreviations
    entrance["dest_abbrev"] = entrance["moving_to"].map(state_to_abbrev)
    entrance["origin_abbrev"] = entrance["living_flag"].map(state_to_abbrev)

    # map abbreviations to integer ids used by the flow map format
    entrance["dest"] = entrance["dest_abbrev"].map(abbrev_to_id)
    entrance["origin"] = entrance["origin_abbrev"].map(abbrev_to_id)

    # keep only columns needed for the flow map and normalize counts
    entrance_lm = entrance[["origin", "dest", "raw_pop_change_moving_to"]].copy()
    entrance_lm = entrance_lm.rename(columns={"raw_pop_change_moving_to": "count"})
    entrance_lm["count"] = entrance_lm["count"] / total_pop

    entrance_lm.to_csv(path_in_base(out_file), index=False)

    return entrance_lm


def main():
    # read lookup for state names and abbreviations
    sl = pd.read_excel(path_in_base("statelookup2.xlsx"))

    # read state education shares and population counts
    state_educ = pd.read_excel(path_in_base("state_educ_shares.xlsx"))
    state_educ = state_educ[["statefip", "skl", "unskl", "state", "abbrev", "state_pop"]]

    # build centroids and ids for all states in the map data
    state_coords_lm = build_state_coords(sl)
    abbrev_to_id = state_coords_lm.set_index("name")["id"]
    state_to_abbrev = sl.set_index("state")["abbrev"]

    # read model output for unskilled and skilled groups
    master_map_unskl2 = pd.read_csv(path_in_base("map_data_unskl2.csv"))
    master_map_skl2 = pd.read_csv(path_in_base("map_data_skl2.csv"))

    # compute share changes for unskilled and skilled groups
    unskl_flows = prepare_flows(master_map_unskl2)
    skl_flows = prepare_flows(master_map_skl2)

    # read shocks by state and education group
    le0 = pd.read_csv(path_in_base("le0_shock0_v2_test2.csv"))
    le0 = le0[["r", "sk", "skill_shr"]].drop_duplicates()
    le0 = le0.rename(
        columns={"sk": "educ_id", "skill_shr": "final_change", "r": "abbrev"}
    )
    le0 = le0.merge(sl, on="abbrev", how="left")

    # split shocks into skilled and unskilled subsets
    le0_skl = le0[le0["educ_id"] == "skl"].copy()
    le0_unskl = le0[le0["educ_id"] == "unskl"].copy()

    # build entrance flows for skilled group
    build_entrance_flows(
        skl_flows,
        le0_skl,
        state_educ,
        state_to_abbrev,
        abbrev_to_id,
        skill_col="skl",
        total_pop=TOTAL_POP,
        out_file="skilled_entrance3.csv",
    )

    # build entrance flows for unskilled group
    build_entrance_flows(
        unskl_flows,
        le0_unskl,
        state_educ,
        state_to_abbrev,
        abbrev_to_id,
        skill_col="unskl",
        total_pop=TOTAL_POP,
        out_file="unskilled_entrance.csv",
    )


if __name__ == "__main__":
    main()
