import numpy as np
import pandas as pd

dfDemands = pd.read_csv('WoolworthsDemands.csv')
dfDurations = pd.read_csv('WoolworthsTravelDurations.csv')
dfLocations = pd.read_csv('WoolworthsLocations.csv')

southAucklandList = []
eastAucklandList = []
centralAucklandList = []
northAucklandList = []
westAucklandList = []

for index, row in dfLocations.iterrows():
    if row['Lat'] < -36.94480584 and row['Store'] != 'Distribution Centre Auckland':
        southAucklandList.append(row['Store'])
    elif row['Lat'] >= -36.94480584 and row['Long'] >= 174.8289359 and row['Store'] != 'Distribution Centre Auckland':
        eastAucklandList.append(row['Store'])
    elif row['Lat'] >= -36.94480584 and row['Lat'] < -36.81111802 and row['Long'] < 174.8289359 and row['Long'] >= 174.7105595 and row['Store'] != 'Distribution Centre Auckland':
        centralAucklandList.append(row['Store'])
    elif row['Lat'] >= -36.81111802 and row['Long'] >= 174.7248776 and row['Store'] != 'Distribution Centre Auckland':
        northAucklandList.append(row['Store'])
    elif row['Store'] != 'Distribution Centre Auckland':
        westAucklandList.append(row['Store'])


