import pandas as pd
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), array_of_dfs)

# Helper: loads and preprocess Treasury auction data only once per run
@st.cache_data(show_spinner=False)
def load_auction_data():
    url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?"
           "filter=record_date:gte:2000-08-16,record_date:lte:2025-08-15"
           "&sort=-auction_date,-issue_date,maturity_date&page[size]=10000")
    resp = requests.get(url).json()
    df = pd.DataFrame(resp['data'])
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['total_accepted'] = pd.to_numeric(df['total_accepted'], errors='coerce')
    return df

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- ISSUANCE IN AUCTION BY SECURITY -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_issuance_by_security(start, end, **kwargs):
    df = load_auction_data()
    auction_issuance_df = df[['record_date','security_type','total_accepted']].copy()
    auction_issuance_df['eom'] = auction_issuance_df['record_date'].dt.to_period('M').dt.to_timestamp('M')
    agg_monthly = auction_issuance_df.groupby(['eom', 'security_type'])['total_accepted'].sum().unstack(fill_value=0)
    agg_monthly = agg_monthly / 1e12
    agg_monthly = agg_monthly.loc[str(start):str(end)]
    colors = {'Bill':'#8ed6f8','Bond':'#008fd5','Note':'#ffc650'}

    fig = go.Figure()
    for sec in ['Bill','Bond','Note']:
        fig.add_trace(go.Scatter(x=agg_monthly.index, y=agg_monthly.get(sec, pd.Series(index=agg_monthly.index)),
                                 name=sec, line=dict(color=colors[sec], width=2)))
    fig.update_layout(
        title='Issuance in Auction By Security',
        yaxis_title='Dollars (Trillions)',
        xaxis_title='Date'
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------- NET BILL ISSUANCE OF TOTAL ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_issuance(start, end, **kwargs):
    df = load_auction_data()
    auction_issuance_df = df[['record_date','security_term','total_accepted']].copy()
    bill_terms = ['4-Week','8-Week','13-Week','26-Week','52-Week']
    bill_issuance = auction_issuance_df[auction_issuance_df['security_term'].isin(bill_terms)].copy()
    bill_issuance['eom'] = bill_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
    bill_issuance = bill_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    bill_issuance = bill_issuance.loc['2020-01-01':str(end)]
    bill_colors = {
        '4-Week':'#9bdaf6','8-Week':'#4dc6c6','13-Week':'#356c82',
        '26-Week':'#001f35','52-Week':'#fbc430'
    }
    fig = go.Figure()
    for col in bill_terms:
        fig.add_trace(go.Scatter(x=bill_issuance.index, y=bill_issuance.get(col, pd.Series(index=bill_issuance.index)),
                                 name=col, line=dict(color=bill_colors[col], width=2)))
    fig.update_layout(
        title="Bill Issuances",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ NET NOTES ISSUANCE OF TOTAL ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_issuance(start, end, **kwargs):
    df = load_auction_data()
    auction_issuance_df = df[['record_date','security_term','total_accepted']].copy()
    note_terms = ['2-Year','3-Year','5-Year','7-Year','10-Year']
    notes_issuance = auction_issuance_df[auction_issuance_df['security_term'].isin(note_terms)].copy()
    notes_issuance['eom'] = notes_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
    notes_issuance = notes_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    notes_issuance = notes_issuance.loc['2020-01-01':str(end)]
    note_colors = {'2-Year':'#9bdaf6','3-Year':'#4dc6c6','5-Year':'#356c82','7-Year':'#001f35','10-Year':'#fbc430'}
    fig = go.Figure()
    for col in note_terms:
        fig.add_trace(go.Scatter(x=notes_issuance.index, y=notes_issuance.get(col, pd.Series(index=notes_issuance.index)),
                                 name=col, line=dict(color=note_colors[col], width=2)))
    fig.update_layout(
        title="Notes Issuances",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------ NET BONDS ISSUANCE OF TOTAL ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_issuance(start, end, **kwargs):
    df = load_auction_data()
    auction_issuance_df = df[['record_date','security_term','total_accepted']].copy()
    bond_terms = ['20-Year','30-Year']
    bonds_issuance = auction_issuance_df[auction_issuance_df['security_term'].isin(bond_terms)].copy()
    bonds_issuance['eom'] = bonds_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
    bonds_issuance = bonds_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    bonds_issuance = bonds_issuance.loc['2020-01-01':str(end)]
    bond_colors = {'20-Year':'#9bdaf6','30-Year':'#fbc430'}
    fig = go.Figure()
    for col in bond_terms:
        fig.add_trace(go.Scatter(x=bonds_issuance.index, y=bonds_issuance.get(col, pd.Series(index=bonds_issuance.index)),
                                 name=col, line=dict(color=bond_colors[col], width=2)))
    fig.update_layout(
        title="Bonds Issuances",
        yaxis_title="Dollars (Trillions)",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- BILLS DEALER TO NON DEALER RATIO -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_dealer_ratio(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term',
               'primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']].copy()
    for col in ['primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data['dealer_to_non_dealer_ratio'] = data['primary_dealer_accepted'] / (
        data['indirect_bidder_accepted'] + data['direct_bidder_accepted']
    )
    bills = data[data['security_type']=='Bill']
    bill_terms = ['4-Week','8-Week','13-Week','26-Week','52-Week']
    out = []
    for term in bill_terms:
        ratio_series = bills[bills['security_term']==term].set_index('record_date')['dealer_to_non_dealer_ratio']
        df_term = pd.DataFrame(ratio_series).resample('ME').last().rename(columns={'dealer_to_non_dealer_ratio':term})
        out.append(df_term)
    bills_merge = merge_dfs(out).ffill().dropna().loc[str(start):str(end)]
    colors = {'4-Week':'#9DDCF9','8-Week':'#4CD0E9','13-Week':'#233852','26-Week':'#F5B820','52-Week':'#E69B93'}
    fig = go.Figure()
    for col in bill_terms:
        fig.add_trace(go.Scatter(x=bills_merge.index, y=bills_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Bills Dealer to Non Dealer Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- BONDS DEALER TO NON DEALER RATIO -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_dealer_ratio(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term',
               'primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']].copy()
    for col in ['primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data['dealer_to_non_dealer_ratio'] = data['primary_dealer_accepted'] / (
        data['indirect_bidder_accepted'] + data['direct_bidder_accepted']
    )
    bonds = data[data['security_type']=='Bond']
    bond_terms = ['20-Year','30-Year']
    out = []
    for term in bond_terms:
        ratio_series = bonds[bonds['security_term']==term].set_index('record_date')['dealer_to_non_dealer_ratio']
        df_term = pd.DataFrame(ratio_series).resample('ME').last().rename(columns={'dealer_to_non_dealer_ratio':term})
        out.append(df_term)
    bonds_merge = merge_dfs(out).dropna().loc[str(start):str(end)]
    colors = {'20-Year':'#9DDCF9','30-Year':'#4CD0E9'}
    fig = go.Figure()
    for col in bond_terms:
        fig.add_trace(go.Scatter(x=bonds_merge.index, y=bonds_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Bonds Dealer to Non Dealer Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- NOTES DEALER TO NON DEALER RATIO -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_dealer_ratio(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term',
               'primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']].copy()
    for col in ['primary_dealer_accepted','indirect_bidder_accepted','direct_bidder_accepted']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data['dealer_to_non_dealer_ratio'] = data['primary_dealer_accepted'] / (
        data['indirect_bidder_accepted'] + data['direct_bidder_accepted']
    )
    notes = data[data['security_type']=='Note']
    note_terms = ['2-Year','3-Year','5-Year','7-Year','10-Year']
    out = []
    for term in note_terms:
        ratio_series = notes[notes['security_term']==term].set_index('record_date')['dealer_to_non_dealer_ratio']
        df_term = pd.DataFrame(ratio_series).resample('ME').last().rename(columns={'dealer_to_non_dealer_ratio':term})
        out.append(df_term)
    notes_merge = merge_dfs(out).ffill().dropna().loc[str(start):str(end)]
    colors = {'2-Year':'#9DDCF9','3-Year':'#4CD0E9','5-Year':'#233852','7-Year':'#F5B820','10-Year':'#E69B93'}
    fig = go.Figure()
    for col in note_terms:
        fig.add_trace(go.Scatter(x=notes_merge.index, y=notes_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Notes Dealer to Non Dealer Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- BILLS BID TO COVER RATIO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_bid_to_cover(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term','bid_to_cover_ratio']].copy()
    for col in ['bid_to_cover_ratio']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    bills = data[data['security_type']=='Bill']
    bill_terms = ['4-Week','8-Week','13-Week','26-Week','52-Week']
    out = []
    for term in bill_terms:
        series = bills[bills['security_term']==term].set_index('record_date')['bid_to_cover_ratio']
        df_term = pd.DataFrame(series).resample('W').last().rename(columns={'bid_to_cover_ratio':term})
        out.append(df_term)
    bills_merge = merge_dfs(out).ffill().dropna().loc[str(start):str(end)]
    colors = {'4-Week':'#9DDCF9','8-Week':'#4CD0E9','13-Week':'#233852','26-Week':'#F5B820','52-Week':'#E69B93'}
    fig = go.Figure()
    for col in bill_terms:
        fig.add_trace(go.Scatter(x=bills_merge.index, y=bills_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Bills Bid to Cover Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- BONDS BID TO COVER RATIO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_bid_to_cover(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term','bid_to_cover_ratio']].copy()
    for col in ['bid_to_cover_ratio']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    bonds = data[data['security_type']=='Bond']
    bond_terms = ['20-Year','30-Year']
    out = []
    for term in bond_terms:
        series = bonds[bonds['security_term']==term].set_index('record_date')['bid_to_cover_ratio']
        df_term = pd.DataFrame(series).resample('ME').last().rename(columns={'bid_to_cover_ratio':term})
        out.append(df_term)
    bonds_merge = merge_dfs(out).dropna().loc[str(start):str(end)]
    colors = {'20-Year':'#9DDCF9','30-Year':'#4CD0E9'}
    fig = go.Figure()
    for col in bond_terms:
        fig.add_trace(go.Scatter(x=bonds_merge.index, y=bonds_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Bonds Bid to Cover Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)

### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------- NOTES BID TO COVER RATIO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_bid_to_cover(start, end, **kwargs):
    df = load_auction_data()
    data = df[['record_date','security_type','security_term','bid_to_cover_ratio']].copy()
    for col in ['bid_to_cover_ratio']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    notes = data[data['security_type']=='Note']
    note_terms = ['2-Year','3-Year','5-Year','7-Year','10-Year']
    out = []
    for term in note_terms:
        series = notes[notes['security_term']==term].set_index('record_date')['bid_to_cover_ratio']
        df_term = pd.DataFrame(series).resample('ME').last().rename(columns={'bid_to_cover_ratio':term})
        out.append(df_term)
    notes_merge = merge_dfs(out).ffill().dropna().loc[str(start):str(end)]
    colors = {'2-Year':'#9DDCF9','3-Year':'#4CD0E9','5-Year':'#233852','7-Year':'#F5B820','10-Year':'#E69B93'}
    fig = go.Figure()
    for col in note_terms:
        fig.add_trace(go.Scatter(x=notes_merge.index, y=notes_merge[col],
                                 name=col, line=dict(color=colors[col], width=2)))
    fig.update_layout(
        title="Notes Bid to Cover Ratio",
        yaxis_title="Ratio",
        xaxis_title="Date"
    )
    st.plotly_chart(fig, use_container_width=True)
