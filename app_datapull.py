### ---------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------- REFRESH DATA FUNCTION ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pandas_datareader import data as pdr
from pathlib import Path
import os
import pickle
from io import StringIO
import ftplib
import io
import pandas as pd
DATA_DIR = os.getenv('DATA_DIR', 'data')

### FUNCTIONS ###

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left,
                                            right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'),
                     array_of_dfs)


def refresh_all_data():
    ### NEW DATES ###
    start = '1990-01-01'
    end = pd.to_datetime('today')
    ### RATES ###
    iorb = pdr.DataReader('IORB', 'fred', start, end)
    with open(Path(DATA_DIR) / 'iorb.pkl', 'wb') as file:
        pickle.dump(iorb, file)
    fed_funds = pdr.DataReader('EFFR', 'fred', start, end)
    with open(Path(DATA_DIR) / 'fed_funds.pkl', 'wb') as file:
        pickle.dump(fed_funds, file)
    sofr = pdr.DataReader('SOFR', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr.pkl', 'wb') as file:
        pickle.dump(sofr, file)
    sofr_1m_avg = pdr.DataReader('SOFR30DAYAVG', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr_1m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_1m_avg, file)
    sofr_3m_avg = pdr.DataReader('SOFR90DAYAVG', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr_3m_avg.pkl', 'wb') as file:
        pickle.dump(sofr_3m_avg, file)
    rrp = pdr.DataReader('RRPONTSYAWARD', 'fred', start, end)
    with open(Path(DATA_DIR) / 'rrp.pkl', 'wb') as file:
        pickle.dump(rrp, file)
    def ofr_to_df(mnemonic):
        base_url = 'https://data.financialresearch.gov/v1/series/timeseries?mnemonic='
        df = pd.DataFrame(requests.get(base_url + mnemonic).json(), columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')

    dvp_df = ofr_to_df('REPO-DVP_AR_OO-P')
    with open(Path(DATA_DIR) / 'dvp_df.pkl', 'wb') as file:
        pickle.dump(dvp_df, file)
    gcf_df = ofr_to_df('REPO-GCF_AR_AG-P')
    with open(Path(DATA_DIR) / 'gcf_df.pkl', 'wb') as file:
        pickle.dump(gcf_df, file)
    tri_df = ofr_to_df('REPO-TRI_AR_OO-P')
    with open(Path(DATA_DIR) / 'tri_df.pkl', 'wb') as file:
        pickle.dump(tri_df, file)
    term1w_df = ofr_to_df('REPO-TRI_AR_LE30-P')
    with open(Path(DATA_DIR) / 'term1w_df.pkl', 'wb') as file:
        pickle.dump(term1w_df, file)
    sofr1 = pdr.DataReader('SOFR1', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr1.pkl', 'wb') as file:
        pickle.dump(sofr1, file)
    sofr25 = pdr.DataReader('SOFR25', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr25.pkl', 'wb') as file:
        pickle.dump(sofr25, file)
    sofr75 = pdr.DataReader('SOFR75', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr75.pkl', 'wb') as file:
        pickle.dump(sofr75, file)
    sofr99 = pdr.DataReader('SOFR99', 'fred', start, end)
    with open(Path(DATA_DIR) / 'sofr99.pkl', 'wb') as file:
        pickle.dump(sofr99, file)
    gc_rate = ('https://markets.newyorkfed.org/api/rates/secured/bgcr/search.'
               'json?startDate=2014-08-01&endDate=2025-08-11&type=rate')
    gc_df = pd.DataFrame(requests.get(gc_rate).json()['refRates'])
    gc_df.index = pd.to_datetime(gc_df['effectiveDate'].values)
    gc_df = pd.DataFrame(gc_df['percentRate']).iloc[::-1]
    with open(Path(DATA_DIR) / 'gc_df.pkl', 'wb') as file:
        pickle.dump(gc_df, file)

    ### VOLUME ###
    treasury = pdr.DataReader('TREAST', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'treasury.pkl', 'wb') as file:
        pickle.dump(treasury, file)
    mbs = pdr.DataReader('WSHOMCB', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'mbs.pkl', 'wb') as file:
        pickle.dump(mbs, file)
    reserves = pdr.DataReader('WRESBAL', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'reserves.pkl', 'wb') as file:
        pickle.dump(reserves, file)
    tga = pdr.DataReader('WTREGEN', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'tga.pkl', 'wb') as file:
        pickle.dump(tga, file)
    rrp_on_volume = pdr.DataReader('RRPONTSYD', 'fred', start, end) * 1e9
    with open(Path(DATA_DIR) / 'rrp_on_volume.pkl', 'wb') as file:
        pickle.dump(rrp_on_volume, file)
    rrp_volume = pdr.DataReader('WLRRAL', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'rrp_volume.pkl', 'wb') as file:
        pickle.dump(rrp_volume, file)
    tri_volume_df = ofr_to_df('REPO-TRI_TV_TOT-P')
    with open(Path(DATA_DIR) / 'tri_volume_df.pkl', 'wb') as file:
        pickle.dump(tri_volume_df, file)
    gcf_volume_df = ofr_to_df('REPO-GCF_TV_TOT-P')
    with open(Path(DATA_DIR) / 'gcf_volume_df.pkl', 'wb') as file:
        pickle.dump(gcf_volume_df, file)
    dvp_volume_df = ofr_to_df('REPO-DVP_TV_TOT-P')
    with open(Path(DATA_DIR) / 'dvp_volume_df.pkl', 'wb') as file:
        pickle.dump(dvp_volume_df, file)
    fed_action = pdr.DataReader('WALCL', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'fed_action.pkl', 'wb') as file:
        pickle.dump(fed_action, file)
    foreign_rrp = pdr.DataReader('WREPOFOR', 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'foreign_rrp.pkl', 'wb') as file:
        pickle.dump(foreign_rrp, file)


    mmf_repo = ofr_to_df('MMF-MMF_RP_TOT-M')
    with open(Path(DATA_DIR) / 'mmf_repo.pkl', 'wb') as file:
        pickle.dump(mmf_repo, file)
    mmf_total = ofr_to_df('MMF-MMF_TOT-M')
    with open(Path(DATA_DIR) / 'mmf_total.pkl', 'wb') as file:
        pickle.dump(mmf_total, file)
    mmf_us_ts = ofr_to_df('MMF-MMF_T_TOT-M')
    with open(Path(DATA_DIR) / 'mmf_us_ts.pkl', 'wb') as file:
        pickle.dump(mmf_us_ts, file)


    ### SOMA HOLDINGS ###
    url = 'https://markets.newyorkfed.org/api/soma/summary.json'
    response = requests.get(url)
    data = response.json()
    soma_holdings = pd.DataFrame(data['soma']['summary'])
    soma_holdings.index = pd.to_datetime(soma_holdings['asOfDate'].values)
    soma_holdings.drop(['asOfDate', 'total'], axis=1, inplace=True)
    soma_holdings = soma_holdings.apply(pd.to_numeric)
    with open(Path(DATA_DIR) / 'soma_holdings.pkl', 'wb') as file:
        pickle.dump(soma_holdings, file)

    ### FED REPO OPERATIONS ###
    repo_url = 'https://markets.newyorkfed.org/api/rp/repo/all/results/last/999.json'
    response = requests.get(repo_url)
    data = response.json()
    repo_fed_df = pd.DataFrame(data['repo']['operations'])
    with open(Path(DATA_DIR) / 'repo_fed_df.pkl', 'wb') as file:
        pickle.dump(repo_fed_df, file)

    ### FED RRP OPERATIONS ###
    rrp_url = 'https://markets.newyorkfed.org/api/rp/reverserepo/all/results/last/999.json'
    response = requests.get(rrp_url)
    data = response.json()
    rrp_fed_df = pd.DataFrame(data['repo']['operations'])
    with open(Path(DATA_DIR) / 'rrp_fed_df.pkl', 'wb') as file:
        pickle.dump(rrp_fed_df, file)

    ### MMF REPO ###
    mmf_repo_url = ('https://www.financialresearch.gov/money-market-funds'
                    '/data/repo_activity_collateral/data.json')
    mmf_repo_allocations = pd.DataFrame(requests.get(mmf_repo_url).json()['datatable']['values'],
                                        columns=['Date', 'Other Repo', 'Agency Repo', 'Treasury Repo'])
    mmf_repo_allocations.index = pd.to_datetime(mmf_repo_allocations['Date'].values)
    mmf_repo_allocations.drop('Date', axis=1, inplace=True)
    with open(Path(DATA_DIR) / 'mmf_repo_allocations.pkl', 'wb') as file:
        pickle.dump(mmf_repo_allocations, file)

    ### MMF INVOLVEMENT IN REPO ###
    mmf_involvement_on_repo = pd.DataFrame(requests.get('https://data.financialresearch.gov/'
                                                        'v1/series/timeseries?mnemonic=MMF-MMF_RP_OO-M').json(),
                                           columns=['Date', 'Values'])
    mmf_involvement_on_repo.index = pd.to_datetime(mmf_involvement_on_repo['Date'].values)
    mmf_involvement_on_repo.drop('Date', axis=1, inplace=True)
    with open(Path(DATA_DIR) / 'mmf_involvement_on_repo.pkl', 'wb') as file:
        pickle.dump(mmf_involvement_on_repo, file)

    ### CFTC DATA ###
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=60000"
    response = requests.get(url)
    cftc_all_futures = pd.read_csv(StringIO(response.text))
    cftc_all_futures.columns
    cftc_all_futures.index = pd.to_datetime(cftc_all_futures['report_date_as_yyyy_mm_dd'].values)
    cftc_all_futures.drop('report_date_as_yyyy_mm_dd', axis=1)
    with open(Path(DATA_DIR) / 'cftc_all_futures.pkl', 'wb') as file:
        pickle.dump(cftc_all_futures, file)

    ### REPO LIABILITIES ###
    brokers_dealers_repo_liabilities = pdr.DataReader('BOGZ1FL662151003Q',
                                          'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'brokers_dealers_repo_liabilities.pkl', 'wb') as file:
        pickle.dump(brokers_dealers_repo_liabilities, file)
    hedge_funds_liabilities = pdr.DataReader('BOGZ1FL622151005Q',
                                 'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'hedge_funds_liabilities.pkl', 'wb') as file:
        pickle.dump(hedge_funds_liabilities, file)
    reit_liabilities = pdr.DataReader('BOGZ1FL642151073Q',
                          'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'reit_liabilities.pkl', 'wb') as file:
        pickle.dump(reit_liabilities, file)

    ### REPO ASSETS ###
    brokers_dealers_repo_assets = pdr.DataReader('BOGZ1FL662051003Q',
                                                      'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'brokers_dealers_repo_assets.pkl', 'wb') as file:
        pickle.dump(brokers_dealers_repo_assets, file)

    hedge_funds_assets = pdr.DataReader('BOGZ1FL622051003Q',
                                             'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'hedge_funds_assets.pkl', 'wb') as file:
        pickle.dump(hedge_funds_assets, file)

    mmf_assets = pdr.DataReader('BOGZ1FL632051000Q',
                                      'fred', start, end) * 1e6
    with open(Path(DATA_DIR) / 'mmf_assets.pkl', 'wb') as file:
        pickle.dump(mmf_assets, file)

    ### SPONSORED VOLUME ###
    pd_total_repo_url = 'https://markets.newyorkfed.org/api/pd/get/PDSORA-UTSETTOT.json'
    pd_total_repo = pd.DataFrame(requests.get(pd_total_repo_url).json()['pd']['timeseries']).drop('keyid', axis=1)
    pd_total_repo['value'] = pd.to_numeric(pd_total_repo['value'], errors='coerce')
    pd_total_repo.dropna(subset=['value'], inplace=True)
    pd_total_repo['asofdate'] = pd.to_datetime(pd_total_repo['asofdate'])
    pd_total_repo.index = pd_total_repo['asofdate'].values
    pd_total_repo.drop('asofdate', axis=1, inplace=True)
    pd_total_repo.columns = ['pd_total_repo']
    with open(Path(DATA_DIR) / 'pd_total_repo.pkl', 'wb') as file:
        pickle.dump(pd_total_repo, file)

    pd_nccbr_repo_on_url = 'https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSET.json'
    pd_nccbr_repo_on = pd.DataFrame(
        requests.get(pd_nccbr_repo_on_url).json()['pd']['timeseries']).drop('keyid',axis=1)
    pd_nccbr_repo_on['value'] = pd.to_numeric(pd_nccbr_repo_on['value'], errors='coerce')
    pd_nccbr_repo_on.dropna(subset=['value'], inplace=True)
    pd_nccbr_repo_on['asofdate'] = pd.to_datetime(pd_nccbr_repo_on['asofdate'])
    pd_nccbr_repo_on.index = pd_nccbr_repo_on['asofdate'].values
    pd_nccbr_repo_on.drop('asofdate', axis=1, inplace=True)
    pd_nccbr_repo_on.columns = ['pd_nccbr_on']
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_on.pkl', 'wb') as file:
        pickle.dump(pd_nccbr_repo_on, file)

    pd_nccbr_repo_terml30_url = 'https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAL30.json'
    pd_nccbr_repo_terml30 = pd.DataFrame(
        requests.get(pd_nccbr_repo_terml30_url).json()['pd']['timeseries']).drop(
        'keyid', axis=1)
    pd_nccbr_repo_terml30['value'] = pd.to_numeric(pd_nccbr_repo_terml30['value'], errors='coerce')
    pd_nccbr_repo_terml30.dropna(subset=['value'], inplace=True)
    pd_nccbr_repo_terml30['asofdate'] = pd.to_datetime(pd_nccbr_repo_terml30['asofdate'])
    pd_nccbr_repo_terml30.index = pd_nccbr_repo_terml30['asofdate'].values
    pd_nccbr_repo_terml30.drop('asofdate', axis=1, inplace=True)
    pd_nccbr_repo_terml30.columns = ['pd_nccbr_l30']
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_terml30.pkl', 'wb') as file:
        pickle.dump(pd_nccbr_repo_terml30, file)

    pd_nccbr_repo_termg30_url = 'https://markets.newyorkfed.org/api/pd/get/PDSORA-UBGUTSETTAG30.json'
    pd_nccbr_repo_termg30 = pd.DataFrame(
        requests.get(pd_nccbr_repo_termg30_url).json()['pd']['timeseries']).drop(
        'keyid', axis=1)
    pd_nccbr_repo_termg30['value'] = pd.to_numeric(pd_nccbr_repo_termg30['value'], errors='coerce')
    pd_nccbr_repo_termg30.dropna(subset=['value'], inplace=True)
    pd_nccbr_repo_termg30['asofdate'] = pd.to_datetime(pd_nccbr_repo_termg30['asofdate'])
    pd_nccbr_repo_termg30.index = pd_nccbr_repo_termg30['asofdate'].values
    pd_nccbr_repo_termg30.drop('asofdate', axis=1, inplace=True)
    pd_nccbr_repo_termg30.columns = ['pd_nccbr_g30']
    with open(Path(DATA_DIR) / 'pd_nccbr_repo_termg30.pkl', 'wb') as file:
        pickle.dump(pd_nccbr_repo_termg30, file)

    mmf_all_volume = ofr_to_df('MMF-MMF_TOT-M')
    mmf_all_volume.columns = ['MMF_TOTAL']
    with open(Path(DATA_DIR) / 'mmf_all_volume.pkl', 'wb') as file:
        pickle.dump(mmf_all_volume, file)

    ### MMF PULLS ###
    mmf_foreign = ofr_to_df('MMF-MMF_RP_wFFI-M')
    mmf_foreign.columns = ['foreign']
    with open(Path(DATA_DIR) / 'mmf_foreign.pkl', 'wb') as file:
        pickle.dump(mmf_foreign, file)
    mmf_fed = ofr_to_df('MMF-MMF_RP_wFR-M')
    mmf_fed.columns = ['fed']
    with open(Path(DATA_DIR) / 'mmf_fed.pkl', 'wb') as file:
        pickle.dump(mmf_fed, file)
    mmf_us_inst = ofr_to_df('MMF-MMF_RP_wDFI-M')
    mmf_us_inst.columns = ['us_inst']
    with open(Path(DATA_DIR) / 'mmf_us_inst.pkl', 'wb') as file:
        pickle.dump(mmf_us_inst, file)
    mmf_ficc = ofr_to_df('MMF-MMF_RP_wFICC-M')
    mmf_ficc.columns = ['ficc']
    with open(Path(DATA_DIR) / 'mmf_ficc.pkl', 'wb') as file:
        pickle.dump(mmf_ficc, file)

    ### AUCTION DATA ###
    url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?"
           "filter=record_date:gte:2000-08-16,record_date:lte:2025-08-15"
           "&sort=-auction_date,-issue_date,maturity_date&page[size]=10000")
    resp = requests.get(url).json()
    auction_df = pd.DataFrame(resp['data'])
    auction_df['record_date'] = pd.to_datetime(auction_df['record_date'])
    auction_df['total_accepted'] = pd.to_numeric(auction_df['total_accepted'], errors='coerce')
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'wb') as file:
        pickle.dump(auction_df, file)

    ### PRIMARY DEALERS ###
    def pd_ofr_to_df(mnemonic):
        base_url = 'https://data.financialresearch.gov/hf/v1/series/full?mnemonic='
        df = pd.DataFrame(
            requests.get(base_url + mnemonic).json()
            [mnemonic]['timeseries']['aggregation'], columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')

    ficc_sponsored_repo_volume = pd_ofr_to_df('FICC-SPONSORED_REPO_VOL')
    ficc_sponsored_repo_volume.columns = ['FICC-SPONSORED_REPO_VOL']
    with open(Path(DATA_DIR) / 'ficc_sponsored_repo_volume.pkl', 'wb') as file:
        pickle.dump(ficc_sponsored_repo_volume, file)

    ficc_sponsored_rrp_volume = pd_ofr_to_df('FICC-SPONSORED_REVREPO_VOL')
    ficc_sponsored_rrp_volume.columns = ['FICC-SPONSORED_REVREPO_VOL']
    with open(Path(DATA_DIR) / 'ficc_sponsored_rrp_volume.pkl', 'wb') as file:
        pickle.dump(ficc_sponsored_rrp_volume, file)

    dvp_sponsored_volume = ofr_to_df('REPO-DVP_TV_TOT-P')
    mmf_ficc.columns = ['ficc']
    with open(Path(DATA_DIR) / 'mmf_ficc.pkl', 'wb') as file:
        pickle.dump(mmf_ficc, file)


    ### PRIMARY DEALER BILLS AND BOND POSITIONS ###
    urls = [
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-B.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21.json'
    ]
    names = ['bills', 'l2', 'g2l3', 'g3l6', 'g6l7', 'g7l11', 'g11l21', 'g21']
    all_pd_bills_bonds_positions = pd.DataFrame()
    for idx in range(len(urls)):
        pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
        pos['value'] = pd.to_numeric(pos['value'], errors='coerce') / 1e3
        pos.dropna(subset=['value'], inplace=True)
        pos['asofdate'] = pd.to_datetime(pos['asofdate'])
        pos.set_index('asofdate', inplace=True)
        pos = pos[['value']]
        pos.columns = [names[idx]]
        pos = pos.sort_index()
        all_pd_bills_bonds_positions = merge_dfs([all_pd_bills_bonds_positions, pos])
    all_pd_bills_bonds_positions = all_pd_bills_bonds_positions.sort_index().loc[str(start):str(end)]
    all_pd_bills_bonds_positions['net_nominal_bonds'] = (
            all_pd_bills_bonds_positions['l2'] +
            all_pd_bills_bonds_positions['g2l3'] +
            all_pd_bills_bonds_positions['g3l6'] +
            all_pd_bills_bonds_positions['g6l7'] +
            all_pd_bills_bonds_positions['g7l11']
    )
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_positions.pkl', 'wb') as file:
        pickle.dump(all_pd_bills_bonds_positions, file)

    ### PRIMARY DEALER BILLS AND BOND NET CHANGES ###
    urls = [
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGS-BC.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-L2C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G2L3C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G3L6C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G6L7C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G7L11C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G11L21C.json',
        'https://markets.newyorkfed.org/api/pd/get/PDPOSGSC-G21C.json'
    ]
    names = ['bills', 'l2', 'g2l3', 'g3l6', 'g6l7', 'g7l11', 'g11l21', 'g21']
    all_pd_bills_bonds_net_changes = pd.DataFrame()
    for idx in range(len(urls)):
        pos = pd.DataFrame(requests.get(urls[idx]).json()['pd']['timeseries']).drop('keyid', axis=1)
        pos['value'] = pd.to_numeric(pos['value'], errors='coerce')
        pos.dropna(subset=['value'], inplace=True)
        pos['asofdate'] = pd.to_datetime(pos['asofdate'])
        pos.set_index('asofdate', inplace=True)
        pos = pos[['value']]
        pos.columns = [names[idx]]
        pos = pos.sort_index()
        all_pd_bills_bonds_net_changes = merge_dfs([all_pd_bills_bonds_net_changes, pos])
    all_pd_bills_bonds_net_changes = all_pd_bills_bonds_net_changes.sort_index().loc[
                                     str(start):str(end)].dropna()
    with open(Path(DATA_DIR) / 'all_pd_bills_bonds_net_changes.pkl', 'wb') as file:
        pickle.dump(all_pd_bills_bonds_net_changes, file)












