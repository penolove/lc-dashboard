import os

import streamlit as st

GS_SHEET_ID = os.environ.get("GS_SHEET_ID", "1wADT0jfyHTXAcu5WK3Sa3KGKWaoCwcFZ_sCQqR2XZrY")

st.header("Look at Leetcode dashboard, Set your goal.")


st.write("Hi, This is penolove,")
st.write(f"This app leetcode data source from a handy maintained google [sheet](https://docs.google.com/spreadsheets/d/{GS_SHEET_ID}/)")

st.write("Feel free to let me know any of your great idea via github [issues](https://github.com/penolove/lc-dashboard/issues).")