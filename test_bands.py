import yahoo as lib
import pandas as pd
calls = pd.read_excel("test_data.xlsx",sheet_name="Calls")
puts = pd.read_excel("test_data.xlsx",sheet_name="Puts")
# remove nans
puts = puts.query("Ticker == Ticker")
calls = calls.query("Ticker == Ticker")
# drop all useless data
calls = calls.drop(columns=["Expiry","Premium","Collateral","Return","Dollar Return", "Duration (Days)"])
puts = puts.drop(columns=["Expiry","Premium","Collateral","Return","Dollar Return", "Duration (Days)"])

calls_assigned = calls.query("Assigned == 1")
puts_assigned = puts.query("Assigned == 1")

calls_assigned = calls_assigned.assign(Upper=None)
calls_assigned = calls_assigned.assign(Safe=None)

puts_assigned = puts_assigned.assign(Lower=None)
puts_assigned = calls_assigned.assign(Safe=None)

for i,row in puts_assigned.iterrows():
    ticka = row[0]
    date = row[1]
    strike = row[2]
    lower = lib.get_band(ticka,start_date=date.strftime(lib._date_format),end_date=date).iloc[0]['Lower']
    puts_assigned.loc[i,'Safe'] = strike < lower
    puts_assigned.loc[i,'Lower'] = lower
for i,row in calls_assigned.iterrows():
    ticka = row[0]
    date = row[1]
    strike = row[2]
    upper = lib.get_band(ticka,start_date=date.strftime(lib._date_format),end_date=date).iloc[0]['Upper']
    calls_assigned.loc[i,'Safe'] = strike > upper
    calls_assigned.loc[i,'Upper'] = upper
print("CALLS: \n")
print(calls_assigned,"\n")
print("PUTS: \n")
print(puts_assigned)