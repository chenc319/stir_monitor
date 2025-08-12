### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------------- AUCTIONS ------------------------------------------------- ###
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
### ------------------------------------ ISSUANCE IN AUCTION BY SECURITY ------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?filter=record_date:"
       "gte:2000-08-16,record_date:lte:2025-08-15&sort=-auction_date,-issue_date,maturity_date&page[size]=10000")
resp = requests.get(url).json()
us_treasury_auction_data = pd.DataFrame(resp['data'])
auction_issuance_df = us_treasury_auction_data[['record_date','security_type','security_term','total_accepted']]
auction_issuance_df['total_accepted'] = pd.to_numeric(auction_issuance_df['total_accepted'], errors='coerce')
auction_issuance_df['record_date'] = pd.to_datetime(auction_issuance_df['record_date'])
auction_issuance_df['eom'] = auction_issuance_df['record_date'].dt.to_period('M').dt.to_timestamp('M')
agg_monthly = auction_issuance_df.groupby(['eom', 'security_type'])['total_accepted'].sum().unstack(fill_value=0)
agg_monthly = agg_monthly / 1e12  # convert to trillions

### PLOT ###
plt.figure(figsize=(10, 6))
plt.plot(agg_monthly.index, agg_monthly.get('Bill', pd.Series(index=agg_monthly.index)), label='Bill', color='#8ed6f8')
plt.plot(agg_monthly.index, agg_monthly.get('Bond', pd.Series(index=agg_monthly.index)), label='Bond', color='#008fd5')
plt.plot(agg_monthly.index, agg_monthly.get('Note', pd.Series(index=agg_monthly.index)), label='Note', color='#ffc650')
plt.title("Issuance in Auction By Security", fontsize=20, fontweight='bold', pad=20)
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- NET BILL ISSUANCE OF TOTAL ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bill_issuance = auction_issuance_df[
    (auction_issuance_df['security_term'] == '4-Week') |
    (auction_issuance_df['security_term'] == '8-Week') |
    (auction_issuance_df['security_term'] == '13-Week') |
    (auction_issuance_df['security_term'] == '26-Week') |
    (auction_issuance_df['security_term'] == '52-Week')
    ]
bill_issuance['record_date'] = pd.to_datetime(bill_issuance['record_date'])
bill_issuance['eom'] = bill_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
bill_issuance = bill_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0)
bill_issuance = bill_issuance / 1e12
bill_issuance = bill_issuance['2020-01-01':]

### PLOT ###
plt.figure(figsize=(10, 6))
plt.plot(bill_issuance.index,
         bill_issuance.get('4-Week', pd.Series(index=bill_issuance.index)), label='4-Week', color='#9bdaf6')
plt.plot(bill_issuance.index,
         bill_issuance.get('8-Week', pd.Series(index=bill_issuance.index)), label='8-Week', color='#4dc6c6')
plt.plot(bill_issuance.index,
         bill_issuance.get('13-Week', pd.Series(index=bill_issuance.index)), label='13-Week', color='#356c82')
plt.plot(bill_issuance.index,
         bill_issuance.get('26-Week', pd.Series(index=bill_issuance.index)), label='26-Week', color='#001f35')
plt.plot(bill_issuance.index,
         bill_issuance.get('52-Week', pd.Series(index=bill_issuance.index)), label='52-Week', color='#fbc430')
plt.title("Bill Issuances", fontsize=20, fontweight='bold', pad=20)
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- NET NOTES ISSUANCE OF TOTAL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
notes_issuance = auction_issuance_df[
    (auction_issuance_df['security_term'] == '2-Year') |
    (auction_issuance_df['security_term'] == '3-Year') |
    (auction_issuance_df['security_term'] == '5-Year') |
    (auction_issuance_df['security_term'] == '7-Year') |
    (auction_issuance_df['security_term'] == '10-Year')
    ]
notes_issuance['record_date'] = pd.to_datetime(notes_issuance['record_date'])
notes_issuance['eom'] = notes_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
notes_issuance = notes_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0)
notes_issuance = notes_issuance / 1e12
notes_issuance = notes_issuance['2020-01-01':]

### PLOT ###
plt.figure(figsize=(10, 6))
plt.plot(notes_issuance.index,
         notes_issuance.get('2-Year', pd.Series(index=notes_issuance.index)), label='2-Year', color='#9bdaf6')
plt.plot(notes_issuance.index,
         notes_issuance.get('3-Year', pd.Series(index=notes_issuance.index)), label='3-Year', color='#4dc6c6')
plt.plot(notes_issuance.index,
         notes_issuance.get('5-Year', pd.Series(index=notes_issuance.index)), label='5-Year', color='#356c82')
plt.plot(notes_issuance.index,
         notes_issuance.get('7-Year', pd.Series(index=notes_issuance.index)), label='7-Year', color='#001f35')
plt.plot(notes_issuance.index,
         notes_issuance.get('10-Year', pd.Series(index=notes_issuance.index)), label='10-Year', color='#fbc430')
plt.title("Notes Issuances", fontsize=20, fontweight='bold', pad=20)
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------- NET BONDS ISSUANCE OF TOTAL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bonds_issuance = auction_issuance_df[
    (auction_issuance_df['security_term'] == '20-Year') |
    (auction_issuance_df['security_term'] == '30-Year')
    ]
bonds_issuance['record_date'] = pd.to_datetime(bonds_issuance['record_date'])
bonds_issuance['eom'] = bonds_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
bonds_issuance = bonds_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0)
bonds_issuance = bonds_issuance / 1e12
bonds_issuance = bonds_issuance['2020-01-01':]

### PLOT ###
plt.figure(figsize=(10, 6))
plt.plot(bonds_issuance.index,
         bonds_issuance.get('20-Year', pd.Series(index=bonds_issuance.index)), label='20-Year', color='#9bdaf6')
plt.plot(bonds_issuance.index,
         bonds_issuance.get('30-Year', pd.Series(index=bonds_issuance.index)), label='30-Year', color='#fbc430')
plt.title("Bonds Issuances", fontsize=20, fontweight='bold', pad=20)
plt.ylabel("Dollars (Trillions)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------- BILLS DEALER TO NON DEALER RATIO ------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

dealer_non_dealer_df = us_treasury_auction_data[['record_date',
                                                 'security_type',
                                                 'security_term',
                                                 'primary_dealer_accepted',
                                                 'indirect_bidder_accepted',
                                                 'direct_bidder_accepted',
                                                 'noncomp_accepted',
                                                 'total_accepted'
                                                 ]]
cols = ['primary_dealer_accepted', 'indirect_bidder_accepted',
        'direct_bidder_accepted', 'noncomp_accepted','total_accepted']
dealer_non_dealer_df[cols] = dealer_non_dealer_df[cols].apply(pd.to_numeric, errors='coerce')
dealer_non_dealer_df.index = pd.to_datetime(dealer_non_dealer_df['record_date'].values)
dealer_non_dealer_df['dealer_to_non_dealer_ratio'] = dealer_non_dealer_df['primary_dealer_accepted'] / (
    dealer_non_dealer_df['indirect_bidder_accepted'] +
    dealer_non_dealer_df['direct_bidder_accepted']
)
bills_dealer_non_dealer_df = dealer_non_dealer_df[dealer_non_dealer_df['security_type'] == 'Bill']
bills_4week = pd.DataFrame(bills_dealer_non_dealer_df[bills_dealer_non_dealer_df['security_term'] == '4-Week']['dealer_to_non_dealer_ratio'])
bills_4week.columns = ['4week']
bills_8week = pd.DataFrame(bills_dealer_non_dealer_df[bills_dealer_non_dealer_df['security_term'] == '8-Week']['dealer_to_non_dealer_ratio'])
bills_8week.columns = ['8week']
bills_13week = pd.DataFrame(bills_dealer_non_dealer_df[bills_dealer_non_dealer_df['security_term'] == '13-Week']['dealer_to_non_dealer_ratio'])
bills_13week.columns = ['13week']
bills_26week = pd.DataFrame(bills_dealer_non_dealer_df[bills_dealer_non_dealer_df['security_term'] == '26-Week']['dealer_to_non_dealer_ratio'])
bills_26week.columns = ['26week']
bills_52week = pd.DataFrame(bills_dealer_non_dealer_df[bills_dealer_non_dealer_df['security_term'] == '52-Week']['dealer_to_non_dealer_ratio'])
bills_52week.columns = ['52week']
bills_merge = merge_dfs([bills_4week.resample('ME').last(),
                         bills_8week.resample('ME').last(),
                         bills_13week.resample('ME').last(),
                         bills_26week.resample('ME').last(),
                         bills_52week.resample('ME').last()]).ffill().dropna()

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(bills_merge.index, bills_merge['4week'],
         label='4-Week', color='#9DDCF9', lw=2)  # light blue
plt.plot(bills_merge.index, bills_merge['8week'],
         label='8-Week', color='#4CD0E9', lw=2)  # cyan
plt.plot(bills_merge.index, bills_merge['13week'],
         label='13-Week', color='#233852', lw=2)  # dark blue
plt.plot(bills_merge.index, bills_merge['26week'],
         label='26-Week', color='#F5B820', lw=2)  # yellow/orange
plt.plot(bills_merge.index, bills_merge['52week'],
         label='52-Week', color='#E69B93', lw=2)  # salmon/pink
plt.ylabel("Ratio")
plt.title("Bills Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ BONDS DEALER TO NON DEALER RATIO ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA AGGREGATION ###
bonds_dealer_non_dealer = dealer_non_dealer_df[dealer_non_dealer_df['security_type'] == 'Bond']
bonds_20year = pd.DataFrame(bonds_dealer_non_dealer[bonds_dealer_non_dealer['security_term'] ==
                                             '20-Year']['dealer_to_non_dealer_ratio'])
bonds_20year.columns = ['20year']
bonds_30year = pd.DataFrame(bonds_dealer_non_dealer[bonds_dealer_non_dealer['security_term'] ==
                                             '30-Year']['dealer_to_non_dealer_ratio'])
bonds_30year.columns = ['30year']
bonds_merge = merge_dfs([bonds_20year.resample('ME').last(),
                         bonds_30year.resample('ME').last()]).dropna()
cols = ['20year', '30year']
bonds_merge[cols] = bonds_merge[cols].apply(pd.to_numeric, errors='coerce')

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(bonds_merge.index, bonds_merge['20year'],
         label='20-Year', color='#9DDCF9', lw=2)  # light blue
plt.plot(bonds_merge.index, bonds_merge['30year'],
         label='30-Year', color='#4CD0E9', lw=2)  # cyan
plt.ylabel("Ratio")
plt.title("Bonds Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ BONDS DEALER TO NON DEALER RATIO ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
notes_dealer_non_dealer = dealer_non_dealer_df[dealer_non_dealer_df['security_type'] == 'Note']
notes_dealer_non_dealer['security_term'].unique()
notes_2yr = pd.DataFrame(notes_dealer_non_dealer[notes_dealer_non_dealer['security_term'] ==
                                                 '2-Year']['dealer_to_non_dealer_ratio'])
notes_2yr.columns = ['2year']
notes_3yr = pd.DataFrame(notes_dealer_non_dealer[notes_dealer_non_dealer['security_term'] ==
                                                 '3-Year']['dealer_to_non_dealer_ratio'])
notes_3yr.columns = ['3year']
notes_5yr = pd.DataFrame(notes_dealer_non_dealer[notes_dealer_non_dealer['security_term'] ==
                                                 '5-Year']['dealer_to_non_dealer_ratio'])
notes_5yr.columns = ['5year']
notes_7yr = pd.DataFrame(notes_dealer_non_dealer[notes_dealer_non_dealer['security_term'] ==
                                                 '7-Year']['dealer_to_non_dealer_ratio'])
notes_7yr.columns = ['7year']
notes_10yr = pd.DataFrame(notes_dealer_non_dealer[notes_dealer_non_dealer['security_term'] ==
                                                  '10-Year']['dealer_to_non_dealer_ratio'])
notes_10yr.columns = ['10year']

notes_merge = merge_dfs([notes_2yr.resample('ME').last(),
                         notes_3yr.resample('ME').last(),
                         notes_5yr.resample('ME').last(),
                         notes_7yr.resample('ME').last(),
                         notes_10yr.resample('ME').last()]).ffill().dropna()
cols = ['2year', '3year', '5year', '7year', '10year']
notes_merge[cols] = notes_merge[cols].apply(pd.to_numeric, errors='coerce')

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(notes_merge.index, notes_merge['2year'],
         label='2-Year', color='#9DDCF9', lw=2)  # light blue
plt.plot(notes_merge.index, notes_merge['3year'],
         label='3-Year', color='#4CD0E9', lw=2)  # cyan
plt.plot(notes_merge.index, notes_merge['5year'],
         label='5-Year', color='#233852', lw=2)  # dark blue
plt.plot(notes_merge.index, notes_merge['7year'],
         label='7-Year', color='#F5B820', lw=2)  # yellow/orange
plt.plot(notes_merge.index, notes_merge['10year'],
         label='10-Year', color='#E69B93', lw=2)  # salmon/pink
plt.ylabel("Ratio")
plt.title("Bonds Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- BILLS BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bid_to_cover = us_treasury_auction_data[['record_date','security_type','security_term','bid_to_cover_ratio']]
bid_to_cover.index = pd.to_datetime(bid_to_cover['record_date'].values)
bills_bid_to_cover = bid_to_cover[bid_to_cover['security_type'] == 'Bill']
bills_4week = pd.DataFrame(bills_bid_to_cover[bills_bid_to_cover['security_term'] == '4-Week']['bid_to_cover_ratio'])
bills_4week.columns = ['4week']
bills_8week = pd.DataFrame(bills_bid_to_cover[bills_bid_to_cover['security_term'] == '8-Week']['bid_to_cover_ratio'])
bills_8week.columns = ['8week']
bills_13week = pd.DataFrame(bills_bid_to_cover[bills_bid_to_cover['security_term'] == '13-Week']['bid_to_cover_ratio'])
bills_13week.columns = ['13week']
bills_26week = pd.DataFrame(bills_bid_to_cover[bills_bid_to_cover['security_term'] == '26-Week']['bid_to_cover_ratio'])
bills_26week.columns = ['26week']
bills_52week = pd.DataFrame(bills_bid_to_cover[bills_bid_to_cover['security_term'] == '52-Week']['bid_to_cover_ratio'])
bills_52week.columns = ['52week']

bills_merge = merge_dfs([bills_4week.resample('ME').last(),
                         bills_8week.resample('ME').last(),
                         bills_13week.resample('ME').last(),
                         bills_26week.resample('ME').last(),
                         bills_52week.resample('ME').last()]).ffill().dropna()
cols = ['4week', '8week', '13week', '26week', '52week']
bills_merge[cols] = bills_merge[cols].apply(pd.to_numeric, errors='coerce')

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(bills_merge.index, bills_merge['4week'],
         label='4-Week', color='#9DDCF9', lw=2)  # light blue
plt.plot(bills_merge.index, bills_merge['8week'],
         label='8-Week', color='#4CD0E9', lw=2)  # cyan
plt.plot(bills_merge.index, bills_merge['13week'],
         label='13-Week', color='#233852', lw=2)  # dark blue
plt.plot(bills_merge.index, bills_merge['26week'],
         label='26-Week', color='#F5B820', lw=2)  # yellow/orange
plt.plot(bills_merge.index, bills_merge['52week'],
         label='52-Week', color='#E69B93', lw=2)  # salmon/pink
plt.ylabel("Ratio")
plt.title("Bills Bid to Cover Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- BONDS BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
bonds_bid_to_cover = bid_to_cover[bid_to_cover['security_type'] == 'Bond']
bonds_20year = pd.DataFrame(bonds_bid_to_cover[bonds_bid_to_cover['security_term'] == '20-Year']['bid_to_cover_ratio'])
bonds_20year.columns = ['20year']
bonds_30year = pd.DataFrame(bonds_bid_to_cover[bonds_bid_to_cover['security_term'] == '30-Year']['bid_to_cover_ratio'])
bonds_30year.columns = ['30year']
bonds_merge = merge_dfs([bonds_20year.resample('ME').last(),
                         bonds_30year.resample('ME').last()]).dropna()
cols = ['20year', '30year']
bonds_merge[cols] = bonds_merge[cols].apply(pd.to_numeric, errors='coerce')

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(bonds_merge.index, bonds_merge['20year'],
         label='20-Year', color='#9DDCF9', lw=2)  # light blue
plt.plot(bonds_merge.index, bonds_merge['30year'],
         label='30-Year', color='#4CD0E9', lw=2)  # cyan
plt.ylabel("Ratio")
plt.title("Bonds Bid to Cover Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- BONDS BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### DATA PULL ###
notes_bid_to_cover = bid_to_cover[bid_to_cover['security_type'] == 'Note']
notes_bid_to_cover['security_term'].unique()
notes_2yr = pd.DataFrame(notes_bid_to_cover[notes_bid_to_cover['security_term'] == '2-Year']['bid_to_cover_ratio'])
notes_2yr.columns = ['2year']
notes_3yr = pd.DataFrame(notes_bid_to_cover[notes_bid_to_cover['security_term'] == '3-Year']['bid_to_cover_ratio'])
notes_3yr.columns = ['3year']
notes_5yr = pd.DataFrame(notes_bid_to_cover[notes_bid_to_cover['security_term'] == '5-Year']['bid_to_cover_ratio'])
notes_5yr.columns = ['5year']
notes_7yr = pd.DataFrame(notes_bid_to_cover[notes_bid_to_cover['security_term'] == '7-Year']['bid_to_cover_ratio'])
notes_7yr.columns = ['7year']
notes_10yr = pd.DataFrame(notes_bid_to_cover[notes_bid_to_cover['security_term'] == '10-Year']['bid_to_cover_ratio'])
notes_10yr.columns = ['10year']

notes_merge = merge_dfs([notes_2yr.resample('ME').last(),
                         notes_3yr.resample('ME').last(),
                         notes_5yr.resample('ME').last(),
                         notes_7yr.resample('ME').last(),
                         notes_10yr.resample('ME').last()]).ffill().dropna()
cols = ['2year', '3year', '5year', '7year', '10year']
notes_merge[cols] = notes_merge[cols].apply(pd.to_numeric, errors='coerce')

### PLOT ###
plt.figure(figsize=(10, 7))
plt.plot(notes_merge.index, notes_merge['2year'],
         label='2-Year', color='#9DDCF9', lw=2)  # light blue
plt.plot(notes_merge.index, notes_merge['3year'],
         label='3-Year', color='#4CD0E9', lw=2)  # cyan
plt.plot(notes_merge.index, notes_merge['5year'],
         label='5-Year', color='#233852', lw=2)  # dark blue
plt.plot(notes_merge.index, notes_merge['7year'],
         label='7-Year', color='#F5B820', lw=2)  # yellow/orange
plt.plot(notes_merge.index, notes_merge['10year'],
         label='10-Year', color='#E69B93', lw=2)  # salmon/pink
plt.ylabel("Ratio")
plt.title("Bonds Bid to Cover Ratio", fontsize=17, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()
