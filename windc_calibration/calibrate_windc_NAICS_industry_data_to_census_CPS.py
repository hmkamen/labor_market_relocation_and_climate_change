#!/usr/bin/env python
# coding: utf_8

#This code takes CPS/ACS microdata and WINDC industry data, maps NAICS industry codes to model sectors, classifies workers by education, age, and #household income, and aggregates wages to build state-level education and age shares. It then constructs census-region by household and sector #wage breakouts, aligns those with GAMS labor endowment and demand tables using deflators, and produces skill-share tables for consumers and #producers for use in the WINDC–GAMS model.

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

GAMS_PYTHON_PATH = "/Library/Frameworks/GAMS.framework/Resources/apifiles/Python/gams"
BASE_DIR = "/Users/hannahkamen/Downloads"

# -------------------------------------------------------------------
# helper functions
# -------------------------------------------------------------------

def load_core_data():
    """
    Load WINDC model industries, CPS/ACS microdata, industry lookups, and state lookups.
    """
    model = pd.read_csv(os.path.join(BASE_DIR, "windc_ind.csv"))

    cps = pd.read_stata(
        os.path.join(
            BASE_DIR,
            "population-migration-master/estimation/1_main_specification/acs5yr0610/dta/acs5yr_0610.dta",
        )
    )

    lookup = pd.read_excel(os.path.join(BASE_DIR, "windc_cps_industry_lookup.xlsx"))
    lookup_final = pd.read_excel(os.path.join(BASE_DIR, "dropped_merge.xlsx"))
    state_lookup = pd.read_excel(os.path.join(BASE_DIR, "state_lookup.xlsx"))

    lookup["NAICS"] = lookup["NAICS"].astype(str).str.strip()
    lookup_final["NAICS"] = lookup_final["NAICS"].astype(str).str.strip()
    lookup_final["cps_code"] = lookup_final["cps_code"].astype(str).str.strip()

    state_lookup["state"] = state_lookup["state"].str.strip()
    state_lookup["abbrev"] = state_lookup["abbrev"].str.strip()

    return model, cps, lookup, lookup_final, state_lookup


def build_naics_cps_mapping(cps, lookup, lookup_final):
    """
    Build a mapping from CPS NAICS strings to lookup NAICS codes
    using three digit prefixes and a manual supplement table.
    """
    cps_codes = pd.DataFrame({"cps_code": cps["indnaics"].str.strip().unique()})
    cps_codes["cps_code3"] = cps_codes["cps_code"].str[0:3]

    lookup["NAICS3"] = lookup["NAICS"].str[0:3]

    merge3 = lookup.merge(
        cps_codes,
        left_on="NAICS3",
        right_on="cps_code3",
        how="inner",
        indicator=True,
    )

    auto_map = merge3[["NAICS", "cps_code"]]
    manual_map = lookup_final[["NAICS", "cps_code"]]

    merge_f = pd.concat([auto_map, manual_map], ignore_index=True).drop_duplicates()

    return merge_f


def classify_workers(cps, merge_f, state_lookup):
    """
    Merge CPS with NAICS mapping and state abbreviations, then create
    education, household income, and age group classifications.
    """
    cps["statefip"] = cps["statefip"].str.lower().str.strip()
    cps["pwstate2"] = cps["pwstate2"].str.lower().str.strip()

    cps_m = (
        cps.merge(merge_f, left_on="indnaics", right_on="cps_code", how="left")
        .merge(state_lookup, left_on="statefip", right_on="state", how="left")
    )
    cps_m = cps_m.rename(columns={"abbrev": "state_residence"})

    cps_m = cps_m.merge(
        state_lookup,
        left_on="pwstate2",
        right_on="state",
        how="left",
        suffixes=("", "_work"),
    )
    cps_m = cps_m.rename(columns={"abbrev_work": "state_work"})

    cps_m["educ_new"] = np.where(
        cps_m["educ"].isin(
            ["2 years of college", "4 years of college", "5+ years of college"]
        ),
        "skl",
        "unskl",
    )

    cps_m["hh"] = ""
    cps_m["hh"] = np.where(cps_m["inctot"] <= 25000, "hh1", cps_m["hh"])
    cps_m["hh"] = np.where(
        (cps_m["inctot"] > 25000) & (cps_m["inctot"] < 50000),
        "hh2",
        cps_m["hh"],
    )
    cps_m["hh"] = np.where(
        (cps_m["inctot"] >= 50000) & (cps_m["inctot"] < 75000),
        "hh3",
        cps_m["hh"],
    )
    cps_m["hh"] = np.where(
        (cps_m["inctot"] >= 75000) & (cps_m["inctot"] < 150000),
        "hh4",
        cps_m["hh"],
    )
    cps_m["hh"] = np.where(cps_m["inctot"] >= 150000, "hh5", cps_m["hh"])

    states_with_codes = cps_m["state_residence"].unique()
    cps_m1 = cps_m[
        (cps_m["state_work"].isin(states_with_codes))
        & (cps_m["state_residence"].isin(states_with_codes))
        & (cps_m["age"] != "90 (90+ in 1980 and 1990)")
    ].copy()

    cps_m1["age"] = cps_m1["age"].astype(int)

    cps_m1["age_id"] = "0"
    cps_m1.loc[(cps_m1["age"] >= 25) & (cps_m1["age"] < 30), "age_id"] = "2"
    cps_m1.loc[(cps_m1["age"] >= 30) & (cps_m1["age"] < 35), "age_id"] = "3"
    cps_m1.loc[(cps_m1["age"] >= 35) & (cps_m1["age"] < 40), "age_id"] = "4"
    cps_m1.loc[(cps_m1["age"] >= 40) & (cps_m1["age"] < 45), "age_id"] = "5"
    cps_m1.loc[(cps_m1["age"] >= 45) & (cps_m1["age"] < 50), "age_id"] = "6"
    cps_m1.loc[(cps_m1["age"] >= 50) & (cps_m1["age"] < 55), "age_id"] = "7"

    return cps_m1


def export_state_shares(cps_m1):
    """
    Build and export state level education by age shares, age shares, and
    education shares using wage counts as weights.
    """
    state_pop = pd.read_excel(os.path.join(BASE_DIR, "state_pop.xlsx"))
    state_pop["state"] = state_pop["state"].str.strip()

    cps_state_split = cps_m1.groupby(
        ["educ_new", "age_id", "statefip", "state_residence"],
        as_index=False,
    ).agg({"incwage": "count"})

    cps_state_split_tot = cps_m1.groupby(
        ["statefip"], as_index=False
    ).agg({"incwage": "count"})
    cps_state_split = cps_state_split.merge(
        cps_state_split_tot, on="statefip", suffixes=("_x", "_y")
    )
    cps_state_split["state_prop"] = (
        cps_state_split["incwage_x"] / cps_state_split["incwage_y"]
    )

    state_split = (
        cps_state_split.pivot(
            index="statefip",
            columns=["educ_new", "age_id"],
            values="state_prop",
        )
        .reset_index()
    )
    state_split.columns = ["_".join(col).strip("_") for col in state_split.columns]

    state_split0 = state_split.merge(
        state_pop, left_on="statefip_", right_on="state", how="left"
    )
    state_split0.to_excel(
        os.path.join(BASE_DIR, "state_pop_educ_shares.xlsx"),
        index=False,
    )

    cps_state_split_age = cps_m1.groupby(
        ["age_id", "statefip", "state_residence"],
        as_index=False,
    ).agg({"incwage": "count"})

    cps_state_split_age_tot = cps_m1.groupby(
        ["statefip"], as_index=False
    ).agg({"incwage": "count"})
    cps_state_split_age = cps_state_split_age.merge(
        cps_state_split_age_tot, on="statefip", suffixes=("_x", "_y")
    )
    cps_state_split_age["state_prop"] = (
        cps_state_split_age["incwage_x"] / cps_state_split_age["incwage_y"]
    )

    state_split_age = (
        cps_state_split_age.pivot(
            index="statefip",
            columns=["age_id"],
            values="state_prop",
        )
        .reset_index()
    )

    state_split_age0 = state_split_age.merge(
        state_pop, left_on="statefip", right_on="state", how="left"
    )
    state_split_age0.to_excel(
        os.path.join(BASE_DIR, "state_age_shares.xlsx"),
        index=False,
    )

    cps_state_split_educ = cps_m1.groupby(
        ["educ_new", "statefip", "state_residence"],
        as_index=False,
    ).agg({"incwage": "count"})

    cps_state_split_educ_tot = cps_m1.groupby(
        ["statefip"], as_index=False
    ).agg({"incwage": "count"})
    cps_state_split_educ = cps_state_split_educ.merge(
        cps_state_split_educ_tot, on="statefip", suffixes=("_x", "_y")
    )
    cps_state_split_educ["state_prop"] = (
        cps_state_split_educ["incwage_x"] / cps_state_split_educ["incwage_y"]
    )

    state_split_educ = (
        cps_state_split_educ.pivot(
            index="statefip",
            columns=["educ_new"],
            values="state_prop",
        )
        .reset_index()
    )

    state_split_educ0 = state_split_educ.merge(
        state_pop, left_on="statefip", right_on="state", how="left"
    )
    state_split_educ0.to_excel(
        os.path.join(BASE_DIR, "state_educ_shares.xlsx"),
        index=False,
    )


def assign_census_regions(df, state_col_prefix):
    """
    Assign census regions for a state column using state abbreviations.
    """
    midwest = ["IA", "OH", "WI", "NE", "IL", "MI", "SD", "ND", "MN", "MO", "IN", "KS"]
    south = [
        "FL",
        "MD",
        "TN",
        "WV",
        "OK",
        "KY",
        "NC",
        "VA",
        "DE",
        "GA",
        "MS",
        "TX",
        "AL",
        "LA",
        "AR",
        "SC",
        "DC",
    ]
    west = [
        "AK",
        "AZ",
        "NM",
        "HI",
        "CA",
        "WA",
        "NV",
        "OR",
        "ID",
        "UT",
        "MT",
        "WY",
        "CO",
    ]
    northeast = ["VT", "NH", "CT", "ME", "MA", "NY", "NJ", "PA", "RI"]

    col = f"census_region_{state_col_prefix}"

    df[col] = ""
    df[col] = np.where(df[state_col_prefix].isin(midwest), "midwest", df[col])
    df[col] = np.where(df[state_col_prefix].isin(south), "south", df[col])
    df[col] = np.where(df[state_col_prefix].isin(west), "west", df[col])
    df[col] = np.where(df[state_col_prefix].isin(northeast), "northeast", df[col])

    return df


def build_all_breakouts(cps_m1, model):
    """
    Build wage breakouts by residence state, work state, NAICS sector,
    household income group, and education status, then map NAICS sectors
    to WINDC model IO codes.
    """
    all_breakouts0 = (
        cps_m1[["state_residence", "state_work", "NAICS", "hh", "educ_new", "incwage"]]
        .groupby(
            ["state_residence", "state_work", "NAICS", "hh", "educ_new"],
            as_index=False,
        )
        .agg({"incwage": "sum"})
    )

    all_breakouts0 = all_breakouts0.rename(
        columns={
            "state_residence": "r",
            "state_work": "q",
            "NAICS": "s",
            "hh": "h",
            "educ_new": "sk",
        }
    )
    all_breakouts0 = all_breakouts0[["r", "q", "s", "h", "sk", "incwage"]]

    model_gr = (
        model.groupby(["IOCode", "gams.IOCode"], as_index=False)
        .sum()[["IOCode", "gams.IOCode"]]
        .drop_duplicates()
    )

    all_breakouts0 = all_breakouts0.merge(
        model_gr,
        left_on="s",
        right_on="IOCode",
        how="left",
    )

    all_breakouts0 = all_breakouts0[all_breakouts0["gams.IOCode"] != "use"].copy()

    all_breakouts0 = all_breakouts0.drop(columns=["s", "IOCode"])
    all_breakouts0 = all_breakouts0.rename(columns={"gams.IOCode": "s"})

    all_breakouts = all_breakouts0[["r", "q", "s", "h", "sk", "incwage"]]

    all_breakouts = assign_census_regions(all_breakouts, "r")
    all_breakouts = assign_census_regions(all_breakouts, "q")

    return all_breakouts


def load_gams_tables():
    """
    Load GAMS labor demand (ld0) and labor endowment (le0) tables.
    """
    gams_dta_ld0 = pd.read_csv(os.path.join(BASE_DIR, "windc_ld0_d2.csv"))
    gams_dta_le0 = pd.read_csv(os.path.join(BASE_DIR, "windc_le0_d.csv"))

    return gams_dta_ld0, gams_dta_le0


def prepare_le_ld_tables(gams_dta_ld0, gams_dta_le0):
    """
    Prepare ld0 and le0 tables with census regions for regions and sectors.
    """
    midwest = ["IA", "OH", "WI", "NE", "IL", "MI", "SD", "ND", "MN", "MO", "IN", "KS"]
    south = [
        "FL",
        "MD",
        "TN",
        "WV",
        "OK",
        "KY",
        "NC",
        "VA",
        "DE",
        "GA",
        "MS",
        "TX",
        "AL",
        "LA",
        "AR",
        "SC",
        "DC",
    ]
    west = [
        "AK",
        "AZ",
        "NM",
        "HI",
        "CA",
        "WA",
        "NV",
        "OR",
        "ID",
        "UT",
        "MT",
        "WY",
        "CO",
    ]
    northeast = ["VT", "NH", "CT", "ME", "MA", "NY", "NJ", "PA", "RI"]

    gams_dta_ld0 = gams_dta_ld0.rename(
        columns={" flx": "q", " int": "s", " scn": "sk", " esubw_oth": "pop"}
    )

    gams_dta_ld0["census_region_q"] = ""
    gams_dta_ld0["census_region_q"] = np.where(
        gams_dta_ld0["q"].isin(midwest), "midwest", gams_dta_ld0["census_region_q"]
    )
    gams_dta_ld0["census_region_q"] = np.where(
        gams_dta_ld0["q"].isin(south), "south", gams_dta_ld0["census_region_q"]
    )
    gams_dta_ld0["census_region_q"] = np.where(
        gams_dta_ld0["q"].isin(west), "west", gams_dta_ld0["census_region_q"]
    )
    gams_dta_ld0["census_region_q"] = np.where(
        gams_dta_ld0["q"].isin(northeast),
        "northeast",
        gams_dta_ld0["census_region_q"],
    )

    ld00 = gams_dta_ld0[["q", "s", "sk", "pop", "census_region_q"]]
    ld0 = (
        gams_dta_ld0[["census_region_q", "s", "pop"]]
        .groupby(["census_region_q", "s"], as_index=False)
        .sum()
    )

    gams_dta_le0 = gams_dta_le0.rename(
        columns={" flx": "r", " int": "q", " scn": "h", " esubw_oth": "sk", " sector": "pop"}
    )

    for col_prefix in ["r", "q"]:
        gams_dta_le0[f"census_region_{col_prefix}"] = ""
        gams_dta_le0[f"census_region_{col_prefix}"] = np.where(
            gams_dta_le0[col_prefix].isin(midwest),
            "midwest",
            gams_dta_le0[f"census_region_{col_prefix}"],
        )
        gams_dta_le0[f"census_region_{col_prefix}"] = np.where(
            gams_dta_le0[col_prefix].isin(south),
            "south",
            gams_dta_le0[f"census_region_{col_prefix}"],
        )
        gams_dta_le0[f"census_region_{col_prefix}"] = np.where(
            gams_dta_le0[col_prefix].isin(west),
            "west",
            gams_dta_le0[f"census_region_{col_prefix}"],
        )
        gams_dta_le0[f"census_region_{col_prefix}"] = np.where(
            gams_dta_le0[col_prefix].isin(northeast),
            "northeast",
            gams_dta_le0[f"census_region_{col_prefix}"],
        )

    le00 = gams_dta_le0[
        ["r", "q", "sk", "census_region_r", "h", "pop", "census_region_q"]
    ]

    return ld00, ld0, le00


def compute_deflators(all_breakouts_lm, ld00, le00):
    """
    Compute deflators to align ACS wage totals with GAMS totals by region,
    household and sector.
    """
    le00_rh = le00.groupby(
        ["census_region_q", "r", "q", "h"],
        as_index=False,
    ).sum()
    le00_rh = le00_rh.rename(columns={"pop": "pop_gams"})

    acs_cons = all_breakouts_lm.groupby(
        ["census_region_q", "r", "q", "h"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_cons = acs_cons.rename(columns={"incwage": "pop"})

    cons_merge = acs_cons.merge(
        le00_rh,
        on=["census_region_q", "r", "q", "h"],
        how="inner",
    )
    cons_merge["deflator"] = cons_merge["pop_gams"] / cons_merge["pop"]
    cons_df = cons_merge[["r", "q", "census_region_q", "h", "deflator"]]

    ld00_qs = ld00.groupby(
        ["census_region_q", "q", "s"],
        as_index=False,
    ).sum()
    ld00_qs = ld00_qs.rename(columns={"pop": "pop_gams"})

    acs_prod = all_breakouts_lm.groupby(
        ["census_region_q", "q", "s"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_prod = acs_prod.rename(columns={"incwage": "pop"})

    prod_merge = acs_prod.merge(
        ld00_qs,
        on=["census_region_q", "q", "s"],
        how="inner",
    )
    prod_merge["deflator"] = prod_merge["pop_gams"] / prod_merge["pop"]
    prod_df = prod_merge[["q", "census_region_q", "s", "deflator"]]

    return cons_df, prod_df


def compute_skill_shares(all_breakouts_lm, cons_df, prod_df, le00, ld00):
    """
    Compute deflated expenditure shares by skill for consumers and producers.
    """
    acs_cons_sk = all_breakouts_lm.groupby(
        ["r", "census_region_q", "q", "h", "sk"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_cons_sk = acs_cons_sk.merge(
        cons_df,
        on=["r", "census_region_q", "q", "h"],
        how="inner",
    )
    acs_cons_sk["pop_adjust"] = acs_cons_sk["incwage"] * acs_cons_sk["deflator"]
    acs_cons_sk = acs_cons_sk[
        ["r", "census_region_q", "q", "h", "sk", "pop_adjust"]
    ]

    acs_cons_tot = all_breakouts_lm.groupby(
        ["r", "census_region_q", "q", "h"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_cons_tot = acs_cons_tot.rename(columns={"incwage": "pop_total"})
    acs_cons_tot = acs_cons_tot.merge(
        cons_df,
        on=["r", "census_region_q", "q", "h"],
        how="inner",
    )
    acs_cons_tot["pop_total_adjust"] = (
        acs_cons_tot["pop_total"] * acs_cons_tot["deflator"]
    )
    acs_cons_tot = acs_cons_tot[
        ["r", "census_region_q", "q", "h", "pop_total_adjust"]
    ]

    acs_cons_adj = acs_cons_sk.merge(
        acs_cons_tot,
        on=["r", "census_region_q", "q", "h"],
        how="inner",
    )
    acs_cons_adj["expenditure_share"] = (
        acs_cons_adj["pop_adjust"] / acs_cons_adj["pop_total_adjust"]
    )

    acs_prod_sk = all_breakouts_lm.groupby(
        ["census_region_q", "q", "s", "sk"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_prod_sk = acs_prod_sk.merge(
        prod_df,
        on=["census_region_q", "q", "s"],
        how="inner",
    )
    acs_prod_sk["pop_adjust"] = acs_prod_sk["incwage"] * acs_prod_sk["deflator"]
    acs_prod_sk = acs_prod_sk[
        ["census_region_q", "q", "s", "sk", "pop_adjust"]
    ]

    acs_prod_tot = all_breakouts_lm.groupby(
        ["census_region_q", "q", "s"],
        as_index=False,
    ).agg({"incwage": "sum"})
    acs_prod_tot = acs_prod_tot.rename(columns={"incwage": "pop_total"})
    acs_prod_tot = acs_prod_tot.merge(
        prod_df,
        on=["census_region_q", "q", "s"],
        how="inner",
    )
    acs_prod_tot["pop_total_adjust"] = (
        acs_prod_tot["pop_total"] * acs_prod_tot["deflator"]
    )
    acs_prod_tot = acs_prod_tot[
        ["census_region_q", "q", "s", "pop_total_adjust"]
    ]

    acs_prod_adj = acs_prod_sk.merge(
        acs_prod_tot,
        on=["census_region_q", "q", "s"],
        how="inner",
    )
    acs_prod_adj["expenditure_share"] = (
        acs_prod_adj["pop_adjust"] / acs_prod_adj["pop_total_adjust"]
    )

    census_cons = acs_cons_adj.groupby(
        ["census_region_q", "h", "sk"],
        as_index=False,
    ).agg({"pop_adjust": "sum"})
    census_cons_tot = acs_cons_adj.groupby(
        ["census_region_q", "h"],
        as_index=False,
    ).agg({"pop_adjust": "sum"})
    census_cons_tot = census_cons_tot.rename(
        columns={"pop_adjust": "pop_adjust_total"}
    )
    census_cons = census_cons.merge(
        census_cons_tot, on=["census_region_q", "h"], how="inner"
    )
    census_cons["expenditure_share"] = (
        census_cons["pop_adjust"] / census_cons["pop_adjust_total"]
    )

    census_prod = acs_prod_adj.groupby(
        ["census_region_q", "s", "sk"],
        as_index=False,
    ).agg({"pop_adjust": "sum"})
    census_prod_tot = acs_prod_adj.groupby(
        ["census_region_q", "s"],
        as_index=False,
    ).agg({"pop_adjust": "sum"})
    census_prod_tot = census_prod_tot.rename(
        columns={"pop_adjust": "pop_adjust_total"}
    )
    census_prod = census_prod.merge(
        census_prod_tot, on=["census_region_q", "s"], how="inner"
    )
    census_prod["expenditure_share"] = (
        census_prod["pop_adjust"] / census_prod["pop_adjust_total"]
    )

    le00_rh = le00.groupby(
        ["census_region_q", "h", "q"],
        as_index=False,
    ).sum()
    le00_rh = le00_rh.rename(columns={"pop": "pop_gams"})

    cons_final = le00_rh.merge(
        census_cons,
        left_on=["census_region_q", "h"],
        right_on=["census_region_q", "h"],
        how="inner",
    )
    cons_final["pop_final"] = (
        cons_final["pop_gams"] * cons_final["expenditure_share"]
    )

    ld00_qs = ld00.groupby(
        ["census_region_q", "q", "s"],
        as_index=False,
    ).sum()
    ld00_qs = ld00_qs.rename(columns={"pop": "pop_gams"})

    prod_final = ld00_qs.merge(
        census_prod,
        on=["census_region_q", "s"],
        how="inner",
    )
    prod_final["pop_final"] = (
        prod_final["pop_gams"] * prod_final["expenditure_share"]
    )

    return cons_final, prod_final


def export_skill_shares(cons_final, prod_final):
    """
    Export final skill share tables for consumers and producers in WINDC format.
    """
    cons_final_out = cons_final.copy()
    cons_final_out["q_out"] = cons_final_out["q"]
    cons_final_out["skill_shr"] = cons_final_out["expenditure_share"]
    cons_final_out[["q_out", "q", "h", "sk", "skill_shr"]].to_csv(
        os.path.join(BASE_DIR, "le0_shr2.csv"),
        index=False,
    )

    prod_final_out = prod_final.copy()
    prod_final_out["q_out"] = prod_final_out["q"]
    prod_final_out["skill_shr"] = (
        prod_final_out["pop_final"] / prod_final_out["pop_gams"]
    )
    prod_final_out[["q_out", "s", "sk", "skill_shr"]].to_csv(
        os.path.join(BASE_DIR, "ld0_shr2.csv"),
        index=False,
    )


def main():
    model, cps, lookup, lookup_final, state_lookup = load_core_data()
    merge_f = build_naics_cps_mapping(cps, lookup, lookup_final)
    cps_m1 = classify_workers(cps, merge_f, state_lookup)

    export_state_shares(cps_m1)

    all_breakouts = build_all_breakouts(cps_m1, model)

    all_breakouts_lm = all_breakouts[
        all_breakouts["census_region_r"] == all_breakouts["census_region_q"]
    ].copy()

    gams_dta_ld0, gams_dta_le0 = load_gams_tables()
    ld00, ld0, le00 = prepare_le_ld_tables(gams_dta_ld0, gams_dta_le0)

    cons_df, prod_df = compute_deflators(all_breakouts_lm, ld00, le00)
    cons_final, prod_final = compute_skill_shares(
        all_breakouts_lm, cons_df, prod_df, le00, ld00
    )

    export_skill_shares(cons_final, prod_final)


if __name__ == "__main__":
    main()
