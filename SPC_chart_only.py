# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 10:04:16 2023

@author: MATTHEW.CHAPMAN
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick
import seaborn as sns
import urllib.request
from PIL import Image


def convert_df(df):
    return df.to_csv().encode("utf-8")

#number of months to look for increasing/decreasing or runs above/below mean
trend_period = 7
df = pd.read_csv("Blank_template.csv")

#performance imporvements nees to be "up", "down" or "nether"
performance_improvement = "up"

#is the data a percentage? ("Yes" or "No")
data_format = "Yes"

y_axis_zero = "no"

chart_title ="test"
  

# SPC icons from github

fail_target_icon = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/AssuranceIconFail.png?raw=true"
hit_or_miss_icon = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/AssuranceIconHitOrMiss.png?raw=true"
pass_target_icon = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/AssuranceIconPass.png?raw=true"
common_cause_variation_icon = "https://github.com/nhsengland/" \
    "making-data-count/blob/main/Icons/VariationIconCommonCause.png?raw=true"
special_cause_concern_high_icon = "https://github.com/nhsengland/" \
    "making-data-count/blob/main/Icons/VariationIconConcernHigh.png?raw=true"
special_cause_concern_low_icon = "https://github.com/nhsengland/" \
    "making-data-count/blob/main/Icons/VariationIconConcernLow.png?raw=true"
special_cause_improvement_high_icon = "https://github.com/nhsengland/" \
    "making-data-count/blob/main/Icons/VariationIconImprovementHigh.png"\
        "?raw=true"
special_cause_improvement_low_icon = "https://github.com/nhsengland/" \
    "making-data-count/blob/main/Icons/VariationIconImprovementLow." \
        "png?raw=true"
special_cause_high_icon = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/VariationIconNeitherHigh.png?raw=true"
special_cause_low_icon = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/VariationIconNeitherLow.png?raw=true"
icon_empty = "https://github.com/nhsengland/making-data-count/" \
    "blob/main/Icons/IconEmpty.png?raw=true"
variation_neither_high = "https://github.com/nhsengland/making-data-count" \
    "/blob/main/Icons/VariationIconNeitherHigh.png?raw=true"
variation_neither_low =  "https://github.com/nhsengland/making-data-count" \
    "/blob/main/Icons/VariationIconNeitherLow.png?raw=true"    

   

#overwrite column headers so rest of code will work if header were changed 
#in the uploaded file

df.columns = ["Month", "plotdata", "phase", "target"]

# calulate mean and create mean line for chart
df["mean"] = df["plotdata"].groupby(df["phase"]).transform("mean")
   
# calculate moving range and add average to dataframe
moving_ranges = [np.nan]
i = 1
for data in range(1, len(df)):
    if df["phase"][i] != df["phase"][i-1]:
        moving_ranges.append(np.nan)
        i += 1
    else:
        moving_ranges.append(abs(df["plotdata"][i] - df["plotdata"][i-1]))
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
df["below_lower"] = (df["plotdata"] < df["lower_limit"])
df["above_upper"] = (df["plotdata"] > df["upper_limit"])


# code for ID'ing runs above and mean
df["run_above_mean"] = df.groupby((df["mean"] 
                                  > df["plotdata"])
                                  .cumsum()).cumcount()

df["special_cause_run_above_mean"] = df["run_above_mean"].\
    shift(1-trend_period).\
        rolling(trend_period, min_periods = 1).\
            max() >= trend_period

df["run_below_mean"] = df.groupby((df["mean"] 
                                  < df["plotdata"])
                                  .cumsum()).cumcount()

df["special_cause_run_below_mean"] = df["run_below_mean"].\
    shift(1-trend_period).\
        rolling(trend_period, min_periods = 1).\
            max() >= trend_period

       
#code for ID'ing runs of ascending and decending points

df["run_ascending"] = df.groupby((df["plotdata"] 
                                  <= df["plotdata"].shift(1))
                                  .cumsum()).cumcount()

df["special_cause_ascending"] = df["run_ascending"].\
    shift(1-trend_period).\
        rolling(trend_period, min_periods = 1).\
            max() >= trend_period

df["run_decending"] = df.groupby((df["plotdata"] 
                                  >= df["plotdata"].shift(1))
                                  .cumsum()).cumcount()

df["special_cause_decending"] = df["run_decending"].\
    shift(1-trend_period).\
        rolling(trend_period, min_periods = 1).\
            max() >= trend_period



## GRAPH ##


figure_1, ax = plt.subplots()

sns.set_theme(style = "ticks")
#sns.set_context("paper")
sns.despine()



#plotting lines
ax.plot(df["Month"], df["plotdata"], marker = "o", markersize = 10, 
        color = "#44546A", markerfacecolor = "grey", markeredgecolor = "grey",
        linewidth = 4)
ax.plot(df["Month"], df["mean"], color = "grey", linewidth = 2)
ax.plot(df["Month"], df["upper_limit"], ls=":", color = "black", linewidth = 2)
ax.plot(df["Month"], df["lower_limit"], ls=":", color = "black", linewidth = 2)
ax.plot(df["Month"], df["target"], ls=":", color = "red", linewidth = 2)

#plotting runs ascending/decending
if performance_improvement == "up":
    ax.plot(df["Month"][df["special_cause_ascending"]],
            df["plotdata"][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["special_cause_decending"]],
            df["plotdata"][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif performance_improvement == "down":
      ax.plot(df["Month"][df["special_cause_ascending"]],
            df["plotdata"][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
      ax.plot(df["Month"][df["special_cause_decending"]],
            df["plotdata"][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
else:
    ax.plot(df["Month"][df["special_cause_ascending"]],
          df["plotdata"][df["special_cause_ascending"]],
          marker= "o", markersize=10, ls = "None", color = "purple")
    ax.plot(df["Month"][df["special_cause_decending"]],
          df["plotdata"][df["special_cause_decending"]],
          marker= "o", markersize=10, ls = "None", color = "purple")


#plotting runs above and below mean
if performance_improvement == "up":
    ax.plot(df["Month"][df["special_cause_run_above_mean"]],
            df["plotdata"][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["special_cause_run_below_mean"]],
            df["plotdata"][df["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif performance_improvement == "down":
    ax.plot(df["Month"][df["special_cause_run_above_mean"]],
            df["plotdata"][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
    ax.plot(df["Month"][df["special_cause_run_below_mean"]],
            df["plotdata"][df["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
else:
    ax.plot(df["Month"][df["special_cause_run_above_mean"]],
            df["plotdata"][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "purple")
    ax.plot(df["Month"][df["special_cause_run_below_mean"]],
            df["plotdata"][df["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "purple")


#plotting points outside limits
if performance_improvement == "up":
    ax.plot(df["Month"][df["below_lower"]], 
            df["plotdata"][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "orange")
    ax.plot(df["Month"][df["above_upper"]], 
            df["plotdata"][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
elif performance_improvement == "down":
    ax.plot(df["Month"][df["below_lower"]], 
            df["plotdata"][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["above_upper"]], 
            df["plotdata"][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "orange")
else:
    ax.plot(df["Month"][df["below_lower"]], 
            df["plotdata"][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "purple")
    ax.plot(df["Month"][df["above_upper"]], 
            df["plotdata"][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "purple")


    


#y axis formatted to percentage if needed

if data_format == "Yes":
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0)) 
    
#set y axis to zero if option selected       
if y_axis_zero == "Yes":
    ax.set_ylim(0)

            
ax.tick_params(axis="x", labelrotation= 90)
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.title(chart_title, fontsize=25)
plt.tight_layout()
figure_1.set_figwidth(18)
figure_1.set_figheight(9)


#Data labels

target = df["target"].iloc[-1]
mean = df["mean"].iloc[-1]
# #upper_limit = df["upper_limit"].iloc[-1]
# lower_limit = df["lower_limit"].iloc[-1]



if data_format == "No":
    target_str = f"{target:.1f}"
    # upper_limit_str = f"{upper_limit:.2f}"
    # lower_limit_str = f"{lower_limit:.2f}"
    mean_str = f"{mean:.1f}"
    
    ax.text(df["Month"].iloc[-2], 
            df["target"].iloc[-1], 
            "Threshold= " + target_str, 
            ha="center", 
            va="baseline", 
            size=17)
    
    ax.text(df["Month"].iloc[-len(df)+2],
            df["upper_limit"].iloc[-len(df)], 
            "Upper process limit" , 
            ha="center", 
            va="baseline", 
            size=17)
    
    if y_axis_zero == "Yes" and df["lower_limit"].iloc[-1] > 0:
        ax.text(df["Month"].iloc[-len(df)+2], 
                df["lower_limit"].iloc[-len(df)], 
                "Lower process limit", 
                ha="center", 
                va="baseline", 
                size=17)
        
    elif y_axis_zero == "No":
        ax.text(df["Month"].iloc[-len(df)+2], 
                df["lower_limit"].iloc[-len(df)], 
                "Lower process limit", 
                ha="center", 
                va="baseline", 
                size=17)
    
    ax.text(df["Month"].iloc[-2], 
            df["mean"].iloc[-1], 
            "Mean= " + mean_str, 
            ha="center", 
            va="baseline",
            size=17)
    
else:
    target = df["target"].iloc[-1]*100
    mean = df["mean"].iloc[-1]*100
    upper_limit = df["upper_limit"].iloc[-1]*100
    lower_limit = df["lower_limit"].iloc[-1]*100
      
    
    target_str = f"{target:.2f}"
    upper_limit_str = f"{upper_limit:.2f}"
    lower_limit_str = f"{lower_limit:.2f}"
    mean_str = f"{mean:.2f}"
    

    ax.text(df["Month"].iloc[-2], 
            df["target"].iloc[-1], 
            "Target= " + target_str + "%", 
            ha="center", 
            va="baseline", 
            size=17)
    
    ax.text(df["Month"].iloc[-len(df)+2],
            df["upper_limit"].iloc[-len(df)], 
            "Upper process limit= " + upper_limit_str + "%", 
            ha="center", 
            va="baseline", 
            size=17)
    
    if y_axis_zero == "Yes" and df["lower_limit"].iloc[-1] > 0:
        ax.text(df["Month"].iloc[-len(df)+2], 
                df["lower_limit"].iloc[-len(df)], 
                "Lower process limit= " + lower_limit_str + "%", 
                ha="center", 
                va="baseline", 
                size=17)
        
    elif y_axis_zero == "No":
        ax.text(df["Month"].iloc[-len(df)+2], 
                df["lower_limit"].iloc[-len(df)], 
                "Lower process limit= " + lower_limit_str + "%", 
                ha="center", 
                va="baseline", 
                size=17)
        
    ax.text(df["Month"].iloc[-2], 
            df["mean"].iloc[-1], 
            "Mean= " + mean_str + "%", 
            ha="center", 
            va="baseline", 
            size=17)
    
#icons to show

special_cause_improvement_high = False
special_cause_concern_low = False
special_cause_improvement_low = False
special_cause_concern_high = False
special_cause_neither_low = False
special_cause_neither_high = False



if performance_improvement == "up":
    
    if df["plotdata"].iloc[-1] > df["upper_limit"].iloc[-1]:
        special_cause_improvement_high = True
        
    elif df["plotdata"].iloc[-1] < df["lower_limit"].iloc[-1]:
        special_cause_concern_low = True    
        
    elif df["special_cause_run_above_mean"].iloc[-1] == True:
        special_cause_improvement_high = True
    
    elif df["special_cause_run_below_mean"].iloc[-1] == True:
        special_cause_concern_low = True
    
    elif df["special_cause_ascending"].iloc[-1] == True:
        special_cause_improvement_high = True
       
    elif df["special_cause_decending"].iloc[-1] == True:
        special_cause_concern_low = True
        
elif performance_improvement == "down":
    if df["plotdata"].iloc[-1] < df["lower_limit"].iloc[-1]:
        special_cause_improvement_low = True
    
    elif df["plotdata"].iloc[-1] > df["upper_limit"].iloc[-1]:
        special_cause_concern_high = True
        
    elif df["special_cause_run_below_mean"].iloc[-1] == True:
        special_cause_improvement_low = True
    
    elif df["special_cause_run_above_mean"].iloc[-1] == True:
        special_cause_concern_high = True
    
    elif df["special_cause_decending"].iloc[-1] == True:
        special_cause_improvement_low = True
                
    elif df["special_cause_ascending"].iloc[-1] == True:
        special_cause_concern_high = True
        
else:
    if df["plotdata"].iloc[-1] < df["lower_limit"].iloc[-1]:
        special_cause_neither_low = True
        
    if df["special_cause_run_below_mean"].iloc[-1] == True:
        special_cause_neither_low = True
    
    if df["special_cause_decending"].iloc[-1] == True:
        special_cause_neither_low = True
        
    if df["plotdata"].iloc[-1] > df["upper_limit"].iloc[-1]:
        special_cause_neither_high = True
        
    if df["special_cause_run_above_mean"].iloc[-1] == True:
        special_cause_neither_high = True
        
    if df["special_cause_ascending"].iloc[-1] == True:
        special_cause_neither_high = True
    
   
variation_icon = common_cause_variation_icon   
        
if special_cause_improvement_high == True:
    variation_icon = special_cause_improvement_high_icon
           
if special_cause_concern_low == True:
    variation_icon = special_cause_concern_low_icon
  
if special_cause_improvement_low == True:
    variation_icon = special_cause_improvement_low_icon
    
if special_cause_concern_high == True:
    variation_icon = special_cause_concern_high_icon
    
if special_cause_neither_high == True:
    variation_icon = variation_neither_high
    
if special_cause_neither_low == True:
    variation_icon = variation_neither_low

#fail, pass or no target

if df["target"].iloc[-1] > df["lower_limit"].iloc[-1] \
    and df["target"].iloc[-1] < df["upper_limit"].iloc[-1]:
    assurance_icon = hit_or_miss_icon  
    
if performance_improvement == "up":
    if df["target"].iloc[-1] < df["lower_limit"].iloc[-1]:
        assurance_icon = pass_target_icon
    
    elif df["target"].iloc[-1] > df["upper_limit"].iloc[-1]:
        assurance_icon = fail_target_icon         
       
if performance_improvement == "down":
    if df["target"].iloc[-1] < df["lower_limit"].iloc[-1]:
        assurance_icon = fail_target_icon
    
    elif df["target"].iloc[-1] > df["upper_limit"].iloc[-1]:
        assurance_icon = pass_target_icon
        
if performance_improvement == "neither":
    assurance_icon = icon_empty
    
     

with urllib.request.urlopen(variation_icon) as url_obj:
    variation_icon = np.array(Image.open(url_obj))

newax_variation = figure_1.add_axes([0.8,0.75,0.15,0.15],
                                    anchor = "NE", zorder=1)
newax_variation.imshow(variation_icon)
newax_variation.axis("off")


if df["target"].iloc[-1] > 0:
    with urllib.request.urlopen(assurance_icon) as url_obj:
        assurance_icon = np.array(Image.open(url_obj))
    newax_assurance =figure_1.add_axes([0.8,0.75,0.15,0.15],
                                       anchor="NW",zorder=1)
    newax_assurance.imshow(assurance_icon)
    newax_assurance.axis("off")
else:
    with urllib.request.urlopen(icon_empty) as url_obj:
        icon_empty = np.array(Image.open(url_obj))
    newax_assurance =figure_1.add_axes([0.8,0.75,0.15,0.15],
                                       anchor="NW",zorder=1)
    newax_assurance.imshow(icon_empty)
    newax_assurance.axis("off")
    

ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, 
                   horizontalalignment = "right")

plt.show