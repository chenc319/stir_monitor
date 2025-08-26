### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------------- AUCTIONS ------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------ ISSUANCE IN AUCTION BY SECURITY ------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_issuance_by_security(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
    auction_issuance_df = df[['record_date','security_type','total_accepted']].copy()
    auction_issuance_df['eom'] = auction_issuance_df['record_date'].dt.to_period('M').dt.to_timestamp('M')
    agg_monthly = auction_issuance_df.groupby(['eom', 'security_type'])['total_accepted'].sum().unstack(fill_value=0)
    agg_monthly = agg_monthly / 1e12
    agg_monthly = agg_monthly.loc[str(start):str(end)]
    colors = {'Bill':'#8ed6f8','Bond':'#008fd5','Note':'#ffc650'}

    # ### PLOT ###
    # plt.figure(figsize=(10, 6))
    # plt.plot(agg_monthly.index, agg_monthly.get('Bill', pd.Series(index=agg_monthly.index)), label='Bill',
    #          color='#8ed6f8')
    # plt.plot(agg_monthly.index, agg_monthly.get('Bond', pd.Series(index=agg_monthly.index)), label='Bond',
    #          color='#008fd5')
    # plt.plot(agg_monthly.index, agg_monthly.get('Note', pd.Series(index=agg_monthly.index)), label='Note',
    #          color='#ffc650')
    # plt.title("Issuance in Auction By Security", fontsize=20, fontweight='bold', pad=20)
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

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
### -------------------------------------- NET BILL ISSUANCE OF TOTAL ---------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_issuance(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 6))
    # plt.plot(bill_issuance.index,
    #          bill_issuance.get('4-Week', pd.Series(index=bill_issuance.index)), label='4-Week', color='#9bdaf6')
    # plt.plot(bill_issuance.index,
    #          bill_issuance.get('8-Week', pd.Series(index=bill_issuance.index)), label='8-Week', color='#4dc6c6')
    # plt.plot(bill_issuance.index,
    #          bill_issuance.get('13-Week', pd.Series(index=bill_issuance.index)), label='13-Week', color='#356c82')
    # plt.plot(bill_issuance.index,
    #          bill_issuance.get('26-Week', pd.Series(index=bill_issuance.index)), label='26-Week', color='#001f35')
    # plt.plot(bill_issuance.index,
    #          bill_issuance.get('52-Week', pd.Series(index=bill_issuance.index)), label='52-Week', color='#fbc430')
    # plt.title("Bill Issuances", fontsize=20, fontweight='bold', pad=20)
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

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
### -------------------------------------- NET NOTES ISSUANCE OF TOTAL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_issuance(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
    auction_issuance_df = df[['record_date','security_term','total_accepted']].copy()
    note_terms = ['2-Year','3-Year','5-Year','7-Year','10-Year']
    notes_issuance = auction_issuance_df[auction_issuance_df['security_term'].isin(note_terms)].copy()
    notes_issuance['eom'] = notes_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
    notes_issuance = notes_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    notes_issuance = notes_issuance.loc['2020-01-01':str(end)]
    note_colors = {'2-Year':'#9bdaf6','3-Year':'#4dc6c6','5-Year':'#356c82','7-Year':'#001f35','10-Year':'#fbc430'}

    # ### PLOT ###
    # plt.figure(figsize=(10, 6))
    # plt.plot(notes_issuance.index,
    #          notes_issuance.get('2-Year', pd.Series(index=notes_issuance.index)), label='2-Year', color='#9bdaf6')
    # plt.plot(notes_issuance.index,
    #          notes_issuance.get('3-Year', pd.Series(index=notes_issuance.index)), label='3-Year', color='#4dc6c6')
    # plt.plot(notes_issuance.index,
    #          notes_issuance.get('5-Year', pd.Series(index=notes_issuance.index)), label='5-Year', color='#356c82')
    # plt.plot(notes_issuance.index,
    #          notes_issuance.get('7-Year', pd.Series(index=notes_issuance.index)), label='7-Year', color='#001f35')
    # plt.plot(notes_issuance.index,
    #          notes_issuance.get('10-Year', pd.Series(index=notes_issuance.index)), label='10-Year', color='#fbc430')
    # plt.title("Notes Issuances", fontsize=20, fontweight='bold', pad=20)
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

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
### -------------------------------------- NET BONDS ISSUANCE OF TOTAL --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_issuance(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
    auction_issuance_df = df[['record_date','security_term','total_accepted']].copy()
    bond_terms = ['20-Year','30-Year']
    bonds_issuance = auction_issuance_df[auction_issuance_df['security_term'].isin(bond_terms)].copy()
    bonds_issuance['eom'] = bonds_issuance['record_date'].dt.to_period('M').dt.to_timestamp('M')
    bonds_issuance = bonds_issuance.groupby(['eom', 'security_term'])['total_accepted'].sum().unstack(fill_value=0) / 1e12
    bonds_issuance = bonds_issuance.loc['2020-01-01':str(end)]
    bond_colors = {'20-Year':'#9bdaf6','30-Year':'#fbc430'}

    # ### PLOT ###
    # plt.figure(figsize=(10, 6))
    # plt.plot(bonds_issuance.index,
    #          bonds_issuance.get('20-Year', pd.Series(index=bonds_issuance.index)), label='20-Year', color='#9bdaf6')
    # plt.plot(bonds_issuance.index,
    #          bonds_issuance.get('30-Year', pd.Series(index=bonds_issuance.index)), label='30-Year', color='#fbc430')
    # plt.title("Bonds Issuances", fontsize=20, fontweight='bold', pad=20)
    # plt.ylabel("Dollars (Trillions)")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

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
### ----------------------------------- BILLS DEALER TO NON DEALER RATIO ------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_dealer_ratio(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(bills_merge.index, bills_merge['4week'],
    #          label='4-Week', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(bills_merge.index, bills_merge['8week'],
    #          label='8-Week', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(bills_merge.index, bills_merge['13week'],
    #          label='13-Week', color='#233852', lw=2)  # dark blue
    # plt.plot(bills_merge.index, bills_merge['26week'],
    #          label='26-Week', color='#F5B820', lw=2)  # yellow/orange
    # plt.plot(bills_merge.index, bills_merge['52week'],
    #          label='52-Week', color='#E69B93', lw=2)  # salmon/pink
    # plt.ylabel("Ratio")
    # plt.title("Bills Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
### ------------------------------------ BONDS DEALER TO NON DEALER RATIO ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_dealer_ratio(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(bonds_merge.index, bonds_merge['20year'],
    #          label='20-Year', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(bonds_merge.index, bonds_merge['30year'],
    #          label='30-Year', color='#4CD0E9', lw=2)  # cyan
    # plt.ylabel("Ratio")
    # plt.title("Bonds Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
### ------------------------------------ BONDS DEALER TO NON DEALER RATIO ------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_dealer_ratio(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(notes_merge.index, notes_merge['2year'],
    #          label='2-Year', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(notes_merge.index, notes_merge['3year'],
    #          label='3-Year', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(notes_merge.index, notes_merge['5year'],
    #          label='5-Year', color='#233852', lw=2)  # dark blue
    # plt.plot(notes_merge.index, notes_merge['7year'],
    #          label='7-Year', color='#F5B820', lw=2)  # yellow/orange
    # plt.plot(notes_merge.index, notes_merge['10year'],
    #          label='10-Year', color='#E69B93', lw=2)  # salmon/pink
    # plt.ylabel("Ratio")
    # plt.title("Bonds Dealer to Non Dealer Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
### --------------------------------------- BILLS BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bills_bid_to_cover(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(bills_merge.index, bills_merge['4week'],
    #          label='4-Week', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(bills_merge.index, bills_merge['8week'],
    #          label='8-Week', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(bills_merge.index, bills_merge['13week'],
    #          label='13-Week', color='#233852', lw=2)  # dark blue
    # plt.plot(bills_merge.index, bills_merge['26week'],
    #          label='26-Week', color='#F5B820', lw=2)  # yellow/orange
    # plt.plot(bills_merge.index, bills_merge['52week'],
    #          label='52-Week', color='#E69B93', lw=2)  # salmon/pink
    # plt.ylabel("Ratio")
    # plt.title("Bills Bid to Cover Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
### --------------------------------------- BONDS BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_bonds_bid_to_cover(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(bonds_merge.index, bonds_merge['20year'],
    #          label='20-Year', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(bonds_merge.index, bonds_merge['30year'],
    #          label='30-Year', color='#4CD0E9', lw=2)  # cyan
    # plt.ylabel("Ratio")
    # plt.title("Bonds Bid to Cover Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
### --------------------------------------- NOTES BID TO COVER RATIO ----------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_notes_bid_to_cover(start, end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        df = pickle.load(file)
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

    # ### PLOT ###
    # plt.figure(figsize=(10, 7))
    # plt.plot(notes_merge.index, notes_merge['2year'],
    #          label='2-Year', color='#9DDCF9', lw=2)  # light blue
    # plt.plot(notes_merge.index, notes_merge['3year'],
    #          label='3-Year', color='#4CD0E9', lw=2)  # cyan
    # plt.plot(notes_merge.index, notes_merge['5year'],
    #          label='5-Year', color='#233852', lw=2)  # dark blue
    # plt.plot(notes_merge.index, notes_merge['7year'],
    #          label='7-Year', color='#F5B820', lw=2)  # yellow/orange
    # plt.plot(notes_merge.index, notes_merge['10year'],
    #          label='10-Year', color='#E69B93', lw=2)  # salmon/pink
    # plt.ylabel("Ratio")
    # plt.title("Bonds Bid to Cover Ratio", fontsize=17, fontweight="bold")
    # plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=6)
    # plt.tight_layout()
    # plt.show()

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
