# app_auctions.py

import pandas as pd
import requests
import functools as ft
import streamlit as st
import plotly.graph_objs as go

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True,
                                                  how='outer'), array_of_dfs)

@st.cache_data(ttl=3600)
def get_auction_data():
    url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/"
           "accounting/od/auctions_query?filter=record_date:gte:2000-08-16,"
           "record_date:lte:2025-08-15&sort=-auction_date,-issue_date,"
           "maturity_date&page[size]=10000")
    resp = requests.get(url).json()
    return pd.DataFrame(resp['data'])

#-------------------------------------------------------
# Issuance by Security
#-------------------------------------------------------
def plot_issuance_by_security(start, end):
    df = get_auction_data()
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['total_accepted'] = pd.to_numeric(df['total_accepted'], errors='coerce')
    df['eom'] = df['record_date'].dt.to_period('M').dt.to_timestamp('M')
    agg_monthly = df.groupby(['eom', 'security_type'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    agg_monthly = agg_monthly.loc[(agg_monthly.index >= pd.to_datetime(start)) & (agg_monthly.index <= pd.to_datetime(end))]
    fig = go.Figure()
    for sec, color in zip(['Bill', 'Bond', 'Note'], ['#8ed6f8', '#008fd5', '#ffc650']):
        if sec in agg_monthly.columns:
            fig.add_trace(go.Scatter(x=agg_monthly.index, y=agg_monthly[sec], name=sec, line=dict(color=color)))
    fig.update_layout(title="Issuance in Auction By Security", yaxis_title="Dollars (Trillions)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
# Helper to build dealer ratio frames
#-------------------------------------------------------
def build_ratio(df, sec_type, terms, freq='ME'):
    subset = df[df['security_type'] == sec_type].copy()
    subset['record_date'] = pd.to_datetime(subset['record_date'])
    merges = []
    for name in terms:
        filt = subset[subset['security_term'] == name]
        r = pd.DataFrame(filt['dealer_to_non_dealer_ratio'])
        r.index = filt['record_date']  # ensure datetime index
        r = r.sort_index()
        colname = (name.split('-')[0] + ('week' if 'Week' in name else 'year')).lower()
        r.columns = [colname]
        merges.append(r.resample(freq).last())
    return merge_dfs(merges).ffill().dropna()

def build_btc(df, sec_type, terms, freq='ME'):
    subset = df[df['security_type'] == sec_type].copy()
    subset['record_date'] = pd.to_datetime(subset['record_date'])
    merges = []
    for name in terms:
        filt = subset[subset['security_term'] == name]
        r = pd.DataFrame(filt['bid_to_cover_ratio'])
        r.index = filt['record_date']
        r = r.sort_index()
        colname = (name.split('-')[0] + ('week' if 'Week' in name else 'year')).lower()
        r.columns = [colname]
        merges.append(r.resample(freq).last())
    return merge_dfs(merges).ffill().dropna()

#-------------------------------------------------------
# Dealer Ratios
#-------------------------------------------------------
def plot_bills_dealer_ratio(start, end):
    df = get_auction_data()
    cols = ['primary_dealer_accepted', 'indirect_bidder_accepted', 'direct_bidder_accepted']
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    df['dealer_to_non_dealer_ratio'] = df['primary_dealer_accepted'] / (df['indirect_bidder_accepted'] + df['direct_bidder_accepted'])
    bills_merge = build_ratio(df, 'Bill', ['4-Week','8-Week','13-Week','26-Week','52-Week'])
    bills_merge = bills_merge.loc[(bills_merge.index >= pd.to_datetime(start)) & (bills_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    fig = go.Figure()
    for col, color in zip(bills_merge.columns, colors):
        fig.add_trace(go.Scatter(x=bills_merge.index, y=bills_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Bills Dealer to Non Dealer Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_bonds_dealer_ratio(start, end):
    df = get_auction_data()
    cols = ['primary_dealer_accepted', 'indirect_bidder_accepted', 'direct_bidder_accepted']
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    df['dealer_to_non_dealer_ratio'] = df['primary_dealer_accepted'] / (df['indirect_bidder_accepted'] + df['direct_bidder_accepted'])
    bonds_merge = build_ratio(df, 'Bond', ['20-Year','30-Year'])
    bonds_merge = bonds_merge.loc[(bonds_merge.index >= pd.to_datetime(start)) & (bonds_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9']
    fig = go.Figure()
    for col, color in zip(bonds_merge.columns, colors):
        fig.add_trace(go.Scatter(x=bonds_merge.index, y=bonds_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Bonds Dealer to Non Dealer Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_notes_dealer_ratio(start, end):
    df = get_auction_data()
    cols = ['primary_dealer_accepted', 'indirect_bidder_accepted', 'direct_bidder_accepted']
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    df['dealer_to_non_dealer_ratio'] = df['primary_dealer_accepted'] / (df['indirect_bidder_accepted'] + df['direct_bidder_accepted'])
    notes_merge = build_ratio(df, 'Note', ['2-Year','3-Year','5-Year','7-Year','10-Year'])
    notes_merge = notes_merge.loc[(notes_merge.index >= pd.to_datetime(start)) & (notes_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    fig = go.Figure()
    for col, color in zip(notes_merge.columns, colors):
        fig.add_trace(go.Scatter(x=notes_merge.index, y=notes_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Notes Dealer to Non Dealer Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
# Bid to Cover Ratios
#-------------------------------------------------------
def plot_bills_bid_to_cover(start, end):
    df = get_auction_data()
    bills_merge = build_btc(df, 'Bill', ['4-Week','8-Week','13-Week','26-Week','52-Week'], freq='W')
    bills_merge = bills_merge.loc[(bills_merge.index >= pd.to_datetime(start)) & (bills_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    fig = go.Figure()
    for col, color in zip(bills_merge.columns, colors):
        fig.add_trace(go.Scatter(x=bills_merge.index, y=bills_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Bills Bid to Cover Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_bonds_bid_to_cover(start, end):
    df = get_auction_data()
    bonds_merge = build_btc(df, 'Bond', ['20-Year','30-Year'])
    bonds_merge = bonds_merge.loc[(bonds_merge.index >= pd.to_datetime(start)) & (bonds_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9']
    fig = go.Figure()
    for col, color in zip(bonds_merge.columns, colors):
        fig.add_trace(go.Scatter(x=bonds_merge.index, y=bonds_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Bonds Bid to Cover Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_notes_bid_to_cover(start, end):
    df = get_auction_data()
    notes_merge = build_btc(df, 'Note', ['2-Year','3-Year','5-Year','7-Year','10-Year'])
    notes_merge = notes_merge.loc[(notes_merge.index >= pd.to_datetime(start)) & (notes_merge.index <= pd.to_datetime(end))]
    colors = ['#9DDCF9', '#4CD0E9', '#233852', '#F5B820', '#E69B93']
    fig = go.Figure()
    for col, color in zip(notes_merge.columns, colors):
        fig.add_trace(go.Scatter(x=notes_merge.index, y=notes_merge[col], name=col, line=dict(color=color)))
    fig.update_layout(title="Notes Bid to Cover Ratio", yaxis_title="Ratio", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
# Individual Issuance group plots (Bills/Notes/Bonds)
#-------------------------------------------------------
def plot_bills_issuance(start, end):
    df = get_auction_data()
    mask = df['security_term'].isin(['4-Week','8-Week','13-Week','26-Week','52-Week'])
    bill = df.loc[mask].copy()
    bill['record_date'] = pd.to_datetime(bill['record_date'])
    bill['total_accepted'] = pd.to_numeric(bill['total_accepted'], errors='coerce')
    bill['eom'] = bill['record_date'].dt.to_period('M').dt.to_timestamp('M')
    bill_issuance = bill.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    bill_issuance = bill_issuance.loc['2020-01-01':]
    bill_issuance = bill_issuance.loc[(bill_issuance.index >= pd.to_datetime(start)) & (bill_issuance.index <= pd.to_datetime(end))]
    colors = ['#9bdaf6', '#4dc6c6', '#356c82', '#001f35', '#fbc430']
    fig = go.Figure()
    for sec, color in zip(['4-Week','8-Week','13-Week','26-Week','52-Week'], colors):
        if sec in bill_issuance.columns:
            fig.add_trace(go.Scatter(x=bill_issuance.index, y=bill_issuance[sec], name=sec, line=dict(color=color)))
    fig.update_layout(title="Bill Issuances", yaxis_title="Dollars (Trillions)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_notes_issuance(start, end):
    df = get_auction_data()
    mask = df['security_term'].isin(['2-Year','3-Year','5-Year','7-Year','10-Year'])
    notes = df.loc[mask].copy()
    notes['record_date'] = pd.to_datetime(notes['record_date'])
    notes['total_accepted'] = pd.to_numeric(notes['total_accepted'], errors='coerce')
    notes['eom'] = notes['record_date'].dt.to_period('M').dt.to_timestamp('M')
    notes_issuance = notes.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    notes_issuance = notes_issuance.loc['2020-01-01':]
    notes_issuance = notes_issuance.loc[(notes_issuance.index >= pd.to_datetime(start)) & (notes_issuance.index <= pd.to_datetime(end))]
    colors = ['#9bdaf6', '#4dc6c6', '#356c82', '#001f35', '#fbc430']
    fig = go.Figure()
    for sec, color in zip(['2-Year','3-Year','5-Year','7-Year','10-Year'], colors):
        if sec in notes_issuance.columns:
            fig.add_trace(go.Scatter(x=notes_issuance.index, y=notes_issuance[sec], name=sec, line=dict(color=color)))
    fig.update_layout(title="Notes Issuances", yaxis_title="Dollars (Trillions)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def plot_bonds_issuance(start, end):
    df = get_auction_data()
    mask = df['security_term'].isin(['20-Year', '30-Year'])
    bonds = df.loc[mask].copy()
    bonds['record_date'] = pd.to_datetime(bonds['record_date'])
    bonds['total_accepted'] = pd.to_numeric(bonds['total_accepted'], errors='coerce')
    bonds['eom'] = bonds['record_date'].dt.to_period('M').dt.to_timestamp('M')
    bonds_issuance = bonds.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    bonds_issuance = bonds_issuance.loc['2020-01-01':]
    bonds_issuance = bonds_issuance.loc[(bonds_issuance.index >= pd.to_datetime(start)) & (bonds_issuance.index <= pd.to_datetime(end))]
    colors = ['#9bdaf6', '#fbc430']
    fig = go.Figure()
    for sec, color in zip(['20-Year','30-Year'], colors):
        if sec in bonds_issuance.columns:
            fig.add_trace(go.Scatter(x=bonds_issuance.index, y=bonds_issuance[sec], name=sec, line=dict(color=color)))
    fig.update_layout(title="Bonds Issuances", yaxis_title="Dollars (Trillions)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
