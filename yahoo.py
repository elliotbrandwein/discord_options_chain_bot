	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
print("please give me a ticka")
ticka = input()
today = dt.date.today()
soonest_friday = today + dt.timedelta((4 - today.weekday()) % 7)
stock_price = si.get_live_price(ticka)
calls = opt.get_calls(ticka,soonest_friday)
puts = opt.get_puts(ticka,soonest_friday)
calls['profit'] = calls['Last Price'] / calls['Strike']
print(calls)
