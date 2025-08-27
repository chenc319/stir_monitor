### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------ BUYBACKS ------------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###

import pandas as pd
import functools as ft
import requests
import streamlit as st
import plotly.graph_objs as go
from matplotlib import pyplot as plt
from pathlib import Path
import os
import pickle
DATA_DIR = os.getenv('DATA_DIR', 'data')

def merge_dfs(array_of_dfs):
    return ft.reduce(lambda left,
                            right: pd.merge(left, right,
                                            left_index=True,
                                            right_index=True,
                                            how='outer'), array_of_dfs)

### ---------------------------------------------------------------------------------------------------------- ###
### --------------------------------------- BUYBACK VOLUME BY MATURITY --------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

def plot_buyback_volume_by_maturity(start,end, **kwargs):
    with open(Path(DATA_DIR) / 'auction_df.pkl', 'rb') as file:
        auction_df = pickle.load(file)
        auction_df.columns

### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------ TOTAL BUYBACK VOLUME ------------------------------------------ ###
### ---------------------------------------------------------------------------------------------------------- ###


