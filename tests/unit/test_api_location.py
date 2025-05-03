import requests
import json

# Test data
test_list = []
test_data = {"city": "Cary", "state": "NC", "postal_code": ""}
test_list.append(test_data)


test_data = {"city": "Cary", "state": "NC", "postal_code": "27513"}
test_list.append(test_data)

test_data = {"city": "", "state": "NC", "postal_code": "27513"}
test_list.append(test_data)

# Send the request
for test_data in test_list:
    print(f"Testing with data: {test_data}")
    # Send the request
    response = requests.post(
        "http://127.0.0.1:5000/api/location",
        headers={"Content-Type": "application/json"},
        json=test_data,
    )

    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Response body: {json.dumps(response.json(), indent=2)}")
