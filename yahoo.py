	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
import pandas as pd
print("please give me a ticka")
ticka = input()
today = dt.date.today()
soonest_friday = today + dt.timedelta((4 - today.weekday()) % 7)
stock_price = si.get_live_price(ticka)
calls = opt.get_calls(ticka,soonest_friday)
puts = opt.get_puts(ticka,soonest_friday)
calls['profit'] = calls['Last Price'] / calls['Strike']

middle = 0 #to save for later
prev_dif = float("Inf") # set this way to make sure it gets past the first iteration
for index,row in calls.iterrows():
    dif = abs(stock_price - row['Strike'])
    if dif < prev_dif:
        prev_dif = dif
        continue
    else:
        middle = index
        break

return_calls = calls.iloc[middle-5:middle+5]
print(return_calls)

# use the same middle for puts
return_puts = puts.iloc[middle-5:middle+5]
print(return_puts)