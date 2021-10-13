import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_bar, facet_wrap, ggtitle, xlab, ylab
import matplotlib.pyplot as plt
import scipy.stats as stats
import math


dfDemandsWeekdays = pd.read_csv('data\DemandsWeekdays.csv', index_col=0)
dfDemandsSaturdays = pd.read_csv('data\DemandsSaturdays.csv', index_col=0)

store_type = []
for store in dfDemandsWeekdays.index.values:
    if 'Countdown' in store and 'Metro' not in store:
        store_type.append('Countdown')
    else:
        store_type.append('Other')
        dfDemandsSaturdays = dfDemandsSaturdays.drop(store, axis=0)

dfDemandsWeekdays['Store_type'] = store_type

dfDemandsWeekdays_pivotLonger = pd.melt(dfDemandsWeekdays, id_vars=['Store_type'],  value_vars=['2021-06-14', '2021-06-15', '2021-06-16', '2021-06-17', '2021-06-18', '2021-06-21', 
                                                                '2021-06-22', '2021-06-23', '2021-06-24', '2021-06-25', '2021-06-28', '2021-06-29', 
                                                                '2021-06-30', '2021-07-01', '2021-07-02', '2021-07-05', '2021-07-06', '2021-07-07', 
                                                                '2021-07-08', '2021-07-09'], var_name='Date', value_name='Demand_Value')

dfDemandsSaturdays_pivotLonger = pd.melt(dfDemandsSaturdays,  value_vars=['2021-06-19', '2021-06-26', '2021-07-03', '2021-07-10'], var_name='Date', value_name='Demand_Value')

plotWeekday = (ggplot(dfDemandsWeekdays_pivotLonger,  aes(x='Demand_Value')) + geom_bar(stat='count', fill="cornflowerblue") + facet_wrap('Store_type', scales = 'free') + 
    ggtitle("Plot of Weekday Demand Distribution for \n Countdown Stores and Other Stores") + xlab("Demand (no. pallets)") + ylab("Frequency"))
print(plotWeekday)

plotSaturday = (ggplot(dfDemandsSaturdays_pivotLonger,  aes(x='Demand_Value')) + geom_bar(stat='count', fill="cornflowerblue") + 
    ggtitle("Plot of Saturday Demand Distribution \n for Countdown Stores") + xlab("Demand (no. pallets)") + ylab("Frequency"))
print(plotSaturday)


mu = 40
variance = 10
sigma = math.sqrt(variance)
delay = np.linspace(mu - 4*sigma, mu + 4*sigma, 10000)
plt.plot(delay, stats.norm.pdf(delay, mu, sigma))
plt.show()