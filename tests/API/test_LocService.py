import pytest
import requests
from unittest.mock import patch, Mock
from app.services.loc_api import LocService


class TestLocService:

    def setup_method(self):
        # Initialize with empty location dict
        self.loc_service = LocService({})

    def test_init(self):
        """Test initialization of LocService with empty location"""
        assert self.loc_service.loc == {
            "postal_code": None,
            "city": None,
            "state": None,
        }

    def test_init_with_location(self):
        """Test initialization with location data"""
        location_data = {"postal_code": "27516", "city": "Chapel Hill", "state": "NC"}
        service = LocService(location_data)
        assert service.loc["postal_code"] == "27516"
        assert service.loc["city"] == "Chapel Hill"
        assert service.loc["state"] == "NC"

    @patch("requests.get")
    def test_fetch_location_postal_code(self, mock_get):
        """Test fetch_location with postal code params"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "35.9132",
                "lon": "-79.0558",
                "display_name": "27516, Chapel Hill, Orange County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with postal code params
        params = {"postalcode": "27516", "format": "json"}
        result = self.loc_service.fetch_location(params, s_type=0)

        # Verify the result includes lat and lon
        assert "lat" in result
        assert "lon" in result
        assert result["lat"] == "35.9132"
        assert result["lon"] == "-79.0558"

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["postalcode"] == "27516"
        assert kwargs["params"]["format"] == "json"

    @patch("requests.get")
    def test_fetch_location_city_state(self, mock_get):
        """Test fetch_location with city/state params"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "35.7915",
                "lon": "-78.7811",
                "display_name": "Cary, Wake County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with city/state params
        params = {"city": "Cary", "state": "NC", "format": "json"}
        result = self.loc_service.fetch_location(params, s_type=1)

        # Verify the result
        assert "lat" in result
        assert "lon" in result
        assert result["lat"] == "35.7915"
        assert result["lon"] == "-78.7811"

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["city"] == "Cary"
        assert kwargs["params"]["state"] == "NC"

    @patch("requests.get")
    def test_get_lat_lon_postal_code(self, mock_get):
        """Test get_lat_lon with postal code"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "35.9132",
                "lon": "-79.0558",
                "display_name": "27516, Chapel Hill, Orange County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with a postal code
        location = {"postal_code": "27516", "city": "", "state": ""}
        result = self.loc_service.get_lat_lon(location)

        # Verify the result
        assert "lat" in result
        assert "lon" in result
        assert result["lat"] == "35.9132"
        assert result["lon"] == "-79.0558"

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["postalcode"] == "27516"

    @patch("requests.get")
    def test_get_lat_lon_city_state(self, mock_get):
        """Test get_lat_lon with city/state"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "35.2271",
                "lon": "-80.8431",
                "display_name": "Charlotte, Mecklenburg County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Test with a city/state
        location = {"postal_code": "", "city": "Charlotte", "state": "NC"}
        result = self.loc_service.get_lat_lon(location)

        # Verify the result
        assert "lat" in result
        assert "lon" in result
        assert result["lat"] == "35.2271"
        assert result["lon"] == "-80.8431"

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["city"] == "Charlotte"
        assert kwargs["params"]["state"] == "NC"

    def test_get_lat_lon_empty(self):
        """Test get_lat_lon with empty data"""
        location = {"postal_code": "", "city": "", "state": ""}
        result = self.loc_service.get_lat_lon(location)
        assert result == {}

    @patch("requests.get")
    def test_show_lat_lon(self, mock_get):
        """Test show_lat_lon method"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "lat": "35.9132",
                "lon": "-79.0558",
                "display_name": "27516, Chapel Hill, Orange County, North Carolina, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Set up the location in our service
        self.loc_service.loc = {"postal_code": "27516", "city": "", "state": ""}

        # Call show_lat_lon
        result = self.loc_service.show_lat_lon()

        # Verify the result matches expected behavior
        assert "lat" in result
        assert "lon" in result

    @patch("requests.get")
    def test_api_error_handling(self, mock_get):
        """Test API error handling"""
        # Mock the API response for an empty result
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Should return empty dict when no results
        location = {"postal_code": "00000", "city": "", "state": ""}
        result = self.loc_service.get_lat_lon(location)
        assert result == {}

    @patch("requests.get")
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        # Mock a connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

        # Should return empty dict on exception
        location = {"postal_code": "27516", "city": "", "state": ""}
        result = self.loc_service.get_lat_lon(location)
        assert result == {}
