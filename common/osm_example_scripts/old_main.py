import streamlit as st
import requests

def generate_prompt():
    st.write("You clicked the button!")

def get_locations(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"
    response = requests.get(url)
    data = response.json()

    # Get user's location
    user_location = []
    for item in data["address"]:
        if item not in ["road", "footway", "path"]:
            user_location.append(data["address"][item])
    user_location = ", ".join(user_location)

    # Get all nearby locations within 1 km
    url = f"https://nominatim.openstreetmap.org/search?format=jsonv2&q=&lat={lat}&lon={lon}&zoom=18&addressdetails=1&limit=10"
    response = requests.get(url)
    data = response.json()

    nearby_locations = []
    for item in data:
        location = []
        for component in item["address"]:
            if component not in ["road", "footway", "path"]:
                location.append(item["address"][component])
        location = ", ".join(location)
        if location != user_location:
            nearby_locations.append(location)

    return nearby_locations

def main():
    st.title("Welcome to my website!")
    st.write("Click the button below to proceed:")

    generate_prompt()
    lat = 32.229210 # Replace with user's latitude
    lon = 34.916866 # Replace with user's longitude
    locations = get_locations(lat, lon)
    st.write(f"Your location: {locations[0]}")
    st.write(f"Nearby locations within 1 km: {locations[1:]}")

if __name__ == "__main__":
    main()
