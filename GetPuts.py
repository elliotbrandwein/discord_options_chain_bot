#
# written by me, J.J. Rosenberg
# No rights are granted to anyone without the express written consent of me or the National Football League
import datetime
from collections import defaultdict

import robin_stocks as r
import keyring
import getpass

########### THINGS YOU MIGHT WANNA CHANGE ####################
MY_RH_USERNAME = "robinhood1@elliotbrandwein.com"
# tickers = ['UAL', 'AAL', 'JETS', 'GME', 'NOK', 'F', 'GE', 'OPK']
MIN_PREMIUM_PERCENTAGE = 1
# MAX_PREMIUM_PERCENTAGE = 2 # to use you must also uncomment code below
##############################################################

pwd = keyring.get_password("robinhood", "my_very_own_rh_username")
if pwd is None:
    print("First time? Securely type in your Robinhood Password please:")
    # Stores password in local system using keyring
    keyring.set_password("robinhood", "my_very_own_rh_username", getpass.getpass())
    pwd = keyring.get_password("robinhood", "my_very_own_rh_username")

login = r.login(MY_RH_USERNAME, pwd)

print("Please input the ticker you want to check")
ticker = input()

latest_prices = r.get_latest_price(ticker)
prices = dict(zip(ticker, list(map(float, latest_prices))))

today = datetime.date.today()
friday = today + datetime.timedelta((4 - today.weekday()) % 7)


#TODO: add input param so it can filter out monthlies, yearlies ect. ect. if asked for

expiration = "{}-{}-{}".format(friday.year, friday.month, friday.day)
price = r.stocks.get_latest_price(ticker)[0]
data = r.options.find_tradable_options(ticker)
print(data[0])
# filtered_data = dict(filter(lambda x: datetime.datetime.strptime(x['expiration_date'],"%Y-%m-%d") < friday.date(), data))
# print(filtered_data)
# sorted_data = sorted(data, key=lambda x: x['expiration_date'], reverse=False)

# data = r.options.find_options_by_expiration(ticker,expiration)
# #if its too late in the week, we need to move up our options to the next week
# if(data == []):
#     friday = friday + datetime.timedelta(7)
#     expiration = "{}-{}-{}".format(friday.year, friday.month, friday.day)
#     price = r.stocks.get_latest_price(ticker)[0]
#     data = r.options.find_options_by_expiration(ticker,expiration)
# putData = r.find_options_by_expiration(ticker, expirationDate=expiration, optionType='put')
# putsToLookAt = defaultdict(lambda: [])
# for put in putData:
#     tick = put["chain_symbol"]
#     curr_stock_price = prices[tick]
#     strike = float(put["strike_price"])
#     if strike > curr_stock_price:
#         # We don't sell puts for strikes above the current stock price
#         continue
#     premium = float(put["bid_price"])  # only the bid price is guaranteed, rest is theoretical
#     if premium < strike * (MIN_PREMIUM_PERCENTAGE / 100):
#         # Not worth it
#         continue
#     # if premium > strike * (MAX_PREMIUM_PERCENTAGE / 100):
#     #     # Probably too risky to consider
#     #     continue
#     putsToLookAt[tick].append("${} strike for ${} = {:.2%}".format(strike, premium, premium / strike))

# print("Puts expiring on {} for strikes below current stock price with profitability above {}%:"
#       .format(expiration, MIN_PREMIUM_PERCENTAGE))
# # for tick in tickers:
# print("*" * 50)
# print("{}: Current Price: {}".format(ticker, prices[ticker]))
# puts = putsToLookAt[ticker]
# if not puts:
#     print("No puts are worth it this week for this guy")
# else:
#     puts.sort()
#     for put in puts:
#         print("\t{}".format(put))
