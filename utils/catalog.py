import os
import requests

# Base URL for the API
# Production
#BASE_URL = "https://dados.gov.pt/api/1/site/catalog.xml"
# Preprod
BASE_URL = "https://preprod.dados.gov.pt/api/1/site/catalog.xml"
# Development
#BASE_URL = "https://172.31.204.12/api/1/site/catalog.xml"
# Test
#BASE_URL = "https://10.55.37.38/api/1/site/catalog.xml"

# Output file name
OUTPUT_FILE = os.path.join(os.getcwd(), "catalog.txt")

# Initialize page counter
page = 1

# Open the output file for writing
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    while True:
        try:
            # Construct the URL with the current page number
            url = f"{BASE_URL}?page={page}&tag=hvd"
            print(f"Fetching: {url}")

            # Make the HTTP GET request
            response = requests.get(url, verify=False)  # Disable SSL verification for this example

            # Check if the response status code indicates success
            if response.status_code == 404:
                print("Received status code 404. No more pages available. Stopping.")
                break

            if response.status_code != 200:
                print(f"Page {page} returned {response.status_code}. Skipping.")
                page += 1
                continue

            # Write the content of the current page to the output file
            file.write(response.text)

            # Increment the page number
            page += 1

        except requests.RequestException as e:
            # Handle network or request-related errors
            print(f"An error occurred: {e}")
            break

print("Fetching completed. Results saved in catalog.ttl.")
