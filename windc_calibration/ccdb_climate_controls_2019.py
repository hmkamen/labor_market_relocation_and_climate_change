#!/usr/bin/env python
# coding: utf-8

#This code builds an updated 2019 MSA-level CCDB-style dataset by merging population/race, income, crime, manufacturing, and federal spending for 2019, harmonizing virtual MSAs for small states, and aligning all geographies to the 2019 MSA definitions. I then aggregate Albouy climate data from PUMA-level to MSA-level using population weights by PUMA and state contributions, then exports both the new CCDB dataset and an MSA-level Albouy climate file.

import pandas as pd
import numpy as np
import scipy.stats  # kept for completeness
import warnings

warnings.filterwarnings("ignore")

gams_python_path = "/Library/Frameworks/GAMS.framework/Resources/apifiles/Python/gams"

# =============================================================================
# 1. Load base lookup files and core inputs
# =============================================================================

# Manual 2019 MSA lookup (used later as "lookup")
lookup = pd.read_excel("/Users/hannahkamen/Downloads/msa_2019_lookup.xlsx")

# 2013 CBSA county file (for completeness; not used downstream in this cleaned script)
cbsa = pd.read_excel(
    "/Users/hannahkamen/Downloads/msa_county_2013.xlsx",
    converters={
        "FIPS State Code": str,
        "FIPS County Code": str,
        "CSA Code": str,
    },
)
cbsa["msa_name"] = cbsa["CBSA Title"].str.lower()

# Population and race (2019 ACS, CCDB-format)
pop_race = pd.read_csv(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/pop_race2019.csv"
)

# ACS 2015–2019 microdata summary (already processed to tract/msa level)
acs = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/acs5yr2019.dta"
)

# Crime files (FBI)
crime2019 = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/crime_fbi_2019.xlsx"
)
crime2018 = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/crime_fbi_2018.xlsx"
)
crime2017 = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/crime_fbi_2017.xls"
)
crime2015 = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/crime_fbi_2015.xls"
)

# Manufacturing data (QCEW singlefile)
manu = pd.read_csv(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/2019.annual.singlefile.csv"
)

# Federal spending by state
fed_spend = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/federal_spending.xlsx"
)

# State population (for diagnostics; not directly used in core output)
pop_race_state = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/state_pop_2019.xlsx"
)

# =============================================================================
# 2. Virtual MSA construction in ACS (met2013)
#    Only the active WY, SD, MT rules are retained here
# =============================================================================

acs["met2013"] = np.where(
    acs["met2013"].isin(["Non-metro, WY", "Casper, WY", "Cheyenne, WY"]),
    "WY Virtual MSA, WY",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"].isin(["Not in identifiable area"]) & (acs["statefip"] == "Wyoming")),
    "WY Virtual MSA, WY",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(["Rapid City, SD", "Non-metro, SD", "Sioux Falls, SD"]),
    "SD Virtual MSA, SD",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"].isin(["Not in identifiable area"]) & (acs["statefip"] == "South Dakota")),
    "SD Virtual MSA, SD",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(
        ["Non-metro, MT", "Great Falls, MT", "Billings, MT", "Missoula, MT"]
    ),
    "MT Virtual MSA, MT",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"].isin(["Not in identifiable area"]) & (acs["statefip"] == "Montana")),
    "MT Virtual MSA, MT",
    acs["met2013"],
)

# =============================================================================
# 3. Crime data: clean and build per-capita measures, then append across years
# =============================================================================

def clean_crime_msa(series: pd.Series) -> pd.Series:
    s = (
        series.astype(str)
        .str.replace(r"\d+", "", regex=True)
        .str.lower()
        .str.replace(" m.s.a.", "", regex=False)
        .str.replace(" m.d.", "", regex=False)
        .str.replace("M.S.A.", "", regex=False)
        .str.replace(" m.s.a", "", regex=False)
        .str.replace(", , ,", "", regex=False)
        .str.strip()
        .str.rstrip(",")
    )
    return s


def build_crime_per_cap(df_raw: pd.DataFrame, washington_pattern: str) -> pd.DataFrame:
    """Construct crime per capita at MSA level from a raw FBI file."""
    df = df_raw.copy()
    df = df[df["Metropolitan Statistical Area"] != washington_pattern]
    df["msa_clean"] = clean_crime_msa(df["Metropolitan Statistical Area"])

    # Population by MSA
    crime_pop = df[~df["msa_clean"].isnull()][["Population", "msa_clean"]]

    # Forward-fill msa_clean for detail rows, then sum crime counts
    df["msa_clean"] = df["msa_clean"].fillna(method="ffill")
    crime_count = df[df["Counties/principal cities"].astype(str).str.contains("actually")]

    crime_cols = [
        "Murder and\nnonnegligent\nmanslaughter",
        "Rape1",
        "Robbery",
        "Aggravated\nassault",
        "Burglary",
        "Larceny-\ntheft",
        "Motor\nvehicle\ntheft",
    ]
    crime_count["total_crime_count"] = crime_count[crime_cols].fillna(0).sum(axis=1)

    crime_count = crime_count[["msa_clean", "total_crime_count"]]
    crime_m = crime_count.merge(crime_pop, on="msa_clean", how="inner")
    crime_m["crime_per_cap"] = crime_m["total_crime_count"] / crime_m["Population"]
    return crime_m[["msa_clean", "total_crime_count", "Population", "crime_per_cap"]]


crime_m1 = build_crime_per_cap(
    crime2019,
    "Washington-Arlington-Alexandria, DC-VA-MD-WV M.D.3, 4",
)
crime_m2 = build_crime_per_cap(
    crime2018,
    "Washington-Arlington-Alexandria, DC-VA-MD-WV M.D.",
)
crime_m3 = build_crime_per_cap(
    crime2017,
    "Washington-Arlington-Alexandria, DC-VA-MD-WV M.D.",
)
crime_m4 = build_crime_per_cap(
    crime2015,
    "Washington-Arlington-Alexandria, DC-VA-MD-WV M.D.",
)

# Append earlier years only where not already present
crime_m = crime_m1.copy()

from_2018 = [x for x in crime_m2["msa_clean"].unique() if x not in crime_m["msa_clean"].unique()]
crime_m = pd.concat(
    [crime_m, crime_m2[crime_m2["msa_clean"].isin(from_2018)]],
    ignore_index=True,
)

from_2017 = [x for x in crime_m3["msa_clean"].unique() if x not in crime_m["msa_clean"].unique()]
crime_m = pd.concat(
    [crime_m, crime_m3[crime_m3["msa_clean"].isin(from_2017)]],
    ignore_index=True,
)

from_2015 = [x for x in crime_m4["msa_clean"].unique() if x not in crime_m["msa_clean"].unique()]
crime_m = pd.concat(
    [crime_m, crime_m4[crime_m4["msa_clean"].isin(from_2015)]],
    ignore_index=True,
)

# Virtual MSAs in crime data
crime_m["msa_clean"] = np.where(
    crime_m["msa_clean"].isin(["billings, mt", "missoula, mt"]),
    "mt virtual msa, mt",
    crime_m["msa_clean"],
)
crime_m["msa_clean"] = np.where(
    crime_m["msa_clean"].isin(["casper, wy", "cheyenne, wy"]),
    "wy virtual msa, wy",
    crime_m["msa_clean"],
)
crime_m["msa_clean"] = np.where(
    crime_m["msa_clean"].isin(["rapid city, sd", "sioux falls, sd"]),
    "sd virtual msa, sd",
    crime_m["msa_clean"],
)

# Collapse within virtual MSAs
crime_m["Population"] = crime_m["Population"].astype(float)
crime_m = crime_m.groupby("msa_clean", as_index=False).sum()
crime_m["crime_per_cap"] = crime_m["total_crime_count"] / crime_m["Population"]
crime_m = crime_m[["msa_clean", "crime_per_cap"]]

# =============================================================================
# 4. Manufacturing data (NAICS 31–33, aggregated to MSA)
# =============================================================================

manu["industry_code_lm"] = manu["industry_code"].astype(str).str.slice(0, 2)
manu_lm = manu[
    ~manu["area_fips"].astype(str).str.contains("[a-zA-Z]")
    & manu["industry_code_lm"].isin(["31", "32", "33"])
].copy()
manu_lm["area_fips"] = manu_lm["area_fips"].astype(int).astype(str)

# FIPS to MSA crosswalk (2019)
fips_lookup = pd.read_excel("/Users/hannahkamen/Downloads/msa_county_2019.xlsx")
fips_lookup = fips_lookup[~fips_lookup["FIPS State Code"].isnull()].copy()

fips_lookup["len_state"] = (
    fips_lookup["FIPS State Code"].astype(int).astype(str).str.len()
)
fips_lookup["len_county"] = (
    fips_lookup["FIPS County Code"].astype(int).astype(str).str.len()
)

fips_lookup["clean_state"] = fips_lookup["FIPS State Code"].astype(int).astype(str)
fips_lookup["clean_county"] = fips_lookup["FIPS County Code"].astype(int).astype(str)

# Construct 5-digit county FIPS
fips_lookup["fips_clean"] = np.where(
    (fips_lookup["len_state"] == 1) & (fips_lookup["len_county"] == 2),
    fips_lookup["clean_state"] + "0" + fips_lookup["clean_county"],
    "",
)
fips_lookup["fips_clean"] = np.where(
    (fips_lookup["len_state"] == 1) & (fips_lookup["len_county"] == 3),
    fips_lookup["clean_state"] + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)

fips_lookup["fips_clean"] = np.where(
    (fips_lookup["len_state"] == 2) & (fips_lookup["len_county"] <= 2),
    fips_lookup["clean_state"] + "0" + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)
fips_lookup["fips_clean"] = np.where(
    (fips_lookup["len_state"] == 2) & (fips_lookup["len_county"] >= 3),
    fips_lookup["clean_state"] + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)

fips_lookup["fips_clean"] = np.where(
    (fips_lookup["len_state"] == 1) & (fips_lookup["len_county"] == 1),
    fips_lookup["clean_state"] + "00" + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)
fips_lookup["fips_clean"] = np.where(
    fips_lookup["len_county"] == 1,
    fips_lookup["clean_state"] + "00" + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)

fips_lookup["fips_clean"] = np.where(
    (fips_lookup["clean_state"].isin(["10", "20", "30", "40", "50"]))
    & (fips_lookup["len_county"] == 1),
    fips_lookup["clean_state"] + "00" + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)
fips_lookup["fips_clean"] = np.where(
    (fips_lookup["clean_state"].isin(["10", "20", "30", "40", "50"]))
    & (fips_lookup["len_county"] == 2),
    fips_lookup["clean_state"] + "0" + fips_lookup["clean_county"],
    fips_lookup["fips_clean"],
)

# Merge manufacturing with county-to-MSA lookup, then aggregate to MSA
manu_m = manu_lm.merge(
    fips_lookup, left_on="area_fips", right_on="fips_clean", how="inner"
)
manu_m = (
    manu_m[["metarea_19", "annual_avg_estabs"]]
    .rename(columns={"metarea_19": "msa_name"})
    .groupby("msa_name", as_index=False)
    .sum()
)

# =============================================================================
# 5. Federal spending by MSA (allocated from state totals using ACS shares)
# =============================================================================

state_lookup = pd.read_excel(
    "/Users/hannahkamen/Downloads/CCDB_updated_vars/state_fips_lookup.xlsx"
)

fed_spend_m = fed_spend.merge(state_lookup, on="state", how="inner")

acs_lm = acs[
    (acs["sample"] == "2015-2019, ACS 5-year")
    & (acs["met2013"] != "Not in identifiable area")
].copy()

state_msa_prop = (
    acs_lm[["met2013", "statefip", "year"]]
    .groupby(["met2013", "statefip"], as_index=False)
    .count()
)

state_msa_prop_tot = (
    acs_lm.groupby("statefip", as_index=False)["year"].count()
    .rename(columns={"year": "year_tot"})
)

state_msa_prop = state_msa_prop.merge(
    state_msa_prop_tot, on="statefip", how="inner"
)
state_msa_prop["prop_msa"] = (
    state_msa_prop["year"] / state_msa_prop["year_tot"]
)

msa_spend = state_msa_prop.merge(
    fed_spend_m, left_on="statefip", right_on="state", how="inner"
)
msa_spend["govt_spend"] = msa_spend["prop_msa"] * msa_spend["federal_spend"]
msa_spend = (
    msa_spend.groupby("met2013", as_index=False)["govt_spend"].sum()
    .rename(columns={"met2013": "msa_name"})
)

# =============================================================================
# 6. Income medians by MSA
# =============================================================================

inc = (
    acs_lm[["met2013", "inctot"]]
    .groupby("met2013", as_index=False)
    .median()
    .rename(columns={"met2013": "msa_name"})
)
inc = inc[inc["msa_name"] != "Not in identifiable area"]

# =============================================================================
# 7. Population, race, and virtual MSAs in population data
# =============================================================================

pop_race = pop_race.rename(
    columns={
        "Geographic Area Name": "msa_name",
        "Estimate!!SEX AND AGE!!Total population": "total_population",
        "Estimate!!RACE!!Total population!!One race!!White": "pop_white",
    }
)

pop_race = pop_race[pop_race["pop_white"] != "N"].copy()

# Virtual MSAs in population data
pop_race["msa_name"] = np.where(
    pop_race["msa_name"].isin(
        [
            "Great Falls, MT Metro Area",
            "Billings, MT Metro Area",
            "Missoula, MT Metro Area",
        ]
    ),
    "mt virtual msa, mt",
    pop_race["msa_name"],
)
pop_race["msa_name"] = np.where(
    pop_race["msa_name"].isin(
        ["Cheyenne, WY Metro Area", "Casper, WY Metro Area"]
    ),
    "wy virtual msa, wy",
    pop_race["msa_name"],
)
pop_race["msa_name"] = np.where(
    pop_race["msa_name"].isin(
        ["Rapid City, SD Metro Area", "Sioux Falls, SD Metro Area"]
    ),
    "sd virtual msa, sd",
    pop_race["msa_name"],
)

pop_race["pop_white"] = pop_race["pop_white"].astype(float)
pop_race = (
    pop_race.groupby("msa_name", as_index=False)[["total_population", "pop_white"]].sum()
)
pop_race["prop_white"] = pop_race["pop_white"] / pop_race["total_population"]
pop_race = pop_race[["msa_name", "total_population", "prop_white"]]

# Correct total population for virtual MSAs where needed
pop_race["total_population"] = np.where(
    pop_race["msa_name"] == "mt virtual msa, mt", 1068778, pop_race["total_population"]
)
pop_race["total_population"] = np.where(
    pop_race["msa_name"] == "sd virtual msa, sd", 884659, pop_race["total_population"]
)
pop_race["total_population"] = np.where(
    pop_race["msa_name"] == "wy virtual msa, wy", 578759, pop_race["total_population"]
)

# =============================================================================
# 8. Prepare 2019 MSA lookup for string-based matching
# =============================================================================

lookup = lookup.copy()
lookup.loc[len(lookup.index)] = ["WY Virtual MSA, WY", ""]
lookup.loc[len(lookup.index)] = ["SD Virtual MSA, SD", ""]
lookup.loc[len(lookup.index)] = ["MT Virtual MSA, MT", ""]
lookup["metarea_19"] = lookup["metarea_19"].str.lower()
lookup = lookup[lookup["metarea_19"] != "not in identifiable area"].copy()
lookup["metarea_07_lookup"] = lookup["metarea_07_lookup"].fillna("")

# =============================================================================
# 9. City/state matching between data MSAs and 2019 lookup
# =============================================================================

datasets = [pop_race, crime_m, manu_m, msa_spend, inc]
patterns_to_strip = [" metro area", " micro area", " m.d.", " m.s.a", "met2013"]

for df in datasets:
    # Base string cleaning for city and state
    df["msa_name"] = df["msa_name"].astype(str)
    df["msa_city"] = (
        df["msa_name"]
        .str.lower()
        .apply(lambda x: x.split(",")[0])
        .str.replace("|".join(patterns_to_strip), "", regex=True)
        .str.strip()
        .str.replace("--", "-")
    )
    df["state"] = (
        df["msa_name"]
        .str.lower()
        .apply(lambda x: x.split(",")[1])
        .str.replace("|".join(patterns_to_strip), "", regex=True)
        .str.strip()
        .str.replace("--", "-")
    )
    df["city_list"] = df["msa_city"].apply(lambda x: x.split("-"))
    df["state_list"] = df["state"].apply(lambda x: x.split("-"))

# Precompute lookup city/state lists
lookup["msa_city"] = (
    lookup["metarea_19"]
    .str.lower()
    .apply(lambda x: x.split(",")[0])
    .str.replace("|".join(patterns_to_strip), "", regex=True)
    .str.strip()
    .str.replace("--", "-")
)
lookup["state"] = (
    lookup["metarea_19"]
    .str.lower()
    .apply(lambda x: x.split(",")[1])
    .str.replace("|".join(patterns_to_strip), "", regex=True)
    .str.strip()
    .str.replace("--", "-")
)
lookup["city_list"] = lookup["msa_city"].apply(lambda x: x.split("-"))
lookup["state_list"] = lookup["state"].apply(lambda x: x.split("-"))

def attach_city_state_matches(df: pd.DataFrame, lookup_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["city_match"] = ""
    df["state_match"] = ""

    # Brute-force loop over city/state combinations
    for idx1, row1 in lookup_df.iterrows():
        for city1 in row1["city_list"]:
            for state1 in row1["state_list"]:
                mask = (
                    df["city_list"].apply(lambda lst: city1 in lst)
                    & df["state_list"].apply(lambda lst: state1 in lst)
                )
                df.loc[mask, "city_match"] = str(row1["city_list"])
                df.loc[mask, "state_match"] = str(row1["state_list"])

    # Convert list-like strings to standardized keys
    df["city_match_str"] = (
        df["city_match"]
        .astype(str)
        .str.replace("]", "")
        .str.replace("[", "")
        .str.replace(",", "-")
        .str.replace("'", "")
        .str.replace("- ", "-")
    )
    df["state_match_str"] = (
        df["state_match"]
        .astype(str)
        .str.replace("]", "")
        .str.replace("[", "")
        .str.replace(",", "-")
        .str.replace("'", "")
        .str.replace("- ", "-")
    )

    return df


# Standardized keys for lookup as well
lookup["city_match_str"] = (
    lookup["city_list"]
    .astype(str)
    .str.replace("]", "")
    .str.replace("[", "")
    .str.replace(",", "-")
    .str.replace("'", "")
    .str.replace("- ", "-")
)
lookup["state_match_str"] = (
    lookup["state_list"]
    .astype(str)
    .str.replace("]", "")
    .str.replace("[", "")
    .str.replace(",", "-")
    .str.replace("'", "")
    .str.replace("- ", "-")
)

pop_race = attach_city_state_matches(pop_race, lookup)
crime_m = attach_city_state_matches(crime_m, lookup)
manu_m = attach_city_state_matches(manu_m, lookup)
msa_spend = attach_city_state_matches(msa_spend, lookup)
inc = attach_city_state_matches(inc, lookup)

# =============================================================================
# 10. Merge all non-climate MSA-level datasets into a single table
# =============================================================================

# Population and race first
master1 = lookup.merge(
    pop_race,
    on=["city_match_str", "state_match_str"],
    how="left",
    indicator=True,
)
dropped1 = master1[master1["_merge"] == "left_only"]["metarea_19"].unique()
master1 = master1[master1["_merge"] == "both"].drop(columns="_merge")

# Crime fixes for naming inconsistencies before merge
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "raleigh-cary, nc", "raleigh, nc"
)
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "sacramento–roseville–arden-arcade, ca",
    "sacramento--roseville--arden-arcade, ca",
)
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "scranton–wilkes-barre–hazleton, pa",
    "scranton--wilkes-barre--hazleton, pa",
)
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "nashville-davidson–murfreesboro–franklin, tn",
    "nashville-davidson--murfreesboro--franklin, tn",
)
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "fayetteville-springdale-rogers, ar",
    "fayetteville-springdale-rogers, ar-mo",
)
crime_m["msa_name"] = crime_m["msa_name"].str.replace(
    "blacksburg-christiansburg, va", "blacksburg-christiansburg-radford, va"
)

# Attach crime
master2 = master1.merge(
    crime_m[["msa_name", "crime_per_cap"]],
    left_on="metarea_19",
    right_on="msa_name",
    how="left",
    indicator=True,
)
dropped2 = master2[master2["_merge"] == "left_only"]["metarea_19"].unique()
master2 = master2[master2["_merge"] == "both"].drop(columns=["_merge", "msa_name"])

# Attach manufacturing
master3 = master2.merge(manu_m, on=["city_match_str", "state_match_str"], how="left", indicator=True)
dropped3 = master3[master3["_merge"] == "left_only"]["metarea_19"].unique()
master3 = master3[master3["_merge"] == "both"].drop(columns="_merge")

# Attach government spending
master4 = master3.merge(
    msa_spend, on=["city_match_str", "state_match_str"], how="left", indicator=True
)
dropped4 = master4[master4["_merge"] == "left_only"]["metarea_19"].unique()
master4 = master4[master4["_merge"] == "both"].drop(columns="_merge")

# Attach income
master5 = master4.merge(
    inc, on=["city_match_str", "state_match_str"], how="left", indicator=True
)
dropped5 = master5[master5["_merge"] == "left_only"]["metarea_19"].unique()
master5 = master5[master5["_merge"] == "both"].drop(columns="_merge")

# Build final CCDB-style MSA table (non-climate)
master_lm = master5[
    [
        "metarea_19",
        "metarea_07_lookup",
        "total_population",
        "prop_white",
        "crime_per_cap",
        "annual_avg_estabs",
        "govt_spend",
        "inctot",
    ]
].copy()

master_lm["crime_per_cap"] = master_lm["crime_per_cap"].astype(float)
master_lm = master_lm.rename(columns={"metarea_19": "metarea"})
master_lm["gov_per_cap"] = master_lm["govt_spend"] / master_lm["total_population"]

# Drop missing or zero spending and non-continental MSAs
master_lm = master_lm[
    (master_lm["govt_spend"] != 0)
    & ~master_lm["govt_spend"].isnull()
]
master_lm = master_lm[
    ~master_lm["metarea"].str.contains("|".join([", ak", ", hi"]))
]

# Final renaming to match CCDB conventions
master_lm = master_lm.rename(
    columns={
        "total_population": "population",
        "crime_per_cap": "pccrime",
        "inctot": "median_income",
        "annual_avg_estabs": "manuf_est",
        "govt_spend": "gvtexpend",
    }
)

print(len(master_lm["metarea"].unique()))
print(len(dropped1), len(dropped2), len(dropped3), len(dropped4), len(dropped5))

master_lm.to_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/new_ccdb.dta",
    write_index=False,
)

# =============================================================================
# 11. Albouy climate data: diagnostics and MSA-level aggregation
# =============================================================================

puma_lkup = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/msa2013_puma2000.dta"
)
albuoy = pd.read_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/albouy_all.dta"
)

# Create virtual MSAs in Albouy data via PUMAID recode
albuoy["PumaID"] = np.where(albuoy["msaname"] == "Non-metro, NH", 996, albuoy["PumaID"])
albuoy["PumaID"] = np.where(
    albuoy["msaname"].isin(["Non-metro, VT", "Burlington, VT"]),
    997,
    albuoy["PumaID"],
)
albuoy["PumaID"] = np.where(
    albuoy["msaname"].isin(["Non-metro, WV", "Charleston, WV"]),
    998,
    albuoy["PumaID"],
)
albuoy["PumaID"] = np.where(
    albuoy["msaname"].isin(["Non-metro, WY", "Casper, WY", "Cheyenne, WY"]),
    999,
    albuoy["PumaID"],
)
albuoy["PumaID"] = np.where(
    albuoy["msaname"] == "Non-metro, ND", 1000, albuoy["PumaID"]
)
albuoy["PumaID"] = np.where(
    albuoy["msaname"].isin(["Rapid City, SD", "Non-metro, SD", "Sioux Falls, SD"]),
    1001,
    albuoy["PumaID"],
)
albuoy["PumaID"] = np.where(
    albuoy["msaname"].isin(
        ["Non-metro, MT", "Great Falls, MT", "Billings, MT", "Missoula, MT"]
    ),
    1002,
    albuoy["PumaID"],
)

# Collapse to PUMAID × statefip averages
albuoy = albuoy.groupby(["PumaID", "statefip"], as_index=False).mean()

# Restrict PUMA lookup and append virtual MSAs
puma_lkup = puma_lkup[
    ["met2013", "msaname_crosswalk", "statefip", "statename", "pctmsapop", "PumaID"]
].copy()
puma_lkup.loc[len(puma_lkup.index)] = [996, "NH Virtual MSA, NH", 33, "New Hampshire", 100, 996]
puma_lkup.loc[len(puma_lkup.index)] = [997, "VT Virtual MSA, VT", 50, "Vermont", 100, 997]
puma_lkup.loc[len(puma_lkup.index)] = [998, "WV Virtual MSA, WV", 54, "West Virginia", 100, 998]
puma_lkup.loc[len(puma_lkup.index)] = [999, "WY Virtual MSA, WY", 56, "Wyoming", 100, 999]
puma_lkup.loc[len(puma_lkup.index)] = [1000, "ND Virtual MSA, ND", 38, "North Dakota", 100, 1000]
puma_lkup.loc[len(puma_lkup.index)] = [1001, "SD Virtual MSA, SD", 46, "South Dakota", 100, 1001]
puma_lkup.loc[len(puma_lkup.index)] = [1002, "MT Virtual MSA, MT", 30, "Montana", 100, 1002]

puma_lkup["msaname_crosswalk_l"] = puma_lkup["msaname_crosswalk"].str.lower()

# Proportion of each MSA in each state using ACS (met2013 × statefip shares)
acs["met2013"] = np.where(
    acs["met2013"] == "Manchester-Nashua, NH", "NH Virtual MSA, NH", acs["met2013"]
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "New Hampshire"),
    "NH Virtual MSA, NH",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(["Burlington-South Burlington, VT", "Burlington, VT"]),
    "VT Virtual MSA, VT",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "Vermont"),
    "VT Virtual MSA, VT",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(
        ["Charleston, WV", "Morgantown, WV", "Parkersburg-Vienna, WV"]
    ),
    "WV Virtual MSA, WV",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "West Virginia"),
    "WV Virtual MSA, WV",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(["Non-metro, WY", "Casper, WY", "Cheyenne, WY"]),
    "WY Virtual MSA, WY",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "Wyoming"),
    "WY Virtual MSA, WY",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"] == "Bismarck, ND", "ND Virtual MSA, ND", acs["met2013"]
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "North Dakota"),
    "ND Virtual MSA, ND",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(["Rapid City, SD", "Non-metro, SD", "Sioux Falls, SD"]),
    "SD Virtual MSA, SD",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "South Dakota"),
    "SD Virtual MSA, SD",
    acs["met2013"],
)

acs["met2013"] = np.where(
    acs["met2013"].isin(
        ["Non-metro, MT", "Great Falls, MT", "Billings, MT", "Missoula, MT"]
    ),
    "MT Virtual MSA, MT",
    acs["met2013"],
)
acs["met2013"] = np.where(
    (acs["met2013"] == "Not in identifiable area") & (acs["statefip"] == "Montana"),
    "MT Virtual MSA, MT",
    acs["met2013"],
)

prop_msa_state = (
    acs[["met2013", "statefip", "year"]]
    .groupby(["met2013", "statefip"], as_index=False)
    .count()
)
prop_msa_state_tot = (
    acs.groupby("met2013", as_index=False)["year"]
    .count()
    .rename(columns={"year": "year_tot"})
)

prop_msa_state = prop_msa_state.merge(
    prop_msa_state_tot, on="met2013", how="inner"
)
prop_msa_state["prop_state_in_msa"] = (
    prop_msa_state["year"] / prop_msa_state["year_tot"]
)

prop_msa_state_lm = prop_msa_state[prop_msa_state["prop_state_in_msa"] > 0].copy()
prop_msa_state_lm["msaname_crosswalk_l"] = prop_msa_state_lm["met2013"].str.lower()
prop_msa_state_lm = prop_msa_state_lm.rename(columns={"statefip": "statename"})

# Merge Albouy climate with PUMA lookup
albuoy_updated = albuoy.merge(puma_lkup, on=["PumaID", "statefip"])
albuoy_updated["propmsapop"] = albuoy_updated["pctmsapop"] / 100.0

# First stage: weight by PUMA share of MSA population
for col in albuoy_updated.columns:
    if col not in [
        "statefip",
        "PumaID",
        "msa",
        "msaname",
        "BootstrapMSA",
        "BootstrapState",
        "met2013",
        "msaname_crosswalk",
        "statename",
        "pctmsapop",
        "pctpumapop",
        "dup",
        "msaname_crosswalk_l",
        "propmsapop",
    ]:
        try:
            albuoy_updated[f"{col}_adj"] = albuoy_updated[col] * albuoy_updated["propmsapop"]
        except Exception:
            pass

name_vars = ["msaname_crosswalk_l", "met2013", "statefip", "statename"]
num_vars = [x for x in albuoy_updated.columns if x.endswith("_adj")]

albuoy_updated_lm = albuoy_updated[name_vars + num_vars]
albuoy_gr = albuoy_updated_lm.groupby(name_vars, as_index=False).sum()

# Second stage: weight by share of MSA in each state
albuoy_gr = albuoy_gr.merge(
    prop_msa_state_lm[["msaname_crosswalk_l", "statename", "prop_state_in_msa"]],
    on=["msaname_crosswalk_l", "statename"],
    how="inner",
)

for col in albuoy_gr.columns:
    if col not in ["msaname_crosswalk_l", "met2013", "statefip", "statename", "prop_state_in_msa"]:
        try:
            albuoy_gr[f"{col}_2"] = albuoy_gr[col] * albuoy_gr["prop_state_in_msa"]
        except Exception:
            pass

name_vars2 = ["msaname_crosswalk_l", "met2013", "statefip", "statename"]
num_vars2 = [x for x in albuoy_gr.columns if x.endswith("_adj_2")]

albuoy_gr2 = albuoy_gr[name_vars2 + num_vars2]
albuoy_gr2 = albuoy_gr2.groupby(["msaname_crosswalk_l", "met2013"], as_index=False).sum()
albuoy_gr2 = albuoy_gr2.rename(columns={"msaname_crosswalk_l": "metarea"})

# Strip suffix to recover original names
albuoy_gr2.columns = [c.replace("_adj_2", "") for c in albuoy_gr2.columns]

albuoy_gr2.to_stata(
    "/Users/hannahkamen/Documents/population-migration2/dta/albuoy_all_msa_level.dta",
    write_index=False,
)
