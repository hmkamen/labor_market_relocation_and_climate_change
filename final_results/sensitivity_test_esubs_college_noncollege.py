#!/usr/bin/env python
# coding: utf-

#This cdoe classifies regions as relatively skilled or unskilled labor abundant based on initial labor shares, reads GAMS wage results for a range of elasticities of substitution between skilled and unskilled labor, and produces line plots of the change in wages relative to a base case for each skill group and region group.

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# ======================================================================
# Labor share data and region classification
# ======================================================================

# Labor shares by origin region r, destination region q, household h, and skill sk
shares = pd.read_csv("/Users/hannahkamen/Downloads/le0_shr2.csv")

# Collapse to unique destination region q and household h, then pivot to skilled and unskilled shares
shares_u = (
    shares.drop_duplicates(subset=["q", "h", "sk"])
    .pivot(index=["q", "h"], columns="sk", values="skill_shr")
    .reset_index()
)

# Skilled minus unskilled share at the q–h level
shares_u["diff"] = shares_u["skl"] - shares_u["unskl"]

# Region level measure of skill abundance based on the average difference in shares
labor_wage_pvt = (
    shares_u.groupby("q", as_index=False)["diff"]
    .mean()
    .rename(columns={"q": "r", "diff": "difference"})
)

# Regions with relatively abundant skilled labor (difference > 0)
skill_abundance = labor_wage_pvt[labor_wage_pvt["difference"] > 0]["r"].unique()

# Regions with relatively abundant unskilled labor (difference < 0)
not_skill_abundance = labor_wage_pvt[labor_wage_pvt["difference"] < 0]["r"].unique()

# ======================================================================
# GAMS output: wages under different elasticities of substitution
# ======================================================================

# Suffix used for the experiment batch
t = "_d2_v2"

# Wage results for a range of elasticities of substitution between skilled and unskilled labor
pl_rpt0 = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/pl_rpt0.csv")

# List of runs corresponding to different values of the elasticity parameter esubl
esubl_list = [
    "staticmodel_d2_v2_it0_1.7_1_2",
    "staticmodel_d2_v2_it0_1.8_1_2",
    "staticmodel_d2_v2_it0_1.9_1_2",
    "staticmodel_d2_v2_it0_2.0_1_2",
    "staticmodel_d2_v2_it0_2.1_1_2",
    "staticmodel_d2_v2_it0_2.2_1_2",
    "staticmodel_d2_v2_it0_2.3_1_2",
    "staticmodel_d2_v2_it0_2.4_1_2",
    "staticmodel_d2_v2_it0_2.5_1_2",
    "staticmodel_d2_v2_it0_0.6_1_2",
    "staticmodel_d2_v2_it0_0.7_1_2",
    "staticmodel_d2_v2_it0_0.8_1_2",
    "staticmodel_d2_v2_it0_0.9_1_2",
    "staticmodel_d2_v2_it0_1.0_1_2",
    "staticmodel_d2_v2_it0_1.1_1_2",
    "staticmodel_d2_v2_it0_1.2_1_2",
    "staticmodel_d2_v2_it0_1.3_1_2",
    "staticmodel_d2_v2_it0_1.4_1_2",
    "staticmodel_d2_v2_it0_1.5_1_2",
    "staticmodel_d2_v2_it0_1.6_1_2",
]

# Keep only the selected runs
pl_rpt0 = pl_rpt0[pl_rpt0["file"].isin(esubl_list)].copy()

# Parse the elasticity parameter from the file name
pl_rpt0["esubl"] = pl_rpt0["file"].apply(lambda x: float(x.split("_")[4])).round(1)

# Mark the run with esubl equal to 1.6 as the base case by relabeling it to 0.5
pl_rpt0["esubl"] = np.where(pl_rpt0["esubl"] == 1.6, 0.5, pl_rpt0["esubl"])

# Drop regions not used in the analysis
drop_regions = ["AK", "DC", "HI", "NH", "VT", "WY", "WV"]
pl_rpt0 = pl_rpt0[~pl_rpt0["region"].isin(drop_regions)]

# Wage change relative to the no shock benchmark
pl_rpt0["pl_diff"] = pl_rpt0["pl_shock0"] - 1.0

# ======================================================================
# Plot wage responses by skill group and region group
# ======================================================================

# Skilled and unskilled labels and plotting settings
skill_codes = ["skl", "unskl"]
skill_labels = ["Skilled", "Unskilled"]
palettes = ["Blues", "Oranges"]
sort_orders = [False, True]  # Sort regions by initial response ascending or descending

sns.set_theme(style="whitegrid")

for sk, slab, pal_name, sort_ascending in zip(
    skill_codes, skill_labels, palettes, sort_orders
):
    for region_list, abundance_label in zip(
        [skill_abundance, not_skill_abundance],
        ["Skilled Labor Abundance", "Unskilled Labor Abundance"],
    ):
        # Filter to the current skill group
        pl_rpt0_sk = pl_rpt0[pl_rpt0["skill"] == sk].copy()

        # Sort by region and elasticity, and compute wage difference relative to the base case
        pl_rpt0_sk = pl_rpt0_sk.sort_values(["region", "esubl"])
        base_diff = pl_rpt0_sk.groupby("region")["pl_diff"].first()
        pl_rpt0_sk = pl_rpt0_sk.sort_values("region")
        pl_rpt0_sk["diff_from_base"] = (
            pl_rpt0_sk.set_index("region")["pl_diff"] - base_diff
        ).values

        # Extract the first difference at esubl equal to 0.7 for each region
        first_diff_rows = []
        for r in pl_rpt0_sk["region"].unique():
            tmp_region = pl_rpt0_sk[
                (pl_rpt0_sk["region"] == r) & (pl_rpt0_sk["esubl"] == 0.7)
            ].copy()
            if tmp_region.empty:
                continue
            tmp_region["first_diff"] = tmp_region["diff_from_base"]
            first_diff_rows.append(tmp_region[["region", "first_diff"]])

        if not first_diff_rows:
            continue

        first_diff = pd.concat(first_diff_rows, ignore_index=True)

        # Merge first difference back on region
        pl_rpt0_sk = pl_rpt0_sk.merge(first_diff, on="region", how="left")

        # Limit to the selected group of regions and order them by initial response
        pl_rpt0_lm = pl_rpt0_sk[pl_rpt0_sk["region"].isin(region_list)].copy()
        pl_rpt0_lm = pl_rpt0_lm.sort_values("first_diff", ascending=sort_ascending)

        # Drop the base case elasticity from the plot (esubl equal to 0.5)
        pl_rpt0_lm = pl_rpt0_lm[pl_rpt0_lm["esubl"] != 0.5]

        if pl_rpt0_lm.empty:
            continue

        fig, ax = plt.subplots(1, 1, figsize=(14, 6))

        sns.lineplot(
            data=pl_rpt0_lm,
            x="esubl",
            y="diff_from_base",
            hue="region",
            palette=pal_name,
            ax=ax,
        )

        ax.set_xlabel(
            "Elasticity of Substitution Between Skilled and Unskilled Labor", fontsize=12
        )
        ax.set_ylabel("Difference in Wage Relative to Base Case", fontsize=12)
        ax.set_title(
            f"Difference in {slab} Wages Relative to Base Case\n"
            f"{abundance_label} Regions",
            fontsize=14,
        )

        ax.legend(ncol=8, fontsize=8)
        plt.tight_layout()
        plt.show()
