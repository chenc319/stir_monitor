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

def pull_on_the_run_interdealer(start,end):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
        treasury_daily_aggregates_full.columns
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    on_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'On-the-run')]
    treasury_daily_aggregates_full['yearsToMaturity'].unique()
    on_the_run_bonds.index = pd.to_datetime(on_the_run_bonds.index)

    ats_interdealer_volume = on_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="atsInterdealerVolume",
        aggfunc="sum"
    )
    ats_interdealer_volume.index = pd.to_datetime(ats_interdealer_volume.index.values)
    ats_interdealer_volume = ats_interdealer_volume[start:end]
    ats_interdealer_volume.columns = ['<2','10<>20','2<>3','>20','3<>5','5<>7','7<>10']
    return(ats_interdealer_volume)

def pull_on_the_run_dealer_client(start,end):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
        treasury_daily_aggregates_full.columns
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    on_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'On-the-run')]
    treasury_daily_aggregates_full['yearsToMaturity'].unique()

    dealer_customer_volume = on_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="dealerCustomerVolume",
        aggfunc="sum"
    )
    dealer_customer_volume.index = pd.to_datetime(dealer_customer_volume.index.values)
    dealer_customer_volume = dealer_customer_volume[start:end]
    dealer_customer_volume.columns = ['<2', '10<>20', '2<>3', '>20', '3<>5', '5<>7', '7<>10']
    return(dealer_customer_volume)

def pull_off_the_run_interdealer(start,end):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
        treasury_daily_aggregates_full.columns
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
    ats_interdealer_volume = ats_interdealer_volume[start:end]
    ats_interdealer_volume.columns = ['<2', '10<>20', '2<>3', '>20', '3<>5', '5<>7', '7<>10']
    return(ats_interdealer_volume)

def pull_off_the_run_dealer_client(start,end):
    with open(Path(DATA_DIR) / 'treasury_daily_aggregates_full.pkl', 'rb') as file:
        treasury_daily_aggregates_full = pickle.load(file)
        treasury_daily_aggregates_full.columns
    treasury_daily_aggregates_full['atsInterdealerVolume'] = treasury_daily_aggregates_full['atsInterdealerVolume'] * 1e9
    treasury_daily_aggregates_full['dealerCustomerVolume'] = treasury_daily_aggregates_full['dealerCustomerVolume'] * 1e9
    off_the_run_bonds = treasury_daily_aggregates_full[
        (treasury_daily_aggregates_full['productCategory'] == 'Nominal Coupons') &
        (treasury_daily_aggregates_full['benchmark'] == 'Off-the-run')]

    dealer_customer_volume = off_the_run_bonds.pivot_table(
        index="tradeDate",
        columns="yearsToMaturity",
        values="dealerCustomerVolume",
        aggfunc="sum"
    )
    dealer_customer_volume.index = pd.to_datetime(dealer_customer_volume.index.values)
    dealer_customer_volume = dealer_customer_volume[start:end]
    dealer_customer_volume.columns = ['<2', '10<>20', '2<>3', '>20', '3<>5', '5<>7', '7<>10']
    return(dealer_customer_volume)

def plot_on_the_run_nominal_coupons(start, end, **kwargs):
    ats_interdealer_volume = pull_on_the_run_interdealer(start,end)
    dealer_customer_volume = pull_on_the_run_dealer_client(start,end)

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
    ats_interdealer_volume = pull_off_the_run_interdealer(start, end)
    dealer_customer_volume = pull_off_the_run_dealer_client(start, end)

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

def plot_on_vs_off(start, end, **kwargs):
    on_the_run_interdealer = pull_on_the_run_interdealer(start, end)
    on_the_run_dealer_client = pull_on_the_run_dealer_client(start, end)
    off_the_run_interdealer = pull_off_the_run_interdealer(start, end)
    off_the_run_dealer_client = pull_off_the_run_dealer_client(start, end)

    on_the_run_total = on_the_run_interdealer + on_the_run_dealer_client
    off_the_run_total = off_the_run_interdealer + off_the_run_dealer_client
    on_off_combined_total = on_the_run_total + off_the_run_total
    on_total_ratio = on_the_run_total / on_off_combined_total
    off_total_ratio = off_the_run_total / on_off_combined_total

    on_off_combined_total_sum = pd.DataFrame(on_off_combined_total.sum(axis=1))
    on_off_combined_total_sum.columns = ['On-the-run + Off-the-run']
    on_the_run_total_sum = pd.DataFrame(on_the_run_total.sum(axis=1))
    on_the_run_total_sum.columns = ['On-the-run Total']
    off_the_run_total_sum = pd.DataFrame(off_the_run_total.sum(axis=1))
    on_the_run_total_sum.columns = ['Off-the-run Total']

    on_merge = merge_dfs([on_the_run_total_sum,on_off_combined_total_sum])
    on_the_run_total_sum_ratio = pd.DataFrame(on_merge.iloc[:,0] / on_merge.iloc[:,1],
                                              columns = ['On-the-run'])
    off_merge = merge_dfs([off_the_run_total_sum, on_off_combined_total_sum])
    off_the_run_total_sum_ratio = pd.DataFrame(off_merge.iloc[:,0] / off_merge.iloc[:,1],
                                               columns = ['Off-the-run'])
    total_sum_ratio_merge = merge_dfs([on_the_run_total_sum_ratio,off_the_run_total_sum_ratio])
    total_sum_ratio_merge.columns = ['On-the-run','Off-the-run']

    ### PLOT ###
    fig = go.Figure()
    cols = on_off_combined_total_sum.columns
    for col in cols:
        fig.add_trace(go.Scatter(x=on_off_combined_total_sum.index, y=on_off_combined_total_sum[col],
                                 mode='lines',
                                 line=dict(color='#83c3f7')))
    fig.update_layout(
        title="Total On-the-Run + Off-the-Run Daily Liquidity",
        xaxis_title="Dollars",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    labels = ['On-the-run', 'Off-the-run']
    cols = total_sum_ratio_merge.columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, ['#2567c4','#e5433a'], labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=total_sum_ratio_merge.index,
                y=total_sum_ratio_merge[col],
                mode='lines',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="On-the-run vs. Off-the-Run",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = on_off_combined_total.columns
    labels = on_off_combined_total.columns
    for col, color, label in zip(cols, colors, labels):
        fig.add_trace(go.Scatter(x=on_off_combined_total.index, y=on_off_combined_total[col],
                                 mode='lines',
                                 name=label,
                                 line=dict(color=color)))
    fig.update_layout(
        title="Total On-the-Run + Off-the-Run Daily Liquidity by Tenor",
        xaxis_title="Dollars",
        showlegend=True,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_dealer_dealer_vs_dealer_client(start, end, **kwargs):
    on_the_run_interdealer = pull_on_the_run_interdealer(start, end)
    on_the_run_dealer_client = pull_on_the_run_dealer_client(start, end)
    off_the_run_interdealer = pull_off_the_run_interdealer(start, end)
    off_the_run_dealer_client = pull_off_the_run_dealer_client(start, end)

    dealer_dealer_total = on_the_run_interdealer + off_the_run_interdealer
    dealer_client_total = on_the_run_dealer_client + off_the_run_dealer_client
    dealer_dealer_total_sum = pd.DataFrame(dealer_dealer_total.sum(axis=1),
                                           columns = ['Dealer-to-Dealer'])
    dealer_client_total_sum = pd.DataFrame(dealer_client_total.sum(axis=1),
                                           columns = ['Dealer-to-Client'])

    ### DEALER TO DEALER ###
    on_the_run_dealer_sum = pd.DataFrame(on_the_run_interdealer.sum(axis=1),
                                         columns=['On-the-run'])
    on_merge = merge_dfs([on_the_run_dealer_sum, dealer_dealer_total_sum])
    on_the_run_dealer_ratio = pd.DataFrame(on_merge.iloc[:, 0] / on_merge.iloc[:, 1],
                                              columns=['On-the-run'])
    off_the_run_dealer_sum = pd.DataFrame(off_the_run_interdealer.sum(axis=1),
                                         columns=['Off-the-run'])
    off_merge = merge_dfs([off_the_run_dealer_sum, dealer_dealer_total_sum])
    off_the_run_dealer_ratio = pd.DataFrame(off_merge.iloc[:, 0] / off_merge.iloc[:, 1],
                                              columns=['Off-the-run'])
    dealer_merge = merge_dfs([on_the_run_dealer_ratio,off_the_run_dealer_ratio])

    ### DEALER TO CLIENT ###
    on_the_run_client_sum = pd.DataFrame(on_the_run_dealer_client.sum(axis=1),
                                         columns=['On-the-run'])
    on_merge = merge_dfs([on_the_run_client_sum, dealer_client_total_sum])
    on_the_run_client_ratio = pd.DataFrame(on_merge.iloc[:, 0] / on_merge.iloc[:, 1],
                                              columns=['On-the-run'])
    off_the_run_client_sum = pd.DataFrame(off_the_run_dealer_client.sum(axis=1),
                                          columns=['Off-the-run'])
    off_merge = merge_dfs([off_the_run_client_sum, dealer_client_total_sum])
    off_the_run_client_ratio = pd.DataFrame(off_merge.iloc[:, 0] / off_merge.iloc[:, 1],
                                               columns=['Off-the-run'])
    client_merge = merge_dfs([on_the_run_client_ratio, off_the_run_client_ratio])

    ### SPREADS ###
    dealer_client_on_spread = pd.DataFrame(on_the_run_interdealer.sum(axis=1) -
                                           on_the_run_dealer_client.sum(axis=1),
                                           columns=['On-the-run Spread'])
    dealer_client_off_spread = pd.DataFrame(off_the_run_interdealer.sum(axis=1) -
                                            off_the_run_dealer_client.sum(axis=1),
                                            columns=['On-the-run Spread'])

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_dealer_total_sum.columns
    for col in cols:
        fig.add_trace(go.Scatter(x=dealer_dealer_total_sum.index, y=dealer_dealer_total_sum[col],
                                 mode='lines',
                                 line=dict(color='#83c3f7')))
    fig.update_layout(
        title="Dealer-to-Dealer Total Daily Liquidity",
        xaxis_title="Dollars",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    labels = ['On-the-run', 'Off-the-run']
    cols = dealer_merge.columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, ['#2567c4', '#e5433a'], labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=dealer_merge.index,
                y=dealer_merge[col],
                mode='lines',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Dealer-to-Dealer: On-the-run vs. Off-the-Run",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_client_total_sum.columns
    for col in cols:
        fig.add_trace(go.Scatter(x=dealer_client_total_sum.index, y=dealer_client_total_sum[col],
                                 mode='lines',
                                 line=dict(color='#83c3f7')))
    fig.update_layout(
        title="Dealer-to-Client Total Daily Liquidity",
        xaxis_title="Dollars",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    labels = ['On-the-run', 'Off-the-run']
    cols = client_merge.columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=labels)
    for i, (col, color, label) in enumerate(zip(cols, ['#2567c4', '#e5433a'], labels)):
        row = i // 2 + 1
        col_position = i % 2 + 1
        fig.add_trace(
            go.Scatter(
                x=client_merge.index,
                y=client_merge[col],
                mode='lines',
                name=label,
                line=dict(color=color)
            ),
            row=row,
            col=col_position
        )
    fig.update_layout(
        title="Dealer-to-Client: On-the-run vs. Off-the-Run",
        showlegend=False,
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_client_total_sum.columns
    for col in cols:
        fig.add_trace(go.Scatter(x=dealer_client_on_spread.index, y=dealer_client_on_spread[col],
                                 mode='lines',
                                 line=dict(color='#2567c4')))
    fig.update_layout(
        title="Dealer-to-Dealer vs. Dealer-to-Client: On-the-Run Spread",
        xaxis_title="Dollars",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    ### PLOT ###
    fig = go.Figure()
    cols = dealer_client_total_sum.columns
    for col in cols:
        fig.add_trace(go.Scatter(x=dealer_client_off_spread.index, y=dealer_client_off_spread[col],
                                 mode='lines',
                                 line=dict(color='#e5433a')))
    fig.update_layout(
        title="Dealer-to-Dealer vs. Dealer-to-Client: Off-the-Run Spread",
        xaxis_title="Dollars",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)





