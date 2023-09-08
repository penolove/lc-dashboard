import os

import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, DataReturnMode
import plotly.express as px

st.set_page_config(layout="wide")

GS_SHEET_ID = os.environ.get(
    "GS_SHEET_ID", "1wADT0jfyHTXAcu5WK3Sa3KGKWaoCwcFZ_sCQqR2XZrY"
)

QUESTION_TAG_GID = os.environ.get("QUESTION_TAG_GID", "1858914435")


@st.cache_data(ttl=86400)
def get_records():
    return pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{GS_SHEET_ID}/export?format=csv"
    )


df = get_records()
df["ts"] = pd.to_datetime(df["ts"], unit="s")

# user id setting
params = st.experimental_get_query_params()

user_ids = list(set(df["name"]))
if params.get("name"):
    user_id_query_idx = user_ids.index(params.get("name")[0])
else:
    user_id_query_idx = 0

user_id = st.sidebar.selectbox(
    "pick your id compare with others",
    user_ids,
    user_id_query_idx,
    help="leetcode id that wanna analysis",
)

st.write(f"Analyze user_id: {user_id} with competition records")

target_user_df = df[df["name"] == user_id]
st.dataframe(target_user_df)


if_filter = st.sidebar.toggle(
    "filter df?",
    help="if this toggled, then the stat will only calculated on filtered records",
)
st.caption(
    "as filter is toggled, filter will affect the percentile calculation, try to filter with country=US"
)
if if_filter:
    df_tmp = AgGrid(
        df,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        height=300,
        width="100%",
    )["data"]
    df_tmp["ts"] = pd.to_datetime(df_tmp["ts"])
    df = pd.concat(
        [target_user_df, df_tmp[df_tmp["name"] != user_id]], axis=0
    ).reset_index(drop=True)
else:
    AgGrid(
        df,
        fit_columns_on_grid_load=True,
        height=300,
        width="100%",
    )

stat = df.groupby(["competition"]).agg(
    ts=("ts", "min"),
    one_percent_rank=("rank", lambda x: x.quantile(0.01)),
    twenty_five_rank=("rank", lambda x: x.quantile(0.25)),
    fifty_rank=("rank", lambda x: x.quantile(0.5)),
    seventy_five_rank=("rank", lambda x: x.quantile(0.75)),
    n_candidates=("ts", "count"),
)

is_calculate_competitors = st.sidebar.toggle(
    "If suggest competitors?",
    help="will pick k candidates who's percentile most close to you",
)
if is_calculate_competitors:
    n_competitors = st.sidebar.number_input(
        "number of competitors?", min_value=1, max_value=10, value=3
    )
    min_competitions = st.sidebar.number_input(
        "minimum number of competition attended?", min_value=1, max_value=10, value=3
    )

is_analysis_questions = st.sidebar.toggle(
    "If analysis your pass rate with question tags",
    help="will using tagged question tag to calculate your pass rate",
)

if user_id:
    person_score = df[df["name"] == user_id][
        ["name", "rank", "competition", "percentile"]
    ]

    # calculate most close competitors
    if is_calculate_competitors:
        user_median = person_score["percentile"].median()
        candidates = df.groupby("name").agg(
            {"percentile": "median", "competition": "count"}
        )
        candidates = candidates[
            (candidates["competition"] >= min_competitions)
            & (candidates.index != user_id)
        ]
        candidates["diff"] = (candidates["percentile"] - user_median).abs()
        suggest_competitors = set(
            candidates.nsmallest(n_competitors, "diff").index
        ) - set([user_id])

    else:
        suggest_competitors = None

    # pick competitors
    competitors = st.multiselect(
        "select competitors", set(df["name"]), suggest_competitors
    )
    # add competitor into dataframe
    for competitor in competitors:
        competitor_score = df[df["name"] == competitor][["rank", "competition"]]
        competitor_score.columns = [competitor, "competition"]
        person_score = person_score.merge(
            competitor_score, on="competition", how="outer"
        )

    merged_result = person_score.merge(stat, on=["competition"])
    available_lines = [
        "one_percent_rank",
        "twenty_five_rank",
        "fifty_rank",
        "seventy_five_rank",
    ] + competitors
    merged_result.sort_values("ts", inplace=True)

    # draw lines
    fig = px.line(
        merged_result[["ts", "rank"] + available_lines],
        x="ts",
        y=["rank"] + available_lines,
        markers=True,
    )

    for selected_line in available_lines:
        fig.update_traces(selector={"name": selected_line}, line={"dash": "dash"})

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    # show metrics you compare to others
    st.write(user_id)
    for row in merged_result.iterrows():
        user_rank, score_1, score_25, score_50, score_75 = (
            row[1]["rank"],
            row[1]["one_percent_rank"],
            row[1]["twenty_five_rank"],
            row[1]["fifty_rank"],
            row[1]["seventy_five_rank"],
        )
        if np.isnan(user_rank):
            continue
        col0, col1, col2, col3, col4 = st.columns(5)
        with col0:
            st.write(row[1]["competition"])
            st.write(user_rank)
        col1.metric(f"compare with 1%:", round(score_1), f"{score_1-user_rank}")
        col2.metric(f"compare with 25%:", round(score_25), f"{score_25-user_rank}")
        col3.metric(f"compare with 50%:", round(score_50), f"{score_50-user_rank}")
        col4.metric(f"compare with 75%:", round(score_75), f"{score_75-user_rank}")

    # analysis your question tag
    if is_analysis_questions:
        st.header("question tag analysis")
        person_score = df[df["name"] == user_id][["competition", "passed_questions"]]
        attended_competitions = set(person_score["competition"])
        person_score["question_id"] = person_score["passed_questions"].str.split(",")
        person_score = person_score.explode("question_id")
        person_score["is_pass"] = True

        question_tag = pd.read_csv(
            f"https://docs.google.com/spreadsheets/d/{GS_SHEET_ID}/export?format=csv&gid={QUESTION_TAG_GID}",
            dtype={"question_id": "str"},
        )
        question_tag = question_tag[
            (~question_tag.level.isna())
            & question_tag["competition"].isin(attended_competitions)
        ]

        submissions = question_tag.merge(
            person_score, on=["competition", "question_id"], how="left"
        )
        submissions["is_pass"].fillna(False, inplace=True)

        st.dataframe(
            submissions[
                ["title", "is_pass", "level", "tag1", "tag2", "competition", "link"]
            ],
            column_config={"link": st.column_config.LinkColumn("link-of-problem")},
        )

        st.write("level analysis")
        level_df = submissions.groupby("level").agg(
            {"is_pass": ["mean", "count", "sum"]}
        )
        level_df.columns = ["pass-ratio", "# of questions", "# passed"]
        st.dataframe(level_df)

        st.write("tags analysis")
        tmp_df2 = submissions[["tag2", "is_pass"]]
        tmp_df2.columns = ["tags", "is_pass"]
        tmp_df1 = submissions[["tag1", "is_pass"]]
        tmp_df1.columns = ["tags", "is_pass"]
        tag_df = (
            pd.concat([tmp_df1, tmp_df2])
            .groupby("tags")
            .agg({"is_pass": ["mean", "count", "sum"]})
        )
        tag_df.columns = ["pass-ratio", "# of questions", "# passed"]
        st.dataframe(tag_df)
