import streamlit as st
from st_aggrid import AgGrid, DataReturnMode
import pandas as pd

st.set_page_config(layout="wide")

df = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/1wADT0jfyHTXAcu5WK3Sa3KGKWaoCwcFZ_sCQqR2XZrY/export?format=csv"
)
df["ts"] = pd.to_datetime(df["ts"], unit="s")

st.write("filter df:")
df = AgGrid(
    df,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    height=300,
    width="100%",
)["data"]

stat = df.groupby(["country", "competition"]).agg(
    ts=("ts", "min"),
    one_percent_rank=("rank", lambda x: x.quantile(0.01)),
    twenty_five_rank=("rank", lambda x: x.quantile(0.25)),
    fifty_rank=("rank", lambda x: x.quantile(0.5)),
    seventy_five_rank=("rank", lambda x: x.quantile(0.75)),
    n_candidates=("ts", "count"),
)

user_id = st.selectbox("pick your id compare with others", list(set(df["name"])))

person_score = df[df["name"] == user_id][["name", "rank", "competition", "percentile"]]

# pick suggest competitors
user_percentile = df.groupby("name").agg({"percentile": "median", "ts": "count"})
user_percentile = user_percentile[user_percentile["ts"] > 3]
user_percentile["diff"] = (
    user_percentile["percentile"] - person_score["percentile"].median()
).abs()
suggest_competitors = set(user_percentile.nsmallest(5, "diff").index) - set([user_id])
competitors = st.multiselect(
    "select competitors", set(user_percentile.index), suggest_competitors
)
# add competitor into dataframe
for competitor in competitors:
    competitor_score = df[df["name"] == competitor][["rank", "competition"]]
    competitor_score.columns = [competitor, "competition"]
    person_score = person_score.merge(competitor_score, on="competition", how="left")


merged_result = person_score.merge(stat, on=["competition"])
available_lines = [
    "one_percent_rank",
    "twenty_five_rank",
    "fifty_rank",
    "seventy_five_rank",
] + competitors
selected_lines = st.multiselect("available platforms", available_lines, available_lines)

# draw lines
st.line_chart(
    merged_result[
        (
            [
                "ts",
                "rank",
            ]
            + selected_lines
        )
    ],
    x="ts",
    y=["rank"] + selected_lines,
    height=500,
)

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
    col0, col1, col2, col3, col4 = st.columns(5)
    with col0:
        st.write(row[1]["competition"])
        st.write(user_rank)
    col1.metric(f"compare with 1%:", round(score_1), f"{score_1-user_rank}")
    col2.metric(f"compare with 25%:", round(score_25), f"{score_25-user_rank}")
    col3.metric(f"compare with 50%:", round(score_50), f"{score_50-user_rank}")
    col4.metric(f"compare with 75%:", round(score_75), f"{score_75-user_rank}")
