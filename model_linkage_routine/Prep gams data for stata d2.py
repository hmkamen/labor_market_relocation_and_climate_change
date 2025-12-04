{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "c9f40966",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import scipy.stats\n",
    "import math\n",
    "import warnings\n",
    "warnings.filterwarnings(\"ignore\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "fc53e8ad",
   "metadata": {},
   "outputs": [],
   "source": [
    "####msa pop data\n",
    "msa=pd.read_stata('/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610/dta/second_stage_dataset_cl.dta')\n",
    "sl=pd.read_excel('/Users/hannahkamen/Downloads/statelookup2.xlsx')\n",
    "sl=sl.rename(columns={'abbrev':'q'})\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f8f1562b",
   "metadata": {},
   "outputs": [],
   "source": [
    "test=pd.read_stata('/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610/dta/projection_data_age2_0_wbmk_v2.dta')\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "876c56d1",
   "metadata": {},
   "outputs": [],
   "source": [
    "test_gr=test.groupby('statefip',as_index=False).agg({'hot':min,'cold':min,'fexthot_28':min,\n",
    " 'fextcold':min})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0652dca7",
   "metadata": {},
   "outputs": [],
   "source": [
    "test_gr['pct_change_hot']=((test_gr['fexthot_28']-test_gr['hot'])/test_gr['hot'])*100\n",
    "test_gr['pct_change_cold']=((test_gr['fextcold']-test_gr['cold'])/test_gr['cold'])*100"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "783b3bcf",
   "metadata": {},
   "outputs": [],
   "source": [
    "test_gr"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "32b8f1c0",
   "metadata": {},
   "outputs": [],
   "source": [
    "list(test)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "03cd5451",
   "metadata": {},
   "source": [
    "#### (6) re-import GAMS results, merge with pop changes"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "be3b230e",
   "metadata": {},
   "outputs": [],
   "source": [
    "pl_rpt[pl_rpt['unskl']>1.03]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "4d163261",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>region</th>\n",
       "      <th>ph_shock0</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>OH</td>\n",
       "      <td>1.004242</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  region  ph_shock0\n",
       "3     OH   1.004242"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "phou_rpt[phou_rpt['region']=='OH']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4284f820",
   "metadata": {},
   "outputs": [],
   "source": [
    "phou_rpt['ph_shock0'].min()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "5cfc3fbc",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th>skill</th>\n",
       "      <th>region</th>\n",
       "      <th>skl</th>\n",
       "      <th>unskl</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>35</th>\n",
       "      <td>OH</td>\n",
       "      <td>1.000663</td>\n",
       "      <td>1.025465</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "skill region       skl     unskl\n",
       "35        OH  1.000663  1.025465"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pl_rpt[pl_rpt['region']=='OH']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "46cc8c44",
   "metadata": {},
   "outputs": [],
   "source": [
    "###merge all fields\n",
    "\n",
    "r_df=phou_rpt.merge(pl_rpt, on='region')\n",
    "r_df=r_df.rename(columns={'region':'q','ph_shock0':'ph','skl':'pl_skl','unskl':'pl_unskl'})\n",
    "r_df=r_df.merge(sl,on='q')\n",
    "r_df=r_df.rename(columns={'q':'abbrev'})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "72424ff1",
   "metadata": {},
   "outputs": [],
   "source": [
    "r_df.to_stata('/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610/dta/gams_dta1_v2_d2.dta')\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "aca95630",
   "metadata": {},
   "outputs": [],
   "source": [
    "r_df['pl_unskl'].min()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "72aab687",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
