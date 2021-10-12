import numpy as np
import pandas as pd
from itertools import permutations
from pulp import *

# Read in data and format into regions for weedays and weekends
######################################################################################################################################################################

# read in data as pandas dataframes
dfDemands = pd.read_csv('Data\WoolworthsDemands.csv', index_col=0)
dfDurations = pd.read_csv('Data\WoolworthsTravelDurations.csv', index_col=0)
dfLocations = pd.read_csv('Data\WoolworthsLocations.csv', index_col=0)

dfDemandsWeekdays = dfDemands.copy()
dfDemandsSaturdays = dfDemands.copy()

WeekendDates = ['2021-06-19', '2021-06-20', '2021-06-26', '2021-06-27', '2021-07-03', '2021-07-04', '2021-07-10', '2021-07-11']
SaturdayDates = ['2021-06-19', '2021-06-26', '2021-07-03', '2021-07-10']

for date in WeekendDates:   
    dfDemandsWeekdays.pop(date)
dfDemandsWeekdays['Upper_Quartile'] = dfDemandsWeekdays.mean(axis=1)

countdownWeekdayMean = 0
otherWeekdayMean = 0

countCountdown = 0
countOther = 0
for store in dfDemandsWeekdays.index.values:
    if 'Countdown' in store and 'Metro' not in store:
        countCountdown += 1
        countdownWeekdayMean += dfDemandsWeekdays.loc[store]['Upper_Quartile']
    else:
        countOther += 1
        otherWeekdayMean += dfDemandsWeekdays.loc[store]['Upper_Quartile']

countdownWeekdayMean = countdownWeekdayMean/countCountdown
otherWeekdayMean = otherWeekdayMean/countOther



for date in dfDemandsSaturdays.columns:
    if date not in SaturdayDates:
        dfDemandsSaturdays.pop(date)
dfDemandsSaturdays['Upper_Quartile'] = dfDemandsSaturdays.mean(axis=1)

countdownSaturdayMean = 0

countCountdown = 0
for store in dfDemandsWeekdays.index.values:
    if 'Countdown' in store and 'Metro' not in store:
        countCountdown += 1
        countdownSaturdayMean += dfDemandsSaturdays.loc[store]['Upper_Quartile']

countdownSaturdayMean = countdownSaturdayMean/countCountdown

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
    elif row['Lat'] >= -36.81111802 and row['Long'] >= 174.7234261 and row['Store'] != 'Distribution Centre Auckland':
        region.append('North')
    elif row['Store'] != 'Distribution Centre Auckland':
        region.append('West')
    else:
        region.append('Distribution Centre Auckland')

# add regions column to dataframe
dfLocations['Region'] = region
dfLocations.to_csv('Data\WoolworthsRegion.csv')

# read in data and initialise region arrays
dfRegions = pd.read_csv('Data\WoolworthsRegion.csv')
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
    elif row['Region'] == 'Central' and row['Store'] != 'Distribution Centre Auckland':
        Central.append(row['Store'])


# Get all possible feasible routes for the weekdays in each region using permutations and constraints
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

# remove route if total demand exceeds 24 crates (leaving 2 crates as leeway)
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        demand = 0
        for store in region[i]:
            if 'Countdown' in store and 'Metro' not in store:
                demand += countdownWeekdayMean
            else:
                demand += otherWeekdayMean
        if demand > 24:
            region.pop(i)

# remove route if total duration exceeds 10000 seconds (leaving 4400 seconds as leeway)
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        duration = len(region[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][region[i][0]] + dfDurations['Distribution Centre Auckland'][region[i][-1]]
        for j in range(len(region[0]) - 2):
            duration = duration + dfDurations[region[i][j]][region[i][j + 1]]
        if duration > 10000:
            region.pop(i)


# initialise array of feasible routes 
feasibleRoutes = []
# append all feasible routes into array
for region in combRegions:
    for route in region:
        feasibleRoutes.append(route)

print("The number of feasible routes is :", len(feasibleRoutes))
print("")

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
    print("Not all stores are accounted for (Weekday)!")
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


# create and solve the weekday lp
######################################################################################################################################################################

probWeekday =  LpProblem("WoolworthsLpWeekday", LpMinimize)

routes_vars = {Route[1]: LpVariable("X_" + str(Route[0]), lowBound = 0, upBound = 1, cat = 'Binary') for Route in lpMat}

# Objective function
probWeekday += lpSum(routes_vars[lpMat[i][1]] * lpMat[i][2] for i in range(len(routes_vars))), "Total Cost of Daily Delivering"

# Constraints added to prob
for store in allStores:   
    probWeekday += lpSum(routes_vars[lpMat[i][1]] for i in range(len(routes_vars)) if store in lpMat[i][1]) == 1  # constraint that each store must be visited once

print(probWeekday)

# Write the lp to a file
probWeekday.writeLP('WoolworthsLpWeekday')

# Solving the problem
probWeekday.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[probWeekday.status])
print("")  

# Each of the chosen routes is added to an array
chosenRouteNums = []
for v in probWeekday.variables():
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
print("Minimised Cost for Weedays  =  $", round(value(probWeekday.objective), 2))
print("")    
print("")    
print("")    


# Get all possible feasible routes for saturday in each region using permutations and constraints
######################################################################################################################################################################


SouthSaturday = []
EastSaturday = []
WestSaturday = []
NorthSaturday = []
CentralSaturday = []
# put each store into their respective region array
for index, row in dfRegions.iterrows():
    if row['Region'] == 'South' and 'Countdown' in row['Store'] and 'Metro' not in row['Store']:
        SouthSaturday.append(row['Store'])
    elif row['Region'] == 'East' and 'Countdown' in row['Store'] and 'Metro' not in row['Store']:
        EastSaturday.append(row['Store'])
    elif row['Region'] == 'West' and 'Countdown' in row['Store'] and 'Metro' not in row['Store']:
        WestSaturday.append(row['Store'])
    elif row['Region'] == 'North' and 'Countdown' in row['Store'] and 'Metro' not in row['Store']:
        NorthSaturday.append(row['Store'])
    elif row['Region'] == 'Central' and 'Countdown' in row['Store'] and 'Metro' not in row['Store']:
        CentralSaturday.append(row['Store'])


# get route permutations of stores in each region
combSouthSaturday5 = list(permutations(SouthSaturday, 5))
combSouthSaturday4 = list(permutations(SouthSaturday, 4))
combSouthSaturday3 = list(permutations(SouthSaturday, 3))
combSouthSaturday2 = list(permutations(SouthSaturday, 2))
combSouthSaturday1 = list(permutations(SouthSaturday, 1))
combEastSaturday5 = list(permutations(EastSaturday, 5))
combEastSaturday4 = list(permutations(EastSaturday, 4))
combEastSaturday3 = list(permutations(EastSaturday, 3))
combEastSaturday2 = list(permutations(EastSaturday, 2))
combEastSaturday1 = list(permutations(EastSaturday, 1))
combWestSaturday5 = list(permutations(WestSaturday, 5))
combWestSaturday4 = list(permutations(WestSaturday, 4))
combWestSaturday3 = list(permutations(WestSaturday, 3))
combWestSaturday2 = list(permutations(WestSaturday, 2))
combWestSaturday1 = list(permutations(WestSaturday, 1))
combNorthSaturday4 = list(permutations(NorthSaturday, 4))
combNorthSaturday3 = list(permutations(NorthSaturday, 3))
combNorthSaturday2 = list(permutations(NorthSaturday, 2))
combNorthSaturday1 = list(permutations(NorthSaturday, 1))
combCentralSaturday5 = list(permutations(CentralSaturday, 5))
combCentralSaturday4 = list(permutations(CentralSaturday, 4))
combCentralSaturday3 = list(permutations(CentralSaturday, 3))
combCentralSaturday2 = list(permutations(CentralSaturday, 2))
combCentralSaturday1 = list(permutations(CentralSaturday, 1))

# intialise array with all route permutations for each region
combRegionsSaturday = [combSouthSaturday5, combSouthSaturday4, combSouthSaturday3, combSouthSaturday2, combSouthSaturday1, combEastSaturday5, combEastSaturday4, combEastSaturday3, combEastSaturday2, combEastSaturday1, combWestSaturday5, combWestSaturday4, combWestSaturday3, combWestSaturday1, combWestSaturday2, combNorthSaturday4, combNorthSaturday3, combNorthSaturday2, combNorthSaturday1, combCentralSaturday5, combCentralSaturday4, combCentralSaturday3, combCentralSaturday2, combCentralSaturday1]

# remove route if total demand exceeds 24 crates
for region in combRegionsSaturday:
    for i in range(len(region) - 1, -1, -1):
        demand = 0
        for store in region[i]:
            demand = demand + countdownSaturdayMean
        if demand > 24:
            region.pop(i)

# remove route if total duration exceeds 10000 seconds
for region in combRegionsSaturday:
    for i in range(len(region) - 1, -1, -1):
        duration = len(region[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][region[i][0]] + dfDurations['Distribution Centre Auckland'][region[i][-1]]
        for j in range(len(region[0]) - 2):
            duration = duration + dfDurations[region[i][j]][region[i][j + 1]]
        if duration > 10000:
            region.pop(i)


# initialise array of feasible routes 
feasibleRoutesSaturday = []
# append all feasible routes into array
for region in combRegionsSaturday:
    for route in region:
        feasibleRoutesSaturday.append(route)

print("The number of feasible routes is :", len(feasibleRoutesSaturday))
print("")
# create a list of all stores
allStoresSaturday = SouthSaturday + NorthSaturday + EastSaturday + WestSaturday + CentralSaturday
missingStoresSaturday = SouthSaturday + NorthSaturday + EastSaturday + WestSaturday + CentralSaturday

# check if any stores are missing from the feasible routes
for route in feasibleRoutesSaturday:
    for store in route:
        if store in missingStoresSaturday:
            missingStoresSaturday.remove(store)

# if any missing stores, code is exited
if missingStoresSaturday != []:
    print("Not all stores are accounted for (Saturday)!")
    exit()

# initialise arrays for the lp
lpMatIndexSaturday = np.zeros((len(feasibleRoutesSaturday)))
lpMatRoutesSaturday = []
lpMatCostsSaturday = np.zeros((len(feasibleRoutesSaturday)))

# create the route number and get the cost for each route
for i in range(len(feasibleRoutesSaturday)):
    lpMatIndexSaturday[i] = i
    lpMatRoutesSaturday.append(feasibleRoutesSaturday[i])
    time = len(feasibleRoutesSaturday[0]) * 7.5 * 60 + dfDurations['Distribution Centre Auckland'][feasibleRoutesSaturday[i][0]] + dfDurations['Distribution Centre Auckland'][feasibleRoutesSaturday[i][-1]]
    for j in range(len(feasibleRoutesSaturday[i]) - 2):
        time = time + dfDurations[feasibleRoutesSaturday[i][j]][feasibleRoutesSaturday[i][j + 1]]
    lpMatCostsSaturday[i] = round(time * 225/3600, 2)

# zip together arrays into one matrix
lpMatSaturday = list(zip(lpMatIndexSaturday, lpMatRoutesSaturday, lpMatCostsSaturday))


# create and solve the saturday lp
######################################################################################################################################################################

probSaturday =  LpProblem("WoolworthsLpSaturday", LpMinimize)

routes_vars_saturday = {Route[1]: LpVariable("X_" + str(Route[0]), lowBound = 0, upBound = 1, cat = 'Binary') for Route in lpMatSaturday}

# Objective function
probSaturday += lpSum(routes_vars_saturday[lpMatSaturday[i][1]] * lpMatSaturday[i][2] for i in range(len(routes_vars_saturday))), "Total Cost of Delivering on Saturday"

# Constraints added to prob
for store in allStoresSaturday:   
    probSaturday += lpSum(routes_vars_saturday[lpMatSaturday[i][1]] for i in range(len(routes_vars_saturday)) if store in lpMatSaturday[i][1]) == 1  # constraint that each store must be visited once

print(probSaturday)

# Write the lp to a file
probSaturday.writeLP('WoolworthsLpSaturday')

# Solving the problem
probSaturday.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[probSaturday.status])
print("")  

# Each of the chosen routes is added to an array
chosenRouteNumsSaturday = []
for v in probSaturday.variables():
    if v.varValue == 1:
        chosenRouteNumsSaturday.append(v.name)

# The stores of each chosen route are added to an array
chosenRouteStoresSaturday = []
keys = list(routes_vars_saturday.items())
for route_name in chosenRouteNumsSaturday:
    for key in keys:
        if route_name == key[1].name:
            chosenRouteStoresSaturday.append(key[0])

# Both above arrays zipped together and printed
chosenSaturday = list(zip(chosenRouteNumsSaturday, chosenRouteStoresSaturday))
for i in chosenSaturday:
    print(i)

# The optimised objective function (minimum cost for deliveries) printed to screen
print("")    
print("Minimised Cost for Saturday  =  $", round(value(probSaturday.objective), 2))

######################################################################################################################################################################
