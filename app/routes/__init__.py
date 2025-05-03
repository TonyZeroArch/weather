# Import Blueprint from blueprint.py
from .blueprint import main

from flask import Blueprint, render_template, session, jsonify
from datetime import datetime
import logging

# Create module-level logger
logger = logging.getLogger(__name__)

# import my services
from app.services.loc_api import LocService
from app.services.weather_service import WeatherService
from app.utils.constants import WEATHER_CODE_MAP

# import shared functions within routes
from .utils import test_print, verify, update_view_cur_frame, update_view_hourly_frame

home_call_counter = 0


# from . import views  # Import all route handlers
@main.route("/")
def home():
    # initialize the session
    # session.clear()  # Clear the session if needed
    global home_call_counter
    home_call_counter += 1

    # Set default values if not already in session
    if "temp_unit" not in session:
        session["temp_unit"] = "F"  # Default to Fahrenheit
    if "wind_unit" not in session:
        session["wind_unit"] = "mph"
    if "precip_unit" not in session:
        session["precip_unit"] = "in"

    logger.debug(f"\nHome route called {home_call_counter} times\n")
    logger.debug(f"\n-------Session data: {session}\n")

    if "cur_location" not in session:
        # Set default values for session variables
        session["cur_location"] = {
            "lat": 35.7915,
            "lon": -78.7811,
            "postal_code": "27511",
            "city": "Cary",
            "state": "NC",
            "city_state": "Cary, NC",
        }
        # session["lat_lon"] = {}
        # session["unit"] = "C"
        # session["unit_type"] = "metric"
    else:
        session["cur_location"]["city_state"] = (
            session["cur_location"]["city"] + ", " + session["cur_location"]["state"]
        )

    # Get current time
    cur_time = datetime.now().strftime("%H:%M")  # 12-hour format
    formatted_cur_time = int(datetime.now().strftime("%H"))

    # Get or create weather data
    try:

        return_data = update_view_cur_frame() | update_view_hourly_frame()

        # With this single logging statement:
        # logger.info(
        #     f"---------Weather data retrieved for home page:-----\n {return_data}\n"
        # )

    except Exception as e:
        logger.error(f"Error getting weather: {e}", exc_info=True)
        # Fallback weather data
        return_data = {
            "city_state": "Cary, NC--Default",
            "updated_time": f"Updated: {cur_time}",
            "current_temp": "120°F",
            "feels_like": "Feels like 77°F",
            "max_temp": "80°F",
            "min_temp": "70°F",
            "uv": 5.0,
            "precip": "0%",
            "wind_speed": "8 mph",
            "condition": "Sunny",
            "icon": "http://openweathermap.org/img/wn/01d@2x.png",
            "current_temperature_2m": 75.0,
            "current_apparent_temperature": 77.0,
            "daily_temperature_2m_max": 80.0,
            "daily_temperature_2m_min": 70.0,
            "daily_uv_index_max": 5.0,
            "daily_precipitation_probability_max": 0,
            "current_wind_speed_10m": 8.0,
            "humidity": 60,
            "daily_weather_code": 0,
            # Add minimal hourly data to avoid template errors
            "hours": ["N/A"],
            "hourly_temperature_2m": [75.0],
            "hourly_precipitation_probability": [0],
            "description_hourly": ["Unavailable"],
            "icon_hourly": ["http://openweathermap.org/img/wn/01d@2x.png"],
        }

    return render_template(
        "home.html", weather=return_data
    )  # Render the "home.html" template


# Import all route handlers from routes.py
from . import routes
