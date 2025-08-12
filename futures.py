### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FUTURES ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import datetime
from fredapi import Fred
from pandas_datareader import data as pdr
import functools as ft
import pandas as pd
import matplotlib.pyplot as plt
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

### DATA PULL ###
url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=60000"
response = requests.get(url)
cftc_all_futures = pd.read_csv(StringIO(response.text))
bonds_cftc_subset = cftc_all_futures[(cftc_all_futures['contract_market_name'] == 'UST 2Y NOTE') |
                                     (cftc_all_futures['contract_market_name'] == 'UST 5Y NOTE') |
                                     (cftc_all_futures['contract_market_name'] == 'UST 10Y NOTE') |
                                     (cftc_all_futures['contract_market_name'] == 'ULTRA UST 10Y')]
bonds_future_leverage_money_short = bonds_cftc_subset[['commodity_name',
                                                       'contract_market_name',
                                                       'report_date_as_yyyy_mm_dd',
                                                       'lev_money_positions_short']]
bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd'] = pd.to_datetime(bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd'])
pivot = bonds_future_leverage_money_short.pivot_table(
    index='report_date_as_yyyy_mm_dd',
    columns='commodity_name',
    values='lev_money_positions_short',
    aggfunc='sum'
)
plt.figure(figsize=(12, 6))
for col in pivot.columns:
    plt.plot(pivot.index, pivot[col], label=col)
plt.title("Leverage Money Short Positions by Treasury Futures Bucket", fontsize=15)
plt.xlabel("Date")
plt.ylabel("Leverage Money Short Positions")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.grid(True)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------- END OF QUARTER SPREADS ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
           'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]

base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
dvp_mnemonic = 'REPO-DVP_AR_OO-P'
gcf_mnemonic = 'REPO-GCF_AR_AG-P'
tri_mnemonic = 'REPO-TRI_AR_OO-P'

dvp_df = pd.DataFrame(requests.get(base_url + dvp_mnemonic).json(), columns=["date", "value"])
dvp_df['date'] = pd.to_datetime(dvp_df['date'])
dvp_df.index = dvp_df['date'].values
dvp_df.drop('date', axis=1, inplace=True)

gcf_df = pd.DataFrame(requests.get(base_url + gcf_mnemonic).json(), columns=["date", "value"])
gcf_df['date'] = pd.to_datetime(gcf_df['date'])
gcf_df.index = gcf_df['date'].values
gcf_df.drop('date', axis=1, inplace=True)

tri_df = pd.DataFrame(requests.get(base_url + tri_mnemonic).json(), columns=["date", "value"])
tri_df['date'] = pd.to_datetime(tri_df['date'])
tri_df.index = tri_df['date'].values
tri_df.drop('date', axis=1, inplace=True)

fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
fed_funds.index = pd.to_datetime(fed_funds.index.values)

quarter_spreads_merge = merge_dfs([gc_df,dvp_df,gcf_df,fed_funds]).resample('QE').last()
quarter_spreads_merge.columns = ['gc','dvp','gcf','effr']
quarter_spreads_merge['gc_effr'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['effr']
quarter_spreads_merge['gc_dvp'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['dvp']
quarter_spreads_merge['gc_gcf'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['gcf']

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_effr'],
         label='GC-EFFR', color='#9DDCF9', lw=2)  # light blue
plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_dvp'],
         label='GC-DVP', color='#4CD0E9', lw=2)  # cyan
plt.plot(quarter_spreads_merge.index, quarter_spreads_merge['gc_gcf'],
         label='GC-GCF', color='#233852', lw=2)  # dark blue
plt.ylabel("Basis Points")
plt.title("End of Quarter Spreads", fontsize=17, fontweight="bold")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- END OF MONTH SPREADS ------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
rrp.index = pd.to_datetime(rrp.index.values)
monthly_spreads_merge = merge_dfs([gc_df,dvp_df,gcf_df,fed_funds,rrp]).resample('ME').last()
monthly_spreads_merge.columns = ['gc','dvp','gcf','effr','rrp']
monthly_spreads_merge['gc_effr'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['effr']
monthly_spreads_merge['gc_dvp'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['dvp']
monthly_spreads_merge['gc_gcf'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['gcf']
monthly_spreads_merge['gc_rrp'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['rrp']

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_effr'],
         label="GC-EFFR",color="#f8b62d", lw=2)
plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_dvp'],
         label="GC-DVP", color="#f8772d", lw=2)
plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_gcf'],
         label="GC-GCF", color="#2f90c5", lw=2)
plt.plot(monthly_spreads_merge.index, monthly_spreads_merge['gc_rrp'],
         label="GC-RRP", color="#67cbe7", lw=2)
plt.title("End of Month Spreads", fontsize=22, fontweight="bold")
plt.ylabel("Basis Points")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- IS THE STABILITY LOWER ROC --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
sofr = pdr.DataReader('SOFR', 'fred', start, end)
sofr.index = pd.to_datetime(sofr.index.values)
combined_data = merge_dfs([sofr,rrp,gc_df,fed_funds,tri_df,dvp_df])
combined_data.columns = ['SOFR','ON_RRP_Rate','BGCR','Fed_Funds','TGCR','DVP']
clean_data = combined_data.dropna(subset=['SOFR', 'BGCR', 'TGCR', 'ON_RRP_Rate', 'Fed_Funds','DVP'])

clean_data['Private_Repo_Avg'] = (clean_data['DVP'] + clean_data['TGCR']) / 2
clean_data['Fed_Facility_Spread'] = clean_data['ON_RRP_Rate'] - clean_data['SOFR']
clean_data['Private_Repo_Spread'] = clean_data['Private_Repo_Avg'] - clean_data['SOFR']
clean_data['Fed_Facility_MA30'] = clean_data['Fed_Facility_Spread'].rolling(window=30).mean()
clean_data['Private_Repo_MA30'] = clean_data['Private_Repo_Spread'].rolling(window=30).mean()
clean_data['Fed_Facility_Z'] = (clean_data['Fed_Facility_MA30'] - clean_data['Fed_Facility_MA30'].mean()) / clean_data[
    'Fed_Facility_MA30'].std()
clean_data['Private_Repo_Z'] = (clean_data['Private_Repo_MA30'] - clean_data['Private_Repo_MA30'].mean()) / clean_data[
    'Private_Repo_MA30'].std()

plot_data = clean_data.dropna(subset=['Fed_Facility_Z', 'Private_Repo_Z'])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(plot_data.index, plot_data['Fed_Facility_Z'],
         label="Fed Facility to Repo Spreads", color="#1f77b4", lw=2)
plt.plot(plot_data.index, plot_data['Private_Repo_Z'],
         label="Private Repo Spreads", color="#2E3A59", lw=2)
for y_val in [-2, -1, 1, 2]:
    plt.axhline(y=y_val, color='gray', linestyle='--', alpha=0.6, linewidth=1)
plt.title("Is the Stability Lower\nRate of Change", fontsize=22, fontweight="bold")
plt.ylabel("Z-Score")
plt.ylim(-5, 5)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.grid(True, alpha=0.3)
plt.figtext(0.02, 0.02, 'Fonte: FED, MacroDispatch. Note: Calculations on a 30 MA Difference',
           fontsize=9, color='gray')
plt.figtext(0.95, 0.02, 'ie', fontsize=14, color='steelblue',
           fontweight='bold', ha='right')
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- HOW DID LEVELS CHANGE ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
clean_data['Fed_Facility_static_Z'] = (clean_data['Fed_Facility_Spread'] - clean_data['Fed_Facility_Spread'].mean()) / clean_data[
    'Fed_Facility_Spread'].std()
clean_data['Private_Repo_static_Z'] = (clean_data['Private_Repo_Spread'] - clean_data['Private_Repo_Spread'].mean()) / clean_data[
    'Private_Repo_Spread'].std()
plot_static_data = clean_data.dropna(subset=['Fed_Facility_static_Z', 'Private_Repo_static_Z'])

### PLOT ###
plt.figure(figsize=(12, 7))
plt.plot(plot_static_data.index, plot_static_data['Fed_Facility_static_Z'],
         label="Fed Facility to Repo Spreads", color="#1f77b4", lw=2)
plt.plot(plot_static_data.index, plot_static_data['Private_Repo_static_Z'],
         label="Private Repo Spreads", color="#2E3A59", lw=2)
for y_val in [-2, -1, 1, 2]:
    plt.axhline(y=y_val, color='gray', linestyle='--', alpha=0.6, linewidth=1)
plt.title("Is the Stability Lower\nRate of Change", fontsize=22, fontweight="bold")
plt.ylabel("Z-Score")
plt.ylim(-5, 5)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
plt.grid(True, alpha=0.3)
plt.figtext(0.95, 0.02, 'ie', fontsize=14, color='steelblue',
           fontweight='bold', ha='right')
plt.tight_layout()
plt.show()


