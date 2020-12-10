import yahoo
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import load

# load classifier once on launch
rf_classifier = load('models/rf_classifier.ai')

def get_prediction(df, std, ma, adjclose):
    
    df['Return'] = df['Last Price']/df['Strike']
    df['SD/MA'] = std/ma
    df['% MA to adj'] = abs((adjclose/ma)-1)
    df['% ADJ to Strike'] = ((df['Strike']/adjclose)-1).apply(lambda x: abs(x))
    df = df.reindex(columns = ['Contract Name', 'Strike', 'Last Price', 'Safe', 'SD/MA', '% MA to adj', '% ADJ to Strike', 'Return'])
    df['Predictions'] = rf_classifier.predict(df[['SD/MA', '% MA to adj', '% ADJ to Strike', 'Return']])
    df['Predictions'] = df['Predictions'].apply(lambda x: "Assigned" if int(x) == 1 else "Not Assigned") 

    df = df.drop(columns=['SD/MA', '% MA to adj', '% ADJ to Strike', 'Return'])
    return df