#!/usr/bin/env python
# coding: utf-8

# process housing supply elasticities for use in Windc from Saiz 2010

#!/usr/bin/env python
# coding: utf-8

"""
Build a housing elasticity lookup table.

1. use from raw text blocks (e1, e2) containing metro names and elasticities. This is only available output from paper
2. Parse each block into three columns:
   - state (token 0 in each split chunk)
   - elasticity (token 1 in each split chunk)
   - city (all remaining tokens, from position 3 onward)
   NOTE: This relies on the specific spacing/formatting of e1 and e2.
3. Concatenate the two parsed tables and export to Excel (`elasticity_lookup.xlsx`)
   for manual cleanup.
4. Read the cleaned file (`elasticity_lookup_final.xlsx`), get the minimum elasticity
   per metro, rename variables, round the elasticity, and export a final CSV.
"""

import numpy as np
import pandas as pd

# ============================================================
# 1. Raw text blocks from the source
# ============================================================

e1 = (
    "1 Miami, FL 0.60 26 Vallejo–Fairfield–Napa, CA 1.14 "
    "2 Los Angeles–Long Beach, CA 0.63 27 Newark, NJ 1.16 "
    "3 Fort Lauderdale, FL 0.65 28 Charleston–North Charleston, SC 1.20 "
    "4 San Francisco, CA 0.66 29 Pittsburgh, PA 1.20 "
    "5 San Diego, CA 0.67 30 Tacoma, WA 1.21 "
    "6 Oakland, CA 0.70 31 Baltimore, MD 1.23 "
    "7 Salt Lake City–Ogden, UT 0.75 32 Detroit, MI 1.24 "
    "8 Ventura, CA 0.75 33 Las Vegas, NV–AZ 1.39 "
    "9 New York, NY 0.76 34 Rochester, NY 1.40 "
    "10 San Jose, CA 0.76 35 Tucson, AZ 1.42 "
    "11 New Orleans, LA 0.81 36 Knoxville, TN 1.42 "
    "12 Chicago, IL 0.81 37 Jersey City, NJ 1.44 "
    "13 Norfolk–Virginia Beach–Newport, VA-NC 0.82 38 Minneapolis–St. Paul, MN–WI 1.45 News, VA–NC "
    "14 West Palm Beach–Boca Raton, FL 0.83 39 Hartford, CT 1.50 "
    "15 Boston–Worcester–Lawrence–Lowell–, MA 0.86 40 Springfield, MA 1.52 Brockton, MA–NH "
    "16 Seattle–Bellevue–Everett, WA 0.88 41 Denver, CO 1.53 "
    "17 Sarasota–Bradenton, FL 0.92 42 Providence–Warwick–Pawtucket, RI 1.61 "
    "18 Riverside–San Bernardino, CA 0.94 43 Washington, DC–MD–VA–WV 1.61 "
    "19 New Haven–Bridgeport–Stamford, CT 0.98 44 Phoenix–Mesa, AZ 1.61 Danbury–Waterbury, CT "
    "20 Tampa–St. Petersburg–Clearwater, FL 1.00 45 Scranton–Wilkes-Barre–Hazleton, PA 1.62 "
    "21 Cleveland–Lorain–Elyria, OH 1.02 46 Harrisburg–Lebanon–Carlisle, PA 1.63 "
    "22 Milwaukee–Waukesha, WI 1.03 47 Bakersfield, CA 1.64 "
    "23 Jacksonville, FL 1.06 48 Philadelphia, PA–NJ 1.65 "
    "24 Portland–Vancouver, OR–WA 1.07 49 Colorado Springs, CO 1.67 "
    "25 Orlando, FL 1.12 50 Albany–Schenectady–Troy, NY 1.70"
)

e2 = (
    "51 Gary, IN 1.74 74 Atlanta, GA 2.55 "
    "52 Baton Rouge, LA 1.74 75 Akron, OH 2.59 "
    "53 Memphis, TN–AR–MS 1.76 76 Richmond–Petersburg, VA 2.60 "
    "54 Buffalo–Niagara Falls, NY 1.83 77 Youngstown–Warren, OH 2.63 "
    "55 Fresno, CA 1.84 78 Columbia, SC 2.64 "
    "56 Allentown–Bethlehem–Easton, PA 1.86 79 Columbus, OH 2.71 "
    "57 Wilmington–Newark, DE–MD 1.99 80 Greenville–Spartanburg–Anderson, SC 2.71 "
    "58 Mobile, AL 2.04 81 Little Rock–North Little Rock, AR 2.79 "
    "59 Stockton–Lodi, CA 2.07 82 Fort Worth–Arlington, TX 2.80 "
    "60 Raleigh–Durham–Chapel Hill, NC 2.11 83 San Antonio, TX 2.98 "
    "61 Albuquerque, NM 2.11 84 Austin–San Marcos, TX 3.00 "
    "62 Birmingham, AL 2.14 85 Charlotte–Gastonia–Rock Hill, NC–SC 3.09 "
    "63 Dallas, TX 2.18 86 Greensboro–Winston–Salem–High Point, NC 3.10 "
    "64 Syracuse, NY 2.21 87 Kansas City, MO–KS 3.19 "
    "65 Toledo, OH 2.21 88 Oklahoma City, OK 3.29 "
    "66 Nashville, TN 2.24 89 Tulsa, OK 3.35 "
    "67 Ann Arbor, MI 2.29 90 Omaha, NE–IA 3.47 "
    "68 Houston, TX 2.30 91 McAllen–Edinburg–Mission, TX 3.68 "
    "69 Louisville, KY–IN 2.34 92 Dayton–Springfield, OH 3.71 "
    "70 El Paso, TX 2.35 93 Indianapolis, IN 4.00 "
    "71 St. Louis, MO–IL 2.36 94 Fort Wayne, IN 5.36 "
    "72 Grand Rapids–Muskegon–Holland, MI 2.39 95 Wichita, KS 5.45 "
    "73 Cincinnati, OH–KY–IN 2.46"
)

# ============================================================
# 2. Parse each block into state / city / elasticity
# ============================================================

# Split on comma+space first, then split each piece on spaces
tokens1 = [chunk.split(" ") for chunk in e1.split(", ")]
tokens2 = [chunk.split(" ") for chunk in e2.split(", ")]

# City name is everything from position 3 onward
city1 = [tok[3:] for tok in tokens1]
city2 = [tok[3:] for tok in tokens2]

# Build DataFrames
data1 = pd.DataFrame(
    {
        "state": [tok[0] for tok in tokens1],
        "city": city1,
        "elasticity": [tok[1] for tok in tokens1],
    }
)

data2 = pd.DataFrame(
    {
        "state": [tok[0] for tok in tokens2],
        "city": city2,
        "elasticity": [tok[1] for tok in tokens2],
    }
)

# Combine
data = pd.concat([data1, data2], ignore_index=True)

# ============================================================
# 3. Export to Excel for manual cleaning
# ============================================================

data.to_excel("/Users/hannahkamen/Downloads/elasticity_lookup.xlsx", index=False)

# ============================================================
# 4. Read cleaned file, get min elasticity per metro, scale & save
# ============================================================

lookup = pd.read_excel("/Users/hannahkamen/Downloads/elasticity_lookup_final.xlsx")

# Group by the first column (Excel may have kept the original index as "Unnamed: 0")
lookup_gr = lookup.groupby("Unnamed: 0", as_index=False).min()

# Rename and keep a “raw” copy for clarity
lookup_gr = lookup_gr.rename(
    columns={"Unnamed: 0": "", "housing_elasticity": "housing_elasticity_raw"}
)

# Scale / round housing elasticity
lookup_gr["housing_elasticity"] = np.round(
    lookup_gr["housing_elasticity_raw"], 4
)

# Drop the raw column and export sorted by elasticity
lookup_gr = lookup_gr.drop(columns="housing_elasticity_raw")
lookup_gr = lookup_gr.sort_values(by="housing_elasticity", ascending=True)

lookup_gr.to_csv(
    "/Users/hannahkamen/Downloads/elasticity_lookup_final_min.csv",
    index=False,
)

# Optional: inspect in the console
print(lookup_gr)
