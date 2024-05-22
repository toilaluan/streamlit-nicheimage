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
                options=[
                    "AnimeV3",
                    "RealitiesEdgeXL",
                    "DreamShaperXL",
                    "JuggernautXL",
                ],
            )
            prompt = st.text_area(
                ":blue[**Enter prompt ✍🏾**]",
                value="cinematic still of a shiba inu, fluffy neck, wearing a suit of ornate metal armor",
            )
            aspect_ratio = st.selectbox(
                ":blue[**Aspect Ratio**]", options=["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16"]
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
            "",
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
    ) = configure_sidebar()
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
        [],
        "txt2img",
        API_TOKEN,
        generated_images_placeholder,
    )
    if not submitted:
        with gallery_placeholder.container():
            with st.container():
                st.info(
                    "👩🏾‍🍳 :blue[**Juggernaut-X]"
                )
                st.balloons()
            with st.container(border=True):
                _ = image_select(
                    label="",
                    images=[
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/265d6db9-9bb4-40b9-b9f1-4404666effd7/width=1248/00078-beautiful%20lady,%20(freckles),%20big%20smile,%20brown%20hazel%20eyes,%20Full%20Bangs,%20dark%20makeup,%20hyperdetailed%20photography,%20soft%20light,%20head%20an.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c86d17eb-665d-454c-9066-69eb4f92768d/width=1248/00081-photograph,%20a%20path%20in%20the%20woods%20with%20leaves%20and%20the%20sun%20shining%20,%20by%20Julian%20Allen,%20dramatic%20autumn%20landscape,%20ears,%20park,%20take%20o.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/f8d6172e-fb2f-4152-af0f-e725fb0882cb/width=832/016216210EFBD7BBEE3F1D139A898EFDDDEDB7C4AFFB500D0AC6C892A91E045C.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d21f78d9-662d-419c-a38a-03a7260aac88/width=832/4AFCAF1B0AE99B392B2E1010D50885C749F595484232AF2724A0570ABDF6B142.jpeg",
                    ],
                    use_container_width=False,
                )
            with st.container():
                st.info(
                    "👩🏾‍🍳 :blue[**DreamShaperXL]"
                )
            with st.container(border=True):
                _ = image_select(
                    label="",
                    images=[
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/fb00718b-227c-462c-ad03-1371f63e3213/width=1224/31072150-554464390-In%20Casey%20Baugh's%20evocative%20style,%20art%20of%20a%20beautiful%20young%20girl%20cyborg%20with%20long%20brown%20hair,%20futuristic,%20scifi,%20intricate,%20elega.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d2d6d082-85ae-4cd5-a31e-ae6075e7e612/width=1224/31072152-3346112079-cinematic%20film%20still,%20close%20up,%20photo%20of%20redheaded%20girl%20near%20grasses,%20fictional%20landscapes,%20(intense%20sunlight_1.4),%20realist%20deta.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/83ef8f36-b054-4845-8b34-866a9a9e5184/width=1152/20240324050414%20745855931%20by%20Ian%20McQue%20and%20Sam%20Spratt,%20%20_lora_EnvyStudioPortraitXL01_0.35_%20,%20%20%20pointing%20a%20pistol%20_lora_pistol_0.60_.jpeg"
                    ],
                    use_container_width=False,
                )
            with st.container():
                st.info(
                    "👩🏾‍🍳 :blue[**AnimeV3]"
                )
            with st.container(border=True):
                _ = image_select(
                    label="",
                    images=[
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c788e346-7af1-4135-928a-c944634a4a51/original=true/Soldier.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/dc86e78e-7587-45b8-b709-b6f611af68fa/original=true/pirate%20(3).jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/cb6aa6c4-6cd6-4efd-84a8-4b3917ca4d24/original=true/00000-1761366536.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/61cad059-f9d8-446f-b33d-b22e078ac5fb/original=true/Scream.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/58d55973-12c9-4854-afbc-4fbd8f5434ef/original=true/CarSakura.jpeg",
                    ],
                    use_container_width=False,
                )
            with st.container():
                st.info(
                    "👩🏾‍🍳 :blue[**RealitiesEdgeXL]"
                )
            with st.container(border=True):
                _ = image_select(
                    label="",
                    images=[
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/7ae8de93-3634-4fb2-acb6-7ba66a630670/original=true/00044-3526680654.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d7a3e977-5433-46d0-82ba-4946386bd28e/original=true/00135-1518921975.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c3852385-4c73-4821-ac6f-b9f0323c7d6f/original=true/08323--3358745561.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/7f6be0cf-4b58-4c16-aa8f-4c396fb135b2/original=true/ComfyUI-1-_01583_.jpeg",
                        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/e9ecf8ad-8f3b-4fc3-9eca-c59389e84a3f/original=true/08314--1054985950.jpeg",
                    ],
                    use_container_width=False,
                )


if __name__ == "__main__":
    asyncio.run(main())
