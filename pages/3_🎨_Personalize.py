import streamlit as st
import base64
import io
import random
import time
from typing import List
from PIL import Image
import aiohttp
import asyncio
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
replicate_logo = "https://nichetensor.com/wp-content/uploads/2024/04/cropped-NicheTensor_logo_transparent.png"
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
            model_name = st.selectbox(
                ":blue[**Select Model**]",
                options=["DreamShaperXL"],
            )
            prompt = st.text_area(
                ":blue[**Enter prompt ✍🏾**]",
                value="Studio Ghibli, soft colors, whimsical style, hand-drawn, highly detailed",
            )
            aspect_ratio = "1:1"
            conditional_image = st.file_uploader(
                ":blue[**Upload your image that contains face**]",
                type=["png", "jpg", "jpeg"],
                help="Upload an image to condition the generation",
            )
            pose_image = st.file_uploader(
                ":blue[**Upload your image that contains pose**]",
                type=["png", "jpg", "jpeg"],
                help="Upload an image to condition the generation",
            )

            if conditional_image:
                st.image(conditional_image)
            if pose_image:
                st.image(pose_image)
            
            ip_adapter_scale = st.slider(
                ":blue[**IP Adapter Scale**]",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.1,
                help="The scale of the IP Adapter",
            )

            controlnet_scale = st.slider(
                ":blue[**ControlNet Scale**]",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.1,
                help="The scale of the ControlNet",
            )

            num_images = 4
            negative_prompt = st.text_area(
                ":blue[**Negative Prompt 🙅🏽‍♂️**]",
                value="low quality, blurry, pixelated, noisy, low resolution, defocused, out of focus, overexposed, bad image, nsfw",
                help="This is a negative prompt, basically type what you don't want to see in the generated image",
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
            model_name,
            prompt,
            negative_prompt,
            aspect_ratio,
            num_images,
            uid,
            secret_key,
            seed,
            conditional_image,
            ip_adapter_scale,
            controlnet_scale,
            pose_image
        )


async def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    The main page function then generates images based on these inputs.
    """
    (
        submitted,
        model_name,
        prompt,
        negative_prompt,
        aspect_ratio,
        num_images,
        uid,
        secret_key,
        seed,
        conditional_image,
        ip_adapter_scale,
        controlnet_scale,
        pose_image
    ) = configure_sidebar()
    if conditional_image:
        conditional_image = Image.open(conditional_image)
        conditional_image = pil_image_to_base64(conditional_image)
    if pose_image:
        pose_image = pil_image_to_base64(Image.open(pose_image))
    await main_page(
        submitted,
        model_name,
        prompt,
        negative_prompt,
        aspect_ratio,
        num_images,
        uid,
        secret_key,
        seed,
        conditional_image,
        controlnet_scale,
        "instantid",
        API_TOKEN,
        generated_images_placeholder,
        ip_adapter_scale,
        pose_image
    )
    if not submitted:
        with generated_images_placeholder.container():
            st.info("🎨 Upload your face image and imagine the possibilities!")
            st.write("Original repo: https://github.com/InstantID/InstantID")
            st.image("https://github.com/InstantID/InstantID/blob/main/assets/compare-c.png?raw=true", use_column_width=True)


if __name__ == "__main__":
    asyncio.run(main())
