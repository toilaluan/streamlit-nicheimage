import streamlit as st
import base64
import io
import random
import time
from typing import List
from PIL import Image
import aiohttp
import asyncio
from streamlit_image_select import image_select
import requests
import streamlit as st
import requests
import zipfile
import io
import pandas as pd
from core import *
from utils import icon
from streamlit_image_select import image_select
from PIL import Image
import random
import time
import base64
from typing import List
import aiohttp
import asyncio
import plotly.express as px
from common import set_page_container_style

replicate_text = "NicheImage - Subnet 23 - Bittensor"
replicate_logo = "assets/NicheTensorTransparent.png"
replicate_link = "https://github.com/NicheTensor/NicheImage"

st.set_page_config(
    page_title="NicheImage Generator", page_icon=replicate_logo, layout="wide"
)
set_page_container_style(
    max_width=1100,
    max_width_100_percent=True,
    padding_top=0,
    padding_right=10,
    padding_left=5,
    padding_bottom=10,
)


def fetch_GoJourney(task_id):
    endpoint = "https://api.midjourneyapi.xyz/mj/v2/fetch"
    data = {"task_id": task_id}
    response = requests.post(endpoint, json=data)
    return response.json()


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


# UI configurations
st.markdown(
    """<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 2rem;}
</style>

""",
    unsafe_allow_html=True,
)
css = """
<style>
section.main > div:has(~ footer ) {
    padding-bottom: 5px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# API Tokens and endpoints from `.streamlit/secrets.toml` file
API_TOKEN = st.secrets["API_TOKEN"]
# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()


def configure_sidebar() -> None:
    """
    Setup and display the sidebar elements.

    This function configures the sidebar of the Streamlit application,
    including the form for user inputs and the resources section.
    """
    with st.sidebar:
        st.image(replicate_logo, use_column_width=True)
        with st.form("my_form"):
            prompt = st.text_area(
                ":blue[**Enter prompt ✍🏾**]",
                value="a beautiful flower under the sun --ar 16:9",
            )
            with st.expander(
                "📚 Advanced",
                expanded=False,
            ):
                uid = st.text_input("Specify an UID", value="-1")
                secret_key = st.text_input("Enter secret key", value="")
                seed = st.text_input("Seed", value="-1")
            # The Big Red "Submit" Button!
            submitted = st.form_submit_button(
                "Submit", type="primary", use_container_width=True
            )

        return (
            submitted,
            prompt,
            uid,
            secret_key,
            seed,
        )


def main_midjourney(submitted, prompt, uid, secret_key, seed):
    data = {
        "key": "capricorn_feb",
        "prompt": prompt,
        "model_name": "GoJourney",
    }
    print(data)
    if submitted:
        with st.status(
            "👩🏾‍🍳 Whipping up your words into art...", expanded=True
        ) as status:
            try:
                if submitted:
                    with generated_images_placeholder.container():
                        loop = get_or_create_eventloop()
                        asyncio.set_event_loop(loop)
                        output = requests.post(
                            "http://127.0.0.1:10002/generate", json=data
                        )
                        output = output.json()
                        print(output)
                        task_id = output["task_id"]
                        task_response = fetch_GoJourney(task_id)
                        task_status = task_response["status"]
                        if task_status == "failed":
                            status.update(label="Task failed", state="error")
                            return
                        while True:
                            task_response = fetch_GoJourney(task_id)
                            if task_response["status"] == "finished":
                                status.update(label="Task finished", state="complete")
                                img_url = task_response["task_result"]["image_url"]
                                st.image(
                                    img_url, use_column_width=True, output_format="PNG"
                                )
                                st.json(task_response)
                                break
                            else:
                                status.update(
                                    label=f"Task is still processing - {task_response['status']} - {task_response['meta']['task_request']['process_mode']}",
                                    state="running",
                                )
                            time.sleep(2)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()


def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    The main page function then generates images based on these inputs.
    """
    (
        submitted,
        prompt,
        uid,
        secret_key,
        seed,
    ) = configure_sidebar()
    main_midjourney(
        submitted,
        prompt,
        uid,
        secret_key,
        seed,
    )
    if not submitted:
        with generated_images_placeholder.container():
            st.image(
                "https://img.midjourneyapi.xyz/mj/a4a88dfe-4e68-4ff3-8ab1-85a4c2ee5792.png",
                use_column_width=True,
            )


if __name__ == "__main__":
    main()
