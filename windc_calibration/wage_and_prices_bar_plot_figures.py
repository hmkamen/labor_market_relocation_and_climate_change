#!/usr/bin/env python
# coding: utf-8

#This code loads welfare, output, wage, and consumption price index results from CSV files produced from Windc and produces a set of bar plots. The figures illustrate how welfare by household and skill group, consumption price indices by household, aggregate output by state, and wages by skill respond to changes in the skilled labor exit or entry shock .

import pandas as pd
import numpy as np
import scipy.stats  # kept for compatibility with original environment
import matplotlib.pyplot as plt
import seaborn as sns

# ======================================================================
# Load model output
# ======================================================================

w = pd.read_csv("/Users/hannahkamen/Downloads/w_rpt.csv")   # welfare index by region, skill, household, pct
y = pd.read_csv("/Users/hannahkamen/Downloads/y_rpt.csv")   # output by region, pct, possibly industry
pl = pd.read_csv("/Users/hannahkamen/Downloads/pl_rpt.csv") # wages by region, skill, pct
pc = pd.read_csv("/Users/hannahkamen/Downloads/pc_rpt.csv") # consumption price index by region, household, pct

# ======================================================================
# Shared plot styling
# ======================================================================

def add_grid(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(color="gray", linestyle="dashed", alpha=0.6)
    ax.xaxis.grid(color="gray", linestyle="dashed", alpha=0.6)

# Color palettes
gray_levels = ["#D4D4D4", "#B4B4B4", "#909090", "#636363", "#494848"]
red_levels = ["#8B0001", "#9E1711", "#B12E21", "#C34632", "#E97452"]

households = ["hh1", "hh2", "hh3", "hh4", "hh5"]

# ======================================================================
# 1. Welfare index by household and skill type in each region
# ======================================================================

for state in ["CO", "TX"]:
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)

    ax.set_xlabel("Skilled Labor Exit Percentage in Texas", fontsize=16)
    ax.set_ylabel("Welfare", fontsize=16)
    ax.set_title(f"Welfare Index by Household and Skill Type in {state}", fontsize=16)

    # Gray scale for skilled, red scale for unskilled
    for skill, palette in zip(["skl", "unskl"], [gray_levels, red_levels]):
        for hh, color in zip(households, palette):
            tmp = (
                w[(w["skill"] == skill) & (w["region"] == state) & (w["household"] == hh)]
                .sort_values(by="pct")
                .reset_index(drop=True)
            )
            if tmp.empty:
                continue

            ax.plot(tmp["pct"], tmp["value"], color=color, alpha=0.7, label=f"{hh} {skill}")

    ax.legend()
    plt.tight_layout()
    plt.show()

# ======================================================================
# 2. Consumption price index by household in each region
# ======================================================================

for state in ["CO", "TX"]:
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)

    ax.set_xlabel("Skilled Labor Exit Percentage in Texas", fontsize=16)
    ax.set_ylabel("Consumption Price Index", fontsize=16)
    ax.set_title(f"Consumption Price Index by Household in {state}", fontsize=16)

    # One gray shade per household
    for hh, color in zip(households, gray_levels):
        tmp = (
            pc[(pc["region"] == state) & (pc["household"] == hh)]
            .sort_values(by="pct")
            .reset_index(drop=True)
        )
        if tmp.empty:
            continue

        ax.plot(tmp["pct"], tmp["value"], color=color, alpha=0.7, label=hh)

    ax.legend()
    plt.tight_layout()
    plt.show()

# ======================================================================
# 3. Aggregate output by region as skilled exit percentage changes
# ======================================================================

# Sum output across all other dimensions within region–pct
y_gr = y.groupby(["region", "pct"], as_index=False)["value"].sum()

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
add_grid(ax)

ax.set_xlabel("Skilled Labor Exit Percentage in Texas", fontsize=16)
ax.set_ylabel("Output", fontsize=16)
ax.set_title("Output by Region", fontsize=16)

for state, color in zip(["CO", "TX"], ["red", "gray"]):
    tmp = (
        y_gr[y_gr["region"] == state]
        .sort_values(by="pct")
        .reset_index(drop=True)
    )
    if tmp.empty:
        continue

    ax.plot(tmp["pct"], tmp["value"], color=color, alpha=0.7, label=state)

ax.legend()
plt.tight_layout()
plt.show()

# ======================================================================
# 4. Wages by skill type in each region
# ======================================================================

for state in ["CO", "TX"]:
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)

    ax.set_xlabel("Skilled Labor Exit Percentage in Texas", fontsize=16)
    ax.set_ylabel("Wages", fontsize=16)
    ax.set_title(f"Wages by Skill Type in {state}", fontsize=16)

    # Gray for skilled, red for unskilled
    for skill, color in zip(["skl", "unskl"], ["gray", "red"]):
        tmp = (
            pl[(pl["skill"] == skill) & (pl["region"] == state)]
            .sort_values(by="pct")
            .reset_index(drop=True)
        )
        if tmp.empty:
            continue

        ax.plot(tmp["pct"], tmp["value"], color=color, alpha=0.7, label=skill)

    ax.legend()
    plt.tight_layout()
    plt.show()
