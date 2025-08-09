### ---------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------- REPO --------------------------------------------------- ###
### ---------------------------------------------------------------------------------------------------------- ###


import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

start = "2019-01-01"
end = "2025-08-06"

# Download all series (values are in millions of dollars unless noted)
# Replace with more refined series as needed
tri_party_rrp    = pdr.DataReader('RRPONTSYD',   'fred', start, end)  # Tri-Party RRP, Fed ON RRP Facility
nccbr_2t         = pdr.DataReader('RRPONTTLD',   'fred', start, end)  # Total RRP (as proxy for 2T NCCBR)
all_repo         = pdr.DataReader('REPO',        'fred', start, end)  # Total repo (as available)
dvp              = pdr.DataReader('GCFREPOT',    'fred', start, end)  # GCF Repo Total (if not available, may need alternate)
# If GCFREPOT is unavailable, leave as all_repo['REPO'] - tri_party_rrp['RRPONTSYD']

# Align all to daily index for plotting and transformations
daily_index = pd.date_range(start=start, end=end, freq='D')
tri_party_rrp = tri_party_rrp.reindex(daily_index, method='ffill')
nccbr_2t      = nccbr_2t.reindex(daily_index, method='ffill')
all_repo      = all_repo.reindex(daily_index, method='ffill')

# If dvp is missing, create a placeholder (zeros)
try:
    dvp = dvp.reindex(daily_index, method='ffill')
except Exception:
    dvp = pd.Series(0, index=daily_index)

# --- Calculate the ratios per chart legend code ---
# Top line (cyan): (Tri Party-RRP + 2T NCCBR) / (All Repo + 2T NCCBR - RRP)
numerator_cyan   = tri_party_rrp['RRPONTSYD'] + nccbr_2t['RRPONTTLD']
denominator_cyan = all_repo['REPO'] + nccbr_2t['RRPONTTLD'] - tri_party_rrp['RRPONTSYD']
proxy_cyan       = numerator_cyan / denominator_cyan * 100

# Black line: Tri-Party RRP / (Tri-Party + DVP + GCF-RPP)
# If dvp or GCF-RPP is unavailable, sum just Tri-Party and DVP
denominator_black = tri_party_rrp['RRPONTSYD'] + dvp
proxy_black       = tri_party_rrp['RRPONTSYD'] / denominator_black * 100

# Combine proxies for plotting
df = pd.DataFrame({
    'Proxy w/o Central Clearing (Cyan)': proxy_cyan,
    'Tri-Party Share (Black)': proxy_black
})

# Smooth with weekly average to mirror the chart's smoothing (optional)
df = df.resample('W-FRI').mean()

# --- Plot ---
plt.figure(figsize=(12, 7))
plt.plot(df.index, df['Proxy w/o Central Clearing (Cyan)'], color='#26bbe3', linewidth=2, label="(Tri Party-RRP + 2T NCCBR)/ (All Repo + 2T NCCBR - RRP)")
plt.plot(df.index, df['Tri-Party Share (Black)'], color='#17293c', linewidth=2, label="Tri Party-RRP / (Tri Party+DVP+GCF-RPP)")
plt.ylabel('Percent of Total Volume')
plt.title('Proxy of Percent Without Central Clearing, 2019–2025')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
