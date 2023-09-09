# -----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Project Title: Daily Weather Forecast Data
# Script Title: Facility Weather Data
# -----------------------------------------------------------------------------
"""
The purpose of this script is to pull weather forecast data at the locations of
US power plants (facilities). 
"""
# -----------------------------------------------------------------------------
# Contributor(s): Evan Perry
# Last Revised: 2023-09-09
# version = 1.0
# -----------------------------------------------------------------------------

###############################################################################
# CODE TO CHANGE WHEN REPLICATING

api_key_file = "C:/Users/eaper/OneDrive/api-keys/eia.txt"
out_dir = "C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts/"

###############################################################################


###############################################################################
# Setup

import json
import pandas as pd
import numpy as np
from datetime import date, timedelta
import time
import os
import requests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

my_date = date.today()

###############################################################################


###############################################################################
# Pull Facility Locations Semiannually

update_when = my_date.day == 1 and (my_date.month == 1  or my_date.month == 7)

if update_when:
    
    # EIA API Key
    with open(api_key_file) as f:
        api_key = f.readlines()[0]
    api_key = "api_key=" + api_key
    
    # Create pull date
    pull_date = my_date - timedelta(days = 175)
    pull_date = pull_date.strftime("%Y-%m")
    
    # States
    states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    
    # Setup API pull
    base_url = 'https://api.eia.gov/v2/electricity/operating-generator-capacity/data/?'
    facets = '&frequency=monthly&data[0]=latitude&data[1]=longitude&facets[stateid][]='
    date_url = '&start=' + pull_date + '&end=' + pull_date
    filters = '&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000'
    
    facilities = []
    
    for state in states:
        
        # Put together pull URL
        full_url = base_url + api_key + facets + state + date_url + filters
        
        # Make data pull
        response = requests.get(full_url)
        temp = response.json()['response']['data']
        temp = json.dumps(temp)
        temp = pd.read_json(temp)
        facilities.append(temp)

    # Put together the full dataset        
    facilities = pd.concat(facilities)
    facilities = facilities[
        ['period', 'plantid', 'latitude', 'longitude']]
    facilities = facilities.drop_duplicates()
    
    # Update the current file
    facilities.to_csv(out_dir + 'reference-data/plants/current-plants.csv', index = False)
    facilities.to_csv(out_dir + 'reference-data/plants/plants-' + pull_date + '.csv', index = False)
    
    del api_key, base_url, date_url, f, facets, facilities, filters, full_url, \
        pull_date, response, state, states, temp      
    
###############################################################################


###############################################################################
# Pull Points Semiannually

# Prep function
def get_point_req(lat, lon):
    
    lat = "{:.4f}".format(lat)
    lon = "{:.4f}".format(lon)

    res = requests.get('https://api.weather.gov/points/' + lat + ',' + lon)
    
    if res.status_code < 399:
        point_url = res.json()['properties']['forecast']
    else:
        point_url = "ERROR"
    
    time.sleep(.25)
    
    return point_url
    
# Semiannually update the point URL
if update_when:
    
    # First, pull latest facility locations
    facilities = pd.read_csv(out_dir + 'reference-data/plants/current-plants.csv')
    
    facilities['point_url'] = [
        get_point_req(facilities.loc[i,'latitude'], facilities.loc[i,'longitude'])
        for i in range(len(facilities.index))
    ]
    
    # Export results
    facilities.to_csv(out_dir + 'reference-data/plant-urls/plant-urls-' + str(my_date) + '.csv', index = False)
    facilities.to_csv(out_dir + 'reference-data/plant-urls/current-plant-urls.csv', index = False)


facilities = pd.read_csv(out_dir + 'reference-data/plant-urls/current-plant-urls.csv')
facilities = facilities[facilities['point_url'] != "ERROR"]

###############################################################################


###############################################################################
# Grab Weather Forecasts

# First, reduce the facility-level data down to just the URL-level (this will 
# prevent us from making duplicate requests if two power plants are in the 
# same forecast zone)
req_urls = facilities[['point_url']]
req_urls = req_urls.drop_duplicates()
req_urls = req_urls.dropna()

# Now make a request for each of the URLs
todays_df = []

progress_update_when = np.linspace(start=0, stop=1, num=21) * (req_urls.size -1)
progress_update_when = np.rint(progress_update_when)

for i in range(len(req_urls)):
    
    # Make request
    res = requests.get(req_urls.iloc[i,0])
    
    if res.status_code < 399:
            
        # Read contents of API pull into dataframe
        contents = res.json()
        
        if contents['type'] != 'https://api.weather.gov/problems/UnexpectedProblem':

            contents = contents['properties']['periods']
            contents = json.dumps(contents)
            contents = pd.read_json(contents)
            
            # Filter observations in the dataframe to just those from today
            contents['startTime'] = pd.to_datetime(contents['startTime']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            contents['endTime'] = pd.to_datetime(contents['endTime']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            contents['startDate'] = pd.to_datetime(contents['startTime']).dt.date
            contents['endDate'] = pd.to_datetime(contents['endTime']).dt.date
            contents['today'] = np.where(contents['startDate'] == my_date, 1, 0)
            contents['today'] = np.where(contents['endDate'] == my_date, 1, contents['today'])
            contents = contents[contents['today'] == 1]
            contents = contents.drop(columns=['today'])
            
            # Add a column with the point URL
            contents['point_url'] = req_urls.iloc[i,0]
            
            # Add dataframe to a list
            todays_df.append(contents)
            
    # Update progress
    if i in progress_update_when:
        print("Facility calls:" + str(round(i/(req_urls.size -1))*100) + "% complete")
    

df = pd.concat(todays_df)

# Clean the retieved data

# Probability of Precipitation
df = pd.concat([df.drop(['probabilityOfPrecipitation'], axis =1), 
                df['probabilityOfPrecipitation'].apply(pd.Series)], axis=1)
df = df.rename(columns = {'unitCode': 'probabilityOfPrecipitationUnit',
                'value': 'probabilityOfPrecipitation'})

# Dewpoint
df = pd.concat([df.drop(['dewpoint'], axis =1), 
                df['dewpoint'].apply(pd.Series)], axis=1)
df = df.rename(columns = {'unitCode': 'dewpointUnit', 'value': 'dewpoint'})

# Relative Humidity
df = pd.concat([df.drop(['relativeHumidity'], axis =1), 
                df['relativeHumidity'].apply(pd.Series)], axis=1)
df = df.rename(columns = {'unitCode': 'relativeHumidityUnit', 
                          'value': 'relativeHumidity'})

# Unit Cleaning
df['probabilityOfPrecipitationUnit'] = df['probabilityOfPrecipitationUnit'].str.replace("wmoUnit:", "")
df['dewpointUnit'] = df['dewpointUnit'].str.replace("wmoUnit:", "")
df['relativeHumidityUnit'] = df['relativeHumidityUnit'].str.replace("wmoUnit:", "")

# Just today and tonight
df['n'] = df.groupby('point_url')['point_url'].transform('count')
df = df.iloc[np.where((df['n'] != 3) | (df['number'] != 1))]

# Final ordering and such
df = df[['point_url', 'name', 'isDaytime', 'startDate', 'endDate', 
         'startTime', 'endTime', 'temperature', 'temperatureUnit', 
         'temperatureTrend', 'windSpeed', 'windDirection',
         'probabilityOfPrecipitation', 'probabilityOfPrecipitationUnit',
         'dewpoint', 'dewpointUnit', 'relativeHumidity', 
         'relativeHumidityUnit', 'shortForecast', 'detailedForecast'
         ]]

# Merge it back with power plant identifiers
facilities = pd.read_csv(out_dir + 'reference-data/plant-urls/current-plant-urls.csv')
df = facilities.merge(df, how = 'outer', on='point_url')

# Clean things up
df = df.dropna(axis = 0, subset = ['isDaytime'])
df = df.drop(columns=['point_url', 'period'])

OBS_NUM_PLANTS = df.size

###############################################################################


###############################################################################
# Export and Clean Up

current_year = str(my_date.year)
current_month = str(my_date.month).rjust(2, '0')

export_file = out_dir + 'facility-weather/' + current_year + '/' + \
                current_year + '-' + current_month + '.csv.gz'

if not os.path.exists(out_dir + 'facility-weather/' + current_year):
    os.makedirs(out_dir + 'facility-weather/' + current_year)

if os.path.exists(export_file):
    full_df = pd.read_csv(export_file)
    full_df = pd.concat([full_df, df])
    full_df.to_csv(export_file, index = False, compression='gzip')
    
else: 
    df.to_csv(export_file, index = False, compression='gzip')
    
###############################################################################