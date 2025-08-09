### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- CASH -------------------------------------------------- ###
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
### --------------------------------------------------- TGA -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
tga_volume = pdr.DataReader('WTREGEN', 'fred', start, end) / 1e3
tga_volume.index = pd.to_datetime(tga_volume.index.values)
tga_roc = tga_volume.resample('W').last().diff(1)
tga_roc.columns = ['TGA ROC']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(tga_roc.index, tga_roc['TGA ROC'],
         label='TGA Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('TGA', fontweight='bold')
plt.legend(loc='best')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------------------- RRP -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) / 1e6
rrp_volume.index = pd.to_datetime(rrp_volume.index.values)
rrp_roc = rrp_volume.resample('W').last().diff(1)
rrp_roc.columns = ['RRP ROC']

### PLOT ###
plt.figure(figsize=(7, 6))
plt.plot(rrp_roc.index, rrp_roc['RRP ROC'],
         label='RRP Weekly ROC', color='#07AFE3', linewidth=2)
plt.title('RRP', fontweight='bold')
plt.legend(loc='best')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- TOTAL BANKING RESERVES ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

tri_volume = pd.DataFrame(requests.get(base_url + 'REPO-TRI_TV_TOT-P').json(), columns=["date", "value"])
tri_volume['date'] = pd.to_datetime(tri_volume['date'])
tri_volume.index = tri_volume['date'].values
tri_volume.drop('date', axis=1, inplace=True)
tri_volume = tri_volume / 1e12

dvp_volume = pd.DataFrame(requests.get(base_url + 'REPO-DVP_TV_TOT-P').json(), columns=["date", "value"])
dvp_volume['date'] = pd.to_datetime(dvp_volume['date'])
dvp_volume.index = dvp_volume['date'].values
dvp_volume.drop('date', axis=1, inplace=True)
dvp_volume = dvp_volume / 1e12

gcf_volume = pd.DataFrame(requests.get(base_url + 'REPO-GCF_TV_TOT-P').json(), columns=["date", "value"])
gcf_volume['date'] = pd.to_datetime(gcf_volume['date'])
gcf_volume.index = gcf_volume['date'].values
gcf_volume.drop('date', axis=1, inplace=True)
gcf_volume = gcf_volume / 1e12


### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- 6M CASH RATE OF CHANGE ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###





### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ MMF REPO VS NON REPO ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###






### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ ASSET ALLOCATION MMF ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###






### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------- RESERVES NON FED REPO + RESERRVES + RRP -------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###








### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- RESERVES LIABILITIES OF THE SYSTEM ----------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###







