	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
import pandas as pd

def ticka_price(ticka):
    return si.get_live_price(ticka)

def get_middle(chain, ticka):
    stock_price = ticka_price(ticka)
    prev_dif = float("Inf") # set this way to make sure it gets past the first iteration
    for index,row in chain.iterrows():
        dif = abs(stock_price - row['Strike'])
        if dif < prev_dif:
            prev_dif = dif
            continue
        else:
            return index
    return -1 # throw an error here, add later

def friday():
    today = dt.date.today()
    return today + dt.timedelta((4 - today.weekday()) % 7)

def calls_chain(ticka):
    calls = opt.get_calls(ticka,friday()) 
    calls['profit'] = calls['Last Price'] / calls['Strike']
    return calls

def puts_chain(ticka):
    puts = opt.get_puts(ticka,friday())
    puts['profit'] = puts['Last Price'] / puts['Strike']
    return puts

def return_puts(ticka):
    puts = puts_chain(ticka)
    put_middle = get_middle(puts, ticka)
    return puts.iloc[put_middle-5:put_middle+5]

def return_calls(ticka):
    calls = calls_chain(ticka)
    call_middle = get_middle(calls, ticka)
    return calls.iloc[call_middle-5:call_middle+5]

if __name__ == '__main__':
    print("please give me a ticka") # will replace with input from bot
    ticka = input()

    calls = calls_chain(ticka)
    puts = puts_chain(ticka)

    call_middle = get_middle(calls, ticka)
    put_middle = get_middle(puts, ticka)

    print(calls.iloc[call_middle-5:call_middle+5])

    print(puts.iloc[put_middle-5:put_middle+5])