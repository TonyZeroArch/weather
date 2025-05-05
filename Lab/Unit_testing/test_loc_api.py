import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.loc_api import LocService


class TestLocService(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test"""
        # Sample location data for testing
        self.zip_location = {"postal_code": "27587", "city": "", "state": ""}
        self.city_state_location = {"postal_code": "", "city": "Raleigh", "state": "NC"}
        self.empty_location = {"postal_code": "", "city": "", "state": ""}

        # Create service instances
        self.zip_service = LocService(self.zip_location)
        self.city_state_service = LocService(self.city_state_location)
        self.empty_service = LocService(self.empty_location)

    def test_init(self):
        """Test LocService initialization"""
        # Test with zip code
        self.assertEqual(self.zip_service.loc["postal_code"], "27587")
        self.assertEqual(self.zip_service.loc["city"], None)
        self.assertEqual(self.zip_service.loc["state"], None)

        # Test with city/state
        self.assertEqual(self.city_state_service.loc["postal_code"], None)
        self.assertEqual(self.city_state_service.loc["city"], "Raleigh")
        self.assertEqual(self.city_state_service.loc["state"], "NC")

        # Test with empty location
        self.assertEqual(self.empty_service.loc["postal_code"], None)
        self.assertEqual(self.empty_service.loc["city"], None)
        self.assertEqual(self.empty_service.loc["state"], None)

    @patch("requests.get")
    def test_fetch_location_zip_code(self, mock_get):
        """Test fetch_location with a valid zip code"""
        # Set up mock response for zip code
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "place_id": 333740569,
                "lat": "35.7915",
                "lon": "-78.7811",
                "display_name": "27587, Wake Forest, Wake County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with zip code
        params = {"postalcode": "27587", "format": "json"}
        result = self.zip_service.fetch_location(params, s_type=0)

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()

        # Verify the result
        self.assertEqual(result["lat"], "35.7915")
        self.assertEqual(result["lon"], "-78.7811")
        self.assertEqual(result["postal_code"], "27587")
        self.assertEqual(result["city"], "Wake Forest")
        self.assertEqual(result["state"], "NC")

    @patch("requests.get")
    def test_fetch_location_city_state(self, mock_get):
        """Test fetch_location with a valid city and state"""
        # Set up mock response for city/state
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "place_id": 298208173,
                "lat": "35.7795897",
                "lon": "-78.6381787",
                "display_name": "Raleigh, Wake County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with city/state
        params = {"city": "Raleigh", "state": "NC", "format": "json"}
        result = self.city_state_service.fetch_location(params, s_type=1)

        # Verify the result
        self.assertEqual(result["lat"], "35.7795897")
        self.assertEqual(result["lon"], "-78.6381787")
        self.assertEqual(result["postal_code"], "")
        self.assertEqual(result["city"], "Raleigh")
        self.assertEqual(result["state"], "NC")

    @patch("requests.get")
    def test_fetch_location_empty_result(self, mock_get):
        """Test fetch_location with an empty result"""
        # Set up mock response for empty result
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Test with non-existent zip code
        params = {"postalcode": "00000", "format": "json"}
        result = self.zip_service.fetch_location(params, s_type=0)

        # Verify the result is an empty dict
        self.assertEqual(result, {})

    @patch("requests.get")
    def test_fetch_location_no_us_result(self, mock_get):
        """Test fetch_location with no US results"""
        # Set up mock response for non-US location
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "place_id": 12345,
                "lat": "48.8566",
                "lon": "2.3522",
                "display_name": "Paris, Île-de-France, France",
            }
        ]
        mock_get.return_value = mock_response

        # Test with non-US location
        params = {"city": "Paris", "format": "json"}
        result = self.zip_service.fetch_location(params, s_type=1)

        # Verify the result is an empty dict (no US location found)
        self.assertEqual(result, {})

    @patch("requests.get")
    def test_fetch_location_exception(self, mock_get):
        """Test fetch_location handling of exceptions"""
        # Set up mock to raise an exception
        mock_get.side_effect = Exception("API Error")

        # Test exception handling
        params = {"postalcode": "27587", "format": "json"}
        result = self.zip_service.fetch_location(params, s_type=0)

        # Verify the result is an empty dict
        self.assertEqual(result, {})

    @patch.object(LocService, "fetch_location")
    def test_get_lat_lon_zip(self, mock_fetch):
        """Test get_lat_lon with a zip code"""
        # Set up mock return value
        mock_fetch.return_value = {
            "lat": "35.7915",
            "lon": "-78.7811",
            "postal_code": "27587",
            "city": "Wake Forest",
            "state": "NC",
        }

        # Call get_lat_lon with zip code
        result = self.zip_service.get_lat_lon(self.zip_location)

        # Verify fetch_location was called with correct parameters
        mock_fetch.assert_called_once()
        args, kwargs = mock_fetch.call_args
        self.assertEqual(args[0], {"postalcode": "27587", "format": "json"})
        self.assertEqual(kwargs.get("s_type", 0), 0)

        # Verify the result
        self.assertEqual(result["lat"], "35.7915")
        self.assertEqual(result["lon"], "-78.7811")

    @patch.object(LocService, "fetch_location")
    def test_get_lat_lon_city_state(self, mock_fetch):
        """Test get_lat_lon with city and state"""
        # Set up mock return value
        mock_fetch.return_value = {
            "lat": "35.7795897",
            "lon": "-78.6381787",
            "postal_code": "",
            "city": "Raleigh",
            "state": "NC",
        }

        # Call get_lat_lon with city/state
        result = self.city_state_service.get_lat_lon(self.city_state_location)

        # Verify fetch_location was called with correct parameters
        mock_fetch.assert_called_once()
        args, kwargs = mock_fetch.call_args
        self.assertEqual(args[0], {"city": "Raleigh", "state": "NC", "format": "json"})
        self.assertEqual(kwargs.get("s_type", 0), 1)

        # Verify the result
        self.assertEqual(result["lat"], "35.7795897")
        self.assertEqual(result["lon"], "-78.6381787")

    @patch.object(LocService, "fetch_location")
    def test_get_lat_lon_empty(self, mock_fetch):
        """Test get_lat_lon with empty location data"""
        # Call get_lat_lon with empty location
        result = self.empty_service.get_lat_lon(self.empty_location)

        # Verify fetch_location was not called
        mock_fetch.assert_not_called()

        # Verify the result is an empty dict
        self.assertEqual(result, {})

    @patch.object(LocService, "fetch_location")
    def test_show_lat_lon(self, mock_fetch):
        """Test show_lat_lon method"""
        # Set up mock return value
        mock_fetch.return_value = {
            "lat": "35.7915",
            "lon": "-78.7811",
            "postal_code": "27587",
            "city": "Wake Forest",
            "state": "NC",
        }

        # Call show_lat_lon
        result = self.zip_service.show_lat_lon()

        # Verify fetch_location was called with correct parameters
        mock_fetch.assert_called_once()

        # Verify the result
        self.assertEqual(result["lat"], "35.7915")
        self.assertEqual(result["lon"], "-78.7811")
        self.assertEqual(result["postal_code"], "27587")
        self.assertEqual(result["city"], "Wake Forest")
        self.assertEqual(result["state"], "NC")


if __name__ == "__main__":
    unittest.main()
