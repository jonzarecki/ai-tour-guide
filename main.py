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
    all_500 = extract_places_in_area(lat, lon, 500)
    rel_500 = [p for p in all_500 if p.user_ratings_total > 30]
    rel_1000 = [p for p in (extract_places_in_area(lat, lon, 1000)) if p.user_ratings_total > 50]
    rel_10000 = [p for p in (extract_places_in_area(lat, lon, 10000)) if p.user_ratings_total > 100]

    query = (
        f"Disregard previous conversations, and answer according to the following rules:\n\n"
        f" * You're a helpful and informative chatbot. You like talking about history and the locations you clients are. \n"
        f" * You should focus more on locations nearer to your client than those farther away.\n"
        f" * You like to answer them in 3 paragraph answers.\n"
        f" * After the last paragraph suggest follow-up questions in markdown bullet format. \n"
        f" * Keep asking follow-up questions throughout the conversation. \n"
        f""
        f"\n"
        f"Your client's question is the following: \n\n "
        + (f"I'm currently near {all_500[0]}" if len(all_500) > 0 else "")
        + (f"and {rel_500[0]}" if len(rel_500) > 0 else "")
        + (
            f". \n" f"I'm also near {' and '.join(str(p) for p in rel_500)} but they are not as important. \n\n"
            if len(rel_500) > 1
            else ""
        )
        + (f"In 1 km vicinity there are {' and '.join(str(p) for p in rel_1000)}.\n\n" if len(rel_1000) > 0 else "")
        + (f"In 10 km vicinity there are {' and '.join(str(p) for p in rel_10000)}.\n\n" if len(rel_1000) > 0 else "")
        + f"Can you tell me more about where I am? "
    )

    return query


def main() -> None:
    image = Image.open(os.path.join(os.path.dirname(__file__), "chatbot.png"))
    st.set_page_config(page_title="AI Tour Guide", page_icon=image)
    st.title("AI Tour Guide Prompt Generator!")
    st.write("Click the below to copy your query to the chatbot, " "the paste the query into ChatGPT:")
    # lat, lon = 41.905965, 12.482790  # spaish steps
    # lat, lon = 32.228513, 34.916937  # mishmeret
    # lat, lon = 41.902301, 12.453113  # vatican

    location = get_geolocation()
    if location is not None:
        lat, lon = location["coords"]["latitude"], location["coords"]["longitude"]
        st.write((lat, lon))
        query = generate_prompt(lat, lon)

        copy_button = Button(label=f"Copy query")
        copy_button.js_event_callbacks = {}  # for it to refresh
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
