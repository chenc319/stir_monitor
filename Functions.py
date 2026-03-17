### ------------------------------------------------------------------------------------ ###
### ------------------------------------- FUNCTION ------------------------------------- ###
### ------------------------------------------------------------------------------------ ###

### FUNCTIONS ###
import streamlit as st
import plotly.graph_objs as go
import plotly.subplots as sp
import pandas as pd
import requests, zipfile, io
import functools as ft
import pickle
import pandas_datareader as pdr
from plotly.subplots import make_subplots
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from io import StringIO
import base64
import seaborn as sns
import numpy as np
from fredapi import Fred
from io import BytesIO
fred = Fred(api_key="6905137c26f03db5c8c09f70b7839150")

def get_fred_series(series_id, start, end):
    s = fred.get_series(series_id, observation_start=start, observation_end=end)
    s = s.to_frame(name=series_id)
    return s

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left, right: pd.merge(left, right,
                                                  left_index=True,
                                                  right_index=True, how='outer'), array_of_dfs)

def static_beta(return_ts, benchmark_ts,):
    returns = merge_dfs([return_ts,benchmark_ts])
    rolling_cov = returns.iloc[:,0].cov(returns.iloc[:,1])
    rolling_var = returns.iloc[:,1].var()
    individual_beta = rolling_cov / rolling_var
    return individual_beta

def rolling_beta(return_ts, benchmark_ts,window):
    returns = merge_dfs([return_ts,benchmark_ts])
    rolling_cov = returns.iloc[:,0].rolling(window).cov(returns.iloc[:,1])
    rolling_var = returns.iloc[:,1].rolling(window).var()
    individual_beta = rolling_cov / rolling_var
    return individual_beta

def rolling_beta_sign(y, x, window, thresh=-0.2):
    """
    Return 1 if beta >= thresh, else -1.
    """
    beta = rolling_beta(y, x, window)
    sign = np.where(beta >= thresh, 1, -1)
    return pd.Series(sign, index=beta.index)

def return_metrics(backtest_returns_data, benchmark_data, ann_factor):
    backtest_returns_data = pd.DataFrame(backtest_returns_data)
    benchmark_data = pd.DataFrame(benchmark_data)
    return_metrics_df = pd.DataFrame(
        columns=['Total Return', 'Avg Return', 'Avg Upside Return', 'Avg Downside Return',
                 'Win Ratio', 'Ann. Return', 'Ann. Volatility', 'Return/Risk',
                 'Max Return', 'Min Return',
                 'Upside Capture', 'Downside Capture', 'Capture Ratio','Beta']
    )
    benchmark_returns = benchmark_data.iloc[:,0].ffill().dropna()

    for x in range(0, len(backtest_returns_data.columns)):
        col = backtest_returns_data.columns[x]
        data = pd.DataFrame(backtest_returns_data[col]).ffill().dropna()
        data.columns = ['returns']
        total_return = ((1 + data['returns']).cumprod()-1)[-1]
        mean_return = data['returns'].mean()
        avg_win_return = data[data['returns'] > 0]['returns'].mean()
        avg_lose_return = data[data['returns'] < 0]['returns'].mean()
        win_ratio = len(data[data['returns'] > 0]) / len(data)
        ann_return = ((1+ mean_return) ** ann_factor)-1
        ann_vol = data['returns'].std() * (ann_factor ** 0.5)
        return_risk = ann_return / ann_vol if ann_vol != 0 else None
        max_return = data['returns'].max()
        min_return = data['returns'].min()

        # Upside/Downside Capture
        upside_mask = benchmark_returns > 0
        downside_mask = benchmark_returns < 0
        upside_capture = (data['returns'][upside_mask].mean() / benchmark_returns[upside_mask].mean()) if upside_mask.any() else None
        downside_capture = (data['returns'][downside_mask].mean() / benchmark_returns[downside_mask].mean()) if downside_mask.any() else None

        # Capture Ratio: Upside / |Downside|
        capture_ratio = (upside_capture / abs(downside_capture)) if (upside_capture is not None and downside_capture not in (None, 0)) else None

        beta = static_beta(data['returns'],benchmark_data)

        return_metrics_df.loc[col] = [
            total_return, mean_return, avg_win_return, avg_lose_return, win_ratio,
            ann_return, ann_vol, return_risk, max_return, min_return,
            upside_capture, downside_capture, capture_ratio,beta
        ]
    return return_metrics_df

def streamlit_plot(
    df,
    columns_array,
    colors_array,
    labels_array,
    graph_title,
    y_axis_label,
    rows: int = 1,
    cols: int = 1
):
    if rows > 1 or cols > 1:
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=labels_array
        )

        for i, (col_name, label, color) in enumerate(
            zip(columns_array, labels_array, colors_array)
        ):
            row = i // cols + 1
            col_pos = i % cols + 1

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col_name],
                    name=label,
                    mode='lines',
                    line=dict(color=color, width=2),
                ),
                row=row,
                col=col_pos
            )
    else:
        fig = go.Figure()
        for col_name, label, color in zip(columns_array, labels_array, colors_array):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col_name],
                    name=label,
                    mode='lines',
                    line=dict(color=color, width=2),
                )
            )

    fig.update_layout(
        height=450,
        hovermode='x unified',
        legend=dict(title='Legend', orientation='h', y=-0.25),
        margin=dict(t=80, b=30),
        title=dict(
            text=graph_title,
            y=0.96,
            x=0.0,
            xanchor='left',
            yanchor='top'
        ),
        yaxis_title=y_axis_label,
        showlegend=(rows == 1 and cols == 1)
    )

    if (rows > 1 or cols > 1) and 'annotations' in fig.layout:
        for ann in fig.layout.annotations:
            ann.y += 0.03

    st.plotly_chart(fig, use_container_width=True)


def streamlit_plot_with_spreads(
    df,
    main_columns,
    colors_array,
    graph_title,
    y_axis_label,
    spread_pairs=None,
    spread_colors=None,
    spread_y_label="Spread"
):
    """
    df: DataFrame with time index.
    main_columns: list of column names to plot on the top chart.
    colors_array: list of colors (same length as main_columns).
    spread_pairs: list of (col_a, col_b) tuples to compute col_a - col_b.
    spread_colors: list of colors for each spread trace (same length as spread_pairs).
    """

    if spread_pairs is None:
        spread_pairs = []
    if spread_colors is None:
        # fallback colors if not provided
        spread_colors = ["#F9C846", "#F9D15B", "#7EC0EE"][:len(spread_pairs)]

    # build subplots only if we have spreads
    rows = 2 if spread_pairs else 1

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3] if rows == 2 else [1.0],
    )

    # top: original series
    for name, color in zip(main_columns, colors_array):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[name],
                name=name,
                mode="lines",
                line=dict(color=color, width=2),
            ),
            row=1, col=1,
        )

    # bottom: one or more spreads
    if spread_pairs:
        for (col_a, col_b), color in zip(spread_pairs, spread_colors):
            spread_name = f"{col_a} - {col_b}"
            spread_values = df[col_a] - df[col_b]

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=spread_values,
                    name=spread_name,
                    mode="lines",
                    line=dict(color=color, width=2),
                ),
                row=2, col=1,
            )

    # layout
    fig.update_layout(
        height=700 if rows == 2 else 450,
        hovermode="x unified",
        legend=dict(title="Legend", orientation="h", y=-0.2),
        margin=dict(t=30, b=40),
        title=graph_title,
    )

    fig.update_yaxes(title_text=y_axis_label, row=1, col=1)
    if spread_pairs:
        fig.update_yaxes(title_text=spread_y_label, row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

### ------------------------------------------------------------------------------------ ###
### ----------------------------------- CAD FUNCTION ----------------------------------- ###
### ------------------------------------------------------------------------------------ ###

def get_boc_historical_timeseries(series_id,col_name):
    url = f"https://www.bankofcanada.ca/valet/observations/{series_id}/json"
    params = {
        "start_date": "1990-01-01",
        "order_dir": "asc",
    }
    data = requests.get(url, params=params).json()
    obs = data["observations"]
    df = pd.DataFrame(
        {"date": [o["d"] for o in obs],
         col_name: [float(o[series_id]["v"]) for o in obs],}
    )
    df["date"] = pd.to_datetime(df["date"])
    df.index = df['date'].values
    df.drop('date', axis=1, inplace=True)
    return df

def get_newyork_fed_data(mnemonic: str) -> pd.DataFrame:
    """
    Fetch NY Fed Primary Dealer time series for a given mnemonic.
    Returns a DataFrame indexed by asofdate with one 'value' column.
    """
    url = f"https://markets.newyorkfed.org/api/pd/get/{mnemonic}.json"
    resp = requests.get(url)
    resp.raise_for_status()
    ts = pd.DataFrame(resp.json()['pd']['timeseries'])
    ts = ts.drop(columns=['keyid'], errors='ignore')
    ts['value'] = pd.to_numeric(ts['value'], errors='coerce')
    ts = ts.dropna(subset=['value'])
    ts['asofdate'] = pd.to_datetime(ts['asofdate'])
    ts = ts.set_index('asofdate').sort_index()
    ts = ts[['value']]
    ts.columns = [mnemonic]
    return ts

def streamlit_plot_subplot_layout(plot_funcs, n_rows: int, n_cols: int):
    """
    Arrange multiple streamlit_plot calls in an n_rows x n_cols grid.

    Parameters
    ----------
    plot_funcs : list[callable]
        Each element is a zero-arg function that, when called,
        executes one streamlit_plot (or any Streamlit chart).
    n_rows : int
        Number of rows in the grid.
    n_cols : int
        Number of columns per row.
    """
    total = len(plot_funcs)
    idx = 0
    for _ in range(n_rows):
        if idx >= total:
            break
        cols = st.columns(n_cols)
        for c in range(n_cols):
            if idx >= total:
                break
            with cols[c]:
                plot_funcs[idx]()  # call the plotting function
            idx += 1

def cot_year(year=2020, cot_report_type="legacy_fut", verbose=True):
    """
    Downloads the selected COT report historical data for a single year
    from cftc.gov as a zip file, reads the desired text file from memory,
    and returns the data as a DataFrame without saving anything locally.
    """

    if verbose:
        print("Selected:", cot_report_type)

    if cot_report_type == "legacy_fut":
        rep = "deacot"
        txt = "annual.txt"
    elif cot_report_type == "legacy_futopt":
        rep = "deahistfo"
        txt = "annualof.txt"
    elif cot_report_type == "supplemental_futopt":
        rep = "dea_cit_txt_"
        txt = "annualci.txt"
    elif cot_report_type == "disaggregated_fut":
        rep = "fut_disagg_txt_"
        txt = "f_year.txt"
    elif cot_report_type == "disaggregated_futopt":
        rep = "com_disagg_txt_"
        txt = "c_year.txt"
    elif cot_report_type == "traders_in_financial_futures_fut":
        rep = "fut_fin_txt_"
        txt = "FinFutYY.txt"
    elif cot_report_type == "traders_in_financial_futures_futopt":
        rep = "com_fin_txt_"
        txt = "FinComYY.txt"
    else:
        raise ValueError(
            'cot_report_type must be one of: '
            '"legacy_fut", "legacy_futopt", "supplemental_futopt", '
            '"disaggregated_fut", "disaggregated_futopt", '
            '"traders_in_financial_futures_fut", '
            '"traders_in_financial_futures_futopt"'
        )

    cot_url = f"https://cftc.gov/files/dea/history/{rep}{year}.zip"
    r = requests.get(cot_url)
    r.raise_for_status()

    # Open zip from memory
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        if verbose:
            print("Downloaded single year data from:", year)
            print("Reading", txt, "from zip in memory...")
        with zf.open(txt) as f:
            df = pd.read_csv(f, low_memory=False)

    return df
