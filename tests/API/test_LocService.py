import pytest
import requests
from unittest.mock import patch, Mock
from app.services.loc_api import LocService


class TestLocService:

    def setup_method(self):
        self.loc_service = LocService()

    def test_init(self):
        """Test initialization of LocService"""
        assert self.loc_service.loc == {
            "postal_code": None,
            "city": None,
            "state": None,
        }

    def test_validate_location_postal_code(self):
        """Test validation of postal code"""
        assert self.loc_service.validate_location("27516") == True
        assert self.loc_service.loc["postal_code"] == "27516"
        assert self.loc_service.loc["city"] is None
        assert self.loc_service.loc["state"] is None

    def test_validate_location_city_state(self):
        """Test validation of city,state"""
        assert self.loc_service.validate_location("Cary, NC") == True
        assert self.loc_service.loc["postal_code"] is None
        assert self.loc_service.loc["city"] == "Cary"
        assert self.loc_service.loc["state"] == "NC"

    def test_validate_location_invalid(self):
        """Test validation of invalid input"""
        assert self.loc_service.validate_location("invalid") == False
        assert self.loc_service.validate_location("Cary") == False
        assert self.loc_service.validate_location("Cary NC") == False  # Missing comma
        assert (
            self.loc_service.validate_location("Cary, North Carolina") == False
        )  # Full state name
        assert (
            self.loc_service.validate_location("1234") == False
        )  # Too short for postal code

    @patch("requests.get")
    def test_get_location_str_postal_code(self, mock_get):
        """Test get_location_str with postal code"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [{"lat": "35.9132", "lon": "-79.0558"}]
        mock_get.return_value = mock_response

        # Test with a postal code
        result = self.loc_service.get_location_str("27516")

        # Verify the result
        assert result == {"lat": "35.9132", "lon": "-79.0558"}

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["postalcode"] == "27516"
        assert kwargs["params"]["format"] == "json"

    @patch("requests.get")
    def test_get_location_str_city_state(self, mock_get):
        """Test get_location_str with city,state"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [{"lat": "35.7915", "lon": "-78.7811"}]
        mock_get.return_value = mock_response

        # Test with a city,state
        result = self.loc_service.get_location_str("Cary, NC")

        # Verify the result
        assert result == {"lat": "35.7915", "lon": "-78.7811"}

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["city"] == "Cary"
        assert kwargs["params"]["state"] == "NC"
        assert kwargs["params"]["format"] == "json"

    @patch("requests.get")
    def test_get_location_json_postal_code(self, mock_get):
        """Test get_location_json with postal code"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [{"lat": "35.9132", "lon": "-79.0558"}]
        mock_get.return_value = mock_response

        # Test with a postal code
        location = {"postal_code": "27516", "city": None, "state": None}
        result = self.loc_service.get_location_json(location)

        # Verify the result
        assert result == {"lat": "35.9132", "lon": "-79.0558"}

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["postalcode"] == "27516"
        assert kwargs["params"]["format"] == "json"

    @patch("requests.get")
    def test_get_location_json_city_state(self, mock_get):
        """Test get_location_json with city,state"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [{"lat": "35.2271", "lon": "-80.8431"}]
        mock_get.return_value = mock_response

        # Test with a city,state
        location = {"postal_code": None, "city": "Charlotte", "state": "NC"}
        result = self.loc_service.get_location_json(location)

        # Verify the result
        assert result == {"lat": "35.2271", "lon": "-80.8431"}

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["city"] == "Charlotte"
        assert kwargs["params"]["state"] == "NC"
        assert kwargs["params"]["format"] == "json"

    def test_get_location_json_empty(self):
        """Test get_location_json with empty data"""
        location = {"postal_code": None, "city": None, "state": None}
        result = self.loc_service.get_location_json(location)
        assert result == {}

    @patch("requests.get")
    def test_api_error_handling(self, mock_get):
        """Test API error handling"""
        # Mock the API response for an empty result
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # This should raise an IndexError when trying to access data[0]
        with pytest.raises(IndexError):
            location = {"postal_code": "00000", "city": None, "state": None}
            self.loc_service.get_location_json(location)

    @patch("requests.get")
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        # Mock a connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

        # This should propagate the exception
        with pytest.raises(requests.exceptions.ConnectionError):
            location = {"postal_code": "27516", "city": None, "state": None}
            self.loc_service.get_location_json(location)
