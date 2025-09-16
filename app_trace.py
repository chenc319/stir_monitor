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

colors = [
    '#5FB3FF',   # Vivid sky blue (QE, stable)
    '#2DCDB2',   # Bright teal/mint (portfolio)
    '#FFC145',   # Sun gold (Treasury)
    '#FF6969',   # Approachable coral (MBS)
    '#54C6EB',   # Aqua blue (permanent lending)
    '#FFD166',   # Citrus yellow-orange (temp lending)
    '#6FE7DD',   # Lively turquoise (repo facility)
]

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

    ats_interdealer_volume = on_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="atsInterdealerVolume",
        aggfunc="sum"
    )
    ats_interdealer_volume.index = pd.to_datetime(ats_interdealer_volume.index.values)
    ats_interdealer_volume.columns = ['<2','10<>20','2<>3','>20','3<>5','5<>7','7<>10']

    dealer_customer_volume = on_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="dealerCustomerVolume",
        aggfunc="sum"
    )
    dealer_customer_volume.index = pd.to_datetime(dealer_customer_volume.index.values)
    dealer_customer_volume.columns = ['<2', '10<>20', '2<>3', '>20', '3<>5', '5<>7', '7<>10']

    ### PLOT ###
    fig = go.Figure()
    cols = ats_interdealer_volume.columns
    labels = ats_interdealer_volume.columns
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=ats_interdealer_volume.index, y=ats_interdealer_volume[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="ATS InterDealer Volume",
        xaxis_title="Dollars",
        showlegend=True,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_customer_volume.columns
    labels = dealer_customer_volume.columns
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=dealer_customer_volume.index, y=dealer_customer_volume[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Dealer Customer Volume",
        xaxis_title="Dollars",
        showlegend=True,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_off_the_run_nominal_coupons(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    off_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'Off-the-run')]

    ats_interdealer_volume = off_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="atsInterdealerVolume",
        aggfunc="sum"
    )
    ats_interdealer_volume.index = pd.to_datetime(ats_interdealer_volume.index.values)
    ats_interdealer_volume.columns = ['<2','10<>20','2<>3','>20','3<>5','5<>7','7<>10']

    dealer_customer_volume = off_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="dealerCustomerVolume",
        aggfunc="sum"
    )
    dealer_customer_volume.index = pd.to_datetime(dealer_customer_volume.index.values)
    dealer_customer_volume.columns = ['<2', '10<>20', '2<>3', '>20', '3<>5', '5<>7', '7<>10']

    ### PLOT ###
    fig = go.Figure()
    cols = ats_interdealer_volume.columns
    labels = ats_interdealer_volume.columns
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=ats_interdealer_volume.index, y=ats_interdealer_volume[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="ATS InterDealer Volume",
        xaxis_title="Dollars",
        showlegend=True,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_customer_volume.columns
    labels = dealer_customer_volume.columns
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=dealer_customer_volume.index, y=dealer_customer_volume[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Dealer Customer Volume",
        xaxis_title="Dollars",
        showlegend=True,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)




