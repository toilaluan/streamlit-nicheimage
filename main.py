import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import copy
import streamlit.components.v1 as components

st.set_page_config(page_title="SN23 Dashboard", layout="wide")

st.markdown(
    """
    <div align="center" style="color: blue">

# **SocialTensor Subnet** <!-- omit in toc -->
    [![Discord Chat](https://img.shields.io/badge/bittensor-discord-green?logo=discord)](https://discord.com/channels/799672011265015819/1191833510021955695)]
    [![Github](https://img.shields.io/badge/nicheimage-github-blue?logo=github)](https://github.com/SocialTensor/SocialTensorSubnet)]

---

## Decentralized AI Detection <!-- omit in toc -->  

### [🌐 Website](https://its-ai.streamlit.app/)  
### [⛏️ Mining Docs](docs/mining.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[🧑‍🏫 Validating Docs](docs/validating.md) 
### [🗺 Vision & Roadmap](docs/vision_and_roadmap.md)  

</div>
    <H1 style='text-align: center; color: blue'>
    # SocialTensor Subnet <!-- omit in toc -->  

    ---
    </H1>
    """,
     unsafe_allow_html=True
)
tabs = st.tabs(["Dashboard", "Playground"])

with tabs[0]:
    VALID_UIDS = ["202", "0", "178", "232", "28", "242", "78", "228", "17", "133", "200"]
    model_incentive_weight = {
        'AnimeV3': 0.20, 
        'JuggernautXL': 0.15, 
        'RealitiesEdgeXL': 0.20, 
        'Gemma7b': 0.03, 
        'StickerMaker': 0.03, 
        'FaceToMany': 0.00, 
        'Kolors': 0.10, 
        'FluxSchnell': 0.12, 
        'DreamShaperXL': 0.00, 
        'Llama3_70b': 0.05, 
        'GoJourney': 0.04, 
        'SUPIR': 0.08
    }
    COLOR_MAP = {
        'AnimeV3': "#1f77b4", 
        'JuggernautXL': "#ff7f0e", 
        'RealitiesEdgeXL': "#2ca02c", 
        'Gemma7b': "#d62728", 
        'StickerMaker': "#9467bd", 
        'FaceToMany': "#8c564b", 
        'Kolors': "#e377c2", 
        'FluxSchnell': "#bcbd22", 
        'DreamShaperXL': "#7f7f7f", 
        'Llama3_70b': "#f7b6d2", 
        'GoJourney': "#17becf", 
        'SUPIR': "#c5b0d5",
        "": "#ffffcc"
    }
    
    st.markdown(
        """
        > **NicheImage is a decentralized network of image generation models, powered by the Bittensor protocol. Below you find information about the current models on the network.**
        """,
        unsafe_allow_html=True,
    )

    def get_total_volumes(miner_info_data):
        VALIDATOR_UID = 202
        model_volumes = {}
        model_counts = {}
        info = miner_info_data[str(VALIDATOR_UID)]["info"]
        for uid, metadata in info.items():
            if metadata["model_name"].strip():
                if metadata["model_name"] not in model_volumes:
                    model_volumes[metadata["model_name"]] = 0
                if metadata["model_name"] not in model_counts:
                    model_counts[metadata["model_name"]] = 0
                model_volumes[metadata["model_name"]] += metadata["total_volume"]
                model_counts[metadata["model_name"]] += 1
        return model_volumes, model_counts

    if "stats" not in st.session_state:
        response = requests.get("http://nichestorage.nichetensor.com:10000/get_miner_info")
        response = response.json()
        st.session_state.stats = response


    all_validator_response = st.session_state.stats
    model_volumes, model_counts = get_total_volumes(all_validator_response)
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

    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]], subplot_titles=("Model Distribution", "Emission Distribution"))
    # Plot Model Distribution
    fig.add_trace(
        go.Pie(
            values=list(model_distribution.values()),
            labels=list(model_distribution.keys()),
            marker=dict(colors=[COLOR_MAP[model] for model in model_distribution.keys()])
        ),
        row=1, col=1
    )
    # Plot Emission Distribution
    fig.add_trace(
        go.Pie(
            values=list(model_incentive_weight.values()),
            labels=list(model_incentive_weight.keys()),
            marker=dict(colors=[COLOR_MAP[model] for model in model_incentive_weight.keys()])
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Distribution",
        width=1000,
        showlegend=True
    )
    st.plotly_chart(fig)

    # Plot volume of models
    models = list(model_volumes.keys())
    volumes = [x * 6 * 24 for x in list(model_volumes.values())]
    organic_volumes = [x * 0.8 for x in volumes]
    volume_per_miners = [volumes[i] / model_counts[model] for i,model in enumerate(models)]
    volume_per_percentage_emission = [volumes[i] / (model_incentive_weight[model] * 100)  if model_incentive_weight[model] > 0 else 0 for i,model in enumerate(models)]
    total_volume = sum(volumes)
    volumes += [total_volume]
    organic_volumes += [sum(organic_volumes)]
    volume_per_miners += [total_volume / sum(model_counts.values())]
    volume_per_percentage_emission += [total_volume / 100] 

    models += ["<b>Total</b>"]
    formatted_volumes = [f"{volume:,.0f}" for volume in organic_volumes]
    formatted_volumes[-1] = f"<b>{formatted_volumes[-1]}</b>"
    formatted_volume_per_miners = [f"{c:,.2f}" for c in volume_per_miners]
    formatted_volume_per_miners[-1] = f"<b>{formatted_volume_per_miners[-1]}</b>"
    formatted_volume_per_percentage_emission = [f"{c:,.2f}" for c in volume_per_percentage_emission]
    formatted_volume_per_percentage_emission[-1] = f"<b>{formatted_volume_per_percentage_emission[-1]}</b>"

    table = go.Figure(data=[go.Table(
        header=dict(values=["Model", "Generations Per Day*", "Average Volume Per Miner", "Average Volume Per Percentage Emission"],
                    fill_color='#4d79ff',
                    font=dict(color='white', size=16),
                    align='center'),
        cells=dict(
            values=[models, formatted_volumes, formatted_volume_per_miners, formatted_volume_per_percentage_emission],
            fill_color=[['#f0f8ff']*(len(model_volumes)) + ['#d9e6ff'],
                        ['#e6f2ff']*(len(model_volumes)) + ['#d9e6ff'],
                        ['#e6f2ff']*(len(model_volumes)) + ['#d9e6ff'],
                        ['#e6f2ff']*(len(model_volumes)) + ['#d9e6ff']],
            align=['left', 'right', 'right', 'right'], 
            font=dict(color='black', size=14),
            height=30 
        ),
        columnwidth=[25, 25, 25, 25]
    )])

    table.update_layout(
        height=30 * (len(models) + 4),
        width=1000,
        margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins for better title positioning
    )
    st.plotly_chart(table)
    st.markdown(
        "<div style='width:1000px;'><p style='font-size:12px; font-style:italic;'>*Generations per day are calculated by taking the total volume miners say they can generate, and multiply with 0.8, since validators by default utilize about 80% of their available volume of generation.</p></div>",
        unsafe_allow_html=True
    )


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

    # plot overall chart
    overall_data = copy.deepcopy(response["info"])
    for uid, inf in overall_data.items():
        inf["scores"] = [f"{x:.4f}"for x in inf["scores"]]
        inf["scores"] = ", ".join(inf["scores"])
        inf["success_rate"] = f"{inf['success_rate']:.2f}"
        inf["mean_process_time"] = f"{inf['mean_process_time']:.2f}"
    pd_data = pd.DataFrame(overall_data).T
        
    st.markdown("**Total Information**", unsafe_allow_html=True)
    st.dataframe(pd_data,
        width=1200,
        column_order = ("model_name", "scores", "total_volume", "success_rate", "mean_process_time", "reward_scale", "rate_limit", "device_info"),
        column_config = {
            "scores": st.column_config.ListColumn(
                "Scores",
            ),
            "model_name": st.column_config.TextColumn(
                "Model"
            ),
            "total_volume": st.column_config.ProgressColumn(
                "Volume",
                format="%f",
                min_value=0,
                max_value=1000,
            ),
            "success_rate": st.column_config.ProgressColumn(
                "Success Rate",
                format="%f",
                min_value=0,
                max_value=1
            ),
            "reward_scale": st.column_config.NumberColumn(
                "Reward Scale"
            ),
            "mean_process_time": st.column_config.NumberColumn(
                "Mean Process Time"
            ),
            "rate_limit": st.column_config.NumberColumn(
                "Rate Limit"
            ),
            "device_info": st.column_config.TextColumn("Device Info"),
        })

    # plot N bar chart for N models, sorted by mean score
    for model in model_distribution.keys():
        model_data = transformed_dict[transformed_dict["model_name"] == model]
        model_data = model_data.sort_values(by="mean_score", ascending=False)
        model_data.uid = model_data.uid.astype(str)
        if model_data.mean_score.sum() == 0:
            continue
        fig = go.Figure(data=[go.Bar(x=model_data.uid, y=model_data.mean_score,
                hovertext=[f"Total volume {volume} - {str(device_info)}" for volume, device_info in zip(model_data.total_volume, model_data.device_info)], marker_color='lightsalmon')])
        fig.update_layout(title_text=f"Model: {model}", xaxis_title="UID", yaxis_title="Mean Score", width=1200)
        
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
            width=1200
        )
        st.plotly_chart(fig)

with tabs[1]:
    components.iframe("https://app.nichetensor.com", height=1024)