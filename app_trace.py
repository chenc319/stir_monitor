### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ FUTURES ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import pandas as pd
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
from plotly.subplots import make_subplots
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

colors = {
    '<2': '#5FB3FF',   # Vivid sky blue (QE, stable)
    '10<>20': '#2DCDB2',   # Bright teal/mint (portfolio)
    '2<>3': '#FFC145',   # Sun gold (Treasury)
    '>20': '#FF6969',   # Approachable coral (MBS)
    '3<>5': '#54C6EB',   # Aqua blue (permanent lending)
    '5<>7': '#FFD166',   # Citrus yellow-orange (temp lending)
    '7<>10': '#6FE7DD',   # Lively turquoise (repo facility)
}

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------------- 2YR --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

'''
- Trades is the count of  trades in the "ATS and Interdealer" and "Dealer-to-Customer" categories, as described below.

- Volume (Par Value)  is  the sum of reported trade sizes, expressed in billions of U.S. dollars 
(original face / par amount, not adjusted for price or inflation).

- The daily period begins after the close of the TRACE system the prior business day through the close of the TRACE 
system on the day of the report. The monthly period begins after the close of the TRACE system on the business day 
prior to the start of the month through the close of the TRACE system on the last business day of the month.

- When-Issued trades* executed on or before the close of the TRACE system on the auction day of the security are 
excluded from the data. For the purpose of this data, when-Issued trades are identified based on the information provided 
by TRACE reporting particpants. 

- The “ATS and Interdealer” category includes the sell side of a trade when (1) a trade is executed on an ATS 
(including ATS sales to non-members or non-member affiliates) or (2) a trade is executed between FINRA members 
outside of an ATS (i.e. dealer-to-dealer trades). The category excludes a FINRA member buy or sell to an ATS. 
This approach takes into account multiple reporting of trades where a trade involves an ATS or both sides are FINRA members.

- The “Dealer-to-Customer” category includes all trades (buys and sells) reported by a FINRA member against non-members or 
non-member affiliate. The category excludes ATS transactions with non-members and non-member affiliates 
(those trades are represented in the “ATS and Interdealer” category as noted above).

- VWAP: the volume-weighted average of reported prices for trades included in the report. 
The VWAP excludes trades where  
Entered volume is less than 1000;
The price type is yield;
The reported price is 50% or more away from the (simple) average of all reported prices;
Settlement is not regular settle; and/or
The reporting firm has applied a special price condition
'''

def plot_on_the_run_nominal_coupons(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    on_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'On-the-run')]
    off_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'Off-the-run')]

    on_the_run_bonds_df = on_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="atsInterdealerVolume",
        aggfunc="sum"
    )

    on_the_run_bonds_df.columns
    # Reset the index if you want tradeDate as a column instead of index
    on_the_run_bonds_df.index = pd.to_datetime(on_the_run_bonds_df.index.values)
    on_the_run_bonds_df.columns = ['<2','10<>20','2<>3','>20','3<>5','5<>7','7<>10']

    fig = go.Figure()
    cols = on_the_run_bonds_df.columns
    labels = on_the_run_bonds_df.columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=on_the_run_bonds_df.index,
                y=on_the_run_bonds_df[col],
                mode='lines',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="On-the-run Nominal Coupons ATS InterDealer Volume",
        showlegend=False,
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_off_the_run_nominal_coupons(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    on_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'On-the-run')]
    off_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'Off-the-run')]




