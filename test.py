"""App testing script"""

import requests
import os

from dotenv import load_dotenv

load_dotenv()

URL = f"http://localhost:{os.getenv('APP_PORT')}/query"
QUERY = ("Top five easiest recipes under 10 minutes")
DATA = {'query': QUERY}

response = requests.post(URL, json=DATA)

print(response.json())
