import requests
import streamlit as st
from streamlit_timeline import st_timeline
import time, datetime
import json, requests
import plotly.graph_objs as go
from datetime import timedelta


# For test
# URL_GET_MINER_TIMELINE = "http://20.62.195.114:8000/get_miner_timeline"
# URL_GET_MINER_INFO = "http://20.62.195.114:8000/get_miner_info"
# VALID_UIDS = [str(x) for x in range(256)]
# DEFAULT_VALIDATOR_UID = 1

# For production
URL_GET_MINER_TIMELINE = "http://nichestorage.nichetensor.com:10000/get_miner_timeline"
URL_GET_MINER_INFO = "http://nichestorage.nichetensor.com:10000/get_miner_info"
VALID_UIDS = ["0", "202", "232", "242", "133", "132", "228", "28", "121"]
DEFAULT_VALIDATOR_UID = 202

LST_MODEL_NAMES = ["GoJourney", "AnimeV3", "JuggernautXL", "RealitiesEdgeXL", "DreamShaperXL", "Gemma7b", "Llama3_70b","FaceToMany", "StickerMaker", "DallE"]
st.set_page_config( layout="wide")

timeline_miner_info, validator_data = {}, []


def get_miner_timeline(validator_id, miner_id):

    json_data = {
        'validator_uid': int(validator_id),
        'miner_uid': int(miner_id),
    }

    response = requests.post(URL_GET_MINER_TIMELINE, json=json_data)
    result = response.json()
    return result

def plot_timeline_chart(dates, values, miner_data):
    if len(values) > 0:
        scores = [float(x) for x in values]
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='Scores'))

        fig.update_layout(
            title=f"Timeline scores of miner {miner_data['uid']} (model {miner_data.get('model_name','')})",
            xaxis_title='Date',
            yaxis_title='Score',
            xaxis=dict(
                tickformat='%H:%M:%S',
                tickangle=-45,
                # tickvals=[date + timedelta(minutes=10) for date in dates]
            ),
            yaxis=dict(
                range=[min(scores) - 0.01, max(scores) + 0.01]
            ),
            width=1200
        )

        st.plotly_chart(fig)
    

def get_miner_info_timeline():
    global timeline_miner_info
    try:
        response = requests.get(URL_GET_MINER_INFO)
        data = response.json()
        timeline_miner_info = data
        st.session_state.timeline_miner_info = timeline_miner_info
    except Exception as ex:
        print("[ERROR] Fetch data: ", str(ex))
        
get_miner_info_timeline()

st.session_state.timeline_miner_info = timeline_miner_info
all_validator_response = st.session_state.timeline_miner_info 
all_validator_response = {k: v for k, v in all_validator_response.items() if str(k) in VALID_UIDS}
validator_uids = list(all_validator_response.keys())

validator_uids = sorted([int(uid) for uid in validator_uids])
validator_select = st.selectbox(
    "Select a validator",
    validator_uids,
    index=validator_uids.index(DEFAULT_VALIDATOR_UID)
)
validator_select = str(validator_select)
validator_data = all_validator_response[validator_select]

model_select = st.selectbox(
    "Select a model",
    LST_MODEL_NAMES,
    index=None
)

miner_uids = [int(k) for k,v  in validator_data.get("info", {}).items() if v["model_name"].strip() and (model_select is None  or v["model_name"]==model_select)]
if len(miner_uids) > 0:
    miner_select = st.selectbox(
        "Select a miner",
        miner_uids,
        index=miner_uids.index(miner_uids[0])
    )


    all_scores = []
    miner_result = {}
    miner_data = get_miner_timeline(validator_id=validator_select, miner_id=miner_select)
    miner_data["uid"] = miner_select

    ### Use st_timeline ###
    # chart_data = []
    # for i,d in enumerate(miner_data.get("timeline_score", [])):
    #     dt_object = datetime.datetime.fromtimestamp(d["time"])
    #     formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    #     chart_data.append({
    #         "id": i + 1, 
    #         "content": str(d["reward"]), 
    #         "start": formatted_date
    #     })
    # timeline = st_timeline(chart_data, groups=[], options={}, height="300px")
    # st.subheader(f"Timeline scores of miner {miner_select} (model {miner_data.get('model_name','')})")
    # st.write(timeline)

    ### Use plotly ###
    plt_chart_data = []
    for i,d in enumerate(miner_data.get("timeline_score", [])):
        dt_object = datetime.datetime.fromtimestamp(d["time"])
        formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        plt_chart_data.append({
            "score": str(d["reward"]), 
            "time": dt_object
        })


    plot_timeline_chart([x["time"] for x in plt_chart_data], [x["score"] for x in plt_chart_data], miner_data)


