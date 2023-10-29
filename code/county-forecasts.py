# -----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Project Title: Daily Weather Forecast Data
# Script Title: County Weather Data
# -----------------------------------------------------------------------------
"""
The purpose of this script is to pull weather forecast data at the centroid of
all US counties. 
"""
# -----------------------------------------------------------------------------
# Contributor(s): Evan Perry
# Last Revised: 2023-09-09
# version = 1.0
# -----------------------------------------------------------------------------

###############################################################################
# CODE TO CHANGE WHEN REPLICATING

out_dir = "C:/Users/eaper/OneDrive/personal-website/daily-weather-forecasts/"

###############################################################################


###############################################################################
# Setup

import requests
import json
import pandas as pd
import numpy as np
from datetime import date, timedelta
import time
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning) 

my_date = date.today()

###############################################################################


###############################################################################
# Prep County-Centroid File - Run Just Once

# # Download here: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
# import geopandas as gpd 

# shp = gpd.read_file(out_dir + 'reference-data/counties/tl_2020_us_county/tl_2020_us_county.shp')

# # Find centroids
# shp = shp.to_crs(4326)
# shp['lon'] = shp.centroid.x  
# shp['lat'] = shp.centroid.y

# # Convert to dataframe and export the relevant columns
# county_cen = pd.DataFrame(shp)
# county_cen = county_cen[['GEOID', 'lat', 'lon']]
# county_cen = county_cen.rename(columns = {'GEOID': 'fips'})

# county_cen.to_csv(out_dir + '/reference-data/counties.csv', index = False)

###############################################################################


###############################################################################
# Pull Points Semiannually

update_when = my_date.day == 1 and (my_date.month == 1  or my_date.month == 7)

# Prep function
def get_point_req(lat, lon):
    
    lat = "{:.4f}".format(lat)
    lon = "{:.4f}".format(lon)

    res = requests.get('https://api.weather.gov/points/' + lat + ',' + lon)
    
    if res.status_code < 399:
        point_url = res.json()['properties']['forecast']
    else:
        point_url = "ERROR"
    
    return point_url
    
# Semiannually update the point URL
if update_when:
    
    # First, pull county centroids
    cnty_cen = pd.read_csv(out_dir + 'reference-data/counties.csv')
    
    # Grab point URLs
    cnty_cen['point_url'] = [
        get_point_req(cnty_cen.loc[i,'lat'], cnty_cen.loc[i,'lon'])
        for i in range(len(cnty_cen.index))
    ]
    
    # Export results
    cnty_cen.to_csv(out_dir + 'reference-data/county-urls/county-urls-' + str(my_date) + '.csv', False)
    cnty_cen.to_csv(out_dir + 'reference-data/county-urls/current-county-urls.csv', index = False)


cnty = pd.read_csv(out_dir + 'reference-data/county-urls/current-county-urls.csv')
cnty = cnty[cnty['point_url'] != "ERROR"]

###############################################################################


###############################################################################
# Grab Weather Forecasts

# First, reduce the facility-level data down to just the URL-level (this will 
# prevent us from making duplicate requests if two power plants are in the 
# same forecast zone)
req_urls = cnty[['point_url']]
req_urls = req_urls.drop_duplicates()
req_urls = req_urls.dropna()

# Now make a request for each of the URLs
todays_df = []

progress_update_when = np.linspace(start=0, stop=1, num=21) * (req_urls.size -1)
progress_update_when = np.rint(progress_update_when)

for i in range(len(req_urls)):

    res = requests.get(req_urls.iloc[i,0])
    
    if res.status_code < 399:
            
        # Read contents of API pull into dataframe
        contents = res.json()
        
        if contents['type'] != 'https://api.weather.gov/problems/UnexpectedProblem':

            contents = contents['properties']['periods']
            contents = json.dumps(contents)
            contents = pd.read_json(contents)
            
            # Filter observations in the dataframe to just those from today
            contents['startTime'] = pd.to_datetime(contents['startTime'], utc = True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            contents['endTime'] = pd.to_datetime(contents['endTime'], utc = True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            contents['startDate'] = pd.to_datetime(contents['startTime'], utc = True).dt.date
            contents['endDate'] = pd.to_datetime(contents['endTime'], utc = True).dt.date
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
        print("County calls:" + str(round(i/(req_urls.size -1)*100)) + "% complete")
            

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

# Merge it back with the county identifiers
cnty = pd.read_csv(out_dir + 'reference-data/county-urls/current-county-urls.csv')
df = cnty.merge(df, how = 'outer', on='point_url')

# Clean things up
df = df.dropna(axis = 0, subset = ['isDaytime'])
df = df.drop(columns=['point_url'])

OBS_NUM_COUNTIES = df['fips'].size

###############################################################################


###############################################################################
# Export and Clean Up

current_year = str(my_date.year)
current_month = str(my_date.month).rjust(2, '0')

export_file = out_dir + 'county-weather/' + current_year + '/' + \
                current_year + '-' + current_month + '.csv.gz'

if not os.path.exists(out_dir + 'county-weather/' + current_year):
    os.makedirs(out_dir + 'county-weather/' + current_year)

if os.path.exists(export_file):
    full_df = pd.read_csv(export_file)
    full_df = pd.concat([full_df, df])
    full_df.to_csv(export_file, index = False, compression='gzip')
    
else: 
    df.to_csv(export_file, index = False, compression='gzip')
    
OBS_NUM_COUNTIES = pd.DataFrame({'num': [OBS_NUM_COUNTIES]})
OBS_NUM_COUNTIES.to_csv(out_dir + "reference-data/daily-obs-counties.csv", index=False)    
    
###############################################################################

