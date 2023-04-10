import os
import sys

import streamlit as st
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from dotenv import load_dotenv
from streamlit_bokeh_events import streamlit_bokeh_events
from streamlit_js_eval import get_geolocation

from PIL import Image  # noqa

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa
from common.google_maps.gmaps_place import extract_places_in_area  # noqa

load_dotenv()


def generate_prompt(lat, lon):
    """Generates a prompt for the chatbot."""
    sort_by_rating = lambda l: sorted(l, key=lambda p: p.user_ratings_total, reverse=True)
    all_500 = extract_places_in_area(lat, lon, 500)
    rel_500 = sort_by_rating(p for p in all_500 if p.user_ratings_total > 50)
    all_500 = sort_by_rating(all_500.difference(rel_500))

    rel_1000 = {p for p in (extract_places_in_area(lat, lon, 1000)) if p.user_ratings_total > 100}
    rel_1000 = sort_by_rating(rel_1000.difference(rel_500))

    st.write(str(rel_1000))
    st.write(str(rel_500))
    # rel_5000 = {p for p in (extract_places_in_area(lat, lon, 5000)) if p.user_ratings_total > 200}
    # rel_5000 = sort_by_rating(rel_5000.difference(rel_500).difference(rel_1000))
    all_locs = rel_500 + rel_1000 + all_500
    if len(all_locs) == 0:
        return "I'm sorry, I don't know anything about this area. Please try again later."

    curr_loc = all_locs[0]
    query = (
        f"Disregard previous conversations and text, and answer according to the following rules:\n\n"
        f" * You're a helpful and informative tour guide. You like talking about history and give recommendation. \n"  # noqa
        f" * You should focus more location in the client's immediate vicinity. \n"
        f" * You answer them in 3 paragraph answers.\n"
        f" * Keep writing follow-up questions in markdown bullet format throughout the conversation.\n"
        f"The questions should not include restaurant/cafe or require knowledge that you don't have.\n"  # noqa
        f"\n"
        f"Your client's question is the following: \n\n "
        f"I'm currently near {curr_loc}. \n"
        + (
            f"Also in the area there are {' and '.join(p.to_str(curr_loc) for p in rel_500[1:])}. \n\n"
            if len(rel_500) > 1
            else ".\n\n"
        )
        + (
            f"In 1 km vicinity there are {' and '.join(p.to_str(curr_loc) for p in rel_1000)}.\n\n"
            if len(rel_1000) > 0
            else ""
        )
        # + (f"In 5 km vicinity there are {' and '.join(str(p) for p in rel_5000)}.\n\n" if len(rel_5000) > 0 else "")
        + f"Can you tell me more about where I am?"
    )
    # st.write(rel_5000)

    return query


def main() -> None:
    image = Image.open(os.path.join(os.path.dirname(__file__), "chatbot.png"))
    st.set_page_config(page_title="AI Tour Guide", page_icon=image)
    st.title("AI Tour Guide Prompt Generator!")
    st.write("Click the below to copy your query to the chatbot, then paste the query into ChatGPT:")
    # lat, lon = 41.905965, 12.482790  # spanish steps
    # lat, lon = 32.228513, 34.916937  # mishmeret
    # lat, lon = 41.902301, 12.453113  # vatican

    location = get_geolocation()
    if location is not None:
        lat, lon = location["coords"]["latitude"], location["coords"]["longitude"]
        st.write((lat, lon))
        query = generate_prompt(lat, lon)

        copy_button = Button(label=f"Copy query")
        copy_button.js_event_callbacks = {}  # for it to refresh    clipboardData.setData('text/plain', 'foo')
        copy_button.js_on_event(
            "button_click", CustomJS(args=dict(), code=f"""navigator.clipboard.writeText("{repr(query)[1:-1]}");""")
        )
        no_event = streamlit_bokeh_events(
            copy_button, events="GET_TEXT", key="get_text", refresh_on_update=True, override_height=40, debounce_time=0
        )
        copy_button.update()

        st.markdown(
            f"""
        <div style="text-align:center">
        <a href="https://chat.openai.com/chat/5225db55-319d-4c45-af16-39b056588b41" align="center" target="_blank"><button style="background-color:GreenYellow;">To ChatGPT</button></a>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("""---""")
        st.subheader("Query Text:")
        st.markdown(query)
    else:
        st.error("No location")


if __name__ == "__main__":
    main()
