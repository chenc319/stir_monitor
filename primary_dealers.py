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
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
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
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- % OF DVP VOLUME THAT IS SPONSORED ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

dvp_volume = pd.DataFrame(requests.get(base_url + 'REPO-DVP_TV_TOT-P').json(), columns=["date", "value"])
dvp_volume['date'] = pd.to_datetime(dvp_volume['date'])
dvp_volume.index = dvp_volume['date'].values
dvp_volume.drop('date', axis=1, inplace=True)
dvp_sponsored_volume = pd.DataFrame(sponsored_volume['DVP_TOTAL_AMOUNT'])

dvp_merge = merge_dfs([dvp_sponsored_volume,dvp_volume]).dropna()
dvp_merge.columns = ['dvp_sponsored','total_dvp']
dvp_merge['pct'] = dvp_merge['dvp_sponsored'] / dvp_merge['total_dvp']

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(dvp_merge.index, dvp_merge['pct'],
         color='#4CD0E9', lw=2)  # cyan
plt.ylabel("%")
plt.title("% of DVP that is Sponsored", fontsize=17, fontweight="bold")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ PRIMARY DEALERS NET POSITIONS BILLS VS BONDS ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bills = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-B.json'
coupon_2 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2.json'
coupon_2_3 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3.json'
coupon_3_6 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6.json'
coupon_6_7 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7.json'
coupon_7_11 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11.json'
coupon_11_21 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21.json'
coupon_21 = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21.json'

urls = [bills,coupon_2,coupon_2_3,coupon_3_6,coupon_6_7,coupon_7_11,coupon_11_21,coupon_21]
column_names = ['bills','l2','g2l3','g3l6','g6l7','g7l11','g11l21','g21']
all_bills_bonds_pos_merge = pd.DataFrame()
for idx in range(0,len(urls)):
    pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
    pos['value'] = pd.to_numeric(pos['value'], errors='coerce') / 1e3
    pos.dropna(subset=['value'], inplace=True)
    pos['asofdate'] = pd.to_datetime(pos['asofdate'])
    pos.index = pos['asofdate'].values
    pos.drop('asofdate', axis=1, inplace=True)
    pos.columns = [column_names[idx]]
    all_bills_bonds_pos_merge = merge_dfs([all_bills_bonds_pos_merge,pos])

all_bills_bonds_pos_merge.dropna()
all_bills_bonds_pos_merge['net_nominal_bonds'] = (
    all_bills_bonds_pos_merge['l2'] +
    all_bills_bonds_pos_merge['g2l3'] +
    all_bills_bonds_pos_merge['g3l6'] +
    all_bills_bonds_pos_merge['g6l7'] +
    all_bills_bonds_pos_merge['g7l11']
)

### PLOT ###
plt.figure(figsize=(13,7))
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['bills'],
         label='Bills', color='#43c4e6', linewidth=2)
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['net_nominal_bonds'],
         label='Net Nominal Bonds', color='#262e39', linewidth=2)
plt.title("Primary Dealers Net Positions Bills VS Bonds", fontsize=20, fontweight="bold")
plt.ylabel("Billions")
plt.xlabel("")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.grid(True, which='major', linestyle='-', color='grey', alpha=0.3)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- PRIMARY DEALERS NET POSITIONS BY BOND TENOR ------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### PLOT ###
plt.figure(figsize=(12,7))
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['l2'],
         label='Bond <2Y', color='#9DDCF9')
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['g2l3'],
         label='Bond 2-3Y', color='#4CD0E9')
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['g3l6'],
         label='Bond 3-6Y', color='#233852')
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['g6l7'],
         label='Bond 6-7Y', color='#F5B820', linewidth=2)
plt.plot(all_bills_bonds_pos_merge.index, all_bills_bonds_pos_merge['g7l11'],
         label='Bond 7-10Y', color='#E69B93')
plt.ylabel("Billions")
plt.title("Primary Dealers Net Positions By Bond Tenor", fontsize=20, fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ ADDITIONAL DATA AND IMPROVEMENTS ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bills_c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-BC.json'
coupon_2c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2C.json'
coupon_2_3c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3C.json'
coupon_3_6c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6C.json'
coupon_6_7c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7C.json'
coupon_7_11c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11C.json'
coupon_11_21c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21C.json'
coupon_21c = 'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21C.json'


urls = [bills_c,coupon_2c,coupon_2_3c,coupon_3_6c,
        coupon_6_7c,coupon_7_11c,coupon_11_21c,coupon_21c]
column_names = ['bills','l2','g2l3','g3l6','g6l7','g7l11','g11l21','g21']
all_bills_bonds_change_merge = pd.DataFrame()
for idx in range(0,len(urls)):
    pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
    pos['value'] = pd.to_numeric(pos['value'], errors='coerce')
    pos.dropna(subset=['value'], inplace=True)
    pos['asofdate'] = pd.to_datetime(pos['asofdate'])
    pos.index = pos['asofdate'].values
    pos.drop('asofdate', axis=1, inplace=True)
    pos.columns = [column_names[idx]]
    all_bills_bonds_change_merge = merge_dfs([all_bills_bonds_change_merge,pos])
all_bills_bonds_change_merge = all_bills_bonds_change_merge.dropna()

### PLOT ###
plt.figure(figsize=(12,7))
plt.plot(all_bills_bonds_change_merge.index, all_bills_bonds_change_merge['l2'],
         label='Bond <2Y', color='#9DDCF9')
plt.plot(all_bills_bonds_change_merge.index, all_bills_bonds_change_merge['g2l3'],
         label='Bond 2-3Y', color='#4CD0E9')
plt.plot(all_bills_bonds_change_merge.index, all_bills_bonds_change_merge['g3l6'],
         label='Bond 3-6Y', color='#233852')
plt.plot(all_bills_bonds_change_merge.index, all_bills_bonds_change_merge['g6l7'],
         label='Bond 6-7Y', color='#F5B820', linewidth=2)
plt.plot(all_bills_bonds_change_merge.index, all_bills_bonds_change_merge['g7l11'],
         label='Bond 7-10Y', color='#E69B93')
plt.ylabel("Billions")
plt.title("Primary Dealers Net Position Change By Bond Tenor", fontsize=20, fontweight='bold')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()


