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

from datetime import datetime
from urllib.parse import unquote
import logging

# Import the Blueprint from blueprint.py instead of __init__.py
from .blueprint import main

# import my services
from app.services.loc_api import LocService
from app.services.weather_service import WeatherService
from app.utils.constants import WEATHER_CODE_MAP

# import shared functions within routes
from .utils import (
    test_print,
    verify,
    update_view_cur_frame,
    update_view_hourly_frame,
    update_view_7_day_frame,
)

# Create module-level logger
logger = logging.getLogger(__name__)


# Development test
@main.route("/base")
def test_base():
    return render_template("base.html")


# Development test
@main.route("/test_home")
def test_home():
    return render_template("draft/home.html")


# @main.route("/hello")
# def hello_world():
#     test_print()
#     return "<p>Hello, World!</p>"


# # Route to handle JSON POST request
# @main.route("/test/json_api", methods=["POST"])
# def json_api():
#     data = request.json  # Read JSON body as Python dict
#     print(f"In case 05,Received JSON data: {data}")

#     city = data.get("city", "Unknown")
#     unit = data.get("unit", "C")
#     print(f"In case 05, city: {city}, unit: {unit}")
#     print(f"type of unit: {type(unit)}")
#     print(f"type of city: {type(city)}")

#     # Simulate weather data
#     temperature = 22 if unit == "C" else 71.6
#     humidity = 60

#     return jsonify(
#         {"city": city, "unit": unit, "temperature": temperature, "humidity": humidity}
#     )


# # Route to handle JSON GET request
# @main.route("/test/case01")
# def test_case01():

#     return render_template("draft/path_param.html")


# @main.route("/test/<city>")
# def test(city):
#     # Get the 'unit' query param (e.g., ?unit=C)
#     unit = request.args.get("unit", "C")  # default to Celsius

#     # Simulate fake data for demo
#     temperature = 22 if unit == "C" else 71.6
#     humidity = 60

#     # Return HTML with interpolated values
#     html = f"""
#     <h2>Weather in {city}</h2>
#     <p>Temperature: {temperature}°{unit}</p>
#     <p>Humidity: {humidity}%</p>
#     <a href="/">Back</a>
#     """
#     return render_template_string(html)
#     # return render_template("draft/l_path_param.html", city=city, unit=unit)


# Route to handle JSON GET request


@main.route("/search", methods=["POST"])
def search():
    # # debug
    # logger.info("search endpoint called")

    data = request.json  # Read JSON body as Python dict

    if verify(data):  # True, if location data is valid

        # debug
        logger.info(f'After Verify....Location data: {session["cur_location"]}\n')
        # debug
        return jsonify(
            session["cur_location"]
            | update_view_cur_frame()
            | update_view_hourly_frame()
        )

    else:
        print("Location data is invalid.")
        return jsonify({})


@main.route("/forecast")
def forecast():

    return_data = (
        update_view_cur_frame()
        | update_view_7_day_frame()
        | {"unit": session["temp_unit"]}
    )

    # debug
    logger.debug(f"weather data forecast in :\n {return_data}\n")
    # return render_template("forecast.html", forecast=forecast_data, city=city)
    return render_template("forecast.html", data=return_data)


@main.route("/hourly")
def hourly():

    # logger.debug("hourly endpoint called\n ---Session data---\n {session}")
    print(f"session data : {session['cur_location']}")
    return_data = (
        {"date": datetime.today().strftime("%Y-%m-%d")}
        | update_view_cur_frame()
        | update_view_hourly_frame(24)
        | {"unit": session["temp_unit"]}
    )

    logger.debug(f"\n-----return data hourly page: {return_data}\n ")

    return render_template("hourly.html", data=return_data)


@main.route("/settings", methods=["GET", "POST"])
def settings():

    current_settings = {
        "temp_unit": "C",
        "wind_unit": "km/h",
        "precip_unit": "mm",
    }

    if request.method == "POST":
        session["temp_unit"] = request.form["temp_unit"]
        session["wind_unit"] = request.form["wind_unit"]
        session["precip_unit"] = request.form["precip_unit"]

        # debug
        print(f"session data in /settings: {session}")

        # return redirect(url_for("main.settings"))

    current_settings = {
        "temp_unit": session["temp_unit"],
        "wind_unit": session["wind_unit"],
        "precip_unit": session["precip_unit"],
    }
    return render_template("settings.html", data=current_settings)


@main.route("/error")
def error():
    return render_template("error.html")


@main.route("/api/location", methods=["POST"])
def api_location():
    print("/api/location API location endpoint called")
    try:
        # Get the JSON data from the request
        data = request.json
        print(f"Received location data: {data}")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Pass the location data to your LocService
        coords = LocService().get_lat_lon(data)
        return coords

    except Exception as e:
        import traceback

        traceback.print_exc()  # Print detailed error for debugging
        return jsonify({"error": str(e)}), 500
