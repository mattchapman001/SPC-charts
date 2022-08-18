# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 13:26:39 2022

@author: MATTHEW.CHAPMAN
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.ticker as mtick

st.title("SPC Chart Creator")

st.write("The uploaded file must be saved as a .csv file and be in the following format")

example_df = pd.DataFrame({
    "Month": ["Dec 21", "Jan 22", "Feb 22"],
    "Data": [50, 65, 70],
    "Phase": [1,1,2],
    "Target": [45, 45, 45]})

st.write("The first column has the month, 2nd column the data, in decimal\
         format for percentages (e.g. 0.5 for 50%), 3rd column has the phase,\
             and the 4th column a target if there is one.")
    
example_df.set_index("Month", inplace = True)

st.write(example_df)

st.write("Drag and drop .csv file in correct format")

#chart title code
chart_title = st.sidebar.text_input("Chart title")

data_format = st.sidebar.radio("Is the data a percentage?", ("Yes", "No"))

performance_improvement = st.sidebar.radio("For this chart what does an improvement look like?",
                                   ("An increasing value is an improvement",
                                    "A decreasing value is an improvement"))

y_axis_zero = st.sidebar.radio("Set y-axis to start at zero", ("yes", "no"))

if performance_improvement == "An increasing value is an improvement":
    performance_improvement = True
else:
    performance_improvement = False


  
# df["plotdata"] refers to the 2nd imported column, as this column name can
# change the column index is used rather than the column name

#Name of import document 
# 1st column= month, 
# 2nd column = data, 
# 3rd column = phase
# 4th column = target
#columns need headers and header of 2nd column is chart title
uploaded_file = st.file_uploader("Upload CSV data")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
else:
    st.warning("No file has been uploaded")
    st.stop()
   
   
#code to use header from .csv if not title has been added
if chart_title != "":
    chart_title = chart_title

else:
    chart_title = df.columns[1]

df["plotdata"] = df.iloc[:, 1]

#number of months to look for increasing/decreasing or runs above/below mean
trend_period = 7

    
#Improvement direction (True/False)
#performance_improvement = True

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


#Streamlit metrics
col1, col2, col3 = st.columns(3)

col1.metric("Mean", df["mean"].iloc[-1].round(2))
col2.metric("Upper limit", df["upper_limit"].iloc[-1].round(2))
col3.metric("Lower limit", df["lower_limit"].iloc[-1].round(2))


## GRAPH ##


figure_1, ax = plt.subplots()



#plotting lines
ax.plot(df["Month"], df["plotdata"], marker = "o", markersize = 10, 
        color = "black", markerfacecolor = "grey", markeredgecolor = "grey")
ax.plot(df["Month"], df["mean"], color = "grey")
ax.plot(df["Month"], df["upper_limit"], ls=":", color = "black")
ax.plot(df["Month"], df["lower_limit"], ls=":", color = "black")
ax.plot(df["Month"], df["target"], ls="-", color = "red")


#plotting points outside limits
if performance_improvement == True:
    ax.plot(df["Month"][df["below_lower"]], 
            df["plotdata"][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "orange")
    ax.plot(df["Month"][df["above_upper"]], 
            df["plotdata"][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
elif performance_improvement == False:
    ax.plot(df["Month"][df["below_lower"]], 
            df["plotdata"][df["below_lower"]], 
            marker="o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["above_upper"]], 
            df["plotdata"][df["above_upper"]], 
            marker="o", markersize=10, ls = "None", color = "orange")

#plotting points above and below mean
if performance_improvement == True:
    ax.plot(df["Month"][df["special_cause_run_above_mean"]],
            df["plotdata"][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["special_cause_run_below_mean"]],
            df["plotdata"][df["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif performance_improvement == False:
    ax.plot(df["Month"][df["special_cause_run_above_mean"]],
            df["plotdata"][df["special_cause_run_above_mean"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
    ax.plot(df["Month"][df["special_cause_run_below_mean"]],
            df["plotdata"][df["special_cause_run_below_mean"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    
#plotting points ascending/decending
if performance_improvement == True:
    ax.plot(df["Month"][df["special_cause_ascending"]],
            df["plotdata"][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")
    ax.plot(df["Month"][df["special_cause_decending"]],
            df["plotdata"][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
elif performance_improvement == False:
      ax.plot(df["Month"][df["special_cause_ascending"]],
            df["plotdata"][df["special_cause_ascending"]],
            marker= "o", markersize=10, ls = "None", color = "orange")
      ax.plot(df["Month"][df["special_cause_decending"]],
            df["plotdata"][df["special_cause_decending"]],
            marker= "o", markersize=10, ls = "None", color = "blue")

#y axis formatted to percentage if needed

if data_format == "Yes":
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, 0)) 
    
    percent_upper_limit = df["upper_limit"].iloc[-1]*100
    plt.text(0.1, 0.95, "Upper Limit=" + percent_upper_limit . \
              round(decimals =2).astype(str) + "%",
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax.transAxes,
              fontsize = 16)
    
    percent_mean = df["mean"].iloc[-1]*100
    plt.text(0.1, 0.9, "Mean= " + percent_mean. \
              round(decimals =2).astype(str) + "%",
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax.transAxes,
              fontsize = 16)
      
  
    percent_lower_limit = df["lower_limit"].iloc[-1]*100
    plt.text(0.1, 0.85, "Lower limit= " + percent_lower_limit. \
              round(decimals =2).astype(str) +"%",
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax.transAxes,
              fontsize = 16)
    
        
    if np.isnan(df["target"].iloc[-1]) == True:
        percent_target = "no target"
        
    else:
        percent_target = df["target"].iloc[-1]*100
        plt.text(0.1, 0.8, "Target= " + percent_target. \
                  round(decimals =2).astype(str) +"%",
                  horizontalalignment='center',
                  verticalalignment='center',
                  transform = ax.transAxes,
                  fontsize = 16)
   

else:    
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
    plt.text(0.1, 0.85, "Lower limit= " + df["lower_limit"]. \
              round(decimals =2).iloc[-1].astype(str),
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax.transAxes,
              fontsize = 16) 
    
    if np.isnan(df["target"].iloc[-1]) == True:
        percent_target = "no target"
        
    else:
        percent_target = df["target"].iloc[-1]
        plt.text(0.1, 0.8, "Target= " + percent_target. \
                  round(decimals =2).astype(str),
                  horizontalalignment='center',
                  verticalalignment='center',
                  transform = ax.transAxes,
                  fontsize = 16)
        
if y_axis_zero == "yes":
    ax.set_ylim(0)

elif y_axis_zero == "no":
    ax.set_ylim()
            
ax.tick_params(axis="x", labelrotation= 90)
ax.set_ylim(0)
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.title(chart_title, fontsize=25)
plt.tight_layout()
figure_1.set_figwidth(18)
figure_1.set_figheight(9)
#figure_1.savefig(f"{chart_title}.png", bbox_inches = "tight")
#figure_1.show()



# arr = np.random.normal(1,1, size =100)
# x = list(range(0, 100))
# fig, ax = plt.subplots()
# ax.bar(x, arr)

st.pyplot(figure_1, width = 1)

#st.download_button("Download chart image", f"{chart_title}.png")



