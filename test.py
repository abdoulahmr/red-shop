import requests
import json

# Define the URL for the API route
url = 'https://redshop.pythonanywhere.com/api/add-order'  # Replace with your actual host and port if different

# Create the order data
order_data = {
    "product_id": 1,            # Replace with the actual product ID
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main Street",
    "quantity": 2,
    "phone_number": "1234567890"
}

# Send the POST request to the API route
response = requests.post(url, json=order_data)

# Print the status code
print(f"Status Code: {response.status_code}")

# Try to get the response as JSON, if possible
try:
    response_json = response.json()
    print(f"Response: {response_json}")
except requests.exceptions.JSONDecodeError:
    # If the response is not JSON, print the raw text
    print("Response is not in JSON format.")
    print(f"Raw Response: {response.text}")
