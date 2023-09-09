# daily-weather-forecasts
 
The National Weather Service creates daily weather forecasts across the country, but does not publish historical daily weather forecasts. This repository---updated daily---archives forecasts beginning in September 2023. Daily forecast data are available at the location of county centroids and US power plants.

## About the Data

This project archives daily forecast data from the National Weather Service. All data come from the [National Weather Service's API](https://weather-gov.github.io/api/). The API's site contains relevant information and documentation about data available in the repository. To collect forecast data from the National Weather Service's API, a user must first use the API to find an endpoint URL for a specific (user provided) latitude and longitude. This latitude and longitude is then mapped to the forecasting grid that the National Weather Service uses, and the API returns a URL of the gridpoint associated with the provided latitude and longitude. Then this endpoint URL can be passed back to the API, which returns forecast data.

Using the API requires us to choose GPS coordinates that we want forecast data from. To keep this most relevant to policy researchers, I choose to use the GPS coordinates of all US county centroids as well as the GPS coordinates of all US power plants. The forecast data returned is at a subdaily frequency---one observation for the daytime and one observation for the nighttime. I restrict the data to just day-of forecasts, omitting forecasts made, for instance, three days ahead.

There are many incredible resources for weather and climate data in the US. Notably, the National Center for Environmental Information provides [county-level climate data](https://www.ncei.noaa.gov/news/noaa-offers-climate-data-counties). Unfortunately these data do not contain potentially relevant fields to policy researchers (e.g., wind speed, wind direction, cloud cover).

## Data Structure

The county-level data contain county FIPS codes as identifiers, and the plant-level data contain EIA plant ID codes as identifiers. Along with the identifiers, the datasets contain the exact latitude and longitude used in the API request (the coordinates of the centroid in the county data and the coordinates of the plant in the plant data.) Both the county- and plant-level data contain the following fields:


| Variable                        | Description                                                                       |
| :------------------------------ | :-------------------------------------------------------------------------------- |
| name	                          |  String description of the time of day; e.g., "Monday Night"                      |
| isDaytime	                      |  Boolean; whether or not the current observation is for the daytime or nighttime  |
| startDate	                      |  Date associated with the start time                                              |
| endDate	                        |  Date associated with the end time                                                |
| startTime	                      |  Datetime when the forecast observation period begins                             |
| endTime	                        |  Datetime when the forecast observation period ends                               | 
| temperature	                    |  Temperature                                                                      |
| temperatureUnit	                |  Temperature unit; Fahrenheit                                                     |
| temperatureTrend	              |  String describing direction of temperatures; e.g., "rising"                      |
| windSpeed	                      |  String of the windspeed; e.g., "5 to 10 mph"                                     |
| windDirection	                  |  String abbreviation for the wind direction                                       |
| probabilityOfPrecipitation	    |  Probability of precipitation                                                     |
| probabilityOfPrecipitationUnit	|  Unit for Probability of precipitation; percent                                   |
| dewpoint	                      |  Dewpoint                                                                         |
| dewpointUnit	                  |  Dewpoint unit; degrees Celsius                                                   |
| relativeHumidity	              |  Relative humidity                                                                |
| relativeHumidityUnit	          |  Relative humidity unit; percent                                                  |
| shortForecast	                  |  Brief description of weather forecast                                            |
| detailedForecast	              |  Longer, detailed description of weather forecast                                 |
