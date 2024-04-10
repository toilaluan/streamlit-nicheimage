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


def main_page_sticker_maker(
    submitted: bool,
    model_name: str,
    prompt: str,
    api_token: str,
    generated_images_placeholder,
) -> None:
    """Main page layout and logic for generating images.

    Args:
        submitted (bool): Flag indicating whether the form has been submitted.
        width (int): Width of the output image.
        height (int): Height of the output image.
        num_inference_steps (int): Number of denoising steps.
        guidance_scale (float): Scale for classifier-free guidance.
        prompt_strength (float): Prompt strength when using img2img/inpaint.
        prompt (str): Text prompt for the image generation.
        negative_prompt (str): Text prompt for elements to avoid in the image.
    """
    if submitted:
        with st.status(
            "👩🏾‍🍳 Whipping up your words into art...", expanded=True
        ) as status:
            try:
                # Only call the API if the "Submit" button was pressed
                if submitted:
                    start_time = time.time()
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        all_images = []  # List to store all generated images
                        data = {
                            "key": api_token,
                            "prompt": prompt,  # prompt
                            "model_name": model_name,  # See avaialble models in https://github.com/NicheTensor/NicheImage/blob/main/configs/model_config.yaml
                            "seed": 0,  # -1 means random seed
                            "miner_uid": int(
                                -1
                            ),  # specify miner uid, -1 means random miner selected by validator
                            "pipeline_type": "txt2img",
                            "pipeline_params": {},
                        }
                        duplicate_data = [data.copy() for _ in range(4)]
                        # Call the NicheImage API
                        loop = get_or_create_eventloop()
                        asyncio.set_event_loop(loop)
                        output = loop.run_until_complete(
                            get_output(
                                "http://proxy_client_nicheimage.nichetensor.com:10003/generate",
                                duplicate_data,
                            )
                        )
                        print(output)
                        while len(output) < 4:
                            output.append(None)
                        for i, image in enumerate(output):
                            if not image:
                                output[i] = Image.new("RGB", (512, 512), (0, 0, 0))
                        print(output)
                        if output:
                            st.toast("Your image has been generated!", icon="😍")
                            end_time = time.time()
                            status.update(
                                label=f"✅ Images generated in {round(end_time-start_time, 3)} seconds",
                                state="complete",
                                expanded=False,
                            )

                            # Save generated image to session state
                            st.session_state.generated_image = output
                            captions = [f"Image {i+1} 🎈" for i in range(4)]
                            all_images = []
                            # Displaying the image
                            _, main_col, _ = st.columns([0.15, 0.7, 0.15])
                            with main_col:
                                cols_1 = st.columns(2)
                                cols_2 = st.columns(2)
                                with st.container(border=True):
                                    for i, image in enumerate(
                                        st.session_state.generated_image[:2]
                                    ):
                                        cols_1[i].image(
                                            image,
                                            caption=captions[i],
                                            use_column_width=True,
                                            output_format="PNG",
                                        )
                                        # Add image to the list
                                        all_images.append(image)
                                    for i, image in enumerate(
                                        st.session_state.generated_image[2:]
                                    ):
                                        cols_2[i].image(
                                            image,
                                            caption=captions[i + 2],
                                            use_column_width=True,
                                            output_format="PNG",
                                        )
                                        all_images.append(image)

                        # Save all generated images to session state
                        st.session_state.all_images = all_images
                        zip_io = io.BytesIO()
                        # Download option for each image
                        with zipfile.ZipFile(zip_io, "w") as zipf:
                            for i, image in enumerate(st.session_state.all_images):
                                image_data = io.BytesIO()
                                image.save(image_data, format="PNG")
                                image_data.seek(0)
                                # Write each image to the zip file with a name
                                zipf.writestr(
                                    f"output_file_{i+1}.png", image_data.read()
                                )
                        # Create a download button for the zip file
                        st.download_button(
                            ":red[**Download All Images**]",
                            data=zip_io.getvalue(),
                            file_name="output_files.zip",
                            mime="application/zip",
                            use_container_width=True,
                        )
                status.update(
                    label="✅ Images generated!", state="complete", expanded=False
                )
            except Exception as e:
                print(e)
                st.error(f"Encountered an error: {e}", icon="🚨")

    # If not submitted, chill here 🍹
    else:
        pass


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
    main_page_sticker_maker(
        submitted,
        "StickerMaker",
        prompt,
        API_TOKEN,
        generated_images_placeholder
    )
    if not submitted:
        with generated_images_placeholder.container():
            st.image(
                "https://img.midjourneyapi.xyz/mj/a4a88dfe-4e68-4ff3-8ab1-85a4c2ee5792.png",
                use_column_width=True,
            )


if __name__ == "__main__":
    main()
