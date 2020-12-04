	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
import pandas as pd
from prettytable import PrettyTable
def percentager(the_number):
    the_number = round(the_number,4)
    return "{:.2%}".format(the_number)

price_cache = {}
def ticka_price(ticka):
    price = si.get_live_price(ticka)
    price_cache[ticka] = price
    return price

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
    puts['profit'] = puts['profit'].apply(percentager)
    return puts.iloc[put_middle-5:put_middle+5]

def return_calls(ticka):
    calls = calls_chain(ticka)
    call_middle = get_middle(calls, ticka)
    calls['profit'] = calls['profit'].apply(percentager)
    return calls.iloc[call_middle-5:call_middle+5]

if __name__ == '__main__':
    print("please give me a ticka") # will replace with input from bot
    ticka = input()
    print("call or put")
    option = input()
    option = option.lower()
    if option == "call":
        ascii_table = PrettyTable()
        data = return_calls(ticka)
        data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
        ascii_table.field_names = data.columns
        for i in range(len(data.index)):
            if i == 4:
                ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","CURRENT PRICE:", round(price_cache[ticka],4)])
            ascii_table.add_row(data.iloc[i])
        print(ascii_table.get_string())

    elif option == "put":
        ascii_table = PrettyTable()
        data = return_puts(ticka)
        data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
        ascii_table.field_names = data.columns
        for i in range(len(data.index)):
            if i == 4:
                ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","CURRENT PRICE:", round(price_cache[ticka],4)])
            ascii_table.add_row(data.iloc[i])
        print(ascii_table.get_string())
    else:
        print("you're an idiot")