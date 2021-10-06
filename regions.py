import numpy as np
import pandas as pd
from itertools import permutations
from pulp import *

# Read in data and format into regions
######################################################################################################################################################################

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
    if row['Region'] == 'South' and row['Store'] != 'Distribution Centre Auckland':
        South.append(row['Store'])
    elif row['Region'] == 'East' and row['Store'] != 'Distribution Centre Auckland':
        East.append(row['Store'])
    elif row['Region'] == 'West' and row['Store'] != 'Distribution Centre Auckland':
        West.append(row['Store'])
    elif row['Region'] == 'North' and row['Store'] != 'Distribution Centre Auckland':
        North.append(row['Store'])
    elif  row['Region'] == 'Central' and row['Store'] != 'Distribution Centre Auckland':
        Central.append(row['Store'])


# Get all possible feasible routes in each region using permutations and constraints
######################################################################################################################################################################

# get route permutations of stores in each region
combSouth4 = list(permutations(South, 4))
combSouth3 = list(permutations(South, 3))
combSouth2 = list(permutations(South, 2))
combSouth1 = list(permutations(South, 1))
combEast4 = list(permutations(East, 4))
combEast3 = list(permutations(East, 3))
combEast2 = list(permutations(East, 2))
combEast1 = list(permutations(East, 1))
combWest5 = list(permutations(West, 5))
combWest4 = list(permutations(West, 4))
combWest3 = list(permutations(West, 3))
combWest2 = list(permutations(West, 2))
combWest1 = list(permutations(West, 1))
combNorth3 = list(permutations(North, 3))
combNorth2 = list(permutations(North, 2))
combNorth1 = list(permutations(North, 1))
combCentral4 = list(permutations(Central, 4))
combCentral3 = list(permutations(Central, 3))
combCentral2 = list(permutations(Central, 2))
combCentral1 = list(permutations(Central, 1))

# intialise array with all route permutations for each region
combRegions = [combSouth4, combSouth3, combSouth2, combSouth1, combEast4, combEast3, combEast2, combEast1, combWest5, combWest4, combWest3, combWest1, combWest2, combNorth3, combNorth2, combNorth1, combCentral4, combCentral3, combCentral2, combCentral1]

# remove route if total demand exceeds 24 crates
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        demand = 0
        for store in region[i]:
            if 'Countdown' in store and 'Metro' not in store:
                demand = demand + 7.5
            else:
                demand = demand + 4.5
        if demand > 26:
            region.pop(i)

# remove route if total duration exceeds 10000 seconds
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        duration = len(region[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][region[i][0]] + dfDurations['Distribution Centre Auckland'][region[i][-1]]
        for j in range(len(region[0]) - 2):
            duration = duration + dfDurations[region[i][j]][region[i][j + 1]]
        if duration > 14400:
            region.pop(i)


# initialise array of feasible routes 
feasibleRoutes = []
# append all feasible routes into array
for region in combRegions:
    for route in region:
        feasibleRoutes.append(route)

# create a list of all stores
allStores = South + North + East + West + Central
missingStores = South + North + East + West + Central

# check if any stores are missing from the feasible routes
for route in feasibleRoutes:
    for store in route:
        if store in missingStores:
            missingStores.remove(store)

# if any missing stores, code is exited
if missingStores != []:
    print("Not all stores are accounted for!")
    exit()

# initialise arrays for the lp
lpMatIndex = np.zeros((len(feasibleRoutes)))
lpMatRoutes = []
lpMatCosts = np.zeros((len(feasibleRoutes)))

# create the route number and get the cost for each route
for i in range(len(feasibleRoutes)):
    lpMatIndex[i] = i
    lpMatRoutes.append(feasibleRoutes[i])
    time = len(feasibleRoutes[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][feasibleRoutes[i][0]] + dfDurations['Distribution Centre Auckland'][feasibleRoutes[i][-1]]
    for j in range(len(feasibleRoutes[i]) - 2):
        time = time + dfDurations[feasibleRoutes[i][j]][feasibleRoutes[i][j + 1]]
    lpMatCosts[i] = round(time * 225/3600, 2)

# zip together arrays into one matrix
lpMat = list(zip(lpMatIndex, lpMatRoutes, lpMatCosts))


# create and solve the lp
######################################################################################################################################################################

prob =  LpProblem("WoolworthsLP", LpMinimize)

routes_vars = {Route[1]: LpVariable("X_" + str(Route[0]), lowBound = 0, upBound = 1, cat = 'Binary') for Route in lpMat}

# Objective function
prob += lpSum(routes_vars[lpMat[i][1]] * lpMat[i][2] for i in range(len(routes_vars))), "Total Cost of Daily Delivering"

# Constraints added to prob
for store in allStores:   
    prob += lpSum(routes_vars[lpMat[i][1]] for i in range(len(routes_vars)) if store in lpMat[i][1]) == 1  # constraint that each store must be visited once

print(prob)

# Write the lp to a file
prob.writeLP('WoolworthsLP')

# Solving the problem
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])
print("")  

# Each of the chosen routes is added to an array
chosenRouteNums = []
for v in prob.variables():
    if v.varValue == 1:
        chosenRouteNums.append(v.name)

# The stores of each chosen route are added to an array
chosenRouteStores = []
keys = list(routes_vars.items())
for route_name in chosenRouteNums:
    for key in keys:
        if route_name == key[1].name:
            chosenRouteStores.append(key[0])

# Both above arrays zipped together and printed
chosen = list(zip(chosenRouteNums, chosenRouteStores))
for i in chosen:
    print(i)

# The optimised objective function (minimum cost for deliveries) printed to screen
print("")    
print("Minimised Cost  =  $", round(value(prob.objective), 2))

######################################################################################################################################################################
