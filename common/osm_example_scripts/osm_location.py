from typing import Dict

import requests

filters = ["road", "footway", "path",
           'highway', 'state_district', 'ISO3166-2-lvl4',
           'postcode', 'country_code', 'state',
           'county', 'ISO3166-2-lvl6', 'suburb', 'quarter']


class OSMLocation:
    def __init__(self, nominatim_response: Dict):
        self.place_id = nominatim_response['place_id']
        self.osm_id = nominatim_response['osm_id']
        self.localname = nominatim_response['localname']
        # self.name = nominatim_response['names'].get('name', None)
        self.importance = nominatim_response['importance']
        self.calculated_importance = nominatim_response['calculated_importance']
        self.rank_address = nominatim_response['rank_address']
        self.rank_search = nominatim_response['rank_search']
        self.address = nominatim_response['address']
        for address in nominatim_response['address']:
            if address.get('place_type') == 'city':
                self.city = address['localname']
            elif address.get('type') == 'country':
                self.country = address['localname']
        self.lon, self.lat = nominatim_response['centroid']['coordinates']

    def __repr__(self):
        return f"OSMLocation({self.lat}, {self.lon}, name={self.localname})"

    def __str__(self):
        return f"{self.localname} in the city {self.city} in {self.country}"

    @classmethod
    def from_osm_id(cls, osm_id) -> "OSMLocation":
        # Construct the search query URL
        url = f"https://nominatim.openstreetmap.org/details.php?osmtype=N&osmid={osm_id}&addressdetails=1&format=json"
        headers = {
            "accept-language": "en-US,en;q=0.9"
        }

        # Send the search query and get the response
        response = requests.get(url, headers=headers)

        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            res = response.json()
            return cls(res)
        else:
            return None

    @classmethod
    def from_node(cls, node):
        return cls.from_osm_id(node.id)
