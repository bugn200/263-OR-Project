import numpy as np
import pandas as pd
from itertools import permutations

# read in data as pandas dataframes
dfDemands = pd.read_csv('WoolworthsDemands.csv', index_col=0)
dfDurations = pd.read_csv('WoolworthsTravelDurations.csv', index_col=0)
dfLocations = pd.read_csv('WoolworthsLocations.csv', index_col=0)

# initialise region array
region = []

# split stores into their respective regions
for index, row in dfLocations.iterrows():
    if row['Lat'] < -36.94480584 and row['Store'] != 'Distribution Centre Auckland':
        region.append('South')
    elif row['Lat'] >= -36.94480584 and row['Long'] >= 174.8289359 and row['Store'] != 'Distribution Centre Auckland':
        region.append('East')
    elif row['Lat'] >= -36.94480584 and row['Lat'] < -36.81111802 and row['Long'] < 174.8289359 and row['Long'] >= 174.7105595 and row['Store'] != 'Distribution Centre Auckland':
        region.append('Central')
    elif row['Lat'] >= -36.81111802 and row['Long'] >= 174.7248776 and row['Store'] != 'Distribution Centre Auckland':
        region.append('North')
    elif row['Store'] != 'Distribution Centre Auckland':
        region.append('West')
    else:
        region.append('Distribution Centre Auckland')

# add regions column to dataframe
dfLocations['Region'] = region
dfLocations.to_csv('WoolworthsRegion.csv')

# read in data and initialise region arrays
dfRegions = pd.read_csv('WoolworthsRegion.csv')
South = []
East = []
West = []
North = []
Central = []
# put each store into their respective region array
for index, row in dfRegions.iterrows():
    if row['Region'] == 'South':
        South.append(row['Store'])
    elif row['Region'] == 'East':
        East.append(row['Store'])
    elif row['Region'] == 'West':
        West.append(row['Store'])
    elif row['Region'] == 'North':
        North.append(row['Store'])
    else: 
        Central.append(row['Store'])

# get route permutations of stores in each region
combSouth = list(permutations(South, 4))
combEast = list(permutations(East, 4))
combWest = list(permutations(West, 5))
combNorth = list(permutations(North, 3))
combCentral = list(permutations(Central, 4))

# intialise array with all route permutations for each region
combRegions = [combSouth, combEast, combWest, combNorth, combCentral]

# remove route if total demand exceeds 24 crates
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        demand = 0
        for store in region[i]:
            if 'Countdown' in store:
                demand = demand + 7.5
            else:
                demand = demand + 4.5
        if demand > 24:
            region.pop(i)

# remove route if total duration exceeds 10000 seconds
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        duration = len(region[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][region[i][0]] + dfDurations['Distribution Centre Auckland'][region[i][-1]]
        for j in range(len(region[0]) - 2):
            duration = duration + dfDurations[region[i][j]][region[i][j + 1]]
        if duration > 10000:
            region.pop(i)

# initialise route array
routes = []
# append all feasible routes into route array
for region in combRegions:
    for route in region:
        routes.append(route)

# print routes
for route in routes:
    print(route)
    
# print number of routes
print(len(routes))
