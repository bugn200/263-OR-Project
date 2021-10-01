import pandas as pd 
from pulp import *

RouteData = #open route data txt

for (i in range (0, len(RouteData))):
    if RouteData[i].truck == woolworths and RouteData[i].time < 4#hrs:
        cost[i] = #(duration from source to first stop + .. last stop to source + 7min*number of stops) * $225/hour
    if RouteData[i].truck == woolworths and RouteData[i].time > 4#hrs:
        cost[i] = #4hrs * $225/hour + extratime*$275/hour
    if RouteData[i].truck == dailyFreight:
        cost[i] = #(1+ time % 4)$2000




prob = LpProblem("Truck Scheduling and Efficiency for Woolworths NZ", LpMinimize)

tie_vars = LpVariable.dicts("Route",RouteData[][1],0)






# Solving routines - no need to modify
prob.writeLP('Truck Scheduling and Efficiency for Woolworths NZ.lp')

prob.solve()

print("Group 19")

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

# Each of the variables is printed with its resolved optimum value
for v in prob.variables():
    print(v.name, "=", v.varValue)

# The optimised objective function valof Ingredients pue is printed to the screen    
print("Total cost = ", value(prob.objective))
