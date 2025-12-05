#This code loads windc GAMS outputs, computes consumption budget shares and factor input intensities (skilled labor, unskilled labor, capital, and intermediates) by region and sector, and produces diagnostic plots showing how expenditure and input use vary across regions and goods.

#!/usr/bin/env python
# coding: utf-8

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# ============================================================
# Configuration
# ============================================================

t = "_d2_v2"  # suffix used in GAMS export file names

# ============================================================
# Import GAMS results and related data
# ============================================================

# Household transfers by region, household, and skill
hhtrn0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/hhtrn0_d_rpt.csv")
hhtrn0_d_rpt = (
    hhtrn0_d_rpt.drop(columns=["file"])
    .groupby(["r", "h", "sk"], as_index=False)
    .sum()
)

# Savings by region, household, and skill
sav0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/sav0_d_rpt.csv")
sav0_d_rpt = sav0_d_rpt.drop(columns=["file"])

# Labor tax rate by region, household, and skill
tl0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/tl0_d_rpt.csv")
tl0_d_rpt = tl0_d_rpt.drop(columns=["file"])

# Capital endowment by region and household
ke0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ke0_d_rpt.csv")
ke0_d_rpt = ke0_d_rpt.drop(columns=["file"])

# Initial labor endowment by region, household, and skill
le0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt.csv")
le0_d_rpt = le0_d_rpt.drop(columns=["file"])

# New labor endowment after shock
le0_d_rpt0 = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt0.csv")
le0_d_rpt0 = le0_d_rpt0.drop(columns=["file"])

# Baseline consumption levels by region, household, and skill
cons0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/cons0_rpt.csv")
cons0_rpt = cons0_rpt.drop(columns=["file"])

# Disaggregated consumption demand by region, good, household, and skill
cd0_h_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/cd0_h_d_rpt.csv")
cd0_h_d_rpt = cd0_h_d_rpt.drop(columns=["file"])

# Sector labor demand by skill and region
ld0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ld0_d_rpt.csv")

# Sectoral output by region and good
ys0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ys0_rpt.csv")
ys0_rpt = ys0_rpt.drop(columns=["file"])

# Capital demand by sector and region
kd0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/kd0_rpt.csv")
kd0_rpt = kd0_rpt.drop(columns=["file"])

# Intermediate goods demand by good and sector in each region
id0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/id0_rpt.csv")
id0_rpt = id0_rpt.drop(columns=["file"])

# Initial benchmark labor supply by region, household, and skill
labor_b = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt00.csv")
labor_b = (
    labor_b[["file", "region", "household", "benchmark_le0", "skill"]]
    .reset_index(drop=True)
    .rename(
        columns={
            "file": "r",
            "region": "q",
            "skill": "sk",
            "household": "h",
        }
    )
)

# Skill share of labor endowment by origin region and household
shares = pd.read_csv("/Users/hannahkamen/Downloads/le0_shr2.csv")
shares_u = (
    shares.drop_duplicates(subset=["q", "h", "sk"])
    .pivot(index=["q", "h"], columns="sk", values="skill_shr")
    .reset_index()
)
shares_u["diff"] = shares_u["skl"] - shares_u["unskl"]

# Labor supply shocks by region and skill
shocks = pd.read_csv("/Users/hannahkamen/Downloads/le0_shock0_v2_test2_adj.csv")
shocks = shocks.rename(columns={"skill_shr": "pct_shock"})
shocks_lm = shocks[shocks["r"] == shocks["q"]].copy()

# ============================================================
# Construct shock differences by region
# ============================================================

shocks_lm = (
    shocks_lm.sort_values(["sk", "pct_shock"], ascending=True)
    .drop_duplicates(subset=["r", "sk"])
)

shocks_lm_pvt = (
    shocks_lm.pivot_table(index="r", columns="sk", values="pct_shock")
    .reset_index()
)
shocks_lm_pvt["difference"] = shocks_lm_pvt["skl"] - shocks_lm_pvt["unskl"]

# Regions sorted by relative skilled minus unskilled shock
sorter = shocks_lm_pvt.sort_values("difference", ascending=True)["r"]

# ============================================================
# Input intensity by sector and region
# ============================================================

# Labor demand by sector, region, and skill
ld0_d_rpt = ld0_d_rpt.rename(columns={"file": "region"})
ld0_d_rpt_pvt = (
    ld0_d_rpt.pivot_table(
        index=["region", "sector"],
        columns="skill",
        values="benchmark_ld0",
    )
    .reset_index()
)

# Intermediate demand grouped to sector and region
id0_rpt_gr = id0_rpt.groupby(["region", "sector"], as_index=False).sum()

# Merge labor, capital, and intermediate demands
int_goods = (
    ld0_d_rpt_pvt.merge(kd0_rpt, on=["region", "sector"], how="inner")
    .merge(id0_rpt_gr, on=["region", "sector"], how="inner")
)

# ============================================================
# Consumption budget shares by region and good
# ============================================================

cd0_gr = cd0_h_d_rpt.groupby(["region", "good"], as_index=False).sum()

cd0_gr_tot = cd0_h_d_rpt.groupby("region", as_index=False).sum()
cd0_gr_tot = cd0_gr_tot.rename(
    columns={"benchmark_disagg_cons": "benchmark_disagg_cons_tot"}
)

cd0_gr = cd0_gr.merge(cd0_gr_tot, on="region", how="inner")
cd0_gr["pct_budget"] = (
    cd0_gr["benchmark_disagg_cons"] / cd0_gr["benchmark_disagg_cons_tot"]
)

# ============================================================
# Plot budget share of housing by region
# ============================================================

cd0_gr_hou = cd0_gr[cd0_gr["good"] == "hou"].copy()
cd0_gr_hou = cd0_gr_hou.sort_values("pct_budget", ascending=False)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=cd0_gr_hou,
    x="region",
    y="pct_budget",
    palette=["#111111"],
    ax=ax,
)
ax.set_ylabel("Share of Consumption Budget on Housing")
ax.set_xlabel("Region")
plt.tight_layout()
plt.show()

# ============================================================
# Expenditure shares by skill type and good
# ============================================================

cd0_exp_skl = cd0_h_d_rpt.groupby(
    ["region", "good", "skill"],
    as_index=False,
).sum()

cd0_exp_skl_tot = cd0_h_d_rpt.groupby(["region", "good"], as_index=False).sum()
cd0_exp_skl_tot = cd0_exp_skl_tot.rename(
    columns={"benchmark_disagg_cons": "benchmark_disagg_cons_tot"}
)

cd0_exp_skl = cd0_exp_skl.merge(
    cd0_exp_skl_tot,
    on=["region", "good"],
    how="inner",
)
cd0_exp_skl["pct_exp"] = (
    cd0_exp_skl["benchmark_disagg_cons"]
    / cd0_exp_skl["benchmark_disagg_cons_tot"]
)

cd0_exp_skl_pvt = (
    cd0_exp_skl.pivot_table(
        index=["region", "good"],
        columns="skill",
        values="pct_exp",
    )
    .reset_index()
)

goods_list = ["amb", "fbp", "hos", "hou", "osv", "res"]
goods_labels = [
    "Ambulatory",
    "Food and Beverage",
    "Hospital",
    "Housing",
    "Other Goods and Services",
    "Restaurants",
]

for good, label in zip(goods_list, goods_labels):
    fig, ax = plt.subplots(1, 1, figsize=(6, 15))

    cd0_exp_skl_lm = cd0_exp_skl_pvt[cd0_exp_skl_pvt["good"] == good].copy()
    cd0_exp_skl_lm = cd0_exp_skl_lm.sort_values("skl", ascending=False)

    (
        cd0_exp_skl_lm.set_index("region")[["skl", "unskl"]]
        .plot(kind="barh", stacked=True, ax=ax)
    )
    plt.title(label)
    plt.legend(labels=["Skilled", "Unskilled"])
    plt.tight_layout()
    plt.show()

# ============================================================
# Input composition by sector (top goods)
# ============================================================

int_goods_gr = int_goods.groupby("sector", as_index=False).sum()
int_goods_gr["total"] = int_goods_gr.sum(axis=1, numeric_only=True)
int_goods_gr = int_goods_gr.sort_values("total", ascending=False)
int_goods_gr = int_goods_gr.drop(columns=["total"])

top_goods_list = ["hou", "hos", "amb", "res", "fbp", "osv"]

int_goods_top = int_goods_gr[int_goods_gr["sector"].isin(top_goods_list)].copy()

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
int_goods_top.set_index("sector").plot(kind="bar", stacked=True, ax=ax)
plt.ylabel("Total Input Use (summed across regions)")
plt.xlabel("Sector")
plt.tight_layout()
plt.show()

# ============================================================
# Weighted factor expenditure by region and sector
# ============================================================

cd0_gr_new = cd0_gr.rename(columns={"good": "sector"})[
    ["region", "sector", "pct_budget"]
]

# Total factor use in each sector-region
int_goods["total"] = int_goods.sum(axis=1, numeric_only=True)

int_goods = int_goods.merge(
    cd0_gr_new,
    on=["region", "sector"],
    how="inner",
)

int_goods["pct_skl"] = int_goods["skl"] / int_goods["total"]
int_goods["pct_unskl"] = int_goods["unskl"] / int_goods["total"]
int_goods["pct_capital_demand"] = (
    int_goods["benchmark_capital_demand"] / int_goods["total"]
)
int_goods["pct_int_demand"] = int_goods["benchmark_int_dmd"] / int_goods["total"]

# Budget weighted factor shares
int_goods["skl_exp"] = int_goods["pct_skl"] * int_goods["pct_budget"]
int_goods["unskl_exp"] = int_goods["pct_unskl"] * int_goods["pct_budget"]
int_goods["capital_demand_exp"] = (
    int_goods["pct_capital_demand"] * int_goods["pct_budget"]
)
int_goods["int_demand_exp"] = (
    int_goods["pct_int_demand"] * int_goods["pct_budget"]
)

# ============================================================
# Plot budget-weighted factor expenditure by region for key goods
# ============================================================

int_goods_lm = int_goods[
    ["region", "sector", "skl_exp", "unskl_exp", "capital_demand_exp", "int_demand_exp"]
].copy()
int_goods_lm = int_goods_lm[int_goods_lm["sector"].isin(top_goods_list)]

for good in goods_list:
    fig, ax = plt.subplots(1, 1, figsize=(6, 15))

    int_goods_lm["total"] = (
        int_goods_lm["skl_exp"]
        + int_goods_lm["unskl_exp"]
        + int_goods_lm["capital_demand_exp"]
        + int_goods_lm["int_demand_exp"]
    )

    int_goods_lm_tmp = int_goods_lm[int_goods_lm["sector"] == good].copy()
    int_goods_lm_tmp = int_goods_lm_tmp.sort_values("total", ascending=False)
    int_goods_lm_tmp = int_goods_lm_tmp.drop(columns=["total"])

    (
        int_goods_lm_tmp.set_index("region")[
            ["skl_exp", "unskl_exp", "capital_demand_exp", "int_demand_exp"]
        ]
        .plot(kind="barh", stacked=True, ax=ax)
    )
    plt.title(good)
    plt.legend(labels=["Skilled", "Unskilled", "Capital", "Intermediate"])
    plt.tight_layout()
    plt.show()

# ============================================================
# Identify top budget goods in each region and plot input mixes
# ============================================================

cd0_gr = cd0_gr.sort_values(["region", "pct_budget"], ascending=False)

top_budget_df = pd.DataFrame()

for region in cd0_gr["region"].unique():
    region_slice = cd0_gr[cd0_gr["region"] == region]
    # Uses overall quantile of pct_budget to pick high budget goods in this region
    high_share = region_slice["pct_budget"].quantile(q=0.90)
    tmp = region_slice[region_slice["pct_budget"] > high_share]

    goods_region = tmp["good"].unique()
    int_goods_tmp = int_goods[
        (int_goods["region"] == region)
        & (int_goods["sector"].isin(goods_region))
    ].copy()

    if not int_goods_tmp.empty:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        (
            int_goods_tmp.set_index("sector")[
                ["skl", "unskl", "benchmark_capital_demand", "benchmark_int_dmd"]
            ]
            .plot(kind="bar", stacked=True, ax=ax)
        )
        plt.title(region)
        plt.ylabel("Input Use")
        plt.tight_layout()
        plt.show()

    top_budget_df = pd.concat([top_budget_df, tmp], ignore_index=True)

# ============================================================
# Capital and labor endowment by household and region
# ============================================================

cons_endow = (
    ke0_d_rpt.merge(le0_d_rpt, on=["region", "household"])
    .groupby(["region", "household"], as_index=False)
    .sum()
)
