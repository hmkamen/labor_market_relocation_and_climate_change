#This code stacks first stage and second stage logit regression outputs across age groups. It:

#Reads separate second stage Stata files for each age group, tags them with an age label, and combines them into one DataFrame, then writes to Excel.

#Reads separate first stage Excel files for each age group, tags them with the same age labels, and combines them into one DataFrame, then writes to excel
#result: two age annotated panels of regression outputs that are easier to inspect and plot.

#!/usr/bin/env python
# coding: utf_8

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/hannahkamen/Documents/population-migration2"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TEMP_DIR = os.path.join(RESULTS_DIR, "temp")
OUT_DIR = "/Users/hannahkamen/Downloads"


def build_second_stage_panel():
    """
    Read second stage regression output by age group and stack into a single DataFrame.
    """

    # age group indices used in file names
    age_indices = np.arange(1, 5, 1)

    # age labels attached to each file
    age_labels = ["21-25", "26-30", "31-35", "36-40"]

    frames = []

    for idx, label in zip(age_indices, age_labels):
        file_path = os.path.join(TEMP_DIR, f"2nd_stage_avg_age{idx}.dta")
        second_stage = pd.read_stata(file_path)

        # tag regression output with age label
        second_stage["age"] = label

        # drop unused string column if present
        if "string" in second_stage.columns:
            second_stage = second_stage.drop(columns=["string"])

        frames.append(second_stage)

    if frames:
        master = pd.concat(frames, ignore_index=True)
    else:
        master = pd.DataFrame()

    return master


def build_first_stage_panel():
    """
    Read first stage regression output by age group and stack into a single DataFrame.
    """

    age_indices = np.arange(1, 5, 1)
    age_labels = ["21-25", "26-30", "31-35", "36-40"]

    frames = []

    for idx, label in zip(age_indices, age_labels):
        file_path = os.path.join(RESULTS_DIR, f"1st_stage_28_age{idx}.xlsx")
        first_stage = pd.read_excel(file_path)

        # tag regression output with age label
        first_stage["age"] = label

        frames.append(first_stage)

    if frames:
        master = pd.concat(frames, ignore_index=True)
    else:
        master = pd.DataFrame()

    return master


def main():
    """
    Build combined first stage and second stage panels and export to Excel.
    """

    # build second stage panel and export
    second_stage_panel = build_second_stage_panel()
    out_second = os.path.join(OUT_DIR, "second_stage_28_1519.xlsx")
    second_stage_panel.to_excel(out_second, index=False)

    # build first stage panel and export
    first_stage_panel = build_first_stage_panel()
    out_first = os.path.join(OUT_DIR, "first_stage_28_1519.xlsx")
    first_stage_panel.to_excel(out_first, index=False)


if __name__ == "__main__":
    main()
