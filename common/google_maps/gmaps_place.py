import os
from typing import Dict

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
api_key = os.getenv('api_key')
logger.debug(f"API key - {api_key}")


class GooglePlace:
    def __init__(self, result: Dict):
        self.name = result["name"]
        self.addr = result.get('plus_code', {'compound_code': ""})['compound_code'][8:]
        self.user_ratings_total = result.get('user_ratings_total', 0)
        self.types = result.get('types', [])

    def __str__(self):
        return f"{self.name} in {self.addr} is of type ({', '.join(t.replace('_', ' ') for t in self.types)})"  # with {self.total_user_ratings} ratings"


def extract_places_in_area(lat, lon, radius):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&key={api_key}"
    response = requests.get(url).json()
    return [GooglePlace(r) for r in response["results"]]
