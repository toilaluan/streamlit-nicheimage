import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

VALID_UIDS = ["202", "0", "178", "232", "28", "242", "78", "228", "17", "133", "200"]
st.set_page_config(page_title="NicheImage Studio", layout="wide")
st.markdown("## :blue[Image Generation Studio by NicheImage]")
replicate_logo = "https://i.ibb.co/rdspnnK/Screenshot-2024-08-01-at-10-54-37.png"
st.markdown(
    """
    **NicheImage is a decentralized network of image generation models, powered by the Bittensor protocol. Below you find information about the current models on the network.**
    """,
    unsafe_allow_html=True,
)

def get_total_volumes(miner_info_data):
    VALIDATOR_UID = 202
    model_volumes = {}
    info = miner_info_data[str(VALIDATOR_UID)]["info"]
    for uid, metadata in info.items():
        if metadata["model_name"].strip():
            if metadata["model_name"] not in model_volumes:
                model_volumes[metadata["model_name"]] = 0
            model_volumes[metadata["model_name"]] += metadata["total_volume"]

    return model_volumes

tabs = st.tabs(["Dashboard", "Timeline Score"])
with st.sidebar:
    st.image(replicate_logo, use_column_width=True)
with tabs[0]:
    if "stats" not in st.session_state:
        response = requests.get("http://nichestorage.nichetensor.com:10000/get_miner_info")
        response = response.json()
        st.session_state.stats = response


    all_validator_response = st.session_state.stats
    model_volumes = get_total_volumes(all_validator_response)
    all_validator_response = {k: v for k, v in all_validator_response.items() if str(k) in VALID_UIDS}
    validator_uids = list(all_validator_response.keys())
    validator_uids = [int(uid) for uid in validator_uids]
    validator_uids = sorted(validator_uids)
    print(validator_uids)
    validator_select = st.selectbox(
        "Select a validator",
        validator_uids,
        index=validator_uids.index(202)
    )
    validator_select = str(validator_select)
    response = all_validator_response[validator_select]
    # Plot distribution of models
    model_distribution = {}
    for uid, info in response["info"].items():
        model_name = info["model_name"]
        model_distribution[model_name] = model_distribution.get(model_name, 0) + 1
    fig = px.pie(
        values=list(model_distribution.values()),
        names=list(model_distribution.keys()),
        title="Model Distribution",
    )
    st.plotly_chart(fig)

    # Plot volume of models
    models = list(model_volumes.keys()) + ["Total Generations per Day"]
    volumes = [x * 6 * 24 for x in list(model_volumes.values())]
    total_volume = sum(volumes)
    volumes += [total_volume]
    formatted_volumes = [f"{volume:,}" for volume in volumes]

    
    table = go.Figure(data=[go.Table(
        header=dict(values=["Model", "Volume per day"],
                    fill_color='#4d79ff',
                    font=dict(color='white', size=14),
                    align='center'),
        cells=dict(
            values=[models, formatted_volumes],
            fill_color=[['#f0f8ff']*(len(model_volumes)) + ['#d9e6ff'],
                        ['#e6f2ff']*(len(model_volumes)) + ['#d9e6ff']],
            align=['left', 'right'], 
            font=dict(color='black', size=12),
            height=30 
        )
    )])

    table.update_layout(
        height=30 * (len(models) + 4),
        title_text='Total Registered Volume per day',
        title_x=0,
        margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins for better title positioning
    )
    
    st.plotly_chart(table)

    transformed_dict = []
    for k, v in response["info"].items():
        if "process_time" in v:
            process_time = [x for x in v["process_time"] if x >0]
            mean_process_time = sum(process_time) / len(process_time) if len(process_time) > 0 else 0
            success_rate = len(process_time) / len(v["process_time"]) if len(v["process_time"]) > 0 else 1
        else:
            process_time = []
            success_rate = 1
            mean_process_time = 0
        transformed_dict.append(
            {
                "uid": k,
                "model_name": v["model_name"],
                "mean_score": (
                    sum(v["scores"]) / 10
                ),
                "total_volume": v["total_volume"] if  v.get("total_volume") else 0,
                "device_info": v.get("device_info", {}),
                "mean_process_time": mean_process_time,
                "success_rate": success_rate
            }
        )
        
        response["info"][k]["mean_process_time"] = mean_process_time
        response["info"][k]["success_rate"] = success_rate

    transformed_dict = pd.DataFrame(transformed_dict)
    # plot N bar chart for N models, sorted by mean score
    for model in model_distribution.keys():
        model_data = transformed_dict[transformed_dict["model_name"] == model]
        model_data = model_data.sort_values(by="mean_score", ascending=False)
        model_data.uid = model_data.uid.astype(str)
        if model_data.mean_score.sum() == 0:
            continue
        fig = go.Figure(data=[go.Bar(x=model_data.uid, y=model_data.mean_score,
                hovertext=[f"Total volume {volume} - {str(device_info)}" for volume, device_info in zip(model_data.total_volume, model_data.device_info)], marker_color='lightsalmon')])
        fig.update_layout(title_text=f"Model: {model}", xaxis_title="UID", yaxis_title="Mean Score")
        
        fig.update_layout(
            xaxis=dict(type="category"),
        )
        st.plotly_chart(fig)
        
        # Plot process time and success rate chart
        df = pd.DataFrame(model_data)
        fig = px.scatter(df, x="mean_process_time", y="success_rate", 
                hover_data=["uid", "model_name", "mean_score"],
                size="total_volume", color="uid"
            )
        fig.update_layout(
            xaxis_title="Mean Process Time (seconds)",
            yaxis_title="Success Rate",
            xaxis=dict(range=[0, df["mean_process_time"].max() * 1.1]),
            yaxis=dict(range=[0, 1.1]),
            legend_title="UID",
        )
        st.plotly_chart(fig)


    pd_data = pd.DataFrame(response["info"])
    st.markdown(
        """
        **Total Information**
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(pd_data.T)

# with tabs[1]:
#     import requests
#     import streamlit as st
#     from streamlit_timeline import st_timeline
#     import time, datetime
#     import json, requests
#     import plotly.graph_objs as go
#     from datetime import timedelta

#     URL_GET_MINER_TIMELINE = "http://nichestorage.nichetensor.com:10000/get_miner_timeline"
#     URL_GET_MINER_INFO = "http://nichestorage.nichetensor.com:10000/get_miner_info"
#     VALID_UIDS = ["0","1", "202", "232", "242", "133", "132", "228", "28", "121", "200"]
#     DEFAULT_VALIDATOR_UID = "202"

#     def get_miner_timeline(validator_id, miner_id):

#         json_data = {
#             'validator_uid': int(validator_id),
#             'miner_uid': int(miner_id),
#         }

#         response = requests.post(URL_GET_MINER_TIMELINE, json=json_data)
#         result = response.json()
#         return result

#     def plot_timeline_chart(dates, values, miner_data):
#         if len(values) > 0:
#             scores = [float(x) for x in values]
#             fig = go.Figure()

#             fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='Scores'))

#             fig.update_layout(
#                 title=f"Timeline scores of miner {miner_data['uid']} (model {miner_data.get('model_name','')})",
#                 xaxis_title='Date',
#                 yaxis_title='Score',
#                 xaxis=dict(
#                     tickformat='%Y-%m-%d %H:%M:%S',
#                     tickangle=-45,
#                     # tickvals=[date + timedelta(minutes=10) for date in dates]
#                 ),
#                 yaxis=dict(
#                     range=[min(scores) - 0.01, max(scores) + 0.01]
#                 ),
#                 width=1200
#             )

#             st.plotly_chart(fig)
        

#     def get_miner_info_timeline():
#         global timeline_miner_info
#         try:
#             response = requests.get(URL_GET_MINER_INFO)
#             data = response.json()
#             timeline_miner_info = data
#             st.session_state.timeline_miner_info = timeline_miner_info
#         except Exception as ex:
#             print("[ERROR] Fetch data: ", str(ex))

#     validator_select = st.selectbox(
#         "Select a validator",
#         VALID_UIDS,
#         index=VALID_UIDS.index(DEFAULT_VALIDATOR_UID)
#     )
#     validator_select = str(validator_select)

#     miner_uids = [int(x) for x in range(256)]
#     miner_select = st.selectbox(
#         "Select a miner",
#         miner_uids,
#         index=miner_uids.index(miner_uids[0])
#     )
#     all_scores = []
#     miner_result = {}
#     miner_data = get_miner_timeline(validator_id=validator_select, miner_id=miner_select)
#     miner_data["uid"] = miner_select

#     plt_chart_data = []
#     for i,d in enumerate(miner_data.get("timeline_score", [])):
#         dt_object = datetime.datetime.fromtimestamp(d["time"])
#         formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
#         print(f"Score: {d['reward']} - Time: {formatted_date}")
#         plt_chart_data.append({
#             "score": str(d["reward"]), 
#             "time": str(formatted_date)
#         })


#     plot_timeline_chart([x["time"] for x in plt_chart_data], [x["score"] for x in plt_chart_data], miner_data)



