import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

# lat, lon = 41.905965, 12.482790  # spaish steps
lat, lon = 32.228513, 34.916937  # mishmeret
# lat, lon = 41.902301, 12.453113  # vatican
url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=650&key={api_key}"
response = requests.get(url).json()
results_500 = response["results"]

# url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=1000&key={api_key}"
# response = requests.get(url).json()
# results_1000 = response["results"]


utl2 = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={response['next_page_token']}&key={api_key}"
response = requests.get(url).json()
results_1000_2 = response["results"]

f_res_500 = [
    (r["name"], r["plus_code"]["compound_code"][8:], r["user_ratings_total"])
    for r in results_500
    if r.get("user_ratings_total", 0) > 500
]
f_res_1000 = [
    (r["name"], r["plus_code"]["compound_code"][8:], r["user_ratings_total"])
    for r in results_1000
    if r.get("user_ratings_total", 0) > 500
]
query = (
    f"You're a helpful and informative chatbot. You like talking about history and the location you clients are. \n"
    f"You like to answer them in 3 paragraph answers.\n"
    f"After the last paragraph suggest follow-up questions in bullet format. \n"
    f"\n"
    f"Your client's question is the following:\n"
    f"I'm currently near {f_res_500[0][0]} in {f_res_500[0][1]} \n"
    f"I'm also near {' and '.join(r[0] for r in f_res_500[1:])} but they are not as important. \n"
    f"In 1 km vicinity there are {' and '.join(r[0] for r in f_res_1000[1:])}.\n"
    f"Can you tell me more about where I am? "
)

print(query)
