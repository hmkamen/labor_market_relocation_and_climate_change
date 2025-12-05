#loads labor share and shock data and windc simulation outputs, builds a measure of relative skilled vs unskilled labor shocks by state, classifies states into “skilled-labor-abundant” vs “unskilled-labor-abundant,” filters a set of counterfactual runs that vary the elasticity of substitution in consumption, and then plots how skilled and unskilled wages in each group respond to changes in that elasticity.

#!/usr/bin/env python
# coding: utf-8

"""
Analyze wage responses to consumption-substitution elasticities.

Steps:
1. Load labor shares and labor shock data; compute skilled–unskilled differences.
2. Load windc benchmark and counterfactual outputsfrom gams  (wages, prices, etc.).
3. Combine shocks and wages to construct a state-level measure of relative
   skilled vs unskilled labor shocks.
4. Use this to classify states into "skilled-labor-abundant" vs
   "unskilled-labor-abundant".
5. For a set of consumption-substitution experiments, compute wage changes
   relative to the lowest elasticity case and plot wage responses by state,
   skill type, and abundance group.
"""

import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats  # noqa: F401 (imported but not explicitly used)
import seaborn as sns

warnings.filterwarnings("ignore")

# ============================================================
# 1. Labor shares and shocks
# ============================================================

# Labor shares by region (q), household (h), and skill (sk)
shares = pd.read_csv("/Users/hannahkamen/Downloads/le0_shr2.csv")

# One row per (q, h), with columns 'skl' and 'unskl'
shares_u = (
    shares.drop_duplicates(subset=["q", "h", "sk"])
    .pivot(index=["q", "h"], columns="sk", values="skill_shr")
    .reset_index()
)
shares_u["diff"] = shares_u["skl"] - shares_u["unskl"]

# Labor shocks by region and skill
shocks = pd.read_csv("/Users/hannahkamen/Downloads/le0_shock0_v2_test2_adj.csv")
shocks = shocks.rename(columns={"skill_shr": "pct_shock"})

# Keep only “own-region” shocks (r == q)
shocks_lm = shocks[shocks["r"] == shocks["q"]]

# ============================================================
# 2. Import GAMS results (benchmark + full results)
# ============================================================

t = "_d2_v2"

# --- Benchmark characteristics ---

# Household transfers by (r, h, sk)
hhtrn0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/hhtrn0_d_rpt.csv"
)
hhtrn0_d_rpt = hhtrn0_d_rpt.drop(columns="file")
hhtrn0_d_rpt = (
    hhtrn0_d_rpt.groupby(["r", "h", "sk"], as_index=False).sum()
)

# Initial labor endowment
le0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/le0_d_rpt.csv"
)
le0_d_rpt = le0_d_rpt.drop(columns="file")

# New (post-shock) labor endowment
le0_d_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/le0_d_rpt0.csv"
)
le0_d_rpt0 = le0_d_rpt0.drop(columns="file")

# Baseline consumption: cons0_rpt(r,h,sk) = c0_h_d(r,h,sk)
cons0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/cons0_rpt.csv"
)
cons0_rpt = cons0_rpt.drop(columns="file")

# Baseline consumption demand by (region, good, skill, household)
cd0_h_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/cd0_h_d_rpt.csv"
)
cd0_h_d_rpt = cd0_h_d_rpt.drop(columns="file")

# Sectoral labor demand by skill
ld0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/ld0_d_rpt.csv"
)
# ld0_d_rpt may still contain 'file', but is commented out in original

# Intermediate goods demand
id0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/id0_rpt.csv"
)
id0_rpt = id0_rpt.drop(columns="file")

# --- Full result characteristics (counterfactuals) ---

# Wages (pl_rpt0), by region, skill, and experiment file
pl_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/pl_rpt0.csv"
)

# Consumer price index
pc_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/pc_rpt0.csv"
)

# Sectoral output changes
y_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/y_rpt0.csv"
)

# Baseline sectoral supply
ys0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/ys0_rpt.csv"
)

# Sectoral output price changes
py_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/exp/csv{t}/py_rpt0.csv"
)

# ============================================================
# 3. Labor shocks + wages: build relative shortage measure
# ============================================================

# Merge “own-region” shocks and wage changes
labor_wage = shocks_lm.drop_duplicates(subset=["r", "sk"]).merge(
    pl_rpt0, left_on=["r", "sk"], right_on=["region", "skill"], how="inner"
)

# Wage percent change relative to baseline
labor_wage["wage_diff"] = labor_wage["pl_shock0"] - 1

# Drop very small states/regions if desired
limit_states = ["HI", "WY", "VT", "AK", "TN", "DC", "NH", "WV"]
labor_wage = labor_wage[~labor_wage["region"].isin(limit_states)]

# Optional subsets (not used later but kept for reference)
labor_wage_skl = labor_wage[labor_wage["skill"] == "skl"]
labor_wage_unskl = labor_wage[
    (labor_wage["skill"] == "unskl")
    & (~labor_wage["pct_shock"].isin(limit_states))
]

# Pivot to get one row per region with skilled/unskilled shocks & wage diffs
labor_wage_pvt = labor_wage.pivot_table(
    index="r", columns="sk", values=["pct_shock", "wage_diff"]
)
labor_wage_pvt.columns = [
    "_".join((outer, inner)) for outer, inner in labor_wage_pvt.columns
]
labor_wage_pvt = labor_wage_pvt.reset_index()

# Difference in shocks: skilled shock minus unskilled shock
labor_wage_pvt["difference"] = (
    labor_wage_pvt["pct_shock_skl"] - labor_wage_pvt["pct_shock_unskl"]
)

# ============================================================
# 4. Select consumption-substitution experiments & compute wage changes
# ============================================================

# All experiment filenames with varying consumption-substitution parameters
cons_exp = [
    "staticmodel_d2_v2_it0_1.6_0.5_2",
    "staticmodel_d2_v2_it0_1.6_0.7_2",
    "staticmodel_d2_v2_it0_1.6_0.9_2",
    "staticmodel_d2_v2_it0_1.6_1.1_2",
    "staticmodel_d2_v2_it0_1.6_1.3_2",
    "staticmodel_d2_v2_it0_1.6_1_2",
]

# Keep only those experiment runs
pl_rpt0 = pl_rpt0[pl_rpt0["file"].isin(cons_exp)]

# Extract the *consumption* elasticity from the file name (6th token)
# e.g. 'staticmodel_d2_v2_it0_1.6_0.5_2' -> esubl = 0.5
pl_rpt0["esubl"] = (
    pl_rpt0["file"].apply(lambda x: x.split("_")[5]).astype(float).round(1)
)

# Drop small states again
pl_rpt0 = pl_rpt0[
    ~pl_rpt0["region"].isin(["AK", "DC", "HI", "NH", "VT", "WY", "WV"])
]

# Wage percent change in each experiment relative to base
pl_rpt0["pl_diff"] = pl_rpt0["pl_shock0"] - 1

# ============================================================
# 5. Classify states by relative skilled/unskilled shock
#    and plot wages vs consumption elasticity
# ============================================================

# Skilled-labor-abundant regions: skilled shock > unskilled shock
skill_abundance = labor_wage_pvt[labor_wage_pvt["difference"] > 0]["r"].unique()
not_skill_abundance = labor_wage_pvt[
    labor_wage_pvt["difference"] < 0
]["r"].unique()

for sk, slab in zip(["skl", "unskl"], ["Skilled", "Unskilled"]):
    for region_list, lab in zip(
        [skill_abundance, not_skill_abundance],
        ["Skilled Labor Abundance", "Unskilled Labor Abundance"],
    ):
        pl_rpt0_sk = pl_rpt0[pl_rpt0["skill"] == sk].copy()

        # Sort by region so groupby().first() is stable
        pl_rpt0_sk = pl_rpt0_sk.sort_values(by=["region", "esubl"])

        # Use the first esubl for each region as the "base" wage diff
        base_diff = pl_rpt0_sk.groupby("region")["pl_diff"].first()

        # Align and compute difference from base within region
        pl_rpt0_sk = pl_rpt0_sk.sort_values(by="region")
        pl_rpt0_sk["Difference in Price Change"] = (
            pl_rpt0_sk.set_index("region")["pl_diff"] - base_diff
        ).values

        # Compute "first difference" at esubl = 0.7 to sort regions by response
        first_diff = []
        for r_name in pl_rpt0_sk["region"].unique():
            tmp = pl_rpt0_sk[
                (pl_rpt0_sk["region"] == r_name)
                & (pl_rpt0_sk["esubl"] == 0.7)
            ].copy()
            if tmp.empty:
                continue
            tmp["first_diff"] = tmp["Difference in Price Change"]
            first_diff.append(tmp[["region", "first_diff"]])

        if not first_diff:
            # No esubl == 0.7 found; skip plotting for this combination
            continue

        first_diff = pd.concat(first_diff, ignore_index=True)

        # Merge back and restrict to regions in the chosen list
        pl_rpt0_sk = pl_rpt0_sk.merge(first_diff, on="region", how="left")
        pl_rpt0_lm = pl_rpt0_sk[
            pl_rpt0_sk["region"].isin(region_list)
        ].sort_values(by="first_diff", ascending=False)

        # Plot: wage difference from base vs consumption elasticity
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(1, 1, figsize=(15, 6))

        sns.set_palette("PuBuGn_d")
        sns.lineplot(
            data=pl_rpt0_lm,
            x="esubl",
            y="Difference in Price Change",
            hue="region",
            palette="Blues",
            ax=ax,
        )

        plt.legend(ncol=8)
        plt.xlabel("Elasticity of Substitution Between Goods in Consumption")
        plt.title(f"{slab} Labor Wages in Relative {lab}")
        plt.tight_layout()
        plt.show()
