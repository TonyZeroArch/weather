import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.7915,
    "longitude": -78.7811,
    "daily": ["sunrise", "sunset"],
    "hourly": ["temperature_2m", "weather_code", "precipitation_probability"],
    "timezone": "auto",
    "forecast_days": 2,
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


# Get timezone as string
timezone_str = (
    response.Timezone().decode("utf-8")
    if isinstance(response.Timezone(), bytes)
    else response.Timezone()
)

# Display for debugging
print(f"Using timezone: {timezone_str}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    ).tz_convert(
        timezone_str
    )  # Convert to location's timezone
}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["weather_code"] = hourly_weather_code
hourly_data["precipitation_probability"] = hourly_precipitation_probability

hourly_dataframe = pd.DataFrame(data=hourly_data)
# Convert timezone-aware datetimes to naive datetimes
hourly_dataframe["date"] = hourly_dataframe["date"].dt.tz_localize(None)

print(f'the type {type(hourly_dataframe["date"])}')

print(f"\n----dataframe----\n{hourly_dataframe}")


# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()

# Convert sunrise timestamps to datetime in the correct timezone
sunrise_times = (
    pd.to_datetime(daily_sunrise, unit="s", utc=True)  # Specify UTC source
    .tz_convert(timezone_str)  # Convert to location's timezone
    .strftime("%Y-%m-%d %H:%M:%S")  # Format without timezone suffix
    .tolist()
)

# Do the same for sunset times
sunset_times = (
    pd.to_datetime(daily_sunset, unit="s", utc=True)
    .tz_convert(timezone_str)
    .strftime("%Y-%m-%d %H:%M:%S")
    .tolist()
)

print(f"Sunrise times: {sunrise_times}")
print(f"Sunset times: {sunset_times}")


daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )
}

daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset

daily_dataframe = pd.DataFrame(data=daily_data)


# print(daily_dataframe)

# print(f"\ndaily_data : {hourly_data}")
# print(f"daily-data datetimeindex: {daily_data['date'][0]}, {daily_data['date'][1]}")
