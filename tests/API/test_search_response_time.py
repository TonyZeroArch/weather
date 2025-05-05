import requests

def test_search_api_response_time():
    """
    Performance Test: Ensure the /search API responds within 2 seconds (2000 ms).
    """

    url = "http://127.0.0.1:5000/search"
    payload = {"city": "Cary"}

    # Send a single POST request and record the time
    response = requests.post(url, json=payload)

    # Calculate response time in milliseconds
    response_time_ms = response.elapsed.total_seconds() * 1000

    # Print the response time for visibility
    print(f"Response Time: {response_time_ms:.2f} ms")

    # Assert that the response time is less than or equal to 2000 milliseconds
    assert response_time_ms <= 2000, f"Response time too slow: {response_time_ms:.2f} ms (limit: 2000 ms)"

    # Also check that the API returns a successful 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
