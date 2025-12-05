#!/usr/bin/env python
# coding: utf-8

#This code loads Windc GAMS general equilibrium outputs, constructs measures of skill intensity and consumption demand by state, and produces diagnostic plots of capital endowments, labor supply shocks, input intensities, export shares, and consumption bundle composition across regions.

import pandas as pd
import numpy as np
import math
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# ============================================================
# File tag for experiment batch
# ============================================================

t = "_tsubsonly"

# ============================================================
# Import GAMS results and related data
# ============================================================

# Household transfers (benchmark, summed over files)
hhtrn0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/hhtrn0_d_rpt.csv")
hhtrn0_d_rpt = (
    hhtrn0_d_rpt.drop(columns=["file"])
    .groupby(["r", "h", "sk"], as_index=False)
    .sum()
)

# Savings
sav0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/sav0_d_rpt.csv")
sav0_d_rpt = sav0_d_rpt.drop(columns=["file"])

# Labor tax rates
tl0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/tl0_d_rpt.csv")
tl0_d_rpt = tl0_d_rpt.drop(columns=["file"])

# Capital endowment (benchmark)
ke0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ke0_d_rpt.csv")
ke0_d_rpt = ke0_d_rpt.drop(columns=["file"])

# Labor endowment (benchmark and counterfactual)
le0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt.csv")
le0_d_rpt = le0_d_rpt.drop(columns=["file"])

le0_d_rpt0 = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt0.csv")
le0_d_rpt0 = le0_d_rpt0.drop(columns=["file"])

# Initial labor supply by origin, destination, household, and skill
labor_b = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt00.csv")
labor_b = (
    labor_b[["file", "region", "household", "benchmark_le0", "skill"]]
    .reset_index(drop=True)
    .rename(columns={"file": "r", "region": "q", "skill": "sk", "household": "h"})
)

# Benchmark consumption demand
cd0_h_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/cd0_h_d_rpt.csv")
cd0_h_d_rpt = cd0_h_d_rpt.drop(columns=["file"])

# Sector labor demand by skill
ld0_d_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ld0_d_rpt.csv")

# Output by sector
ys0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/ys0_rpt.csv")
ys0_rpt = ys0_rpt.drop(columns=["file"])

# Capital demand by sector
kd0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/kd0_rpt.csv")
kd0_rpt = kd0_rpt.drop(columns=["file"])

# Intermediate goods demand
id0_rpt = pd.read_csv(f"/Users/hannahkamen/Downloads/clim/csv{t}/id0_rpt.csv")
id0_rpt = id0_rpt.drop(columns=["file"])

# Skill share matrix and shocks
shares = pd.read_csv("/Users/hannahkamen/Downloads/le0_shr2.csv")

shares_u = (
    shares.drop_duplicates(subset=["q", "h", "sk"])
    .pivot(index=["q", "h"], columns="sk", values="skill_shr")
    .reset_index()
)
shares_u["diff"] = shares_u["skl"] - shares_u["unskl"]

shocks = pd.read_csv("/Users/hannahkamen/Downloads/le0_shock0_v2_test2_adj.csv")
shocks = shocks.rename(columns={"skill_shr": "pct_shock"})

# Restrict shocks to home region equal to destination region
shocks_lm = shocks[shocks["r"] == shocks["q"]].copy()

# ============================================================
# Capital endowment by region and skill
# ============================================================

capital_gr = (
    ke0_d_rpt.groupby(["region", "skill"], as_index=False)
    .agg({"benchmark_k": "sum"})
    .sort_values(["skill", "benchmark_k"], ascending=True)
    .reset_index(drop=True)
)

fig, ax = plt.subplots(1, 1, figsize=(15, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=capital_gr,
    x="region",
    y="benchmark_k",
    hue="skill",
    palette=["#111111", "#777777"],
    ax=ax,
)
ax.set_ylabel("Benchmark Capital Endowment")
ax.set_xlabel("Region")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()

# ============================================================
# Labor supply shocks by region and skill
# ============================================================

shocks_lm = (
    shocks_lm.sort_values(["sk", "pct_shock"], ascending=True)
    .reset_index(drop=True)
)

fig, ax = plt.subplots(1, 1, figsize=(15, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=shocks_lm,
    x="r",
    y="pct_shock",
    hue="sk",
    palette=["#111111", "#777777"],
    ax=ax,
)
ax.set_ylabel("Percent Change in Labor Supply")
ax.set_xlabel("Region")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()

# ============================================================
# Skill intensity of production by state including intermediate goods
# ============================================================

# Collapse shocks to region-skill means for later use
shocks_lm = (
    shocks_lm.sort_values(["sk", "pct_shock"], ascending=True)
    .drop_duplicates(subset=["r", "sk"])
)
shocks_lm_pvt = shocks_lm.pivot_table(
    index="r", columns="sk", values="pct_shock"
).reset_index()

# Labor demand by sector and region
ld0_d_rpt = ld0_d_rpt.rename(columns={"file": "region"})
ld0_d_rpt_pvt = ld0_d_rpt.pivot_table(
    index=["region", "sector"], columns="skill", values="benchmark_ld0"
).reset_index()

# Intermediate demand by sector and region
id0_rpt_gr = id0_rpt.groupby(["region", "sector"], as_index=False).sum()

# Merge labor, capital, and intermediate goods demand to compute cost shares
int_goods = (
    ld0_d_rpt_pvt.merge(kd0_rpt, on=["region", "sector"], how="inner")
    .merge(id0_rpt_gr, on=["region", "sector"], how="inner")
)

int_goods["total_value"] = (
    int_goods["skl"]
    + int_goods["unskl"]
    + int_goods["benchmark_capital_demand"]
    + int_goods["benchmark_int_dmd"]
)

int_goods["pct_skl"] = int_goods["skl"] / int_goods["total_value"]
int_goods["pct_unskl"] = int_goods["unskl"] / int_goods["total_value"]
int_goods["pct_capital"] = (
    int_goods["benchmark_capital_demand"] / int_goods["total_value"]
)

# Map skill and capital content of intermediate goods into using sectors
int_dmd_brkdown = id0_rpt.merge(
    int_goods, left_on=["region", "good"], right_on=["region", "sector"]
)

int_dmd_brkdown["skl_int_good"] = (
    int_dmd_brkdown["pct_skl"] * int_dmd_brkdown["benchmark_int_dmd_x"]
)
int_dmd_brkdown["unskl_int_good"] = (
    int_dmd_brkdown["pct_unskl"] * int_dmd_brkdown["benchmark_int_dmd_x"]
)
int_dmd_brkdown["capital_int_good"] = (
    int_dmd_brkdown["pct_capital"] * int_dmd_brkdown["benchmark_int_dmd_x"]
)

int_dmd_brkdown_gr = (
    int_dmd_brkdown.groupby(["region", "sector_x"], as_index=False)
    .sum()[["region", "sector_x", "skl_int_good", "unskl_int_good", "capital_int_good"]]
    .rename(columns={"sector_x": "sector"})
)

# Add intermediate input content back into original breakdown
int_goods_all = int_goods.merge(
    int_dmd_brkdown_gr, on=["region", "sector"], how="inner"
)

int_goods_all["skl_input"] = (
    int_goods_all["skl"] + int_goods_all["skl_int_good"]
)
int_goods_all["unskl_input"] = (
    int_goods_all["unskl"] + int_goods_all["unskl_int_good"]
)
int_goods_all["benchmark_capital_demand"] = (
    int_goods_all["benchmark_capital_demand"]
    + int_goods_all["capital_int_good"]
)

int_goods_all = int_goods_all[
    ["region", "sector", "skl_input", "unskl_input", "benchmark_capital_demand"]
]

int_goods_all["total"] = (
    int_goods_all["skl_input"]
    + int_goods_all["unskl_input"]
    + int_goods_all["benchmark_capital_demand"]
)

int_goods_all["pct_skl_input"] = int_goods_all["skl_input"] / int_goods_all["total"]
int_goods_all["pct_unskl_input"] = (
    int_goods_all["unskl_input"] / int_goods_all["total"]
)
int_goods_all["pct_capital_input"] = (
    int_goods_all["benchmark_capital_demand"] / int_goods_all["total"]
)

# ============================================================
# Consumption demand intensities by state and skill
# ============================================================

# Aggregate consumption demand by region, good, and skill
cd0_gr = cd0_h_d_rpt.groupby(["region", "good", "skill"], as_index=False).sum()
cd0_gr_pvt = cd0_gr.pivot_table(
    index=["region", "good"],
    columns="skill",
    values="benchmark_disagg_cons",
).reset_index()
cd0_gr_pvt = cd0_gr_pvt.rename(
    columns={"skl": "skl_dmd", "unskl": "unskl_dmd"}
)

# Merge consumption demand with input cost shares
cons_dmd_intensity = cd0_gr_pvt.merge(
    int_goods_all, left_on=["region", "good"], right_on=["region", "sector"]
)

# Skill and capital content of consumption demand by skill type
cons_dmd_intensity["skl_skl_dmd"] = (
    cons_dmd_intensity["skl_dmd"] * cons_dmd_intensity["pct_skl_input"]
)
cons_dmd_intensity["skl_unskl_dmd"] = (
    cons_dmd_intensity["skl_dmd"] * cons_dmd_intensity["pct_unskl_input"]
)
cons_dmd_intensity["skl_cap_dmd"] = (
    cons_dmd_intensity["skl_dmd"] * cons_dmd_intensity["pct_capital_input"]
)

cons_dmd_intensity["unskl_skl_dmd"] = (
    cons_dmd_intensity["unskl_dmd"] * cons_dmd_intensity["pct_skl_input"]
)
cons_dmd_intensity["unskl_unskl_dmd"] = (
    cons_dmd_intensity["unskl_dmd"] * cons_dmd_intensity["pct_unskl_input"]
)
cons_dmd_intensity["unskl_cap_dmd"] = (
    cons_dmd_intensity["unskl_dmd"] * cons_dmd_intensity["pct_capital_input"]
)

cons_dmd_intensity = cons_dmd_intensity[
    [
        "region",
        "good",
        "skl_skl_dmd",
        "skl_unskl_dmd",
        "skl_cap_dmd",
        "unskl_skl_dmd",
        "unskl_unskl_dmd",
        "unskl_cap_dmd",
    ]
]

cons_dmd_intensity_gr = cons_dmd_intensity.groupby("region", as_index=False).sum()

# ============================================================
# Stacked bar plot of consumption demand intensity
# ============================================================

cons_dmd_intensity_gr_lm = cons_dmd_intensity_gr[
    ["region", "skl_skl_dmd", "skl_unskl_dmd", "unskl_skl_dmd", "unskl_unskl_dmd"]
].copy()

cons_dmd_intensity_gr_lm = cons_dmd_intensity_gr_lm.sort_values(
    "skl_skl_dmd", ascending=False
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set(style="white")

cons_dmd_intensity_gr_lm.set_index("region").plot(
    kind="bar", stacked=True, ax=ax
)
ax.set_ylabel("Consumption Demand Intensity by Skill Type and Region")
ax.set_xlabel("Region")
plt.tight_layout()
plt.show()

# ============================================================
# Ratios of skilled to unskilled demand by region
# ============================================================

cons_dmd_intensity_gr_lm["skl_su_ratio"] = (
    cons_dmd_intensity_gr_lm["skl_skl_dmd"]
    / cons_dmd_intensity_gr_lm["skl_unskl_dmd"]
)
cons_dmd_intensity_gr_lm["unskl_su_ratio"] = (
    cons_dmd_intensity_gr_lm["unskl_skl_dmd"]
    / cons_dmd_intensity_gr_lm["unskl_unskl_dmd"]
)
cons_dmd_intensity_gr_lm["ratio_diff"] = (
    cons_dmd_intensity_gr_lm["skl_su_ratio"]
    - cons_dmd_intensity_gr_lm["unskl_su_ratio"]
)

# Plot difference in ratios
cons_dmd_intensity_gr_lm_diff = cons_dmd_intensity_gr_lm.sort_values(
    "ratio_diff", ascending=False
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=cons_dmd_intensity_gr_lm_diff,
    x="region",
    y="ratio_diff",
    color="#111111",
    ax=ax,
)
ax.set_ylabel("Difference in Skilled and Unskilled Demand Ratios")
ax.set_xlabel("Region")
plt.tight_layout()
plt.show()

# Plot unskilled demand ratios
cons_dmd_intensity_gr_lm_unskl = cons_dmd_intensity_gr_lm.sort_values(
    "unskl_su_ratio", ascending=False
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=cons_dmd_intensity_gr_lm_unskl,
    x="region",
    y="unskl_su_ratio",
    color="#111111",
    ax=ax,
)
ax.set_ylabel("Unskilled Demand Ratio (Skilled Inputs over Unskilled Inputs)")
ax.set_xlabel("Region")
plt.tight_layout()
plt.show()

# Plot skilled demand ratios
cons_dmd_intensity_gr_lm_skl = cons_dmd_intensity_gr_lm.sort_values(
    "skl_su_ratio", ascending=False
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=cons_dmd_intensity_gr_lm_skl,
    x="region",
    y="skl_su_ratio",
    color="#111111",
    ax=ax,
)
ax.set_ylabel("Skilled Demand Ratio (Skilled Inputs over Unskilled Inputs)")
ax.set_xlabel("Region")
plt.tight_layout()
plt.show()

# ============================================================
# Export intensity and labor composition
# ============================================================

# Percent of supply exported by industry and region
cons_b_gr = cd0_h_d_rpt.groupby(["region", "good"], as_index=False).sum()
ys0_gr = ys0_rpt.groupby(["region", "good"], as_index=False).sum()

benchmark_exports = cons_b_gr.merge(ys0_gr, on=["region", "good"], how="inner")
benchmark_exports["exports"] = (
    benchmark_exports["benchmark_supply"]
    - benchmark_exports["benchmark_disagg_cons"]
)
benchmark_exports["pct_exports_supply"] = (
    benchmark_exports["exports"] / benchmark_exports["benchmark_supply"]
)

# Plot export shares for selected industries
for g in ["hou", "amb", "fbp", "hos", "res", "osv"]:
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    benchmark_exports_lm = benchmark_exports[
        benchmark_exports["good"] == g
    ].sort_values("pct_exports_supply", ascending=False)

    sns.set_theme(style="whitegrid")
    sns.barplot(
        data=benchmark_exports_lm,
        x="region",
        y="pct_exports_supply",
        hue="good",
        ax=ax,
    )
    ax.set_ylabel("Percent of Output Exported")
    ax.set_xlabel("Region")
    ax.set_title(f"Export Share of Industry {g}")
    plt.tight_layout()
    plt.show()

# Labor composition by region
labor_breakout = le0_d_rpt.groupby(["region", "skill"], as_index=False).sum()

labor_breakout_tot = (
    le0_d_rpt.groupby("region", as_index=False)
    .sum()[["region", "benchmark_le0"]]
    .rename(columns={"benchmark_le0": "benchmark_le0_tot"})
)

labor_breakout = labor_breakout.merge(labor_breakout_tot, on="region", how="inner")
labor_breakout["pct_total"] = (
    labor_breakout["benchmark_le0"] / labor_breakout["benchmark_le0_tot"]
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
labor_breakout = labor_breakout.sort_values("pct_total", ascending=True)
sns.set_theme(style="whitegrid")

sns.barplot(
    data=labor_breakout,
    x="region",
    y="pct_total",
    hue="skill",
    palette=["#111111", "#777777"],
    ax=ax,
)
ax.set_ylabel("Share of Total Labor Endowment")
ax.set_xlabel("Region")
ax.legend(ncol=2)
plt.tight_layout()
plt.show()

# ============================================================
# Expenditure shares on selected goods
# ============================================================

# Expenditure on selected goods and total consumption by region
cd0_breakout = (
    cd0_h_d_rpt[cd0_h_d_rpt["good"].isin(["hou", "amb", "fbp", "hos", "res"])]
    .groupby(["region", "good"], as_index=False)
    .sum()
)

cd0_breakout_tot = (
    cd0_h_d_rpt.groupby("region", as_index=False)
    .sum()[["region", "benchmark_disagg_cons"]]
    .rename(columns={"benchmark_disagg_cons": "benchmark_disagg_cons_tot"})
)

cd0_breakout = cd0_breakout.merge(
    cd0_breakout_tot, on="region", how="inner"
)
cd0_breakout["pct_total"] = (
    cd0_breakout["benchmark_disagg_cons"]
    / cd0_breakout["benchmark_disagg_cons_tot"]
)

# Remove small or special-case regions
exclude_regions = ["AK", "DC", "HI", "NH", "VT", "WY", "WV"]
cd0_breakout = cd0_breakout[
    ~cd0_breakout["region"].isin(exclude_regions)
].copy()

cd0_breakout = cd0_breakout.sort_values("pct_total", ascending=True)

fig, ax = plt.subplots(1, 1, figsize=(18, 6))
sns.set_theme(style="whitegrid")

sns.barplot(
    data=cd0_breakout,
    x="region",
    y="pct_total",
    hue="good",
    ax=ax,
)
ax.set_ylabel("Percent of Total Consumer Expenditure Bundle")
ax.set_xlabel("Region")
ax.legend(ncol=2)
plt.tight_layout()
plt.show()
