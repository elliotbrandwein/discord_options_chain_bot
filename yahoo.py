	
from yahoo_fin import options as opt
from yahoo_fin import stock_info as si
import datetime as dt
import pandas as pd
from prettytable import PrettyTable
import math
price_cache = {}
_date_format ="%m-%d-%Y"
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

stock_expiry_cache = {}
def friday():
    today = dt.date.today()
    return today + dt.timedelta((4 - today.weekday()) % 7)

def calls_chain(ticka):
    calls = pd.DataFrame()
    stock_expiry_cache[ticka] = friday()
    while(calls.empty):
        try:
            calls = opt.get_calls(ticka,stock_expiry_cache[ticka])
        except: 
            stock_expiry_cache[ticka] = stock_expiry_cache[ticka] + dt.timedelta(days=7) 
    calls['profit'] = calls['Last Price'] / calls['Strike']
    return calls

def puts_chain(ticka):
    puts = pd.DataFrame()
    stock_expiry_cache[ticka] = friday()
    while(puts.empty):
        try:
            puts = opt.get_puts(ticka,stock_expiry_cache[ticka])
        except:
            stock_expiry_cache[ticka] = stock_expiry_cache[ticka] + dt.timedelta(days=7) 
    puts['profit'] = puts['Last Price'] / puts['Strike']
    return puts

def return_puts(ticka, window = 5):
    puts = puts_chain(ticka)
    if len(puts) == 0:
        return puts
    put_middle = get_middle(puts, ticka)
    puts['profit'] = puts['profit'].apply(percentager)
    return puts.iloc[0 if put_middle - window < 0 else put_middle - window:put_middle+window]

def return_calls(ticka, window=5):
    calls = calls_chain(ticka)
    if len(calls) == 0:
        return []
    call_middle = get_middle(calls, ticka)
    calls['profit'] = calls['profit'].apply(percentager)
    return calls.iloc[0 if call_middle - window < 0 else call_middle - window:call_middle+window]

def get_todays_safe_options(ticka,window_length=None,option="call"):
    option = option.lower()
    opt_case = None
    if "call" in option:
        opt_case = 1
    elif "put" in option:
        opt_case = 2
    if opt_case == None:
        return []
    if window_length != None:
        start_date = dt.datetime.now() - dt.timedelta(window_length)
        end_date = dt.datetime.now() + dt.timedelta(1)
    else:
        window_length = 20
        start_date = dt.datetime.now() - dt.timedelta(window_length)
        end_date = dt.datetime.now() + dt.timedelta(1)
    data = si.get_data(ticka,start_date=start_date,end_date=end_date)
    stockprices = data.drop(columns=['open', 'high', 'low', 'close', 'volume', 'ticker'])
    MA = stockprices['adjclose'].mean()
    STD = stockprices['adjclose'].std()
    UPPER = MA + (STD * 2)
    LOWER = MA - (STD * 2)
    
    if opt_case == 1:
        output = calls_chain(ticka).drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
        output.query('Strike > @UPPER',inplace=True)
    else:
        output = puts_chain(ticka).drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
        output.query('Strike < @LOWER',inplace=True)
    output['profit'] = output['profit'].apply(percentager)
    output.query('Volume > 100',inplace=True)
    bad_bids = output[output['Bid'] == '-'].index
    output.drop(bad_bids, inplace=True)
    return output

def get_band(ticka,start_date=None,end_date=None,band_age=None):
    if start_date != None:
        try:
            start_date = dt.datetime.strptime(start_date,"%m-%d-%Y")
        except:
            pass
            # print("ERROR, start_date but be in the format mm-dd-yyyy (%m-%d-%Y)") 
        if band_age == None:
            band_age = 30  
        if end_date == None or end_date == start_date:
            end_date = start_date + dt.timedelta(1)
        start_date = start_date - dt.timedelta(band_age)
    
    else:
        if band_age == None:
            band_age = 30
        start_date = dt.datetime.now() - dt.timedelta(band_age * 2)
    #TODO: if there is an end_date without a start date, figure out what that means
        
    data = si.get_data(ticka,start_date=start_date,end_date=end_date)
    # # we only need date  and adjusted price
    stockprices = data.drop(columns=['open', 'high', 'low', 'close', 'volume', 'ticker'])
    # for exact dates, we might not end on a trading day, so this rounds that off
    if len(data) < band_age:
        band_age = len(data)
    # #we calc the avg from the half way point, which should be roughly the first time we can calc the band
    stockprices['MA'] = stockprices['adjclose'].rolling(window=band_age).mean()
    stockprices['STD'] = stockprices['adjclose'].rolling(window=band_age).std() 
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