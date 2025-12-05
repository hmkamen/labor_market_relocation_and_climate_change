#!/usr/bin/env python

# this code transforms the migration flow dataframes into tables used in final version of paper
import os
import pandas as pd

# base directory for all input and output files
BASE_DIR = "/Users/hannahkamen/Downloads"

# total population factor used to turn normalized counts into head counts
TOTAL_POP = 14412444.2


def path_in_base(name):
    """
    Build full file path inside the base directory.
    """
    return os.path.join(BASE_DIR, name)


def load_location_lookup():
    """
    Read the flow map location lookup and keep only the columns needed
    for mapping numeric ids to state names.
    """
    sl = pd.read_csv(path_in_base("flowmap_location_lookup.csv"))
    sl = sl[["id", "name"]].copy()
    return sl


def build_flow_table(flow_filename, sl, total_pop, top_n_dest=10):
    """
    Construct a migration table for a given flow file.

    Steps:
    1. Read origin destination counts and rescale to actual head counts.
    2. Attach state names to origin and destination ids using the lookup table.
    3. Drop within state moves.
    4. Identify the top destination states by total inflows.
    5. For each of those destination states, keep the origin with the largest flow.
    6. Format counts with comma separators and return a compact table ready for LaTeX.
    """
    # read flow data
    flows = pd.read_csv(path_in_base(flow_filename))

    # rescale counts from shares to head counts
    flows["count"] = flows["count"] * total_pop

    # merge in origin state names
    flows = flows.merge(sl, left_on="origin", right_on="id", how="left")
    flows = flows.rename(columns={"name": "Origin"})
    flows = flows.drop(columns=["id"])

    # merge in destination state names
    flows = flows.merge(sl, left_on="dest", right_on="id", how="left")
    flows = flows.rename(columns={"name": "Destination"})
    flows = flows.drop(columns=["id"])

    # drop within state moves so only cross state flows remain
    flows = flows[flows["Origin"] != flows["Destination"]].copy()

    # rename count column for clarity
    flows = flows.rename(columns={"count": "Number of Migrants"})

    # compute total inflow by destination state
    dest_totals = (
        flows.groupby("Destination", as_index=False)["Number of Migrants"]
        .sum()
        .sort_values("Number of Migrants", ascending=False)
    )

    # keep only top destination states by total inflows
    top_dest = dest_totals.head(top_n_dest)["Destination"]
    flows_top = flows[flows["Destination"].isin(top_dest)].copy()

    # within the top destination states, keep the origin with the largest flow
    idx_max = flows_top.groupby("Destination")["Number of Migrants"].idxmax()
    table = flows_top.loc[idx_max, ["Origin", "Destination", "Number of Migrants"]].copy()

    # format counts as integers with thousands separators
    table["Number of Migrants"] = (
        table["Number of Migrants"]
        .round()
        .astype(int)
        .map("{:,}".format)
    )

    # sort by destination name for a stable and readable table
    table = table.sort_values("Destination").reset_index(drop=True)

    return table


def main():
    """
    Build unskilled and skilled migration tables and print LaTeX versions.
    """
    # read state id to name lookup
    sl = load_location_lookup()

    # unskilled migration table
    unskilled_table = build_flow_table(
        flow_filename="unskilled_entrance3.csv",
        sl=sl,
        total_pop=TOTAL_POP,
        top_n_dest=10,
    )
    print("Unskilled migration table")
    print(unskilled_table.to_latex(index=False, column_format="lll"))

    # skilled migration table
    skilled_table = build_flow_table(
        flow_filename="skilled_entrance3.csv",
        sl=sl,
        total_pop=TOTAL_POP,
        top_n_dest=10,
    )
    # optionally sort skilled table by number of migrants in ascending order
    skilled_table_sorted = skilled_table.sort_values(
        "Number of Migrants", ascending=True
    ).reset_index(drop=True)

    print("\nSkilled migration table")
    print(skilled_table_sorted.to_latex(index=False, column_format="lll"))


if __name__ == "__main__":
    main()
