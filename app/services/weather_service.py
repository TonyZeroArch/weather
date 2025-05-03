import json
import requests
from datetime import datetime
from flask import session

import numpy as np  # Add this import

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import logging

# Create module-level logger
logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        """
        Initialize the WeatherService class.
        """
        pass

    def get_7_day_forecast(self, coords):
        """
        Get 7-day forecast for a city.

        Args:
            coords: Dictionary containing latitude and longitude

        Returns:
            List of dictionaries with forecast data
        """
        # Implementation to be added
        _7_day_params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "weather_code",
            ],
            "timezone": "auto",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
        }
        # Setup the Open-Meteo API client with cache and retry on error
        return self.fetch_weather_data(_7_day_params, "daily")
        # return self.weather_data_daily

    def get_cur_forecast(self, coords):
        """
        Get current weather data for a given set of coordinates.

        Args:
            coords: Dictionary containing latitude and longitude

        Returns:
            Dictionary containing current weather data
        """

        today = datetime.today().strftime("%Y-%m-%d")

        cur_params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "uv_index_max",
                "precipitation_probability_max",
            ],
            "current": [
                "temperature_2m",
                "is_day",
                "wind_speed_10m",
                "weather_code",
                "apparent_temperature",
                "precipitation",
            ],
            "timezone": "auto",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
        }

        return self.fetch_weather_data(cur_params, "cur")

    def get_hourly_forecast(self, coords):
        """
        Get hourly forecast for a city on a following day.

        Args:
           coords: Dictionary containing latitude and longitude


        Returns:
            List of dictionaries with hourly forecast data
        """
        # Implementation to be added
        today = datetime.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.today() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        # hourly_params = {
        #     "latitude": coords["lat"],
        #     "longitude": coords["lon"],
        #     "hourly": ["temperature_2m", "weather_code", "precipitation_probability"],
        #     "timezone": "America/New_York",
        #     "wind_speed_unit": "mph",
        #     "temperature_unit": "fahrenheit",
        #     "start_date": today,
        #     "end_date": today,
        # }
        hourly_params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "daily": ["sunrise", "sunset"],
            "hourly": [
                "temperature_2m",
                "weather_code",
                "precipitation_probability",
            ],
            "timezone": "auto",
            "forecast_days": 2,
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
        }

        return self.fetch_weather_data(hourly_params, "hourly")

    def fetch_weather_data(self, params, type):
        """
        Fetch weather data from Open-Meteo API.

        Args:
            params: Dictionary containing parameters for the API request
            type: Type of weather data to fetch (current, daily, hourly)

        Returns:
            Response object from the API
        """
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        responses = openmeteo.weather_api(url, params=params)
        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Get timezone as string
        timezone_str = (
            response.Timezone().decode("utf-8")
            if isinstance(response.Timezone(), bytes)
            else response.Timezone()
        )

        # # Display for debugging
        # logger.info(f"\nUsing timezone: {timezone_str}\n")

        # Initialize an empty dictionary for weather data
        weather_data = {}

        # according to the type of data requested, we can process the response
        if type == "cur":
            # Current values. The order of variables needs to be the same as requested.
            current = response.Current()
            daily = response.Daily()

            # combine current and daily data
            weather_data = {
                "current_temperature_2m": int(current.Variables(0).Value()),
                "is_day": int(current.Variables(1).Value()),
                "current_wind_speed_10m": round(current.Variables(2).Value(), 1),
                "current_weather_code": int(current.Variables(3).Value()),
                "current_apparent_temperature": int(current.Variables(4).Value()),
                "current_precipitation": round(current.Variables(5).Value(), 1),
                "daily_temperature_2m_max": int(daily.Variables(0).ValuesAsNumpy()[0]),
                "daily_temperature_2m_min": int(daily.Variables(1).ValuesAsNumpy()[0]),
                "daily_uv_index_max": round(
                    float(daily.Variables(2).ValuesAsNumpy()[0]), 1
                ),
                "daily_precipitation_probability_max": int(
                    daily.Variables(3).ValuesAsNumpy()[0]
                ),
                "timezone": timezone_str,
            }

            # # debug
            # logger.info(f"\n-----weather_data in cur:\n {weather_data}\n")

        elif type == "daily":
            # Process daily data. The order of variables needs to be the same as requested.
            daily = response.Daily()

            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left",
                )
            }

            # # debug
            # logger.debug(f"\n-----daily_data: {daily_data}\n")
            # Process daily data. The order of variables needs to be the same as requested.
            weather_data = {
                "date": daily_data["date"].strftime("%Y-%m-%d").tolist(),
                "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
                "precipitation_probability_max": daily.Variables(2).ValuesAsNumpy(),
                "weather_code": daily.Variables(3).ValuesAsNumpy(),
            }

            # debug
            logger.debug(f"\n-----weather_data in daily: \n {weather_data}\n")

        elif type == "hourly":  # 24 hours data

            # First get the hourly data object BEFORE using it
            hourly = response.Hourly()

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

            # Add to your weather data dictionary (2 days)
            weather_data["daily_sunrise"] = sunrise_times
            weather_data["daily_sunset"] = sunset_times

            # # logger.debug(f"\n-----hourly--\n: {hourly}\n")
            # logger.info(f"\n-----daily--\n: {sunrise_times}, {sunset_times}\n")

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
            hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()

            data_hours = {
                "hours": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ).tz_convert(
                    timezone_str
                )  # Convert to location's timezone
            }
            data_hoursframe = pd.DataFrame(data=data_hours)
            # Convert timezone-aware datetimes to naive datetimes
            data_hoursframe["hours"] = data_hoursframe["hours"].dt.tz_localize(None)

            hours_series = []
            for hour_str in data_hoursframe["hours"]:
                hours_series.append(hour_str)

            # logger.info(f"\n-----data_hours_frame: \n {data_hoursframe}\n")

            # data_hours = data_hours.dt.tz_localize(None)  # Convert to naive datetime

            weather_data = {
                "hours": hours_series,
                "hourly_temperature_2m": hourly_temperature_2m,
                "hourly_weather_code": hourly_weather_code,
                "hourly_precipitation_probability": hourly_precipitation_probability,
                "daily_sunrise": sunrise_times,
                "daily_sunset": sunset_times,
                "timezone": timezone_str,
                # "utc_offset": response.UtcOffset(),
            }

            # # debug
            # logger.info(f"\n-----weather_data in hourly: \n {weather_data}\n")

        else:
            raise ValueError("Invalid type. Must be 'cur', 'daily', or 'hourly'.")
            # Convert NumPy arrays to lists before returning
        for key, value in weather_data.items():
            if isinstance(value, np.ndarray):
                weather_data[key] = value.tolist()
        # # debug
        # logger.debug(f"\n-----weather_data in fetch_weather_data: \n {weather_data}\n")

        if len(weather_data) > 0:
            return weather_data
        else:
            print("Failed to fetch weather data.")
            return None

    def get_sunrise_sunset(self, coords):
        """
        Get sunrise and sunset times for a given set of coordinates.

        Args:
            coords: Dictionary containing latitude and longitude

        Returns:
            Dictionary containing sunrise and sunset times
            {'date': '2025-04-15', 'sunrise': '6:43:06 AM', 'sunset': '7:49:15 PM',
            'first_light': '5:12:54 AM', 'last_light': '9:19:27 PM',
            'dawn': '6:16:45 AM', 'dusk': '8:15:36 PM', 'solar_noon': '1:16:11 PM',
            'golden_hour': '7:14:59 PM', 'day_length': '13:06:08',
            'timezone': 'America/New_York', 'utc_offset': -240}
        """
        # Implementation to be added
        url = f"https://api.sunrisesunset.io/json"
        params = {
            "lat": coords["lat"],
            "lng": coords["lon"],
        }  # Note: API uses 'lng' not 'lon'
        headers = {"User-Agent": "weather-dashboard-app/1.0 (tony@example.com)"}

        try:
            response = requests.get(url, params=params, headers=headers)

            # Check if request was successful
            if response.status_code == 200:
                data = response.json()

                # The API returns data in a nested structure
                if data["status"] == "OK":
                    return data["results"]
                else:
                    print(f"API returned non-OK status: {data['status']}")
                    return {}
            else:
                print(f"Request failed with status code: {response.status_code}")
                return {}
            # debug
            logger.info(f"\n-----sunrise_sunset_data: \n {data}\n")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching sunrise/sunset data: {e}")
            return {}
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return {}

    def get_day_night(self, current_time, coords):
        """
        Determine if it is currently day or night based on sunrise and sunset times.

        Args:
            current_time: Current time in 'YYYY-MM-DD HH:MM:SS' format


        Returns:
            String indicating whether it is 'day' or 'night'
        """
        # Get sunrise and sunset times
        sunrise_sunset = self.get_sunrise_sunset(coords)
        sunrise = sunrise_sunset["sunrise"]
        sunset = sunrise_sunset["sunset"]
        # Format current time and sunrise/sunset times to datetime objects
        # current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        # sunrise = datetime.strptime(sunrise, "%Y-%m-%d %H:%M:%S")
        # sunset = datetime.strptime(sunset, "%Y-%m-%d %H:%M:%S")

        current_time = datetime.strptime(current_time, "%I:%M %p").time()
        sunrise = datetime.strptime(sunrise, "%I:%M:%S %p").time()
        sunset = datetime.strptime(sunset, "%I:%M:%S %p").time()

        if sunrise <= current_time <= sunset:
            return "day"
        else:
            return "night"


# # # debug
# test = WeatherService()
# print(test.get_sunrise_sunset({"lat": 35.7915, "lon": -78.7811}))
# print(f"\n------------------------")
# print(
#     f'test for today: {test.get_day_night("9:00 AM", {"lat": 35.7915, "lon": -78.7811})}'
# )
# print

# # debug current
# test = WeatherService()
# print(f"\n------------------------")
# print(test.get_cur_forecast({"lat": 35.7915, "lon": -78.7811}))
# print(f"\n------------------------")


# # debug hourly
# today = datetime.today().strftime("%Y-%m-%d")
# # test = WeatherService()
# print(today)  # Output: "2025-04-15"
# print(f"\n------------------------")
# print(
#     f'test for today: {test.get_hourly_forecast({"lat": 35.7915, "lon": -78.7811})}\n'
# )

# debug daily
test = WeatherService()
print(f"\n------------------------")
print(f'test for today: {test.get_7_day_forecast({"lat": 35.7915, "lon": -78.7811})}')
print(f"\n------------------------")
