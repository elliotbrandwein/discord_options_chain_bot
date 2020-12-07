import yahoo as lib
import pandas as pd
calls = pd.read_excel("test_data.xlsx",sheet_name="Calls")
puts = pd.read_excel("test_data.xlsx",sheet_name="Puts")
# calls = pd.read_excel("test_2.ods",sheet_name="calls",engine="odf")
# puts = pd.read_excel("test_2.ods",sheet_name="puts",engine="odf")

# remove nans
puts = puts.query("Ticker == Ticker")
calls = calls.query("Ticker == Ticker")
# drop all useless data
calls = calls.drop(columns=["Expiry","Premium","Collateral","Return","Dollar Return", "Duration (Days)"])
puts = puts.drop(columns=["Expiry","Premium","Collateral","Return","Dollar Return", "Duration (Days)"])

calls_assigned = calls.query("Assigned == 1")
puts_assigned = puts.query("Assigned == 1")
calls_unassigned = calls.query("Assigned != 1")
puts_unassigned = puts.query("Assigned != 1")

calls_assigned = calls_assigned.assign(Upper=None)
calls_unassigned = calls_unassigned.assign(Upper=None)
calls_assigned = calls_assigned.assign(Safe=None)
calls_unassigned = calls_unassigned.assign(Safe=None)

puts_assigned = puts_assigned.assign(Lower=None)
puts_unassigned = puts_unassigned.assign(Lower=None)
puts_assigned = puts_assigned.assign(Safe=None)
puts_unassigned = puts_unassigned.assign(Safe=None)

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

for i,row in puts_unassigned.iterrows():
    ticka = row[0]
    date = row[1]
    strike = row[2]
    lower = lib.get_band(ticka,start_date=date.strftime(lib._date_format),end_date=date).iloc[0]['Lower']
    puts_unassigned.loc[i,'Safe'] = strike < lower
    puts_unassigned.loc[i,'Lower'] = lower
for i,row in calls_unassigned.iterrows():
    ticka = row[0]
    date = row[1]
    strike = row[2]
    upper = lib.get_band(ticka,start_date=date.strftime(lib._date_format),end_date=date).iloc[0]['Upper']
    calls_unassigned.loc[i,'Safe'] = strike > upper
    calls_unassigned.loc[i,'Upper'] = upper

total_calls_assigned = len(calls_assigned.index)
total_calls_unassigned = len(calls_unassigned.index)
total_puts_assigned = len(puts_assigned.index)
total_puts_unassigned = len(puts_unassigned.index)

print("Accuracy for calls_assigned", len(calls_assigned.query('Safe == False').index) / total_calls_assigned )
print("Accuracy for calls_unassigned", len(calls_unassigned.query('Safe == True').index) / total_calls_unassigned )
print("Accuracy for puts_assigned", len(puts_assigned.query('Safe == False').index) / total_puts_assigned )
print("Accuracy for puts_unassigned", len(puts_unassigned.query('Safe == True').index) / total_puts_unassigned )
calls_assigned.to_csv('calls_assigned.csv')
calls_unassigned.to_csv('calls_unassigned.csv')
puts_assigned.to_csv('puts_assigned.csv')
puts_unassigned.to_csv('puts_unassigned.csv')

