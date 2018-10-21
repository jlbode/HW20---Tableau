# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 12:10:36 2018

@author: bodej
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt

# =============================================================================
# 01 Read in Files, Sample, and Combine
# =============================================================================
# Due to file size (1.9M observation per month, I took a 1% sample from each month)

#A. List of years and months
years = ["2017", "2018"]
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

#B. Empty Dataframe to hold all data
data = pd.DataFrame([])
    
#C. Read in files one month at a time, sample, and add to data
for year in years: 
    for month in months:
        try:
            file = "Resources/Trip-data/"+year+month+"-citibike-tripdata.csv"
            newdata = pd.read_csv(file)
            newdata['yearmonth'] = year+month
            newdata.sample(frac=0.001, replace = False) #Take a 1% sample so we can use a longer time span
            data = data.append(newdata)
            print(f"File {year}-{month} added")

        except:
            print(f"File {year}-{month} not available")

# =============================================================================
# 02 Extract date and time components for main file
# =============================================================================

#A. Convert to datetime
data.starttime = pd.to_datetime(data.starttime)
data.stoptime = pd.to_datetime(data.stoptime)
    
#B. Extract detail about timing   
data['year'] = data['starttime'].dt.year
data['month'] = data['starttime'].dt.month
data['dayofweek'] = data['starttime'].dt.dayofweek
data['dayofyear'] = data['starttime'].dt.dayofyear
data['date'] = data['starttime'].dt.date
data['hour'] = data['starttime'].dt.hour

#C. Calculate distance
data['distance'] = ((data['start station latitude']-data['end station latitude'])**2 +
    (data['start station latitude']-data['end station latitude'])**2)**0.5 *100000
        

data.to_csv("Resources/Aug_2017_Jul_2018_Bike_Trip_Data.csv")

# =============================================================================
# 03 Pull in weather data for JFK - inlcuding temperature, rain, snow, humidity
# =============================================================================


# =============================================================================
# 04 Summarize data (Groupby) for Tableau
# =============================================================================

# A. By Date and hour
bygroup = data.groupby(["date", "hour", "year", "month", "dayofweek", "dayofyear"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True) 
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['avg_trip_time'] = bygroup['tripduration'].mean()
data_grouped['pctindex_trips'] = data_grouped.trips/data_grouped.trips[0]*100
data_grouped.to_csv("Resources/01_Summmary_by_Date_and_hour.csv")


# B. By Date and Gender  
bygroup = data.groupby(["date", "gender", "year", "month", "dayofweek", "dayofyear"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True) 
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['avg_trip_time'] = bygroup['tripduration'].mean()
data_grouped['pctindex_trips'] = data_grouped.trips/data_grouped.trips[0]*100
data_grouped.to_csv("Resources/02_Summmary_by_Date_and_gender.csv")

# C. By Date and Subscriber type  
bygroup = data.groupby(["date", "usertype", "year", "month", "dayofweek", "dayofyear"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True) 
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['avg_trip_time'] = bygroup['tripduration'].mean()
data_grouped['pctindex_trips'] = data_grouped.trips/data_grouped.trips[0]*100
data_grouped.to_csv("Resources/03_Summmary_by_Date_and_usertype.csv")

# D. By start station
bygroup = data.groupby(["start station name"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True)
data_grouped['bikes'] = bygroup['bikeid'].nunique() 
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['start latitude'] = bygroup['start station latitude'].mean()
data_grouped['start longitude'] = bygroup['start station longitude'].mean()
data_grouped['rank'] = data_grouped.trips.rank(method= 'first', ascending=False) # Rank by # of trips
data_grouped = data_grouped.loc[((data_grouped['start latitude']>40.6) & 
                                 (data_grouped['start latitude']<40.8))]  #Drop stations not in NYC
start_sites = data_grouped
data_grouped.to_csv("Resources/04_Summmary_by_startstation.csv")


# E. End stations 
bygroup = data.groupby(["end station name"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True)
data_grouped['bikes'] = bygroup['bikeid'].nunique() 
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['end latitude'] = bygroup['end station latitude'].mean()
data_grouped['end longitude'] = bygroup['end station longitude'].mean()
data_grouped['rank'] = data_grouped.trips.rank(method= 'first', ascending=False) # Rank by # of trips
data_grouped = data_grouped.loc[((data_grouped['end latitude']>40.6) & 
                                 (data_grouped['end latitude']<40.8))]  #Drop stations not in NYC
data_grouped.to_csv("Resources/05_Summmary_by_endstation.csv")


# F. Age and Average Distance
data["age"] = data.year - data["birth year"]
bins = [0, 10, 18, 25, 35, 45, 55, 65, 100] 
bin_names = ["Under 10", "10 to 18", "18 to 25", "25 to 35", "35 to 45", "45 to 55",
               "55 to 65", "65+"] 
data["age_bins"] = pd.cut(data["age"], bins, labels = bin_names)

byage = data.groupby(["birth year", "age", "age_bins"])
data_age = pd.DataFrame(byage['bikeid'].count())
data_age.rename(columns = { "bikeid": "trips"}, inplace = True) 
data_age['total_trip_time'] = byage['tripduration'].sum()
data_age['avg_trip_time'] = byage['tripduration'].mean()
data_age['avg_distance'] = byage['distance'].mean()
data_age.to_csv("Resources/06_Summmary_by_age.csv")

# G. Utilization by Bike ID
bygroup = data.groupby(["bikeid"])
data_grouped = pd.DataFrame(bygroup['bikeid'].count())
data_grouped.rename(columns = { "bikeid": "trips"}, inplace = True)
data_grouped['total_trip_time'] = bygroup['tripduration'].sum()
data_grouped['start latitude'] = bygroup['start station latitude'].mean()
data_grouped['start longitude'] = bygroup['start station longitude'].mean()
data_grouped['end latitude'] = bygroup['end station latitude'].mean()
data_grouped['end longitude'] = bygroup['end station longitude'].mean()
data_grouped['rank'] = data_grouped.trips.rank(method= 'first', ascending=False) # Rank by # of trips
data_grouped = data_grouped.loc[((data_grouped['end latitude']>40.6) & 
                                 (data_grouped['end latitude']<40.8))]  #Drop stations not in NYC
data_grouped = data_grouped.loc[((data_grouped['start latitude']>40.6) & 
                                 (data_grouped['start latitude']<40.8))]  #Drop stations not in NYC
data_grouped.to_csv("Resources/07_Summmary_by_bikeid.csv")

