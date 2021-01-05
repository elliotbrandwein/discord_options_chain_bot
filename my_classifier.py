import yahoo
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import load
import dateutil.parser as dp
import datetime

# load classifier once on launch
rf_classifier = load('models/rf_classifier.ai')

def get_expiry_from_name(c_name, ticker):
    offset = len(ticker)
    expiry = c_name[offset:offset+3] + c_name[offset+3:offset+5] + c_name[offset+5:offset+6]
    expiry = expiry[2:] + expiry[0:2]
    return dp.parse(expiry)

def get_prediction(df, std, ma, adjclose, ticker):
    df = df.reset_index()
    expiry = get_expiry_from_name(df['Contract Name'][0], ticker)
    df['IV'] = df['Implied Volatility'].apply(lambda x: float(x.replace('%','').replace(',',''))/100)
    df = df.drop(columns=['Implied Volatility'])
    df['days_to_expiry'] = expiry - datetime.datetime.today()
    df['days_to_expiry'] = df['days_to_expiry'].apply(lambda x: x.days+1)
    df['SD/MA'] = std/ma
    df['% MA to adj'] = abs((adjclose/ma)-1)
    df['% ADJ to Strike'] = ((df['Strike']/adjclose)-1).apply(lambda x: abs(x))

    df = df.reindex(columns = ['Strike', 'Last Price', 'IV', 'Safe', 'days_to_expiry', 'SD/MA', '% MA to adj', '% ADJ to Strike'])
    df['Predictions'] = rf_classifier.predict(df[['IV', 'days_to_expiry', 'SD/MA', '% MA to adj', '% ADJ to Strike']])
    df['Predictions'] = df['Predictions'].apply(lambda x: "Assigned" if int(x) == 1 else "Not Assigned") 

    df = df.drop(columns=['days_to_expiry', 'SD/MA', '% MA to adj', '% ADJ to Strike'])
    df['IV'] = df['IV'].apply(lambda x: round(x, 2))
    return df
