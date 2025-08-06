### ---------------------------------------------------------------------------------------------------------- ###
### ---------------------------------------------- RISK CHECKS ----------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###

### PACKAGES ###
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import datetime

### FUNCTIONS ###

### ---------------------------------------------------------------------------------------------------------- ###
### -------------------------------------------- FED FUNDS - IORB -------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###



# Set date range for several recent years, update for your analysis
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime.today()

# Pull data directly from FRED
df_iorb = pdr.DataReader('IORB', 'fred', start, end)
df_effr = pdr.DataReader('EFFR', 'fred', start, end)

# Merge on date index
df = df_iorb.join(df_effr, how='inner', lsuffix='_IORB', rsuffix='_EFFR')

# Calculate spread in basis points
df['Spread_bp'] = (df['EFFR'] - df['IORB']) * 100

# Plot to replicate the chart
plt.figure(figsize=(10,5))
plt.step(df.index, df['Spread_bp'], where='post', color='skyblue', alpha=0.85, linewidth=3)
plt.title('Monitoring the Dash For Cash\nFed Funds - IORB', fontsize=18, fontweight='bold', loc='left')
plt.ylabel('Basis Points', fontsize=13)
plt.xlabel('')
plt.grid(alpha=0.17)
plt.tight_layout()
plt.ylim([-12, 22])  # Set y-limits as in the chart
plt.show()











