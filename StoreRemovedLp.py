from re import I
import numpy as np
import pandas as pd
from itertools import permutations
from pulp import *
import math
from plotnine import aes, ggplot, geom_bar, facet_wrap, ggtitle, xlab, ylab, geom_histogram
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib.ticker import MaxNLocator
from scipy.stats import truncnorm
import statsmodels.stats.weightstats as sms


# Read in data and format into regions for weedays and weekends
######################################################################################################################################################################

# read in data as pandas dataframes
dfDemands = pd.read_csv('data\WoolworthsDemands.csv', index_col=0)
dfDurations = pd.read_csv('data\WoolworthsTravelDurations.csv', index_col=0)
dfLocations = pd.read_csv('data\WoolworthsLocations.csv', index_col=0)
dfDistances = pd.read_csv('data\WoolworthsDistances.csv', index_col=0)

dfDemandsWeekdays = dfDemands.copy()
dfDemandsSaturdays = dfDemands.copy()

WeekendDates = ['2021-06-19', '2021-06-20', '2021-06-26', '2021-06-27', '2021-07-03', '2021-07-04', '2021-07-10', '2021-07-11']
SaturdayDates = ['2021-06-19', '2021-06-26', '2021-07-03', '2021-07-10']

#   Find the two closest stores and remove one.
min = 99999999
for i in dfDistances:
    for j in range(0, len(dfDistances[i])):
        if dfDistances[i].iloc[j] < min and dfDistances[i].iloc[j] > 0:
            min=dfDistances[i].iloc[j]
            I = i
            J = j

print('The two closest stores are ' + I + ' and '+  dfDistances.iloc[J].name + ', we will consider dropping ' + dfDistances.iloc[J].name)
removed_store = dfDemandsWeekdays.iloc[J].name
dfDemandsWeekdays=dfDemandsWeekdays.drop(dfDemandsWeekdays.iloc[J].name, axis=0)
dfLocations = dfLocations.drop(dfLocations.iloc[J].name, axis=0)


for date in WeekendDates:   
    dfDemandsWeekdays.pop(date)
dfDemandsWeekdays['Mean'] = dfDemandsWeekdays.mean(axis=1)



# write to csv
dfDemandsWeekdays.to_csv('data\SRDemandsWeekdays.csv')

countdownWeekdayMean = 0
otherWeekdayMean = 0

countCountdown = 0
countOther = 0
for store in dfDemandsWeekdays.index.values:
    if 'Countdown' in store and 'Metro' not in store:
        countCountdown += 1
        countdownWeekdayMean += dfDemandsWeekdays.loc[store]['Mean']
    else:
        countOther += 1
        otherWeekdayMean += dfDemandsWeekdays.loc[store]['Mean']

countdownWeekdayMean = countdownWeekdayMean/countCountdown
otherWeekdayMean = otherWeekdayMean/countOther


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
dfLocations.to_csv('data\SRWoolworthsRegion.csv')

# read in data and initialise region arrays
dfRegions = pd.read_csv('data\SRWoolworthsRegion.csv')
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

# remove route if total demand exceeds 24 crates
for region in combRegions:
    for i in range(len(region) - 1, -1, -1):
        demand = 0
        for store in region[i]:
            if 'Countdown' in store and 'Metro' not in store:
                demand = demand + countdownWeekdayMean
            else:
                demand = demand + otherWeekdayMean
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


# Create and solve the weekday lp
######################################################################################################################################################################

probWeekday =  LpProblem("SRWoolworthsLpWeekday", LpMinimize)

routes_vars = {Route[1]: LpVariable("X_" + str(Route[0]), lowBound = 0, upBound = 1, cat = 'Binary') for Route in lpMat}

# Objective function
probWeekday += lpSum(routes_vars[lpMat[i][1]] * lpMat[i][2] for i in range(len(routes_vars))), "Total Cost of Daily Delivering"

# Constraints added to prob
for store in allStores:   
    probWeekday += lpSum(routes_vars[lpMat[i][1]] for i in range(len(routes_vars)) if store in lpMat[i][1]) == 1  # constraint that each store must be visited once

print(probWeekday)

# Write the lp to a file
probWeekday.writeLP('SRWoolworthsLpWeekday')

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
print("Minimised Cost for Weekdays  =  $", round(value(probWeekday.objective), 2))
print("")    
print("")    
print("")    


# Save Weekday routes coordinates to a csv file
######################################################################################################################################################################

chosenRouteCoords = []
for route in chosenRouteStores:
    Route = []
    for store in route:
        for i in range(0, len(dfLocations)):
            if dfLocations.iloc[i, 1] == store:
                Route.append([dfLocations.iloc[i, 2], dfLocations.iloc[i, 3]])
    chosenRouteCoords.append(Route)

dfRoutes = pd.DataFrame(chosenRouteCoords)

dfRoutes.to_csv('data/SRWeekdayRoutes.csv')


# Save Weekday routes as a txt file
######################################################################################################################################################################

textfile = open("data/SRWeekdayRouteStores.txt", "w")
for element in chosenRouteStores:
    for i in element:
        textfile.write(i + ", ")
    textfile.write("\n")
textfile.close()



# Simulation
######################################################################################################################################################################

# read in files
dfDemandsWeekdays = pd.read_csv('data\SRDemandsWeekdays.csv', index_col=0)


# create attribute based on whether a store is a Countdown store or not
store_type = []
for store in dfDemandsWeekdays.index.values:
    if 'Countdown' in store and 'Metro' not in store:
        store_type.append('Countdown')
    else:
        store_type.append('Other')
        
# add attributes to dataframes
dfDemandsWeekdays['Store_type'] = store_type


# pivot the weekday data
dfDemandsWeekdays_pivotLonger = pd.melt(dfDemandsWeekdays, id_vars=['Store_type'],  value_vars=['2021-06-14', '2021-06-15', '2021-06-16', '2021-06-17', '2021-06-18', '2021-06-21', 
                                                                '2021-06-22', '2021-06-23', '2021-06-24', '2021-06-25', '2021-06-28', '2021-06-29', 
                                                                '2021-06-30', '2021-07-01', '2021-07-02', '2021-07-05', '2021-07-06', '2021-07-07', 
                                                                '2021-07-08', '2021-07-09'], var_name='Date', value_name='Demand_Value')
dfDemandsWeekdays_pivotLonger.to_csv('data/SRdfDemandsWeekdays_pivotLonger.csv')


# plot weekday demand distribution based on whether store type is countdown or other
plotWeekday = (ggplot(dfDemandsWeekdays_pivotLonger,  aes(x='Demand_Value')) + geom_bar(stat='count', fill="cornflowerblue") + facet_wrap('Store_type', scales = 'free') + 
    ggtitle("Plot of Weekday Demand Distribution for \n Countdown Stores and Other Stores") + xlab("Demand (no. pallets)") + ylab("Frequency"))
print(plotWeekday)


# create and plot normal distribution for traffic delays
mu = 40
variance = 10
sigma = math.sqrt(variance)
delay = np.linspace(mu - 4*sigma, mu + 4*sigma, 10000)
plt.plot(delay, stats.norm.pdf(delay, mu, sigma))
plt.title("Normal Distribution to Model Delays due to Traffic")
plt.xlabel("Time (minutes)")
plt.ylabel("Probability")
plt.show()

# sample from weekday demand distribution for countdown stores and plot
fig, ax1 = plt.subplots(1)
weekendDemandsSampledCountdown = dfDemandsWeekdays_pivotLonger[dfDemandsWeekdays_pivotLonger.Store_type == 'Countdown'].Demand_Value.sample(n=100000, replace=True)
ax1.hist(weekendDemandsSampledCountdown, bins=13, range=(2.5, 15.5), edgecolor='black', linewidth=1.2, density=True)
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Daily Demand Distribution for Countdown Stores on Weekdays with "+ removed_store + ' removed.')
plt.xlabel("Daily Demand (no. pallets)")
plt.ylabel("Probability")
plt.show()

# sample from weekday demand distribution for other stores  =and plot
fig, ax2 = plt.subplots(1)
weekendDemandsSampledOther = dfDemandsWeekdays_pivotLonger[dfDemandsWeekdays_pivotLonger.Store_type == 'Other'].Demand_Value.sample(n=100000, replace=True)
ax2.hist(weekendDemandsSampledOther, bins=8, range=(1.5, 9.5), edgecolor='black', linewidth=1.2, density=True)
ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Daily Demand Distribution for 'Other' Stores on Weekdays with "+ removed_store + ' removed.')
plt.xlabel("Daily Demand (no. pallets)")
plt.ylabel("Probability")
plt.show()


# define a function to simplify truncnorm function
def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

# create truncated normal distribution for traffic delays       
traffic = get_truncated_normal(mu, sigma, low=15, upp=65)

# sample from truncated traffic delay distribution and plot
trafficSampled = traffic.rvs(10000)
fig, ax4 = plt.subplots(1)
ax4.hist(trafficSampled, edgecolor='black', linewidth=1.2, density=True)
plt.title("Histogram Sampled from Traffic Normal Distribution with "+ removed_store + ' removed.')
plt.xlabel("Time (minutes)")
plt.ylabel("Probability")
plt.show()

# initialise simulation array for daily weekday cost
costWeekdayArray = [] 

# get number of routes on each weekday
file = open("data\SRWeekdayRouteStores.txt", "r")
line_count_weekday = 0
for line in file:
    if line != "\n":
        line_count_weekday += 1
file.close()

# run the monte carlo simulation 1000 times for weedays
for i in range(1000):
    # initialise variables
    costWeekday = 6226.73  # initial cost without sampling considerations
    extraTrucks = 0
    time = 0
    # looping through routes
    for route in chosenRouteStores:
        # intialise array for demand at each store in the route
        demand = []
        # add the duration of each route to the time
        for routeCost in lpMat:
            if route == routeCost[1]:
                time += routeCost[2]*3600/225
        # looping through each store in the route
        for store in route:
            # sampling from demand distributions based on the store type
            if 'Countdown' in store and 'Metro' not in store:
                demand.append(dfDemandsWeekdays_pivotLonger[dfDemandsWeekdays_pivotLonger.Store_type == 'Countdown'].Demand_Value.sample(n=1, replace=True))
            else:
                demand.append(dfDemandsWeekdays_pivotLonger[dfDemandsWeekdays_pivotLonger.Store_type == 'Other'].Demand_Value.sample(n=1, replace=True))
        # turn tuple into list so it is mutable
        route = list(route)
        # if demand is exceeded then remove the first store from the route
        while np.sum(demand) > 26:
            demand.pop(0)
            storeRemoved = route.pop(0)
            extraTrucks += 1
            # change routes and thus overall time
            time = time - dfDurations[storeRemoved][route[0]] + dfDurations['Distribution Centre Auckland'][route[0]]  + dfDurations[storeRemoved]['Distribution Centre Auckland']
    # if all trucks are used up then use wetlease trucks
    if extraTrucks > (60 - line_count_weekday):
        # get random delay for each route and add it to the time and cost
        for i in range(60):
            # getting a random delay from the truncated normal traffic distribution
            randDelay = traffic.rvs()
            costWeekday += randDelay*60*225/3600
            time += randDelay*60
            # wet lease trucks
            costWeekday += (extraTrucks - 60)*2000
    else:
        # get random delay for each route and add it to the time and cost
        for i in range(line_count_weekday + extraTrucks):
            randDelay = traffic.rvs()
            costWeekday += randDelay*60*225/3600
            time += randDelay*60
    # if four hours exceeded for route then add overtime
    if time > 14400:
        costWeekday += (time - 14400)*50/3600
    # append final cost to the cost array
    costWeekdayArray.append(costWeekday)



# plot the cost distributions for weekdays
fig, ax1 = plt.subplots(1)
ax1.hist(costWeekdayArray, edgecolor='black', linewidth=1.2, density=True)

ax1.set_title("Daily Cost Distribution for Weekdays with "+ removed_store + ' removed.')
ax1.set_xlabel("Daily Cost ($)")
ax1.set_ylabel("Probability")

plt.show()

print("")
print("")
print("Confidence interval for weekdays is ", sms.DescrStatsW(costWeekdayArray).tconfint_mean(alpha=0.05))