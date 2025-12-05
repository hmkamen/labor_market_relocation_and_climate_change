#!/usr/bin/env python
# coding: utf_8

#This script takes WinDC GAMS output for housing price shocks and wage shocks by state from the first equilibrium model iteration, merges them with a state abbreviation lookup, and writes a stata file (gams_dta1_v2_d2.dta) that contains housing price changes and skilled/unskilled wage changes keyed by state abbreviation for use in the logit stage.

    
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


def csv_path(name):
    """
    Build full path to a CSV file in the base directory.
    """
    return os.path.join(BASE_DIR, name)


def main():
    """
    Read GAMS outputs for housing and wage shocks, attach state abbreviations, and
    write a compact Stata file for the logit stage.
    """

    # read state lookup with abbreviations
    sl = pd.read_excel(os.path.join(BASE_DIR, "statelookup2.xlsx"))
    sl = sl.rename(columns={"abbrev": "q"})

    # read GAMS housing price shocks by region
    # expected columns include region and ph_shock0
    phou_rpt = pd.read_csv(csv_path("phou_rpt.csv"))

    # read GAMS wage shocks by region
    # expected columns include region, skl, and unskl
    pl_rpt = pd.read_csv(csv_path("pl_rpt.csv"))

    # merge housing and wage shocks on region
    r_df = phou_rpt.merge(pl_rpt, on="region")

    # rename columns to a consistent set used in later scripts
    r_df = r_df.rename(
        columns={
            "region": "q",
            "ph_shock0": "ph",
            "skl": "pl_skl",
            "unskl": "pl_unskl",
        }
    )

    # attach state abbreviations
    r_df = r_df.merge(sl, on="q")
    r_df = r_df.rename(columns={"q": "abbrev"})

    # write Stata dataset used as input to the logit routine
    out_path = dta_path("gams_dta1_v2_d2.dta")
    r_df.to_stata(out_path, write_index=False)


if __name__ == "__main__":
    main()
