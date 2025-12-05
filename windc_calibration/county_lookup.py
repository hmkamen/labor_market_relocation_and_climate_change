#!/usr/bin/env python
# coding: utf_8

#This code builds a crosswalk between 2019 metropolitan area names and the 2013 CBSA county delineation file. Steps outlined below

#Reads the MSA 2019 lookup file and the 2013 CBSA county file.

#Defines virtual metropolitan areas for Wyoming, South Dakota, and Montana, both in the county file and in the lookup table.

#Normalizes metropolitan names to lowercase.

#Aggregates the CBSA file by metropolitan area and county.

#Merges the lookup table with the aggregated CBSA data.

#Writes the resulting MSA county mapping to an Excel file.

#!/usr/bin/env python
# coding: utf_8

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/hannahkamen/Downloads"


def main():
    """
    Build a crosswalk between 2019 metropolitan areas and 2013 CBSA county delineations.
    """

    # step 1 read lookup files and CBSA county delineation file
    lookup_path_2019 = os.path.join(BASE_DIR, "msa_2019_lookup.xlsx")
    msa_2007_path = os.path.join(BASE_DIR, "msa_2007.xlsx")  # kept for reference if needed
    cbsa_path = os.path.join(BASE_DIR, "msa_county_2013.xlsx")

    lookup = pd.read_excel(lookup_path_2019)

    # read CBSA with FIPS codes as strings
    cbsa = pd.read_excel(
        cbsa_path,
        converters={
            "FIPS State Code": str,
            "FIPS County Code": str,
            "CSA Code": str,
        },
    )

    # step 2 construct lowercase metropolitan names in CBSA file
    cbsa["msa_name"] = cbsa["CBSA Title"].str.lower()

    # step 3 define virtual metropolitan areas in CBSA file for selected states
    cbsa["msa_name"] = np.where(
        cbsa["FIPS State Code"] == "56",
        "wy virtual msa, wy",
        cbsa["msa_name"],
    )
    cbsa["msa_name"] = np.where(
        cbsa["FIPS State Code"] == "46",
        "sd virtual msa, sd",
        cbsa["msa_name"],
    )
    cbsa["msa_name"] = np.where(
        cbsa["FIPS State Code"] == "30",
        "mt virtual msa, mt",
        cbsa["msa_name"],
    )

    # step 4 add matching virtual metropolitan area rows to 2019 lookup
    # assumes lookup has a column named metarea_19
    new_rows = pd.DataFrame(
        {
            "metarea_19": [
                "WY Virtual MSA, WY",
                "SD Virtual MSA, SD",
                "MT Virtual MSA, MT",
            ],
            # second column is left empty as in the original script
            lookup.columns[1]: ["", "", ""],
        }
    )

    lookup = pd.concat([lookup, new_rows], ignore_index=True)

    # convert metropolitan names in lookup to lowercase to align with CBSA
    lookup["metarea_19"] = lookup["metarea_19"].str.lower()

    # step 5 aggregate CBSA file by metropolitan area and county
    group_cols = [
        "msa_name",
        "Central/Outlying County",
        "FIPS County Code",
        "FIPS State Code",
        "County/County Equivalent",
    ]

    cbsa_grouped = (
        cbsa.groupby(group_cols, as_index=False)
        .sum()
        .sort_values(by="msa_name")
        .reset_index(drop=True)
    )

    # step 6 merge 2019 lookup with grouped CBSA file
    merged = lookup.merge(
        cbsa_grouped,
        left_on="metarea_19",
        right_on="msa_name",
        how="inner",
    )

    # step 7 write result to Excel
    out_path = os.path.join(BASE_DIR, "msa_county_2019.xlsx")
    merged.to_excel(out_path, index=False)


if __name__ == "__main__":
    main()
