import requests  # Import the requests library to make HTTP requests

# Define a test function that will be automatically discovered by pytest
def test_load_search_api():
    """
    Load Test: Send multiple POST requests to the /search API endpoint
    and assert that each response returns a 200 OK status.
    """

    # Set the URL of the API endpoint to test
    url = "http://127.0.0.1:5000/search"

    # Define the JSON payload to send in the body of each POST request
    payload = {"city": "Cary"}

    # Set the number of requests to send in the load test
    num_requests = 10

    # Loop to send multiple requests
    for i in range(num_requests):
        # Send a POST request with the payload
        response = requests.post(url, json=payload)

        # Print the result of each request (helpful for real-time monitoring)
        print(f"Request {i+1}: Status Code = {response.status_code}")

        # Assert that the response status code is 200 (OK)
        # If not, the test will fail and display which request failed
        assert response.status_code == 200, f"Request {i+1} failed with status code {response.status_code}"

