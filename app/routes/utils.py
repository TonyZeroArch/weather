# Utility functions within routes
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
    render_template_string,
)

import pandas as pd
import logging

# Create module-level logger
logger = logging.getLogger(__name__)

from datetime import datetime
import pytz
from tzlocal import get_localzone

from app.services.loc_api import LocService
from app.services.weather_service import WeatherService
from app.utils.constants import WEATHER_CODE_MAP


def test_print():
    """Utility function that can be called from any route"""
    print("test_print function called")


# Debug function
def debug_print_session(func_name):
    """Utility function to print session data"""
    print(f"-------------------------")
    print(f"Session data in {func_name}:")
    print(f"{session}")
    print(f"-------------------------\n")


def verify(loc_data):

    if len(loc_data) == 0:
        return False
    else:
        print("Location data provided.")
        print(f"Location data: {loc_data}\n")
        # Pass the location data to your LocService
        cur_location = LocService(loc_data).show_lat_lon()
        print(f"\n Coordinates received: {cur_location}")
        if len(cur_location) == 0:
            print("No coordinates found.")
            return False

        else:
            session["cur_location"] = cur_location
            print(f'Coordinates found---{session["cur_location"]}\n')
            return True


def update_view_cur_frame():

    weather = WeatherService()
    weather_data = weather.get_cur_forecast(session["cur_location"])

    logger.info(
        f"\n---Current weather data in update_view_cur_frame():\n {weather_data}\n"
    )

    cur_local_time = get_time_in_timezone(weather_data["timezone"])

    # logger.debug(
    #     f"---Received Timezone data in update_view_cur_frame():\n {cur_local_time}\n"
    # )
    # logger.debug(f'--dest_time: {cur_local_time["dest_time"]}')

    # get current weather data
    cur_data = {
        "updated_time": cur_local_time["dest_time"].strftime("%H:%M"),
        "unit": session["temp_unit"],
    }
    # logger.info(f'---cur_data_updated_time: {cur_data["updated_time"]}')
    logger.debug(f"---cur_session: {session}")

    if session["temp_unit"] == "C":
        weather_data["current_temperature_2m"] = convert_to_celsius(
            weather_data["current_temperature_2m"]
        )
        weather_data["current_apparent_temperature"] = convert_to_celsius(
            weather_data["current_apparent_temperature"]
        )
        weather_data["daily_temperature_2m_max"] = convert_to_celsius(
            weather_data["daily_temperature_2m_max"]
        )
        weather_data["daily_temperature_2m_min"] = convert_to_celsius(
            weather_data["daily_temperature_2m_min"]
        )

    if weather_data["is_day"] == 1:
        datetime_str = "day"
    else:
        datetime_str = "night"

    weather_pics = {
        "icon": WEATHER_CODE_MAP[str(weather_data["current_weather_code"])][
            datetime_str
        ]["image"],
        "description": WEATHER_CODE_MAP[str(weather_data["current_weather_code"])][
            datetime_str
        ]["description"],
    }

    # Combine location and weather data
    cur_data = cur_data | session["cur_location"] | weather_data | weather_pics

    # logger.debug(f"---return data in  update_view_cur_frame():\n {cur_data}\n")

    return cur_data


def update_view_hourly_frame(hour_length=6):

    # get hourly data
    weather = WeatherService()
    hourly_data = weather.get_hourly_forecast(session["cur_location"])

    # # # debug
    # logger.debug(
    #     f"\n---Received Hourly weather data in update_view_hourly_frame():\n {hourly_data}\n"
    # )

    start_time_index = 0
    time_zone_data = get_time_in_timezone(hourly_data["timezone"])

    # logger.debug(
    #     f"\n---Received Timezone data in update_view_hourly_frame():\n {time_zone_data}\n"
    # )

    # print(f"\n-------------------------")
    # print(f"Time zone data: {type(time_zone_data["dest_time"])}")

    for i in range(len(hourly_data["hours"])):
        # # Convert timestamp to string format for comparison
        hour_str = hourly_data["hours"][i].strftime("%Y-%m-%d %H:%M:%S")
        dest_time_str = time_zone_data["dest_time"].strftime("%Y-%m-%d %H:%M:%S")

        if dest_time_str < hour_str:
            start_time_index = i
            break

    # logger.info(f" the start index is {start_time_index}")

    formatted_hourly_data = {
        "hours": hourly_data["hours"][
            start_time_index : start_time_index + hour_length
        ],
        "hourly_temperature_2m": [
            f"{int(val)}"
            for val in hourly_data["hourly_temperature_2m"][
                start_time_index : start_time_index + hour_length
            ]
        ],
        "hourly_weather_code": [
            f"{int(val)}"
            for val in hourly_data["hourly_weather_code"][
                start_time_index : start_time_index + hour_length
            ]
        ],
        "hourly_precipitation_probability": [
            f"{int(val)}"
            for val in hourly_data["hourly_precipitation_probability"][
                start_time_index : start_time_index + hour_length
            ]
        ],
    }
    logger.debug(
        f"\n---Formatted Hourly weather data in update_view_hourly_frame():\n {formatted_hourly_data}\n"
    )
    if session["temp_unit"] == "C":
        # Convert temperature to Celsius
        for i in range(len(formatted_hourly_data["hourly_temperature_2m"])):
            formatted_hourly_data["hourly_temperature_2m"][i] = convert_to_celsius(
                int(formatted_hourly_data["hourly_temperature_2m"][i])
            )

    icon_hourly = {"icon_hourly": [], "description_hourly": []}
    for i in range(0, hour_length):

        is_day_str = get_is_day(
            formatted_hourly_data["hours"][i],
            hourly_data["daily_sunrise"],
            hourly_data["daily_sunset"],
        )

        icon_hourly["icon_hourly"].append(
            WEATHER_CODE_MAP[str(int(formatted_hourly_data["hourly_weather_code"][i]))][
                is_day_str
            ]["image"]
        )

        icon_hourly["description_hourly"].append(
            WEATHER_CODE_MAP[str(int(formatted_hourly_data["hourly_weather_code"][i]))][
                is_day_str
            ]["description"]
        )

        # Convert the start time index to a string format
    for i in range(0, hour_length):
        formatted_hourly_data["hours"][i] = formatted_hourly_data["hours"][i].strftime(
            "%H:%M"
        )

    return_data = formatted_hourly_data | icon_hourly | session

    return return_data


def update_view_7_day_frame():
    # get daily data
    weather = WeatherService()
    daily_data = weather.get_7_day_forecast(session["cur_location"])

    # # # debug
    # logger.debug(
    #     f"\n---Received Daily weather data in update_view_daily_frame():\n {daily_data}\n"
    # )

    formatted_daily_data = {
        "date": daily_data["date"],
        "temperature_2m_max": [
            f"{int(val)}" for val in daily_data["temperature_2m_max"]
        ],
        "temperature_2m_min": [
            f"{int(val)}" for val in daily_data["temperature_2m_min"]
        ],
        "weather_code": [f"{int(val)}" for val in daily_data["weather_code"]],
        "precipitation_probability_max": [
            f"{int(val)}" for val in daily_data["precipitation_probability_max"]
        ],
    }

    if session["temp_unit"] == "C":
        # Convert temperature to Celsius
        for i in range(len(formatted_daily_data["temperature_2m_max"])):
            formatted_daily_data["temperature_2m_max"][i] = convert_to_celsius(
                int(formatted_daily_data["temperature_2m_max"][i])
            )
            formatted_daily_data["temperature_2m_min"][i] = convert_to_celsius(
                int(formatted_daily_data["temperature_2m_min"][i])
            )

    icon_daily = {"icon_daily": [], "description_daily": []}
    for i in range(len(formatted_daily_data["weather_code"])):

        icon_daily["icon_daily"].append(
            WEATHER_CODE_MAP[str(int(formatted_daily_data["weather_code"][i]))]["day"][
                "image"
            ]
        )

        icon_daily["description_daily"].append(
            WEATHER_CODE_MAP[str(int(formatted_daily_data["weather_code"][i]))]["day"][
                "description"
            ]
        )

    return_data = session["cur_location"] | formatted_daily_data | icon_daily

    logger.debug("return data in update_view_daily_frame():\n {return_data}\n")

    return return_data


def get_time_in_timezone(timezone_str="America/New_York"):
    """
    Get current time in specified timezone

    Args:
        timezone_str: IANA timezone string (e.g., 'America/New_York')

    Returns:
        Dictionary with local and destination time information
    """
    try:
        # Get local timezone
        local_timezone = get_localzone()
        local_time = datetime.now(local_timezone)

        # Get destination timezone
        dest_timezone = pytz.timezone(timezone_str)
        dest_time = local_time.astimezone(dest_timezone)

        # logger.info(f"\n-----------------")
        # logger.info(f"dest_time : {dest_time}")
        # logger.info(f"local_time : {local_time}")
        # logger.info(f"local_timezone : {local_timezone}")
        # logger.info(f"dest_timezone : {dest_timezone}")
        # logger.info(f"\n-----------------")

        return {
            "local_timezone": str(local_timezone),
            "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
            "dest_timezone": timezone_str,
            # "dest_time": dest_time.strftime("%Y-%m-%d %H:%M:%S"),
            "dest_time": dest_time,
            "time_difference_hours": (
                dest_time.utcoffset() - local_time.utcoffset()
            ).total_seconds()
            / 3600,
        }

    except Exception as e:
        logger.error(f"Error converting timezone: {e}")
        return {}


def get_is_day(target_time, sunrise, sunset):
    """
    Get whether the target time is daytime or nighttime
    """

    # Extract sunrise and sunset times from the dictionary
    sunrise_time_0 = datetime.strptime(sunrise[0], "%Y-%m-%d %H:%M:%S")
    sunrise_time_1 = datetime.strptime(sunrise[1], "%Y-%m-%d %H:%M:%S")
    sunset_time_0 = datetime.strptime(sunset[0], "%Y-%m-%d %H:%M:%S")
    sunset_time_1 = datetime.strptime(sunset[1], "%Y-%m-%d %H:%M:%S")

    # Compare the target time with sunrise and sunset times
    if (sunrise_time_0 < target_time < sunset_time_0) or (
        sunrise_time_1 < target_time < sunset_time_1
    ):
        return "day"  # Daytime
    else:
        return "night"  # Nighttime

    # if (sunrise)


def convert_to_celsius(temp_f):
    """
    Convert Fahrenheit to Celsius
    """
    return int((temp_f - 32) * 5 / 9)


# timezone = "Asia/Tokyo"

# time_info = get_time_in_timezone(timezone)
# print(f"Local time: {time_info['local_time']}")
# print(f"Destination time: {time_info['dest_time']}")
# print(f"Time info: {time_info}")
