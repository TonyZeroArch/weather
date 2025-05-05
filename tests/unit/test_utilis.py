import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime
import pytz
import json
from flask import Flask, session
import numpy as np

# Import the functions from utils.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.routes.utils import (
    test_print,
    debug_print_session,
    verify,
    update_view_cur_frame,
    update_view_hourly_frame,
    update_view_7_day_frame,
    get_time_in_timezone,
    get_is_day,
    convert_to_celsius,
)
from app.utils.constants import WEATHER_CODE_MAP


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test-key"

        # Sample location data
        self.sample_location = {
            "lat": 35.7915,
            "lon": -78.7811,
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
            "hours": [
                datetime.datetime(2025, 5, 3, 7, 0),
                datetime.datetime(2025, 5, 3, 8, 0),
                datetime.datetime(2025, 5, 3, 9, 0),
                datetime.datetime(2025, 5, 3, 10, 0),
                datetime.datetime(2025, 5, 3, 11, 0),
                datetime.datetime(2025, 5, 3, 12, 0),
                datetime.datetime(2025, 5, 3, 13, 0),
                datetime.datetime(2025, 5, 3, 14, 0),
            ],
            "hourly_temperature_2m": np.array(
                [44.5, 48.4, 52.9, 55.3, 57.6, 59.6, 62.8, 65.2]
            ),
            "hourly_weather_code": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "hourly_precipitation_probability": np.array(
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ),
            "timezone": "America/New_York",
            "daily_sunrise": ["2025-05-03 06:43:06", "2025-05-04 06:42:01"],
            "daily_sunset": ["2025-05-03 19:49:15", "2025-05-04 19:50:21"],
        }

        self.sample_daily = {
            "date": [
                "2025-05-03",
                "2025-05-04",
                "2025-05-05",
                "2025-05-06",
                "2025-05-07",
                "2025-05-08",
                "2025-05-09",
            ],
            "temperature_2m_max": np.array([66.0, 70.2, 72.5, 68.4, 65.8, 67.3, 69.0]),
            "temperature_2m_min": np.array([44.0, 46.2, 48.5, 47.5, 45.0, 45.8, 46.2]),
            "weather_code": np.array([0.0, 0.0, 2.0, 3.0, 1.0, 0.0, 0.0]),
            "precipitation_probability_max": np.array(
                [0.0, 0.0, 20.0, 40.0, 10.0, 0.0, 0.0]
            ),
        }

    def test_test_print(self):
        """Test simple test_print function"""
        with patch("builtins.print") as mock_print:
            test_print()
            mock_print.assert_called_once_with("test_print function called")

    def test_debug_print_session(self):
        """Test debug_print_session function"""
        with patch("builtins.print") as mock_print:
            with self.app.test_request_context():
                session["test_key"] = "test_value"
                debug_print_session("test_function")

                # Check print was called 4 times
                self.assertEqual(mock_print.call_count, 4)

    @patch("app.routes.utils.LocService")
    def test_verify_with_valid_data(self, mock_loc_service):
        """Test verify function with valid data"""
        # Set up mock
        mock_instance = mock_loc_service.return_value
        mock_instance.show_lat_lon.return_value = self.sample_location

        with self.app.test_request_context():
            result = verify({"city": "Cary", "state": "NC"})
            self.assertTrue(result)
            self.assertEqual(session["cur_location"], self.sample_location)

    @patch("app.routes.utils.LocService")
    def test_verify_with_empty_data(self, mock_loc_service):
        """Test verify function with empty data"""
        with self.app.test_request_context():
            result = verify({})
            self.assertFalse(result)

    @patch("app.routes.utils.LocService")
    def test_verify_with_invalid_data(self, mock_loc_service):
        """Test verify function with invalid coordinates"""
        # Set up mock
        mock_instance = mock_loc_service.return_value
        mock_instance.show_lat_lon.return_value = {}

        with self.app.test_request_context():
            result = verify({"city": "InvalidCity", "state": "XX"})
            self.assertFalse(result)

    @patch("app.routes.utils.WeatherService")
    @patch("app.routes.utils.get_time_in_timezone")
    def test_update_view_cur_frame_fahrenheit(self, mock_time, mock_weather_service):
        """Test update_view_cur_frame with Fahrenheit units"""
        # Set up mocks
        mock_instance = mock_weather_service.return_value
        mock_instance.get_cur_forecast.return_value = self.sample_current

        mock_time.return_value = {
            "dest_time": datetime.datetime.now(),
            "local_timezone": "America/Chicago",
            "dest_timezone": "America/New_York",
            "local_time": "2025-05-03 07:00:00",
            "time_difference_hours": 1.0,
        }

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "F"
            result = update_view_cur_frame()

            # Verify result contains expected data
            self.assertEqual(result["current_temperature_2m"], 47.0)
            self.assertEqual(result["city"], "Cary")
            self.assertEqual(result["state"], "NC")
            self.assertEqual(result["unit"], "F")

    @patch("app.routes.utils.WeatherService")
    @patch("app.routes.utils.get_time_in_timezone")
    def test_update_view_cur_frame_celsius(self, mock_time, mock_weather_service):
        """Test update_view_cur_frame with Celsius units"""
        # Set up mocks
        mock_instance = mock_weather_service.return_value
        mock_instance.get_cur_forecast.return_value = self.sample_current

        mock_time.return_value = {
            "dest_time": datetime.datetime.now(),
            "local_timezone": "America/Chicago",
            "dest_timezone": "America/New_York",
            "local_time": "2025-05-03 07:00:00",
            "time_difference_hours": 1.0,
        }

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "C"
            result = update_view_cur_frame()

            # Verify result contains expected data converted to Celsius
            self.assertEqual(result["current_temperature_2m"], 8)  # 47F -> 8C
            self.assertEqual(result["daily_temperature_2m_max"], 18)  # 66F -> 18C
            self.assertEqual(result["daily_temperature_2m_min"], 6)  # 44F -> 6C

    @patch("app.routes.utils.WeatherService")
    @patch("app.routes.utils.get_time_in_timezone")
    def test_update_view_hourly_frame_fahrenheit(self, mock_time, mock_weather_service):
        """Test update_view_hourly_frame with Fahrenheit units"""
        # Set up mocks
        mock_instance = mock_weather_service.return_value
        mock_instance.get_hourly_forecast.return_value = self.sample_hourly

        mock_time.return_value = {
            "dest_time": datetime.datetime(2025, 5, 3, 6, 0),
            "dest_timezone": "America/New_York",
        }

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "F"
            result = update_view_hourly_frame()

            # Verify result contains expected data
            self.assertEqual(len(result["hours"]), 6)
            self.assertEqual(result["hourly_temperature_2m"][0], "44")
            self.assertEqual(result["hourly_precipitation_probability"][0], "0")

    @patch("app.routes.utils.WeatherService")
    @patch("app.routes.utils.get_time_in_timezone")
    def test_update_view_hourly_frame_celsius(self, mock_time, mock_weather_service):
        """Test update_view_hourly_frame with Celsius units"""
        # Set up mocks
        mock_instance = mock_weather_service.return_value
        mock_instance.get_hourly_forecast.return_value = self.sample_hourly

        mock_time.return_value = {
            "dest_time": datetime.datetime(2025, 5, 3, 6, 0),
            "dest_timezone": "America/New_York",
        }

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "C"
            result = update_view_hourly_frame()

            # Verify result contains temperature converted to Celsius
            self.assertEqual(result["hourly_temperature_2m"][0], "6")  # 44F -> 6C

    @patch("app.routes.utils.WeatherService")
    def test_update_view_7_day_frame_fahrenheit(self, mock_weather_service):
        """Test update_view_7_day_frame with Fahrenheit units"""
        # Set up mock
        mock_instance = mock_weather_service.return_value
        mock_instance.get_7_day_forecast.return_value = self.sample_daily

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "F"
            result = update_view_7_day_frame()

            # Verify result contains expected data
            self.assertEqual(len(result["date"]), 7)
            self.assertEqual(result["temperature_2m_max"][0], "66")
            self.assertEqual(result["temperature_2m_min"][0], "44")
            self.assertEqual(
                result["icon_daily"][0], WEATHER_CODE_MAP["0"]["day"]["image"]
            )

    @patch("app.routes.utils.WeatherService")
    def test_update_view_7_day_frame_celsius(self, mock_weather_service):
        """Test update_view_7_day_frame with Celsius units"""
        # Set up mock
        mock_instance = mock_weather_service.return_value
        mock_instance.get_7_day_forecast.return_value = self.sample_daily

        with self.app.test_request_context():
            session["cur_location"] = self.sample_location
            session["temp_unit"] = "C"
            result = update_view_7_day_frame()

            # Verify temperatures are converted to Celsius
            self.assertEqual(result["temperature_2m_max"][0], "18")  # 66F -> 18C
            self.assertEqual(result["temperature_2m_min"][0], "6")  # 44F -> 6C

    @patch("tzlocal.get_localzone")
    @patch("datetime.datetime")
    def test_get_time_in_timezone_success(self, mock_datetime, mock_get_localzone):
        """Test get_time_in_timezone with valid timezone"""
        # Setup mocks
        local_tz = pytz.timezone("America/Chicago")
        mock_get_localzone.return_value = local_tz

        local_dt = datetime.datetime(2025, 5, 3, 6, 0)
        mock_datetime.now.return_value = local_dt

        # Real function behavior for timezone conversion
        mock_datetime.now = datetime.datetime.now

        result = get_time_in_timezone("America/New_York")

        # Verify result contains expected keys
        self.assertIn("local_timezone", result)
        self.assertIn("local_time", result)
        self.assertIn("dest_timezone", result)
        self.assertIn("dest_time", result)
        self.assertIn("time_difference_hours", result)
        self.assertEqual(result["dest_timezone"], "America/New_York")

    def test_get_time_in_timezone_error(self):
        """Test get_time_in_timezone with invalid timezone"""
        result = get_time_in_timezone("Invalid/Timezone")
        self.assertEqual(result, {})

    def test_get_is_day_daytime(self):
        """Test get_is_day during daytime hours"""
        # Create test data
        target_time = datetime.datetime(2025, 5, 3, 12, 0)  # Noon
        sunrise = ["2025-05-03 06:00:00", "2025-05-04 06:00:00"]
        sunset = ["2025-05-03 20:00:00", "2025-05-04 20:00:00"]

        result = get_is_day(target_time, sunrise, sunset)
        self.assertEqual(result, "day")

    def test_get_is_day_nighttime(self):
        """Test get_is_day during nighttime hours"""
        # Create test data
        target_time = datetime.datetime(2025, 5, 3, 22, 0)  # 10 PM
        sunrise = ["2025-05-03 06:00:00", "2025-05-04 06:00:00"]
        sunset = ["2025-05-03 20:00:00", "2025-05-04 20:00:00"]

        result = get_is_day(target_time, sunrise, sunset)
        self.assertEqual(result, "night")

    def test_convert_to_celsius(self):
        """Test Fahrenheit to Celsius conversion"""
        # Test freezing point
        self.assertEqual(convert_to_celsius(32), 0)

        # Test boiling point
        self.assertEqual(convert_to_celsius(212), 100)

        # Test common temperature
        self.assertEqual(convert_to_celsius(68), 20)

        # Test negative temperature
        self.assertEqual(convert_to_celsius(-4), -20)


if __name__ == "__main__":
    unittest.main()
