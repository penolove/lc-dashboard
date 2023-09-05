import time
import requests

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, DataReturnMode


# since global ranking is keep changing, I wanna show only the current status
# also in order speed up user experience, I will only track up to 1000 pages
def get_user_info(user):
    return {
        "user_name": user["username"],
        "countryCode": user["profile"]["countryCode"],
    }


@st.cache_data(ttl=86400)
def get_global_user_info(page_index):
    """
    parameters
    ----------
    page_index: int
        the page index of global ranking result

    returns
    -------
    user_ranking: pd.DataFrame
        a dataframe with columns:
        user_name, countryCode, ranking, currentRating, currentGlobalRanking, dataRegion
    """
    session = requests.Session()

    # get the csrftoken
    page = f"https://leetcode.com/contest/globalranking/{page_index}/"
    session.get(page)
    headers = {
        "x-csrftoken": session.cookies["csrftoken"],
        "referer": page,
    }

    body = """
    {
    globalRanking(page: page_index_) {
        rankingNodes {
        ranking
        currentRating
        currentGlobalRanking
        dataRegion
        user {
            username
            profile {
            countryCode
            }
        }
        }
    }
    }
    """.replace(
        "page_index_", str(page_index)
    )

    url = "https://leetcode.com/graphql"

    response = session.post(url=url, json={"query": body}, headers=headers)

    print("response status code: ", response.status_code)
    if response.status_code == 200:
        print("response : ", response.content)
    df = pd.DataFrame(response.json()["data"]["globalRanking"]["rankingNodes"])
    result = pd.concat(
        [
            pd.DataFrame(df["user"].apply(get_user_info).values.tolist()),
            df[["ranking", "currentRating", "currentGlobalRanking", "dataRegion"]],
        ],
        axis=1,
    )
    # avoid ddos
    time.sleep(0.025)
    return result


@st.cache_data(ttl=86400 * 3)
def get_user_latest_rating(user_id):
    """
    parameters
    ----------
    user_id: str
        the user id to fetch records

    returns
    -------
    user_rating: tuple
        user_id, rating, ranking
    """

    session = requests.Session()
    user_page = f"https://leetcode.com/{user_id}/"

    session.get(user_page)

    body = """
    {
        userContestRanking(username: "user_id_") {
            rating
            globalRanking
        }
    }
    """.replace(
        "user_id_", user_id
    )

    headers = {"x-csrftoken": session.cookies["csrftoken"], "referer": user_page}

    url = "https://leetcode.com/graphql"

    response = session.post(url=url, json={"query": body}, headers=headers)

    user_info = response.json()["data"]["userContestRanking"]
    # avoid ddos
    time.sleep(0.025)
    return (user_id, user_info["rating"], user_info["globalRanking"])


n_pages_to_fetch = st.sidebar.number_input(
    "number of pages?", min_value=100, max_value=1000, value=100
)

is_precise_mode = st.sidebar.toggle(
    "precise mode (while filtered user < 1000)",
    help="leetcode global ranking is not so precise, while you toggle this on and also the filter result < 1000, thus precise mode will be enabled",
)


bar = st.progress(0, text="Fetching global rank in progress. Please wait.")
df_list = []
for page_index in range(1, n_pages_to_fetch + 1):
    bar.progress(
        page_index / n_pages_to_fetch,
        text="Fetching global rank in progress. Please wait.",
    )
    df_list.append(get_global_user_info(page_index))

df = pd.concat(df_list)

df = AgGrid(
    df,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    height=500,
    width="100%",
    editable=True,
)["data"]

st.write("adding rank with filtered users:")

if is_precise_mode and df.shape[0] <= 1000:
    bar = st.progress(0, text="Fetching precise rating in progress. Please wait.")
    logs = []
    for idx, user_name in enumerate(df["user_name"]):
        bar.progress(
            (idx + 1) / len(df["user_name"]),
            text="Fetching precise rating in progress. Please wait.",
        )
        logs.append(get_user_latest_rating(user_name))

    precise_df = pd.DataFrame(
        logs,
        columns=["user_name", "currentRating", "currentGlobalRanking"],
    )
    df.drop("currentRating", axis=1, inplace=True)
    df.drop("currentGlobalRanking", axis=1, inplace=True)
    df = df.merge(precise_df, on="user_name")

df["rank"] = df["currentGlobalRanking"].rank()

st.dataframe(
    df,
    column_config={
        "ranking": st.column_config.LineChartColumn(
            "ranking trending plot (competition rank, lower better)",
        ),
    },
)
