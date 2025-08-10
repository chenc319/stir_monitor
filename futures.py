### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FUTURES ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import datetime
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import functools as ft
import requests
from io import StringIO
fred = Fred(api_key='6905137c26f03db5c8c09f70b7839150')

### FUNCTIONS ###
def merge_dfs(array_of_dfs):
    new_df = ft.reduce(lambda left,
                              right: pd.merge(left,
                                                    right,
                                                    left_index=True,
                                                    right_index=True,
                                                    how='outer'), array_of_dfs)
    return(new_df)

### SET DATES ###
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime.today()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- FUTURES LEVERAGE MONEY SHORT -------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO

# Download full CFTC TFF data from Socrata API (Futures Only, all contracts)
url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=60000"
response = requests.get(url)
df = pd.read_csv(StringIO(response.text))

# Normalize contract names, mapping to desired tenor buckets
def contract_bucket(name):
    # Lower and clean up input for robust matching
    n = name.strip().lower()
    if "2 yr" in n or "2-year" in n or "2yr" in n:
        return "2 Year"
    elif "5 yr" in n or "5-year" in n or "5yr" in n:
        return "5 Year"
    elif "ultra 10-yr" in n or "ultra 10 year" in n:
        return "6.5-8 Years"       # Ultra 10-Year approximates 7-year as no direct 7y contract
    elif "7 yr" in n or "7-year" in n or "7yr" in n:
        return "6.5-8 Years"
    elif "10 yr" in n or "10-year" in n or "10yr" in n:
        return "9.5/12-10 Years"
    else:
        return None

df['bucket'] = df['name'].apply(contract_bucket)

df.columns

df['commodity_name']

# Filter to only our 4 buckets of interest and non-null leveraged shorts
df = df[df['bucket'].notnull()]

# Convert dates and relevant columns
df['report_date_as_yyyy_mm_dd'] = pd.to_datetime(df['report_date_as_yyyy_mm_dd'])
df['short_positions_leveraged_money'] = pd.to_numeric(df['short_positions_leveraged_money'], errors='coerce').fillna(0)

# Sum/aggregate by report_date and bucket (works across multiple delivery months)
agg = df.groupby(['report_date_as_yyyy_mm_dd', 'bucket'])['short_positions_leveraged_money'].sum().reset_index()
pivot = agg.pivot(index='report_date_as_yyyy_mm_dd', columns='bucket', values='short_positions_leveraged_money')

# Fill missing dates (weekly data, but ensure alignment)
pivot = pivot.asfreq('W-WED')  # TFF reports as of Tuesday, usually published Friday

# Fill missing values (0 = no position reported)
pivot = pivot.fillna(0)

# Order per visual legend and plot
plot_order = ['2 Year', '6.5-8 Years', '9.5/12-10 Years', '5 Year']
colors = ['#6cbde6', '#8cc4df', '#ffc73b', '#fc9442']   # Match your sample chart's color style

# Make the area/stacked plot
plt.figure(figsize=(13,7))
pivot[plot_order].plot(
    kind='area',
    stacked=True,
    color=colors,
    linewidth=0,
    alpha=0.95,
    ax=plt.gca()
)

plt.title('Futures Leverage Money Short', fontsize=18, fontweight='bold')
plt.ylabel('Face Value Notional')
plt.xlabel('')
plt.legend(plot_order, loc='upper left')
plt.grid(axis='y', color='gray', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.show()








### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------- THE RATES COMPLEX, LEAKY CEILINGS AND SOGGY FLOOR --------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###








### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- END OF QUARTER SPREADS ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###







### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- END OF MONTH SPREADS ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###








### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- IS THE STABILITY LOWER ROC --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###







### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- HOW DID LEVELS CHANGE ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###






