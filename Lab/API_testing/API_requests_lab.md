## Lab 1: API Testing with Python requests & Pytest
-------
### Objective
Verify that LocService.get_lat_lon returns correct structure and values for both postal‑code and city/state lookups against the Nominatim API.

-----

### Tools Used
- **Language:** Python 3.8+

- **HTTP Client:** requests library 

- **Test Runner:** Pytest 


- **Service Under Test:** LocService calling Nominatim’s /search endpoint from Flask-based weather app.
--------

### Lab Setup
**1. Clone the repository to your local machine.**
**2. Create and activate venv**
```
python3 -m venv venv
source venv/bin/activate
```
**3. Install dependencies**
```
pip install pytest requests
```

**4.  Install requirements.txt**
```
pip install requirements.txt
```
------

### Test Implementation

**1. Postal‑code lookup**
```
# tests/test_postal_code_lookup.py
import pytest

def test_postal_code_lookup(loc_service):
    # Arrange: set the service’s loc and expected postal_code
    loc_service.loc = {"postal_code":"27511","city":"","state":""} # Change postal code as needed.
    # Act: call get_lat_lon which uses s_type=0
    result = loc_service.get_lat_lon(loc_service.loc)
    # Assert: structure & specific fields
    assert result, "Expected non-empty result dict"
    assert "lat" in result and "lon" in result
    assert result["postal_code"] == "27511" # Insert postal code here.
    assert result["city"], "City should be populated"  # non-empty :contentReference[oaicite:5]{index=5}
    assert result["state"], "State should be populated"
```

**2. City/State lookup**
```
# tests/test_city_state_lookup.py
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
```
-------------------------------------
#### Run & Validate
```
pytest
```
- You should see both tests pass, confirming that your LocService correctly handles both search modes.