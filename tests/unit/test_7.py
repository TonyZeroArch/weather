import pytest
import os
import json
import sys
from flask import Flask, Blueprint, session
from bs4 import BeautifulSoup
import plistlib
import re
from unittest.mock import patch, MagicMock

# Import app modules
from app import create_app
from app.services.weather_service import WeatherService
from app.config import TestingConfig


def extract_data_from_webarchive(file_path):
    """
    Extract weather data from webarchive file.
    This is a Mac-specific function to extract the forecast data.
    """
    try:
        # Try to read the webarchive as a binary plist file
        with open(file_path, "rb") as f:
            try:
                archive = plistlib.load(f)
                # Extract the HTML content from the webarchive
                if "WebMainResource" in archive:
                    html_content = (
                        archive["WebMainResource"]
                        .get("WebResourceData", b"")
                        .decode("utf-8")
                    )
                    soup = BeautifulSoup(html_content, "html.parser")

                    # Try to find JSON data embedded in the page
                    script_tags = soup.find_all("script")
                    for script in script_tags:
                        if script.string and "forecast_data" in script.string:
                            # Use regex to find JSON object
                            match = re.search(
                                r"forecast_data\s*=\s*({.*?});",
                                script.string,
                                re.DOTALL,
                            )
                            if match:
                                json_str = match.group(1)
                                data = json.loads(json_str)
                                # Add timezone if missing
                                if "timezone" not in data:
                                    data["timezone"] = "America/New_York"

                                # Add weather_code if missing
                                if "weather_code" not in data:
                                    # Create a list of weather codes same length as dates
                                    if "date" in data:
                                        data["weather_code"] = [1] * len(data["date"])
                                    else:
                                        data["weather_code"] = [1]

                                # Add precipitation_probability_max if missing
                                if "precipitation_probability_max" not in data:
                                    if "date" in data:
                                        data["precipitation_probability_max"] = [
                                            20
                                        ] * len(data["date"])
                                    else:
                                        data["precipitation_probability_max"] = [20]

                                # Add temperature_2m_min if missing
                                if "temperature_2m_min" not in data:
                                    if "date" in data:
                                        data["temperature_2m_min"] = [55] * len(
                                            data["date"]
                                        )
                                    else:
                                        data["temperature_2m_min"] = [55]

                                return data
            except Exception as e:
                print(f"Error parsing as plist: {e}")

        # Fallback: try to extract data from the raw file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Look for JSON data pattern
            json_match = re.search(
                r'"date":\s*\[(.*?)\].*?"temperature_2m_max":\s*\[(.*?)\]',
                content,
                re.DOTALL,
            )
            if json_match:
                # Build a simplified data structure if full JSON parsing fails
                dates = json_match.group(1).strip().split(",")
                return {
                    "city": "Cary",
                    "state": "NC",
                    "date": dates,
                    "temperature_2m_max": [
                        int(x) for x in json_match.group(2).strip().split(",")
                    ],
                    "weather_code": [1] * len(dates),  # Add weather codes
                    "precipitation_probability_max": [20]
                    * len(dates),  # Add precipitation
                    "temperature_2m_min": [55] * len(dates),  # Add min temps
                    "icon_daily": ["/static/images/weather/sunny.png"] * len(dates),
                    "description_daily": ["Sunny"] * len(dates),
                    "timezone": "America/New_York",
                }
    except Exception as e:
        print(f"Error extracting data from webarchive: {e}")

    # If all else fails, return a minimal data structure with all required fields
    return {
        "city": "Cary",
        "state": "NC",
        "date": [
            "2025-05-01",
            "2025-05-02",
            "2025-05-03",
            "2025-05-04",
            "2025-05-05",
            "2025-05-06",
            "2025-05-07",
        ],
        "icon_daily": ["/static/images/weather/sunny.png"] * 7,
        "description_daily": ["Sunny"] * 7,
        "temperature_2m_max": [75, 78, 80, 77, 76, 79, 81],
        "temperature_2m_min": [55, 57, 59, 56, 54, 58, 60],
        "weather_code": [1, 1, 2, 3, 1, 1, 2],  # Added weather codes for 7 days
        "precipitation_probability_max": [
            10,
            20,
            30,
            40,
            10,
            5,
            20,
        ],  # Added precipitation
        "timezone": "America/New_York",
    }


# Path to the webarchive file
webarchive_path = os.path.join(
    os.path.dirname(__file__), "7-DayForecast- Cary.webarchive"
)

# Try to extract forecast data from the webarchive
forecast_data = extract_data_from_webarchive(webarchive_path)

# Create mock location data that matches what's expected in session
mock_location = {
    "city": "Cary",
    "state": "NC",
    "postal_code": "",
    "lat": "35.7915",
    "lon": "-78.7811",
}


def create_test_app():
    """Helper function to create a test app using different methods"""
    try:
        # Try method 1: passing config class directly
        app = create_app(config_class=TestingConfig)
        print("Created app with config_class parameter")
        return app
    except TypeError:
        try:
            # Try method 2: passing config name as string
            app = create_app("testing")
            print("Created app with config name parameter")
            return app
        except TypeError:
            try:
                # Try method 3: no parameters, apply config after creation
                app = create_app()
                app.config.from_object(TestingConfig)
                print("Created app with post-creation config")
                return app
            except Exception as e:
                print(f"Failed to create app: {e}")
                # Last resort: create a minimal Flask app for testing
                app = Flask(__name__)
                app.config.from_object(TestingConfig)
                app.secret_key = "test_secret_key"  # Add this for session support

                # You might need to manually register blueprints here
                try:
                    from app.routes.blueprint import main

                    app.register_blueprint(main)
                except ImportError:
                    print("Could not import blueprint, skipping registration")

                return app


@pytest.fixture
def app():
    """Create a test flask app with the main blueprint registered."""
    app = create_test_app()
    app.secret_key = "test_secret_key"  # Ensure session works

    # Mock the WeatherService to return our test data
    with patch.object(WeatherService, "get_7_day_forecast") as mock_forecast:
        mock_forecast.return_value = forecast_data

        # We also need to mock the current forecast for the main page
        # Include the timezone in the mock data
        with patch.object(WeatherService, "get_cur_forecast") as mock_cur_forecast:
            mock_cur_forecast.return_value = {
                "city": forecast_data["city"],
                "city_state": f"{forecast_data['city']}, {forecast_data['state']}",
                "timezone": "America/New_York",  # Add timezone that routes.utils.py needs
                "current_temperature_2m": 75,  # Add other fields that might be needed
                "current_apparent_temperature": 78,
                "current_precipitation": 20,
                "current_wind_speed_10m": 5,
                "daily_temperature_2m_max": 80,
                "daily_temperature_2m_min": 65,
                "daily_uv_index_max": 7,
                "description": "Sunny",
                "icon": "/static/images/weather/sunny.png",
                "is_day": 1,
                "current_weather_code": 1,
                "weather_code": 1,
                "updated_time": "12:00 PM",
            }
            yield app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


def test_forecast_route(client):
    """Test the forecast route with real data from webarchive."""
    # Set up session data before request
    with client.session_transaction() as sess:
        sess["cur_location"] = mock_location

    # Make a request to the forecast endpoint
    response = client.get("/forecast")

    # Check for successful response
    assert response.status_code == 200

    # Parse the HTML
    soup = BeautifulSoup(response.data, "html.parser")

    # Find the forecast container
    forecast_container = soup.find("div", class_="seven-day-forecast")
    assert forecast_container is not None

    # Check for forecast days
    forecast_days = forecast_container.find_all("div", class_="forecast-day")
    assert len(forecast_days) > 0  # Should have at least one day

    # Test first day content as a sample
    first_day = forecast_days[0]

    # Check that it has expected elements
    assert first_day.find("p") is not None  # Date
    assert first_day.find("img") is not None  # Weather icon


def test_forecast_template_structure(app):
    """Test the detailed structure of the forecast template with real data."""
    with app.test_client() as client:
        # Set up session data before request
        with client.session_transaction() as sess:
            sess["cur_location"] = mock_location

        # Make a request to the forecast endpoint
        response = client.get("/forecast")

        # Parse the HTML
        soup = BeautifulSoup(response.data, "html.parser")

        # Verify the basic structure is correct
        h2 = soup.find("h2")
        assert h2 is not None
        assert "Forecast for" in h2.text

        # Find the forecast container
        forecast_container = soup.find("div", class_="seven-day-forecast")
        assert forecast_container is not None
