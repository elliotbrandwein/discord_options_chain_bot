import yahoo as lib
import pandas as pd
from tqdm import tqdm

print("reading all sheets.....")

our_calls = [
    pd.read_excel("sheets/test_2.ods", sheet_name="calls", engine="odf"),
    pd.read_excel("sheets/test_y.ods", sheet_name="Calls", engine="odf"),
    pd.read_excel("sheets/Wheels_JJ.ods", sheet_name="Calls", engine="odf")
]
our_puts = [
    pd.read_excel("sheets/test_2.ods", sheet_name="puts", engine="odf"),
    pd.read_excel("sheets/test_y.ods", sheet_name="Puts", engine="odf"),
    pd.read_excel("sheets/Wheels_JJ.ods", sheet_name="Puts", engine="odf")
]

for frame in our_calls:
    frame.columns = [i.strip() for i in frame.columns]
for frame in our_puts:
    frame.columns = [i.strip() for i in frame.columns]

print('combining all sheets....')

calls = pd.concat(our_calls)
puts = pd.concat(our_puts)

calls = calls.dropna(subset=['Ticker', 'Premium'])
puts = puts.dropna(subset=['Ticker', 'Premium'])

bad_returns = calls[calls['Return'] == '#DIV/0!'].index
calls = calls.drop(bad_returns)
bad_returns = puts[puts['Return'] == '#DIV/0!'].index
puts = puts.drop(bad_returns)

calls = calls.drop(columns=["Expiry", "Collateral", "Premium", "Dollar Return", "Duration (Days)"])
puts = puts.drop(columns=["Expiry", "Collateral", "Premium", "Dollar Return", "Duration (Days)"])

calls = calls.drop_duplicates()
puts = puts.drop_duplicates()

calls = calls.reset_index(drop=True)
puts = puts.reset_index(drop=True)

for idx in tqdm(calls.index):
    ticka = calls.loc[idx, 'Ticker']
    date = calls.loc[idx, 'Date']
    strike = calls.loc[idx, 'Strike']
    bands_data = lib.get_band(ticka, start_date=date.strftime(lib._date_format), end_date=date)
    bands_data_short = lib.get_band(ticka, start_date=date.strftime(lib._date_format), end_date=date, band_age=3)
    calls.loc[idx, 'MA'] = bands_data['MA'][0]
    calls.loc[idx, '3-MA'] = bands_data_short['MA'][0]
    calls.loc[idx, 'STD'] = bands_data['STD'][0]
    calls.loc[idx, '3-STD'] = bands_data_short['STD'][0]
    calls.loc[idx, 'adjclose'] = bands_data['adjclose'][0]
    calls.loc[idx, 'Safe'] = 1 if strike > bands_data['Upper'][0] else 0


for idx in tqdm(puts.index):
    ticka = puts.loc[idx, 'Ticker']
    date = puts.loc[idx, 'Date']
    strike = puts.loc[idx, 'Strike']
    bands_data = lib.get_band(ticka, start_date=date.strftime(lib._date_format), end_date=date)
    bands_data_short = lib.get_band(ticka, start_date=date.strftime(lib._date_format), end_date=date, band_age=3)
    puts.loc[idx, 'MA'] = bands_data['MA'][0]
    puts.loc[idx, '3-MA'] = bands_data_short['MA'][0]
    puts.loc[idx, 'STD'] = bands_data['STD'][0]
    puts.loc[idx, '3-STD'] = bands_data_short['STD'][0]
    puts.loc[idx, 'adjclose'] = bands_data['adjclose'][0]
    puts.loc[idx, 'Safe'] = 1 if strike < bands_data['Lower'][0] else 0


puts.to_csv('outputs/puts_output.csv')
calls.to_csv('outputs/calls_output.csv')
