import requests
import time
from bs4 import BeautifulSoup

# URL of the page
url = "https://www.nseindia.com/reports-indices-historical-index-data"

# Send GET request
response = requests.get(url)

if response.status_code == 429:
    wait = int(response.headers.get("Retry-After", 5))
    time.sleep(wait)

# Parse with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Print raw HTML
print(soup.prettify())   # formatted HTML
# OR
# print(str(soup))       # raw HTML without formatting