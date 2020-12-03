#
# written by me, J.J. Rosenberg
# No rights are granted to anyone without the express written consent of me or the National Football League
import datetime
from collections import defaultdict

import robin_stocks as r
import keyring
import getpass

########### THINGS YOU MIGHT WANNA CHANGE ####################
MY_RH_USERNAME = ""
tickers = ['UAL', 'AAL', 'JETS', 'GME', 'NOK', 'F', 'GE', 'OPK']
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


latest_prices = r.get_latest_price(tickers)
prices = dict(zip(tickers, list(map(float, latest_prices))))

today = datetime.date.today()
friday = today + datetime.timedelta((4 - today.weekday()) % 7)
# If it's late in the week and you want to look at next week, uncomment the below line
# friday = friday + datetime.timedelta(7)

expiration = "{}-{}-{}".format(friday.year, friday.month, friday.day)

putData = r.find_options_by_expiration(tickers, expirationDate=expiration, optionType='put')


putsToLookAt = defaultdict(lambda: [])
for put in putData:
    tick = put["chain_symbol"]
    curr_stock_price = prices[tick]
    strike = float(put["strike_price"])
    if strike > curr_stock_price:
        # We don't sell puts for strikes above the current stock price
        continue
    premium = float(put["bid_price"])  # only the bid price is guaranteed, rest is theoretical
    if premium < strike * (MIN_PREMIUM_PERCENTAGE / 100):
        # Not worth it
        continue
    # if premium > strike * (MAX_PREMIUM_PERCENTAGE / 100):
    #     # Probably too risky to consider
    #     continue
    putsToLookAt[tick].append("${} strike for ${} = {:.2%}".format(strike, premium, premium / strike))

print("Puts expiring on {} for strikes below current stock price with profitability above {}%:"
      .format(expiration, MIN_PREMIUM_PERCENTAGE))
for tick in tickers:
    print("*" * 50)
    print("{}: Current Price: {}".format(tick, prices[tick]))
    puts = putsToLookAt[tick]
    if not puts:
        print("No puts are worth it this week for this guy")
    else:
        puts.sort()
        for put in puts:
            print("\t{}".format(put))
