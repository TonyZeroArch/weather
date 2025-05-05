import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from datetime import datetime
from flask import session, template_rendered
from contextlib import contextmanager

# Import the app and routes
from app.config import TestingConfig
from app import create_app
from app.services.weather_service import WeatherService
from app.services.loc_api import LocService


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test."""
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
            "lat": "35.7915",
            "lon": "-78.7811",
            "postal_code": "27511",
            "city": "Cary",
            "state": "NC",
            "city_state": "Cary, NC",
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
            "current_weather_code": 0,
            "is_day": 1,
            "timezone": "America/New_York",
        }

        self.sample_hourly = {
            "hours": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00"],
            "hourly_temperature_2m": [45, 48, 53, 55, 58, 60],
            "hourly_weather_code": [0, 0, 0, 0, 0, 0],
            "hourly_precipitation_probability": [0, 0, 0, 0, 0, 0],
            "daily_sunrise": ["2025-05-03 06:43:06", "2025-05-04 06:42:01"],
            "daily_sunset": ["2025-05-03 19:49:15", "2025-05-04 19:50:21"],
        }

        self.sample_7day = {
            "date": ["2025-05-03", "2025-05-04", "2025-05-05", "2025-05-06"],
            "temperature_2m_max": [66, 70, 73, 68],
            "temperature_2m_min": [44, 46, 49, 48],
            "weather_code": [0, 0, 2, 3],
            "precipitation_probability_max": [0, 0, 20, 40],
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

    def test_base_route(self):
        """Test the base template route."""
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/base")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "base.html")

    def test_test_home_route(self):
        """Test the test_home route."""
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/test_home")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "draft/home.html")

    @patch("app.routes.routes.verify")
    def test_search_route_valid_location(self, mock_verify):
        """Test the search route with valid location data."""
        # Set up mock
        mock_verify.return_value = True

        # Set up session data
        with self.client.session_transaction() as sess:
            sess["cur_location"] = self.sample_location
            sess["temp_unit"] = "F"
            sess["wind_unit"] = "mph"
            sess["precip_unit"] = "in"

        # Set up mocks for update_view functions
        with patch("app.routes.routes.update_view_cur_frame") as mock_cur_frame, patch(
            "app.routes.routes.update_view_hourly_frame"
        ) as mock_hourly_frame:

            mock_cur_frame.return_value = {"current_temp": 75}
            mock_hourly_frame.return_value = {"hourly_forecast": [70, 72, 74]}

            # Send search request
            response = self.client.post(
                "/search",
                data=json.dumps({"city": "Cary", "state": "NC"}),
                content_type="application/json",
            )

            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)

            # Verify data contains merged results
            self.assertIn("city", data)
            self.assertIn("current_temp", data)
            self.assertIn("hourly_forecast", data)

    @patch("app.routes.routes.verify")
    def test_search_route_invalid_location(self, mock_verify):
        """Test the search route with invalid location data."""
        # Set up mock
        mock_verify.return_value = False

        # Send search request
        response = self.client.post(
            "/search",
            data=json.dumps({"city": "InvalidCity"}),
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Verify data is empty
        self.assertEqual(data, {})

    @patch("app.routes.routes.update_view_cur_frame")
    @patch("app.routes.routes.update_view_7_day_frame")
    def test_forecast_route(self, mock_7day_frame, mock_cur_frame):
        """Test the forecast route."""
        # Set up mocks
        mock_cur_frame.return_value = {"current_temp": 75}
        mock_7day_frame.return_value = {
            "date": self.sample_7day["date"],
            "temperature_2m_max": self.sample_7day["temperature_2m_max"],
        }

        # Set up session data
        with self.client.session_transaction() as sess:
            sess["cur_location"] = self.sample_location
            sess["temp_unit"] = "F"
            sess["wind_unit"] = "mph"
            sess["precip_unit"] = "in"

        # Test with captured templates
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/forecast")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered with correct data
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "forecast.html")
            self.assertIn("data", context)
            self.assertEqual(context["data"]["unit"], "F")
            self.assertEqual(context["data"]["current_temp"], 75)
            # Verify icon_daily exists
            self.assertIn("icon_daily", context["data"])

    @patch("app.routes.routes.update_view_cur_frame")
    @patch("app.routes.routes.update_view_hourly_frame")
    def test_hourly_route(self, mock_hourly_frame, mock_cur_frame):
        """Test the hourly route."""
        # Set up mocks
        mock_cur_frame.return_value = {"current_temp": 75}
        mock_hourly_frame.return_value = {"hours": self.sample_hourly["hours"]}

        # Set up session data
        with self.client.session_transaction() as sess:
            sess["cur_location"] = self.sample_location
            sess["temp_unit"] = "F"
            sess["wind_unit"] = "mph"
            sess["precip_unit"] = "in"

        # Test with captured templates
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/hourly")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered with correct data
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "hourly.html")
            self.assertIn("data", context)
            self.assertEqual(context["data"]["unit"], "F")
            self.assertIn("date", context["data"])
            self.assertEqual(context["data"]["current_temp"], 75)

    def test_settings_route_get(self):
        """Test the settings route with GET method."""
        # Set up session data
        with self.client.session_transaction() as sess:
            sess["temp_unit"] = "F"
            sess["wind_unit"] = "mph"
            sess["precip_unit"] = "in"

        # Test with captured templates
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/settings")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered with correct data
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "settings.html")
            self.assertIn("data", context)
            self.assertEqual(context["data"]["temp_unit"], "F")
            self.assertEqual(context["data"]["wind_unit"], "mph")
            self.assertEqual(context["data"]["precip_unit"], "in")

    def test_settings_route_post(self):
        """Test the settings route with POST method."""
        # Test with captured templates
        with self.captured_templates(self.app) as templates:
            response = self.client.post(
                "/settings",
                data={"temp_unit": "C", "wind_unit": "km/h", "precip_unit": "mm"},
            )

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered with correct data
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "settings.html")
            self.assertIn("data", context)
            self.assertEqual(context["data"]["temp_unit"], "C")
            self.assertEqual(context["data"]["wind_unit"], "km/h")
            self.assertEqual(context["data"]["precip_unit"], "mm")

            # Check session was updated
            with self.client.session_transaction() as sess:
                self.assertEqual(sess["temp_unit"], "C")
                self.assertEqual(sess["wind_unit"], "km/h")
                self.assertEqual(sess["precip_unit"], "mm")

    def test_error_route(self):
        """Test the error route."""
        with self.captured_templates(self.app) as templates:
            response = self.client.get("/error")

            # Check response
            self.assertEqual(response.status_code, 200)

            # Check template was rendered
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, "error.html")

    @patch("app.routes.routes.LocService")
    def test_api_location_route_success(self, mock_loc_service):
        """Test the api_location route with valid data."""
        # Set up mock
        mock_instance = mock_loc_service.return_value
        mock_instance.get_lat_lon.return_value = {"lat": "35.7915", "lon": "-78.7811"}

        # Send request
        response = self.client.post(
            "/api/location",
            data=json.dumps({"city": "Cary", "state": "NC"}),
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["lat"], "35.7915")
        self.assertEqual(data["lon"], "-78.7811")

    def test_api_location_route_no_data(self):
        """Test the api_location route with no data."""
        # Send request with empty body
        response = self.client.post(
            "/api/location", data=json.dumps({}), content_type="application/json"
        )

        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("app.routes.routes.LocService")
    def test_api_location_route_error(self, mock_loc_service):
        """Test the api_location route handling exceptions."""
        # Set up mock to raise exception
        mock_instance = mock_loc_service.return_value
        mock_instance.get_lat_lon.side_effect = Exception("API error")

        # Send request
        response = self.client.post(
            "/api/location",
            data=json.dumps({"city": "Cary", "state": "NC"}),
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "API error")


if __name__ == "__main__":
    unittest.main()
