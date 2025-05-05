""" 
This test sets the service's internal location to a known postal code (27511),
    invokes get_lat_lon (which uses s_type=0 for postal lookup), and asserts that:
      - the result is non-empty,
      - latitude (“lat”) and longitude (“lon”) keys are present,
      - the returned postal_code matches the input,
      - city and state fields are populated.

    This ensures that the postal‑code search path in LocService processes Nominatim
    responses correctly and maps components into the expected output structure.
"""

import pytest

def test_postal_code_lookup(loc_service):
    # Arrange: set the service’s loc and expected postal_code
    loc_service.loc = {"postal_code":"27511","city":"","state":""}
    # Act: call get_lat_lon which uses s_type=0
    result = loc_service.get_lat_lon(loc_service.loc)
    # Assert: structure & specific fields
    assert result, "Expected non-empty result dict"
    assert "lat" in result and "lon" in result
    assert result["postal_code"] == "27511"
    assert result["city"], "City should be populated"  # non-empty :contentReference[oaicite:5]{index=5}
    assert result["state"], "State should be populated"

