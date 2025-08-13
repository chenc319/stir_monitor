import pandas as pd
import requests
import functools as ft
from pandas_datareader import data as pdr
import streamlit as st
import plotly.graph_objs as go
from io import StringIO

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------- FUTURES LEVERAGE MONEY SHORT -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_futures_leverage_money_short(start, end, **kwargs):
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=60000"
    response = requests.get(url)
    cftc_all_futures = pd.read_csv(StringIO(response.text))
    bonds_cftc_subset = cftc_all_futures[
        cftc_all_futures['contract_market_name'].isin([
            'UST 2Y NOTE', 'UST 5Y NOTE', 'UST 10Y NOTE', 'ULTRA UST 10Y'
        ])
    ]
    bonds_future_leverage_money_short = bonds_cftc_subset[[
        'commodity_name','contract_market_name','report_date_as_yyyy_mm_dd','lev_money_positions_short'
    ]].copy()
    bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd'] = pd.to_datetime(
        bonds_future_leverage_money_short['report_date_as_yyyy_mm_dd']
    )
    pivot = bonds_future_leverage_money_short.pivot_table(
        index='report_date_as_yyyy_mm_dd',
        columns='commodity_name',
        values='lev_money_positions_short',
        aggfunc='sum'
    )
    pivot = pivot.loc[str(start):str(end)]
    fig = go.Figure()
    for col in pivot.columns:
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], name=col))
    fig.update_layout(
        title="Leverage Money Short Positions by Treasury Futures Bucket",
        yaxis_title="Leverage Money Short Positions",
        xaxis_title="Date",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ END OF QUARTER SPREADS ---------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_end_of_quarter_spreads(start, end, **kwargs):
    gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
               'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
    gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
    gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
    gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='

    def ofr_df(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date","value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df.astype(float)

    dvp_df = ofr_df('REPO-DVP_AR_OO-P')
    gcf_df = ofr_df('REPO-GCF_AR_AG-P')
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    fed_funds.index = pd.to_datetime(fed_funds.index)

    quarter_spreads_merge = merge_dfs([gc_df, dvp_df, gcf_df, fed_funds]).resample('QE').last()
    quarter_spreads_merge.columns = ['gc','dvp','gcf','effr']
    quarter_spreads_merge = quarter_spreads_merge.loc[str(start):str(end)]
    quarter_spreads_merge['gc_effr'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['effr']
    quarter_spreads_merge['gc_dvp'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['dvp']
    quarter_spreads_merge['gc_gcf'] = quarter_spreads_merge['gc'] - quarter_spreads_merge['gcf']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_effr'],
                             name="GC-EFFR", line=dict(color="#9DDCF9", width=2)))
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_dvp'],
                             name="GC-DVP", line=dict(color="#4CD0E9", width=2)))
    fig.add_trace(go.Scatter(x=quarter_spreads_merge.index, y=quarter_spreads_merge['gc_gcf'],
                             name="GC-GCF", line=dict(color="#233852", width=2)))
    fig.update_layout(
        title="End of Quarter Spreads",
        yaxis_title="Basis Points",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ END OF MONTH SPREADS ------------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_end_of_month_spreads(start, end, **kwargs):
    gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
               'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
    gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
    gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
    gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    def ofr_df(mnemonic):
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date","value"])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df.astype(float)
    dvp_df = ofr_df('REPO-DVP_AR_OO-P')
    gcf_df = ofr_df('REPO-GCF_AR_AG-P')
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    fed_funds.index = pd.to_datetime(fed_funds.index)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    rrp.index = pd.to_datetime(rrp.index)
    monthly_spreads_merge = merge_dfs([gc_df, dvp_df, gcf_df, fed_funds, rrp]).resample('ME').last()
    monthly_spreads_merge.columns = ['gc','dvp','gcf','effr','rrp']
    monthly_spreads_merge = monthly_spreads_merge.loc[str(start):str(end)]
    monthly_spreads_merge['gc_effr'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['effr']
    monthly_spreads_merge['gc_dvp'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['dvp']
    monthly_spreads_merge['gc_gcf'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['gcf']
    monthly_spreads_merge['gc_rrp'] = monthly_spreads_merge['gc'] - monthly_spreads_merge['rrp']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_effr'],
                             name="GC-EFFR", line=dict(color="#f8b62d", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_dvp'],
                             name="GC-DVP", line=dict(color="#f8772d", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_gcf'],
                             name="GC-GCF", line=dict(color="#2f90c5", width=2)))
    fig.add_trace(go.Scatter(x=monthly_spreads_merge.index, y=monthly_spreads_merge['gc_rrp'],
                             name="GC-RRP", line=dict(color="#67cbe7", width=2)))
    fig.update_layout(
        title="End of Month Spreads",
        yaxis_title="Basis Points",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------- IS THE STABILITY LOWER ROC -------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_stability_lower_roc(start, end, **kwargs):
    sof = pdr.DataReader('SOFR', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
               'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
    gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
    gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
    gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date","value"])
    tri_df['date'] = pd.to_datetime(tri_df['date'])
    tri_df.set_index('date', inplace=True)
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date","value"])
    dvp_df['date'] = pd.to_datetime(dvp_df['date'])
    dvp_df.set_index('date', inplace=True)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    fed_funds.index = pd.to_datetime(fed_funds.index)

    combined_data = merge_dfs([sof, rrp, gc_df, fed_funds, tri_df, dvp_df])
    combined_data.columns = ['SOFR','ON_RRP_Rate','BGCR','Fed_Funds','TGCR','DVP']
    clean_data = combined_data.dropna(subset=['SOFR','BGCR','TGCR','ON_RRP_Rate','Fed_Funds','DVP'])

    clean_data['Private_Repo_Avg'] = (clean_data['DVP'] + clean_data['TGCR']) / 2
    clean_data['Fed_Facility_Spread'] = clean_data['ON_RRP_Rate'] - clean_data['SOFR']
    clean_data['Private_Repo_Spread'] = clean_data['Private_Repo_Avg'] - clean_data['SOFR']
    clean_data['Fed_Facility_MA30'] = clean_data['Fed_Facility_Spread'].rolling(30).mean()
    clean_data['Private_Repo_MA30'] = clean_data['Private_Repo_Spread'].rolling(30).mean()
    clean_data['Fed_Facility_Z'] = (
        (clean_data['Fed_Facility_MA30'] - clean_data['Fed_Facility_MA30'].mean())
        / clean_data['Fed_Facility_MA30'].std()
    )
    clean_data['Private_Repo_Z'] = (
        (clean_data['Private_Repo_MA30'] - clean_data['Private_Repo_MA30'].mean())
        / clean_data['Private_Repo_MA30'].std()
    )
    plot_data = clean_data.dropna(subset=['Fed_Facility_Z','Private_Repo_Z'])
    plot_data = plot_data.loc[str(start):str(end)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Fed_Facility_Z'],
                             name="Fed Facility to Repo Spreads", line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Private_Repo_Z'],
                             name="Private Repo Spreads", line=dict(color="#2E3A59", width=2)))
    for y_val in [-2, -1, 1, 2]:
        fig.add_hline(y=y_val, line_color='gray', line_dash='dash', opacity=0.6)
    fig.update_layout(
        title="Is the Stability Lower\nRate of Change",
        yaxis_title="Z-Score",
        xaxis_title="Date",
        yaxis_range=[-5, 5]
    )
    st.plotly_chart(fig, use_container_width=True)


### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ HOW DID LEVELS CHANGE ----------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_how_did_levels_change(start, end, **kwargs):
    sof = pdr.DataReader('SOFR', 'fred', start, end)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
               'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
    gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
    gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
    gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]
    base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
    tri_df = pd.DataFrame(requests.get(base_url + 'REPO-TRI_AR_OO-P').json(), columns=["date","value"])
    tri_df['date'] = pd.to_datetime(tri_df['date'])
    tri_df.set_index('date', inplace=True)
    dvp_df = pd.DataFrame(requests.get(base_url + 'REPO-DVP_AR_OO-P').json(), columns=["date","value"])
    dvp_df['date'] = pd.to_datetime(dvp_df['date'])
    dvp_df.set_index('date', inplace=True)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    fed_funds.index = pd.to_datetime(fed_funds.index)

    combined_data = merge_dfs([sof, rrp, gc_df, fed_funds, tri_df, dvp_df])
    combined_data.columns = ['SOFR','ON_RRP_Rate','BGCR','Fed_Funds','TGCR','DVP']
    clean_data = combined_data.dropna(subset=['SOFR','BGCR','TGCR','ON_RRP_Rate','Fed_Funds','DVP'])

    clean_data['Private_Repo_Avg'] = (clean_data['DVP'] + clean_data['TGCR']) / 2
    clean_data['Fed_Facility_Spread'] = clean_data['ON_RRP_Rate'] - clean_data['SOFR']
    clean_data['Private_Repo_Spread'] = clean_data['Private_Repo_Avg'] - clean_data['SOFR']
    clean_data['Fed_Facility_static_Z'] = (
        (clean_data['Fed_Facility_Spread'] - clean_data['Fed_Facility_Spread'].mean()) /
        clean_data['Fed_Facility_Spread'].std()
    )
    clean_data['Private_Repo_static_Z'] = (
        (clean_data['Private_Repo_Spread'] - clean_data['Private_Repo_Spread'].mean()) /
        clean_data['Private_Repo_Spread'].std()
    )
    plot_static_data = clean_data.dropna(subset=['Fed_Facility_static_Z','Private_Repo_static_Z'])
    plot_static_data = plot_static_data.loc[str(start):str(end)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_static_data.index, y=plot_static_data['Fed_Facility_static_Z'],
                             name="Fed Facility to Repo Spreads", line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=plot_static_data.index, y=plot_static_data['Private_Repo_static_Z'],
                             name="Private Repo Spreads", line=dict(color="#2E3A59", width=2)))
    for y_val in [-2, -1, 1, 2]:
        fig.add_hline(y=y_val, line_color='gray', line_dash='dash', opacity=0.6)
    fig.update_layout(
        title="Is the Stability Lower\nRate of Change",
        yaxis_title="Z-Score",
        xaxis_title="Date",
        yaxis_range=[-5,5],
        annotations=[
            dict(
                x=plot_static_data.index[-1], y=-4.7,
                text='<b>ie</b>', showarrow=False,
                font=dict(size=14, color='steelblue', family="Arial"),
                xanchor='right', yanchor='bottom'
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
