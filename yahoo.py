	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
import pandas as pd
from prettytable import PrettyTable
import datetime
import math
price_cache = {}

def percentager(the_number):
    the_number = round(the_number,4)
    return "{:.2%}".format(the_number)

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
    try:
        calls = opt.get_calls(ticka,friday())
    except: 
        return [] 
    calls['profit'] = calls['Last Price'] / calls['Strike']
    return calls

def puts_chain(ticka):
    try:
        puts = opt.get_puts(ticka,friday())
    except:
        return []
    puts['profit'] = puts['Last Price'] / puts['Strike']
    return puts

def return_puts(ticka):
    puts = puts_chain(ticka)
    if len(puts) == 0:
        return puts
    put_middle = get_middle(puts, ticka)
    puts['profit'] = puts['profit'].apply(percentager)
    return puts.iloc[put_middle-5:put_middle+5]

def return_calls(ticka):
    calls = calls_chain(ticka)
    if len(calls) == 0:
        return []
    call_middle = get_middle(calls, ticka)
    calls['profit'] = calls['profit'].apply(percentager)
    return calls.iloc[call_middle-5:call_middle+5]

def get_band(ticka, band_age=None):
    if(band_age == None):
        band_age = 30
    band_age *= 2
    #to get the start's rolling avg, we need to start at the age before it
    start_date = datetime.datetime.now() - datetime.timedelta(band_age)
    data = si.get_data(ticka,start_date=start_date)
    # we only need date  and adjusted price
    stockprices = data.drop(columns=['open', 'high', 'low', 'close', 'volume', 'ticker'])
    #we calc the avg from the half way point, which should be roughly the first time we can calc the band
    start_rolling = math.floor(len(stockprices) / 2)
    stockprices['MA'] = stockprices['adjclose'].rolling(window=start_rolling).mean()
    stockprices['STD'] = stockprices['adjclose'].rolling(window=start_rolling).std() 
    stockprices['Upper'] = stockprices['MA'] + (stockprices['STD'] * 2)
    stockprices['Lower'] = stockprices['MA'] - (stockprices['STD'] * 2)
    #filter out all the NaN's from the bands we didnt cal
    stockprices = stockprices.query('MA == MA')
    return stockprices
    
if __name__ == '__main__':
    print("please give me a ticka") # will replace with input from bot
    ticka = input()
    print("call or put")
    option = input()
    option = option.lower()
    if option == "band":
        print(get_band(ticka))
    elif option == "call":
        ascii_table = PrettyTable()
        data = return_calls(ticka)
        if len(data) == 0:
            print("no calls found for ticka", ticka)
        else:
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
            if len(data) == 0:
                print("no puts found for ticka", ticka)
            else:
                data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
                ascii_table.field_names = data.columns
                for i in range(len(data.index)):
                    if i == 4:
                        ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","CURRENT PRICE:", round(price_cache[ticka],4)])
                    ascii_table.add_row(data.iloc[i])
                print(ascii_table.get_string())
    else:
        print("you're an idiot")