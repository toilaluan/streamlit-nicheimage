import streamlit as st
from pymongo import MongoClient
import pandas as pd

MONGO_DB_HOST = st.secrets["MONGO_DB_HOST"]
MONGO_DB_PORT = st.secrets["MONGO_DB_PORT"]
MONGO_DB_USER = st.secrets["MONGO_DB_USER"]
MONGO_DB_PASS = st.secrets["MONGO_DB_PASS"]

mongo_client = MongoClient(
    "mongodb://%s:%s@%s:%s"
    % (MONGO_DB_USER, MONGO_DB_PASS, MONGO_DB_HOST, MONGO_DB_PORT)
)
db = mongo_client["nicheimage"]
image_collection = db["images"]
text_collection = db["texts"]
st.write(
    "**Below are sample of miners' responses from the NicheImage and NicheText databases.**"
)
tabs = st.tabs(["🌆 NicheImage", "📚 NicheText"])
with tabs[0]:
    st.title("🌆 NicheImage Database")
    model_name = st.selectbox(
        "Select Model",
        ["GoJourney", "StickerMaker", "FaceToMany"],
    )
    query = {"model_name": model_name}

    cursor = image_collection.find(query, limit=32)
    cursor.sort("_id", -1)
    n_row = 2
    count = 0
    cols = st.columns(n_row)
    for image in cursor:
        bucket_name = image["bucket"]
        object_key = image.get("jpg_key", image["key"])
        image_url = f"http://{bucket_name}.s3.amazonaws.com/{object_key}"
        cols[count % n_row].image(
            image_url, caption=image["prompt"], use_column_width=True
        )
        count += 1

with tabs[1]:
    st.title("📚 NicheText Database")
    model_name = st.selectbox("Select Model", ["Gemma7b", "Llama3_70b"])
    query = {"metadata.model_name": model_name}

    cursor = text_collection.find(query, limit=48)
    cursor.sort("_id", -1)
    data = []
    for text in cursor:
        prompt_input = text["prompt_input"]
        output = text["prompt_output"]["choices"][0]["text"]
        message = st.chat_message("user")
        message.write(prompt_input)
        message = st.chat_message("assistant")
        message.write(output)
