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
import seaborn as sns

def convert_df(df):
    return df.to_csv().encode("utf-8")

#number of months to look for increasing/decreasing or runs above/below mean
trend_period = 7


st.title("SPC Chart Creator")

st.write("To create a chart upload a .csv file in the following format:")
         
st.write("- First column = Month")
st.write("- Second column = Data (percentages need to be in decimal format, \
         eg, 0.5 for 50% )")
st.write("- Third column = Phase, this defines the mean along with the upper \
         and lower limit values. Start at 1, if there has been a significant \
         underlying change to the data a new phase may be justified.")
st.write("- Fourth column = Target")

st.subheader("Example of required .csv format")


example_df = pd.DataFrame({
    "Month": ["Dec 21", "Jan 22", "Feb 22"],
    "Data": [50, 65, 70],
    "Phase": [1,1,2],
    "Target": [45, 45, 45]})
          
example_df.set_index("Month", inplace = True)

st.dataframe(example_df)

#Blank csv template to download   

blank_df = pd.DataFrame({"Month":[], "data":[], "phase":[], "target":[]})

blank_df.set_index("Month", inplace = True)

csv = convert_df(blank_df)

st.download_button("Click here to download a blank template", 
                   data = csv, file_name = "Blank_template.csv",
                   help = "A blank template that can be populated with data\
                       and uploaded")

st.subheader("Drag and drop .csv file in correct format into the box below")

#chart title code
chart_title = st.sidebar.text_input("Chart title")

data_format = st.sidebar.radio("Is the data a percentage?", ("Yes", "No"))

performance_improvement = \
    st.sidebar.radio("For this chart what does an improvement look like?",
                                   ("An increasing value is an improvement",
                                    "A decreasing value is an improvement"))

y_axis_zero = st.sidebar.radio("Chart y-axis to start at zero?", ("Yes", "No"))

if performance_improvement == "An increasing value is an improvement":
    performance_improvement = True
else:
    performance_improvement = False


  
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


#Streamlit metrics

if data_format == "No":

    col1, col2, col3 = st.columns(3)
    
    col1.metric("Mean", df["mean"].iloc[-1].round(2))
    col2.metric("Upper limit", df["upper_limit"].iloc[-1].round(2))
    col3.metric("Lower limit", df["lower_limit"].iloc[-1].round(2))
    
else:
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Mean (%)", ((df["mean"].iloc[-1])*100).round(2))
    col2.metric("Upper limit (%)", ((df["upper_limit"].iloc[-1])*100).round(2))
    col3.metric("Lower limit (%)", ((df["lower_limit"].iloc[-1])*100).round(2))


## GRAPH ##


figure_1, ax = plt.subplots()

sns.set_theme()
sns.set_context("paper")

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

#plotting runs above and below mean
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
    
#plotting runs ascending/decending
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
upper_limit = df["upper_limit"].iloc[-1]
lower_limit = df["lower_limit"].iloc[-1]



if data_format == "No":
    target_str = f"{target:.2f}"
    upper_limit_str = f"{upper_limit:.2f}"
    lower_limit_str = f"{lower_limit:.2f}"
    mean_str = f"{mean:.2f}"
    
    ax.text(df["Month"].iloc[-2], 
            df["target"].iloc[-1], 
            "Target= " + target_str, 
            ha="center", 
            va="center", 
            size=15)
    
    ax.text(df["Month"].iloc[-2],
            df["upper_limit"].iloc[-1], 
            "Upper process limit= " + upper_limit_str, 
            ha="center", 
            va="center", 
            size=15)
    
    if y_axis_zero == "Yes" and df["lower_limit"].iloc[-1] > 0:
        ax.text(df["Month"].iloc[-2], 
                df["lower_limit"].iloc[-1], 
                "Lower process limit= " + lower_limit_str, 
                ha="center", 
                va="center", 
                size=15)
        
    elif y_axis_zero == "No":
        ax.text(df["Month"].iloc[-2], 
                df["lower_limit"].iloc[-1], 
                "Lower process limit= " + lower_limit_str, 
                ha="center", 
                va="center", 
                size=15)
    
    ax.text(df["Month"].iloc[-2], 
            df["mean"].iloc[-1], 
            "Mean= " + mean_str, 
            ha="center", 
            va="center",
            size=15)
    
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
            va="center", 
            size=15)
    
    ax.text(df["Month"].iloc[-2],
            df["upper_limit"].iloc[-1], 
            "Upper process limit= " + upper_limit_str + "%", 
            ha="center", 
            va="center", 
            size=15)
    
    if y_axis_zero == "Yes" and df["lower_limit"].iloc[-1] > 0:
        ax.text(df["Month"].iloc[-2], 
                df["lower_limit"].iloc[-1], 
                "Lower process limit= " + lower_limit_str + "%", 
                ha="center", 
                va="center", 
                size=15)
        
    elif y_axis_zero == "No":
        ax.text(df["Month"].iloc[-2], 
                df["lower_limit"].iloc[-1], 
                "Lower process limit= " + lower_limit_str + "%", 
                ha="center", 
                va="center", 
                size=15)
        
    ax.text(df["Month"].iloc[-2], 
            df["mean"].iloc[-1], 
            "Mean= " + mean_str + "%", 
            ha="center", 
            va="center", 
            size=15)


st.pyplot(figure_1, width = 1)

csv_df = convert_df(df)

st.download_button("Click here to download data extract", 
                   data = csv_df, file_name = "Data_extract.csv",
                   help = 
                   "A .csv file of the data generated to create the chart")


