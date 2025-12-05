#This code loads climate-migration shock outputs from windc, constructs an adjusted welfare measure for skilled labor, and produces diagnostic plots showing how welfare, output, prices, and wages in the warm (“exit”) region vary with the share of skilled labor.

#!/usr/bin/env python
# coding: utf-8

"""
Climate migration diagnostic charts

- Load welfare (u), wages (pl), output prices (py), and output levels (y)
- Construct an adjusted welfare measure for skilled workers
- Plot:
    1) Welfare vs skilled share in the warm ("exit") region
    2) Output vs skilled share in the warm region (by industry)
    3) Output prices vs skilled share in the warm region (by industry)
    4) Wages vs skilled share in the warm region (by skill type)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Load data
# ============================================================

u = pd.read_csv("/Users/hannahkamen/Downloads/climate_migration_results/u_report.csv")
pl = pd.read_csv("/Users/hannahkamen/Downloads/climate_migration_results/pl_report.csv")
py = pd.read_csv("/Users/hannahkamen/Downloads/climate_migration_results/py_report.csv")
y = pd.read_csv("/Users/hannahkamen/Downloads/climate_migration_results/y_report.csv")

# Strip any stray whitespace from column names
u.columns = [c.strip() for c in u.columns]
y.columns = [c.strip() for c in y.columns]
pl.columns = [c.strip() for c in pl.columns]
py.columns = [c.strip() for c in py.columns]


# ============================================================
# Construct adjusted welfare for skilled workers
# ============================================================

# Start with raw welfare
u["adjusted_welfare"] = u["value"]

# Scale skilled welfare in the warm/“exit” region ("s") by the skilled share
mask_s_skl = (u["region"] == "s") & (u["labor_type"] == "skl")
u.loc[mask_s_skl, "adjusted_welfare"] = (
    u.loc[mask_s_skl, "value"] / u.loc[mask_s_skl, "prop_skl_s"]
)

# Alternative adjustment for skilled welfare in the cold/"n" region
mask_n_skl = (u["region"] == "n") & (u["labor_type"] == "skl")
u.loc[mask_n_skl, "adjusted_welfare"] = (
    u.loc[mask_n_skl, "value"] / (1 + (1 - u.loc[mask_n_skl, "prop_skl_s"]))
)


# ============================================================
# Helper function for consistent plot styling
# ============================================================

def setup_axes(
    xlabel: str,
    ylabel: str,
    xlim: tuple | None = None,
    ylim: tuple | None = None,
    figsize=(8, 6),
):
    """Create a figure and axis with common grid and labels."""
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_axisbelow(True)
    ax.yaxis.grid(color="gray", linestyle="dashed")
    ax.xaxis.grid(color="gray", linestyle="dashed")
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    return fig, ax


# ============================================================
# 1) Welfare vs skilled share in the warm ("exit") region
# ============================================================

fig, ax = setup_axes(
    xlabel="Proportion Skilled Labor in Climate Exit Region",
    ylabel="Welfare",
)

for hh, c in zip(["skl", "unskl"], ["black", "red"]):
    tmp = u[(u["labor_type"] == hh) & (u["region"] == "s")].copy()
    tmp = tmp.sort_values(by="prop_skl_s").reset_index(drop=True)
    ax.plot(tmp["prop_skl_s"], tmp["adjusted_welfare"], c=c, alpha=0.5, label=hh)

ax.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 2) Output vs skilled share in warm region, by industry
# ============================================================

fig, ax = setup_axes(
    xlabel='Proportion Skilled Labor in Climate "Exit Region"',
    ylabel="Output In Climate Exit Region",
)
ax.set_xlim(0, 0.5)

for ind, c in zip(["hou", "con"], ["black", "red"]):
    tmp = y[(y["industry"] == ind) & (y["region"] == "s")].copy()
    tmp = tmp.sort_values(by="prop_skl_s").reset_index(drop=True)
    ax.plot(tmp["prop_skl_s"], tmp["value"], c=c, alpha=0.5, label=ind)

ax.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 3) Output prices vs skilled share in warm region, by industry
# ============================================================

# Example: drop specific grid points if desired
py_lm = py[
    (py["prop_skl_s"] != 0.25)
    & (py["prop_skl_s"] != 0.6)
    & (py["prop_skl_s"] != 0.4)
].copy()

fig, ax = setup_axes(
    xlabel='Proportion Skilled Labor in Climate "Exit Region"',
    ylabel="Price of Output in Climate Exit Region",
    xlim=(0, 0.8),
    ylim=(0, 2),
)

for ind, c in zip(["hou", "con"], ["black", "red"]):
    tmp = py_lm[(py_lm["industry"] == ind) & (py_lm["region"] == "s")].copy()
    tmp = tmp.sort_values(by="prop_skl_s").reset_index(drop=True)
    ax.plot(tmp["prop_skl_s"], tmp["value"], c=c, alpha=0.5, label=ind)

ax.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 4) Wages vs skilled share in warm region, by skill type
# ============================================================

# Optional filtering of specific grid points
pl_lm = pl[(pl["prop_skl_s"] != 0.2) & (pl["prop_skl_s"] != 0.35)].copy()

fig, ax = setup_axes(
    xlabel='Proportion Skilled Labor in Climate "Exit Region"',
    ylabel="Wages In Climate Exit Region",
    xlim=(0, 0.8),
)

for hh, c in zip(["skl", "unskl"], ["black", "red"]):
    tmp = pl_lm[(pl_lm["labor_type"] == hh) & (pl_lm["region"] == "s")].copy()
    tmp = tmp.sort_values(by="prop_skl_s").reset_index(drop=True)
    ax.plot(tmp["prop_skl_s"], tmp["value"], c=c, alpha=0.5, label=hh)

ax.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 5) (Optional) Additional plots
#    These require `data`, `predict_chart_w`, and `predict_chart_d`
#    to be defined elsewhere in your notebook / script.
# ============================================================

# Example structure if you want to keep these for later:
#
# fig, ax = setup_axes(
#     xlabel='Proportion Skilled Labor in Climate "Exit Region"',
#     ylabel="Welfare",
# )
#
# for r in ["n", "s"]:
#     tmp = data[data["region"] == r]
#     for hh in ["skl", "unskl"]:
#         tmp2 = tmp[tmp["labor_type"] == hh].copy()
#         tmp2 = tmp2.sort_values(by="prop_skl_s").reset_index(drop=True)
#         ax.plot(tmp2["prop_skl_s"], tmp2["value"], alpha=0.5, label=f"{r}-{hh}")
#
# ax.legend()
# plt.tight_layout()
# plt.show()
#
# # Bar chart for forecast-month profit losses (needs predict_chart_w/d)
# fig, ax = plt.subplots(1, 1, figsize=(15, 6))
# ax.set_axisbelow(True)
# ax.yaxis.grid(color="gray", linestyle="dashed")
# ax.xaxis.grid(color="gray", linestyle="dashed")
#
# X = ["Jan", "Feb", "Mar", "Apr"]
# X_axis = np.arange(len(X))
#
# ax.bar(
#     X_axis + 0.2,
#     predict_chart_w["Pct. Losses Relative to Forecast Certainty"],
#     0.4,
#     label="Wet",
# )
# ax.bar(
#     X_axis - 0.2,
#     predict_chart_d["Pct. Losses Relative to Forecast Certainty"],
#     0.4,
#     label="Dry",
# )
#
# ax.set_xticks(X_axis)
# ax.set_xticklabels(X)
# ax.legend()
# ax.set_xlabel("Forecast Month", fontsize=16)
# ax.set_ylabel("Est. Losses Relative to Certainty", fontsize=16)
# ax.set_title("Profit Losses vs Forecast Month", fontsize=16)
#
# plt.tight_layout()
# plt.savefig("/Users/hannahkamen/Downloads/Losses_from_Imperfect_Info_CO_Dry.png")
# plt.show()
