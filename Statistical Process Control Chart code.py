# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 11:22:05 2022

@author: matthew.chapman
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick


# df.iloc[:, 1] refers to the 2nd imported column, as this column name can
# change the column index is used rather than the column name

#Name of import document 
# 1st column= month, 
# 2nd column = data, 
# 3rd column = phase
# 4th column = target
#columns need headers and header of 2nd column is chart title
df = pd.read_csv("test.csv")


#number of months to look for increasing/decreasing or runs above/below mean
trend_period = 7

#chart title code
chart_title = df.columns[1]


#Improvement direction (True/False)
improvement_is_increase = False

# calulate mean and create mean line for chart
df["mean"] = df.iloc[:, 1].groupby(df["phase"]).transform("mean")
   
# calculate moving range and add average to dataframe
moving_ranges = [np.nan]
i = 1
for data in range(1, len(df)):
    if df["phase"][i] != df["phase"][i-1]:
        moving_ranges.append(np.nan)
        i += 1
    else:
        moving_ranges.append(abs(df.iloc[:, 1][i] - df.iloc[:, 1][i-1]))
        i += 1
df["moving_range"] = moving_ranges

#  calulate moving range average and add to dataframe
df["moving_range_average"] = df["moving_range"]. \
                             groupby(df["phase"]).transform("mean")

# upper limit
df["upper_limit"] = df["mean"] + (2.66 * df["moving_range_average"])

# lower limit
df["lower_limit"] = df["mean"] - (2.66 * df["moving_range_average"])


#finds points outside limits and used to plot
df["below_lower"] = (df.iloc[:, 1] < df["lower_limit"])
df["above_upper"] = (df.iloc[:, 1] > df["upper_limit"])



# code for ID'ing runs above and mean
df["run_above_mean"] = df.groupby((df.iloc[:, 1] 
                                  < df["mean"]).cumsum()).cumcount()

df["special_cause_run_above_mean"] = (df['test data'] <= df['mean']).cumsum(), df['test data'] > df['mean'].apply(lambda g: g.assign(runcount = (g['test data']>g['mean']).sum())).reset_index(drop = True)

df["special_cause_run_above_mean"] = df["runcount"] >= trend_period


df["run_below_mean"] = df.groupby((df.iloc[:, 1] 
                                  > df["mean"]).cumsum()).cumcount()


special_cause_run_below_mean = (df.groupby(
    [(df['test data'] >= df['mean']).cumsum(), 
      df['test data'] < df['mean']
      ])
    .apply(lambda g: g.assign(runcount = (g['test data']>g['mean']).sum()))
    .reset_index(drop = True)
)

special_cause_run_below_mean["special_cause_below_mean"] = \
    special_cause_run_below_mean["runcount"] >= trend_period



special_cause_run_below_mean["special_cause_run_below_mean"] =  \
    special_cause_run_below_mean["runcount"] >= trend_period

       
#code for ID'ing runs of ascending and decending points

df["run_ascending"] = df.groupby((df.iloc[:, 1] 
                                  <= df.iloc[:, 1].shift(1))
                                  .cumsum()).cumcount()

df["special_cause_ascending"] = df["run_ascending"] >= trend_period 

df["run_decending"] = df.groupby((df.iloc[:, 1] 
                                  >= df.iloc[:, 1].shift(1))
                                  .cumsum()).cumcount()

df["special_cause_decending"] = df["run_decending"] >= trend_period 


## GRAPH ##


figure_1, ax = plt.subplots()



#plotting lines
ax.plot(df["Month"], df.iloc[:, 1], marker = "d")
ax.plot(df["Month"], df["mean"], color = "grey")
ax.plot(df["Month"], df["upper_limit"], ls=":", color = "black")
ax.plot(df["Month"], df["lower_limit"], ls=":", color = "black")
ax.plot(df["Month"], df["target"], ls="-", color = "red")

#plotting points outside limits
if improvement_is_increase == True:
    ax.plot(df["Month"][df["below_lower"]], 
            df.iloc[:, 1][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "orange")
    ax.plot(df["Month"][df["above_upper"]], 
            df.iloc[:, 1][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
elif improvement_is_increase == False:
    ax.plot(df["Month"][df["below_lower"]], 
            df.iloc[:, 1][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["above_upper"]], 
            df.iloc[:, 1][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "orange")

#plotting points above and below mean
if improvement_is_increase == True:
    ax.plot(df["Month"]\
            [df["special_cause_run_above_mean"]],
            df.iloc[:, 1][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"]\
            [special_cause_run_below_mean["special_cause_below_mean"]],
            df.iloc[:, 1][special_cause_run_below_mean\
                          ["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif improvement_is_increase == False:
    ax.plot(df["Month"]\
            [special_cause_run_below_mean["special_cause_run_below_mean"]],
            df.iloc[:, 1][special_cause_run_below_mean\
                          ["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"]\
            [df["special_cause_run_above_mean"]],
            df.iloc[:, 1][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
    
#plotting points ascending/decending
if improvement_is_increase == True:
    ax.plot(df["Month"][df["special_cause_ascending"]],
            df.iloc[:, 1][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["special_cause_decending"]],
            df.iloc[:, 1][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif improvement_is_increase == False:
      ax.plot(df["Month"][df["special_cause_ascending"]],
            df.iloc[:, 1][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
      ax.plot(df["Month"][df["special_cause_decending"]],
            df.iloc[:, 1][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
      


#y axis formatted to percentage if needed

if df.iloc[:, 1].max() < 1.5:
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0)) 
    

# chart formatting
plt.text(0.1, 0.95, "Upper Limit= " + df["upper_limit"].iloc[-1]. \
          round(decimals =2).astype(str),
          horizontalalignment='center',
          verticalalignment='center',
          transform = ax.transAxes,
          fontsize = 16)
plt.text(0.1, 0.9, "Mean= " + df["mean"].iloc[-1]. \
          round(decimals =2).astype(str),
          horizontalalignment='center',
          verticalalignment='center',
          transform = ax.transAxes,
          fontsize = 16)
plt.text(0.1, 0.85, "lower limit= " + df["lower_limit"]. \
          round(decimals =2).iloc[-1].astype(str),
          horizontalalignment='center',
          verticalalignment='center',
          transform = ax.transAxes,
          fontsize = 16)  
ax.tick_params(axis="x", labelrotation= 45)
plt.xticks(ha="right", fontsize = 16)
plt.yticks(fontsize = 16)
plt.title(chart_title, fontsize=25)
plt.tight_layout()
figure_1.set_figwidth(18)
figure_1.set_figheight(9)
figure_1.savefig(f"{chart_title}.png", bbox_inches = "tight")
figure_1.show()