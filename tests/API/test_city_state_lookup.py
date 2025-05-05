"""
    Verify get_lat_lon returns the correct city and state for a city/state lookup.

    This test configures the LocService fixture with city “Raleigh” and state “NC”, 
    invokes get_lat_lon (s_type=1 for city/state), and asserts that:
      - the result dictionary is not empty,
      - the “city” field equals “Raleigh”,
      - the “state” field equals “NC”,
      - latitude and longitude values are parseable as floats.
"""

import pytest

def test_city_state_lookup(loc_service):
    # Arrange: city/state search_type=1
    loc_service.loc = {"postal_code":None,"city":"Raleigh","state":"NC"}
    # Act
    result = loc_service.get_lat_lon(loc_service.loc)
    # Assert
    assert result, "Expected non-empty result dict"
    assert result["city"] == "Raleigh"
    assert result["state"] == "NC"
    # lat/lon plausibility (strings convertible to floats)
    float(result["lat"])
    float(result["lon"])