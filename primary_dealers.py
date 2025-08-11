### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import datetime
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import functools as ft
import requests
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
### ----------------------------------- SPONSORED VOLUMES - THE SOLUTION? ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### OFR DATA PULLS ###
# https://www.dtcc.com/charts/membership - note that we need paid account to pull in the data

sponsored_volume = pd.read_csv('data/SponsoredVolume.csv').dropna()
sponsored_volume = sponsored_volume.iloc[::-1].reset_index(drop=True)
sponsored_volume.index = pd.to_datetime(sponsored_volume['BUSINESS_DATE'].values)
sponsored_volume = sponsored_volume.drop('BUSINESS_DATE',axis=1)
sponsored_volume.columns
sponsored_volume['DVP_TOTAL_AMOUNT'] = (
    sponsored_volume['DVP_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
sponsored_volume['GC_TOTAL_AMOUNT'] = (
    sponsored_volume['GC_TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
sponsored_volume['TOTAL_REPO_AMOUNT'] = (
    sponsored_volume['TOTAL_REPO_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
sponsored_volume['TOTAL_REVERSE_REPO_AMOUNT'] = (
    sponsored_volume['TOTAL_REVERSE_REPO_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))
sponsored_volume['TOTAL_AMOUNT'] = (
    sponsored_volume['TOTAL_AMOUNT'].replace('[\$,]', '', regex=True).astype(float))


### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(sponsored_volume.index, sponsored_volume['DVP_TOTAL_AMOUNT'],
         label='DVP Sponsored', color='#4CD0E9', lw=2)  # cyan
plt.plot(sponsored_volume.index, sponsored_volume['GC_TOTAL_AMOUNT'],
         label='GC Sponsored', color='#233852', lw=2)  # dark blue
plt.ylabel("Trillions")
plt.title("Sponsored Volumes - The Solutions?", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------- SPONSORED VOLUMES -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
base_url = 'https://data.financialresearch.gov/hf/v1/series/full?mnemonic='

sponsored_repo_json = pd.DataFrame(requests.get(base_url + 'FICC-SPONSORED_REPO_VOL').json())
sponsored_repo_volume = sponsored_repo_json['FICC-SPONSORED_REPO_VOL']['timeseries']['aggregation']
sponsored_repo_volume = pd.DataFrame(sponsored_repo_volume, columns=["date", "Value"])
sponsored_repo_volume['date'] = pd.to_datetime(sponsored_repo_volume['date'])
sponsored_repo_volume.index = sponsored_repo_volume['date'].values
sponsored_repo_volume.drop('date', axis=1, inplace=True)

sponsored_rrp_json = pd.DataFrame(requests.get(base_url + 'FICC-SPONSORED_REVREPO_VOL').json())
sponsored_rrp_volume = sponsored_rrp_json['FICC-SPONSORED_REVREPO_VOL']['timeseries']['aggregation']
sponsored_rrp_volume = pd.DataFrame(sponsored_rrp_volume, columns=["date", "Value"])
sponsored_rrp_volume['date'] = pd.to_datetime(sponsored_rrp_volume['date'])
sponsored_rrp_volume.index = sponsored_rrp_volume['date'].values
sponsored_rrp_volume.drop('date', axis=1, inplace=True)

sponsored_repo_rrp_merge = merge_dfs([sponsored_repo_volume,sponsored_rrp_volume])
sponsored_repo_rrp_merge.columns = ['sponsored_repo','sponsored_rrp']

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(sponsored_repo_rrp_merge.index, sponsored_repo_rrp_merge['sponsored_repo'],
         label='Repo Sponsored', color='#4CD0E9', lw=2)  # cyan
plt.plot(sponsored_repo_rrp_merge.index, sponsored_repo_rrp_merge['sponsored_rrp'],
         label='RRP Sponsored', color='#233852', lw=2)  # dark blue
plt.ylabel("Trillions")
plt.title("Sponsored Volumes", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- % OF DVP VOLUME THAT IS SPONSORED ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###






### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(sponsored_repo_rrp_merge.index, sponsored_repo_rrp_merge['sponsored_repo'],
         label='Repo Sponsored', color='#4CD0E9', lw=2)  # cyan
plt.ylabel("Trillions")
plt.title("Sponsored Volumes", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ PRIMARY DEALERS NET POSITIONS BILLS VS BONDS ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###







### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- PRIMARY DEALERS NET POSITIONS BY BOND TENOR ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###









### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- PRIMARY DEALERS --------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###



