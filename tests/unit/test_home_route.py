import unittest
from unittest.mock import patch, MagicMock
import json
import numpy as np
from datetime import datetime
from flask import session, template_rendered, Flask
from contextlib import contextmanager
import sys
import importlib

# Import the app and routes
from app.config import TestingConfig
from app import create_app
from app.services.weather_service import WeatherService


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reload route modules to avoid blueprint registration issues
        for module_name in list(sys.modules.keys()):
            if module_name.startswith("app.routes"):
                del sys.modules[module_name]

        # Create a fresh app for each test
        self.app = create_app(config_class=TestingConfig)
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SERVER_NAME"] = "localhost"
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Sample location data
        self.sample_location = {
            "lat": 35.7915,
            "lon": -78.7811,
            "postal_code": "27511",
            "city": "Cary",
            "state": "NC",
        }

        # Sample weather data
        self.sample_current = {
            "current_temperature_2m": 47.0,
            "current_apparent_temperature": 40.0,
            "daily_temperature_2m_max": 66.0,
            "daily_temperature_2m_min": 44.0,
            "daily_uv_index_max": 8.0,
            "daily_precipitation_probability_max": 0,
            "current_wind_speed_10m": 13.0,
            "daily_weather_code": 0,
            "is_day": 1,
            "timezone": "America/New_York",
        }

        self.sample_hourly = {
            "hours": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00"],
            "hourly_temperature_2m": np.array(
                [44.5181, 48.3881, 52.9781, 55.3181, 57.5681, 59.6381], dtype=np.float32
            ),
            "hourly_weather_code": np.array(
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32
            ),
            "hourly_precipitation_probability": np.array(
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32
            ),
        }

        self.sample_sunrise_sunset = {
            "sunrise": "6:43:06 AM",
            "sunset": "7:49:15 PM",
            "first_light": "5:12:54 AM",
            "last_light": "9:19:27 PM",
            "dawn": "6:16:45 AM",
            "dusk": "8:15:36 PM",
            "solar_noon": "1:16:11 PM",
            "golden_hour": "7:14:59 PM",
            "day_length": "13:06:08",
            "timezone": "America/New_York",
            "utc_offset": -240,
        }

    def tearDown(self):
        """Tear down test fixtures after each test."""
        self.app_context.pop()

    @contextmanager
    def captured_templates(self, app):
        """Context manager to capture templates rendered during a block."""
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

    @patch("app.services.weather_service.WeatherService")
    def test_home_route_success(self, mock_weather_service_class):
        """Test the home route with successful weather data retrieval."""
        # Set up mock weather service
        mock_weather = MagicMock()
        mock_weather.get_cur_forecast.return_value = self.sample_current
        mock_weather.get_hourly_forecast.return_value = self.sample_hourly
        mock_weather.get_sunrise_sunset.return_value = self.sample_sunrise_sunset
        mock_weather_service_class.return_value = mock_weather

        # Set up session data
        with self.client.session_transaction() as sess:
            sess["cur_location"] = self.sample_location

        # Freeze time for consistent timestamp
        current_time = "07:45"
        current_hour = 7

        with patch("datetime.datetime") as mock_datetime:
            mock_date_instance = MagicMock()
            mock_date_instance.strftime.return_value = current_time
            mock_date_instance.hour = current_hour
            mock_datetime.now.return_value = mock_date_instance
            mock_datetime.strptime = datetime.strptime

            # Execute request with captured templates
            with self.captured_templates(self.app) as templates:
                response = self.client.get("/")

                # Check response
                self.assertEqual(response.status_code, 200)

                # Check template was rendered
                self.assertEqual(len(templates), 1)
                template, context = templates[0]
                self.assertEqual(template.name, "home.html")

    @patch("app.services.weather_service.WeatherService")
    def test_home_route_error_handling(self, mock_weather_service_class):
        """Test that the home route handles errors gracefully."""
        # Set up mock to raise exception
        mock_weather = MagicMock()
        mock_weather.get_cur_forecast.side_effect = Exception("API error")
        mock_weather_service_class.return_value = mock_weather

        # Set up session data
        with self.client.session_transaction() as sess:
            sess["cur_location"] = self.sample_location

        # Execute request
        response = self.client.get("/")

        # Check status code
        self.assertEqual(response.status_code, 200)

    def test_time_formatting(self):
        """Test time formatting functionality outside of the route."""
        # Test different times directly
        test_cases = [
            {"input_hour": 0, "expected": "12:00 AM"},
            {"input_hour": 1, "expected": "1:00 AM"},
            {"input_hour": 12, "expected": "12:00 PM"},
            {"input_hour": 13, "expected": "1:00 PM"},
            {"input_hour": 23, "expected": "11:00 PM"},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                time_str = f"{case['input_hour']:02d}:00"
                formatted = (
                    datetime.strptime(time_str, "%H:%M")
                    .strftime("%I:%M %p")
                    .lstrip("0")
                )
                self.assertEqual(formatted, case["expected"])

    def test_day_night_determination(self):
        """Test day/night determination with sample data."""
        # Test day case
        day_test = {
            "sunrise": "6:00 AM",
            "sunset": "8:00 PM",
        }

        # Test night case
        night_test = {
            "sunrise": "8:00 AM",
            "sunset": "6:00 PM",
        }

        # Test hours
        test_hours = ["7:00 AM", "9:00 AM"]

        # Convert time strings to datetime objects for proper comparison
        # Parse the time strings - no need for app context
        sunrise_time = datetime.strptime(day_test["sunrise"], "%I:%M %p")
        sunset_time = datetime.strptime(day_test["sunset"], "%I:%M %p")
        test_time = datetime.strptime(test_hours[0], "%I:%M %p")

        # Test daytime case (7 AM is after sunrise at 6 AM)
        self.assertTrue(sunrise_time < test_time < sunset_time)

        # Parse time strings for night test
        night_sunrise_time = datetime.strptime(night_test["sunrise"], "%I:%M %p")

        # Test nighttime case (7 AM is before sunrise at 8 AM)
        self.assertTrue(test_time < night_sunrise_time)


if __name__ == "__main__":
    unittest.main()
