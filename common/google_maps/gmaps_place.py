import os
from typing import Dict, Set

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
api_key = os.getenv("api_key")
logger.debug(f"API key - {api_key}")

good_place_types = [
    "airport",
    "amusement_park",
    "aquarium",
    "art_gallery",
    "campground",
    # 'casino', 'cemetery', 'church', 'city_hall',
    "courthouse",
    # 'hindu_temple',
    "library",
    # 'local_government_office',
    # 'mosque',
    "museum",
    "park",
    # 'rv_park',
    "shopping_mall",
    "stadium",
    # 'synagogue',
    "tourist_attraction",
    "train_station",
    "university",
    "zoo",
    "food",
    "landmark",
    "natural_feature",
    "place_of_worship",
    # 'point_of_interest',
    "town_square",
]
bad_place_types = [
    "restaurant",
    "store",
    "lodging",
    "bar",
    "cafe",
    "locality",
    "embassy",
    "school",
    "general_contractor",
]


class GooglePlace:
    def __init__(self, result: Dict):
        self.name = result["name"]
        self.addr = result.get("plus_code", {"compound_code": ""})["compound_code"][8:]
        self.user_ratings_total = result.get("user_ratings_total", 0)
        self.types = set(result.get("types", [])).difference(["point_of_interest", "establishment"])

    def __str__(self):
        return f"{self.name} in {self.addr}" + (
            f" of type ({', '.join(t.replace('_', ' ') for t in self.types)})" if len(self.types) > 0 else ""
        )  # noqa

    def __hash__(self):
        return hash(self.name)


def extract_places_in_area(lat, lon, radius, next_page_token=None, place_type=None) -> Set[GooglePlace]:
    if place_type is None and next_page_token is None:
        rel_types_places = set()
        return rel_types_places.union(
            *[extract_places_in_area(lat, lon, radius, place_type=t) for t in good_place_types]
        )

    next_pages_places: Set[GooglePlace] = set()
    if next_page_token is None:
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}"
            f"&language=en"
            f"&type={place_type}"
            f"&key={api_key}"
        )
        # f"&keyword=point\ of\ interest" \
        #               f"&type=establishment" \
        # f"&keyword=sarona+market" \
        # f"&type=town_square" \
        # f"&keyword=interesting" \
    else:
        logger.info(f"next_page_token: {next_page_token}")
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={api_key}"

    response = requests.get(url).json()
    if "next_page_token" in response:
        next_pages_places = (
            extract_places_in_area(lat, lon, radius, response["next_page_token"])
            if response["next_page_token"]
            else set()
        )

    places = [GooglePlace(r) for r in response["results"]]
    filtered_places = [
        p
        for p in places
        if len(p.types.intersection(good_place_types)) >= 0 and len(p.types.intersection(bad_place_types)) == 0
    ]
    logger.debug(f"({lat}, {lon}) in {radius}: {filtered_places[:3]}")
    logger.debug(url)
    return set(filtered_places).union(next_pages_places)
