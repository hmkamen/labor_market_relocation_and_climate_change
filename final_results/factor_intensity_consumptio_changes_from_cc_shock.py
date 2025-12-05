#!/usr/bin/env python
# coding: utf-8

"""
this code looks at how climate labor supply shocks change:
- Input composition (skilled, unskilled, capital) by sector and state,
- Consumption-driven demand intensities for each input,
- Relative prices, production vs. consumption, and export shares by industry and region,
using GAMS output and labor-share/shock data.
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
# 0. Quick welfare sanity check for one example (IA, HH1, skilled)
# ============================================================

# The welfare report calculates new consumption per capita as:
#   ((ra) / (price index)) / (new labor endowment)
# Example values:
ra_val = 0.865767
price_index = 0.999024
new_labor_endowment = 0.254310906294

new_c_pc = (ra_val / price_index) / new_labor_endowment
print(new_c_pc)

# Old values:
old_total_c = 0.975728
old_labor = 0.286974
old_c_pc = old_total_c / old_labor

welfare_ratio = new_c_pc / old_c_pc
print(welfare_ratio)

# ============================================================
# 1. MSA variables and location lookups
# ============================================================

msa_id = pd.read_stata(
    "/Users/hannahkamen/Downloads/population-migration-master/"
    "estimation/1_main_specification/acs5yr0610/dta/msa_identifier.dta"
)
state_lookup = pd.read_excel("/Users/hannahkamen/Downloads/statelookup2.xlsx")
state_age_shares = pd.read_excel("/Users/hannahkamen/Downloads/state_age_shares.xlsx")
msa_vars = pd.read_stata(
    "/Users/hannahkamen/Downloads/population-migration-master/"
    "estimation/1_main_specification/acs5yr0610/dta/second_stage_dataset_cl.dta"
)

labor_fullf = pd.read_csv("/Users/hannahkamen/Downloads/le0_factorial.csv")
labor_fullf.to_stata("/Users/hannahkamen/Downloads/le0_factorial.dta")

# ============================================================
# 2. Import GAMS results (producer-substitution-only experiments)
# ============================================================

t = "_psubsonly"

# --- Household/asset side ---

hhtrn0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/hhtrn0_d_rpt.csv"
)
hhtrn0_d_rpt = hhtrn0_d_rpt.drop(columns="file")
hhtrn0_d_rpt = hhtrn0_d_rpt.groupby(["r", "h", "sk"], as_index=False).sum()

sav0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/sav0_d_rpt.csv"
).drop(columns="file")

tl0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/tl0_d_rpt.csv"
).drop(columns="file")

ke0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/ke0_d_rpt.csv"
).drop(columns="file")

# Initial and new labor endowments
le0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt.csv"
).drop(columns="file")
le0_d_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/le0_d_rpt0.csv"
).drop(columns="file")

# Baseline consumption: cons0_rpt(r,h,sk) = c0_h_d(r,h,sk)
cons0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/cons0_rpt.csv"
).drop(columns="file")

# Welfare index after shock
w_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/w_rpt0.csv"
).drop(columns="file")

# Wages, price index, rental rate of capital
pl_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/pl_rpt0.csv"
).drop(columns="file")
pc_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/pc_rpt0.csv"
).drop(columns="file")
rk_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/rk_rpt0.csv"
).drop(columns="file")

# --- Production side ---

cd0_h_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/cd0_h_d_rpt.csv"
).drop(columns="file")

ld0_d_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/ld0_d_rpt.csv"
)
# (file column intentionally not dropped in original code here)

y_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/y_rpt0.csv"
).drop(columns="file")

a_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/a_rpt0.csv"
).drop(columns="file")

ys0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/ys0_rpt.csv"
).drop(columns="file")

py_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/py_rpt0.csv"
).drop(columns="file")

pk_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/pk_rpt0.csv"
).drop(columns="file")

pfx_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/pfx_rpt0.csv"
).drop(columns="file")

pn_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/pn_rpt0.csv"
).drop(columns="file")

ra_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/ra_rpt0.csv"
).drop(columns="file")

c_rpt0 = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/c_rpt0.csv"
).drop(columns="file")

kd0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/kd0_rpt.csv"
).drop(columns="file")

id0_rpt = pd.read_csv(
    f"/Users/hannahkamen/Downloads/clim/csv{t}/id0_rpt.csv"
).drop(columns="file")

# ============================================================
# 3. Labor shares and shocks
# ============================================================

shares = pd.read_csv("/Users/hannahkamen/Downloads/le0_shr2.csv")
shares_u = (
    shares.drop_duplicates(subset=["q", "h", "sk"])
    .pivot(index=["q", "h"], columns="sk", values="skill_shr")
    .reset_index()
)
shares_u["diff"] = shares_u["skl"] - shares_u["unskl"]

shocks = pd.read_csv("/Users/hannahkamen/Downloads/le0_shock0_v2_test2_adj.csv")
shocks = shocks.rename(columns={"skill_shr": "pct_shock"})
shocks_lm = shocks[shocks["r"] == shocks["q"]]

# ============================================================
# 4. Skill intensity of demand by state
#    (direct and indirect input demand by sector)
# ============================================================

# Skilled/unskilled shocks by region (pivoted)
shocks_lm = (
    shocks_lm.sort_values(by=["sk", "pct_shock"], ascending=True)
    .drop_duplicates(subset=["r", "sk"])
)
shocks_lm_pvt = shocks_lm.pivot_table(
    index="r", columns="sk", values="pct_shock"
).reset_index()

# Sectoral labor demand by skill (baseline)
ld0_d_rpt = ld0_d_rpt.rename(columns={"file": "region"})
ld0_d_rpt_pvt = ld0_d_rpt.pivot_table(
    index=["region", "sector"], columns="skill", values="benchmark_ld0"
).reset_index()

# Aggregate intermediate demand by region × sector
id0_rpt_gr = id0_rpt.groupby(["region", "sector"], as_index=False).sum()

# Merge labor, capital, and intermediate goods for each sector and region
int_goods = (
    ld0_d_rpt_pvt
    .merge(kd0_rpt, on=["region", "sector"], how="inner")
    .merge(id0_rpt_gr, on=["region", "sector"], how="inner")
)

# Compute percent composition of inputs (direct, before adding intermediates)
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

# ============================================================
# 5. Add indirect (intermediate) input usage to intensities
# ============================================================

# Break down intermediate goods by the inputs used to produce them
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

# Sum intermediate-input usage over demanding sectors
int_dmd_brkdown_gr = (
    int_dmd_brkdown.groupby(["region", "sector_x"], as_index=False)
    .sum()[["region", "sector_x", "skl_int_good", "unskl_int_good", "capital_int_good"]]
    .rename(columns={"sector_x": "sector"})
)

# Add indirect (intermediate) usage on top of direct usage
int_goods_all = int_goods.merge(int_dmd_brkdown_gr, on=["region", "sector"])

int_goods_all["skl"] = int_goods_all["skl"] + int_goods_all["skl_int_good"]
int_goods_all["unskl"] = int_goods_all["unskl"] + int_goods_all["unskl_int_good"]
int_goods_all["benchmark_capital_demand"] = (
    int_goods_all["benchmark_capital_demand"] + int_goods_all["capital_int_good"]
)

int_goods_all = int_goods_all[
    ["region", "sector", "skl", "unskl", "benchmark_capital_demand"]
].rename(columns={"skl": "skl_input", "unskl": "unskl_input"})

# Recompute input shares after including indirect usage
int_goods_all["total"] = (
    int_goods_all["skl_input"]
    + int_goods_all["unskl_input"]
    + int_goods_all["benchmark_capital_demand"]
)
int_goods_all["pct_skl_input"] = int_goods_all["skl_input"] / int_goods_all["total"]
int_goods_all["pct_unskl_input"] = int_goods_all["unskl_input"] / int_goods_all["total"]
int_goods_all["pct_capital_input"] = (
    int_goods_all["benchmark_capital_demand"] / int_goods_all["total"]
)

# ============================================================
# 6. Consumption-weighted demand intensity by skill and region
# ============================================================

# Aggregate consumption by region × good × skill
cd0_gr = cd0_h_d_rpt.groupby(
    ["region", "good", "skill"], as_index=False
).sum()

# Pivot to get separate columns for skilled/unskilled demand per region × good
cd0_gr_pvt = cd0_gr.pivot_table(
    index=["region", "good"], columns="skill", values="benchmark_disagg_cons"
).reset_index()
cd0_gr_pvt = cd0_gr_pvt.rename(columns={"skl": "skl_dmd", "unskl": "unskl_dmd"})

# Merge with input intensities for those goods
cons_dmd_intensity = cd0_gr_pvt.merge(
    int_goods_all, left_on=["region", "good"], right_on=["region", "sector"]
)

# Demand intensity: how much each skill/capital is used to satisfy demand of each skill group
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

# Keep only the intensity columns we need and aggregate to the state level
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
# 7. Plots: stacked bar and skill-bias ratios
# ============================================================

# Stacked bar of demand intensity: skilled demand on skl vs unskl (and vice versa)
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set(style="white")

cons_dmd_intensity_gr_lm = cons_dmd_intensity_gr[
    ["region", "skl_skl_dmd", "skl_unskl_dmd", "unskl_skl_dmd", "unskl_unskl_dmd"]
].copy()
cons_dmd_intensity_gr_lm = cons_dmd_intensity_gr_lm.sort_values(
    by="skl_skl_dmd", ascending=False
)
cons_dmd_intensity_gr_lm.set_index("region").plot(
    kind="bar", stacked=True, ax=ax
)

# --- Ratios: S/U intensity for skilled and unskilled demand ---

# Ratio of (skilled input / unskilled input) in consumption by skill group
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

# 7a. Difference in S/U ratios between skilled and unskilled demand
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")
tmp = cons_dmd_intensity_gr_lm.sort_values(by="ratio_diff", ascending=False)
sns.barplot(data=tmp, x="region", y="ratio_diff", palette=["#111111"], ax=ax)

# 7b. Unskilled demand S/U ratio
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")
tmp = cons_dmd_intensity_gr_lm.sort_values(
    by="unskl_su_ratio", ascending=False
)
sns.barplot(data=tmp, x="region", y="unskl_su_ratio", palette=["#111111"], ax=ax)

# 7c. Skilled demand S/U ratio
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
sns.set_theme(style="whitegrid")
tmp = cons_dmd_intensity_gr_lm.sort_values(
    by="skl_su_ratio", ascending=False
)
sns.barplot(data=tmp, x="region", y="skl_su_ratio", palette=["#111111"], ax=ax)

# ============================================================
# 8. Price change by good and region
# ============================================================

for g in ["hou", "amb", "fbp", "hos", "res", "osv"]:
    py_g = py_rpt0[py_rpt0["good"] == g].copy()
    py_g["price_change"] = py_g["py0"] - 1

    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    py_g = py_g.sort_values(by="price_change", ascending=False)

    sns.set_theme(style="whitegrid")
    sns.barplot(
        data=py_g, x="region", y="price_change", hue="good",
        palette=["#111111"], ax=ax
    )

# ============================================================
# 9. Weighted consumption shares and relative prices vs national
# ============================================================

# Share of each (region, household, skill) in total region consumption
cons_b_total = cons0_rpt.groupby("region", as_index=False).sum()
cons_b_total = cons_b_total.rename(
    columns={"benchmark_cons": "benchmark_cons_tot"}
)
cons0_rpt = cons0_rpt.merge(cons_b_total, on="region")
cons0_rpt["pct_total_cons"] = (
    cons0_rpt["benchmark_cons"] / cons0_rpt["benchmark_cons_tot"]
)

# Price change relative to national price for each good
price_rel_nat = py_rpt0.merge(pn_rpt0, on="good")
price_rel_nat_lm = price_rel_nat[
    price_rel_nat["good"].isin(["hou", "amb", "fbp", "hos", "res", "osv"])
].copy()

for g in ["hou", "amb", "fbp", "hos", "res", "osv"]:
    tmp = price_rel_nat_lm[price_rel_nat_lm["good"] == g].copy()
    tmp["price_rel_nat"] = tmp["py0"] - tmp["pn0"]

    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    tmp = tmp.sort_values(by="price_rel_nat", ascending=False)

    sns.set_theme(style="whitegrid")
    sns.barplot(
        data=tmp, x="region", y="price_rel_nat", hue="good",
        palette=["#111111"], ax=ax
    )

# ============================================================
# 10. Production vs. consumption: trade orientation index
# ============================================================

# Weight consumption shock by baseline consumption shares
c_rpt0_weighted = c_rpt0.merge(
    cons0_rpt, on=["region", "household", "skill"]
)
c_rpt0_weighted["weighted_cons_shock"] = (
    c_rpt0_weighted["cons_shock0"] * c_rpt0_weighted["pct_total_cons"]
)
c_rpt0_weighted_gr = c_rpt0_weighted.groupby("region", as_index=False).sum()
c_rpt0_weighted_gr = c_rpt0_weighted_gr[["region", "weighted_cons_shock"]]

trade = c_rpt0_weighted_gr.merge(y_rpt0, on="region")
trade["prod_to_cons_ratio"] = (
    trade["output_shock0"] / trade["weighted_cons_shock"]
)

trade_lm = trade[
    trade["sector"].isin(["hou", "amb", "fbp", "hos", "res", "osv"])
]

for g in ["hou", "amb", "fbp", "hos", "res", "osv"]:
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    tmp = trade_lm[trade_lm["sector"] == g].copy()
    tmp = tmp.sort_values(by="prod_to_cons_ratio", ascending=False)

    sns.set_theme(style="whitegrid")
    sns.barplot(
        data=tmp, x="region", y="prod_to_cons_ratio", hue="sector", ax=ax
    )

# ============================================================
# 11. Percent local exports by industry
# ============================================================

cons_b_gr = cd0_h_d_rpt.groupby(["region", "good"], as_index=False).sum()
ys0_gr = ys0_rpt.groupby(["region", "good"], as_index=False).sum()

benchmark_exports = cons_b_gr.merge(ys0_gr, on=["region", "good"])
benchmark_exports["exports"] = (
    benchmark_exports["benchmark_supply"]
    - benchmark_exports["benchmark_disagg_cons"]
)
benchmark_exports["pct_exports_supply"] = (
    benchmark_exports["exports"] / benchmark_exports["benchmark_supply"]
)

for g in ["hou", "amb", "fbp", "hos", "res", "osv"]:
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    tmp = benchmark_exports[benchmark_exports["good"] == g].copy()
    tmp = tmp.sort_values(by="pct_exports_supply", ascending=False)

    sns.set_theme(style="whitegrid")
    sns.barplot(
        data=tmp, x="region", y="pct_exports_supply", hue="good", ax=ax
    )

# ============================================================
# 12. Labor supply composition and exports (housing example)
# ============================================================

# Relative size of skilled vs unskilled labor endowment by region
labor_breakout = le0_d_rpt.groupby(
    ["region", "skill"], as_index=False
).sum()
labor_breakout_tot = le0_d_rpt.groupby("region", as_index=False).sum()
labor_breakout_tot = labor_breakout_tot.rename(
    columns={"benchmark_le0": "benchmark_le0_tot"}
)
labor_breakout = labor_breakout.merge(labor_breakout_tot, on="region")
labor_breakout["pct_total"] = (
    labor_breakout["benchmark_le0"] / labor_breakout["benchmark_le0_tot"]
)

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
labor_breakout = labor_breakout.sort_values(by="pct_total", ascending=True)
sns.set_theme(style="whitegrid")
sns.barplot(
    data=labor_breakout,
    x="region",
    y="pct_total",
    hue="skill",
    palette=["#111111", "#777777"],
    ax=ax,
)
plt.legend(ncol=2)

# Housing export share by region (example)
ys0_rpt_gr = ys0_rpt.groupby(["region", "good"], as_index=False).sum()
cd0_gr = cd0_h_d_rpt.groupby(["region", "good"], as_index=False).sum()

trade_df = ys0_rpt_gr.merge(cd0_gr, on=["region", "good"], how="inner")
trade_df["exports"] = (
    trade_df["benchmark_supply"] - trade_df["benchmark_disagg_cons"]
)
trade_df["pct_export"] = trade_df["exports"] / trade_df["benchmark_supply"]

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
trade_df_hou = trade_df[trade_df["good"] == "hou"].copy()
trade_df_hou = trade_df_hou.sort_values(by="exports", ascending=True)

sns.set_theme(style="whitegrid")
sns.barplot(
    data=trade_df_hou,
    x="region",
    y="pct_export",
    palette=["#111111"],
    ax=ax,
)
plt.legend(ncol=2)
