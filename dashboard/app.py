"""Live decision dashboard.   streamlit run dashboard/app.py"""
import os

import pandas as pd
import streamlit as st

PATH = "logs/decisions.jsonl"
st.set_page_config(page_title="Tripwire", layout="wide")
st.title("Tripwire: live decisions")
st.caption("Every tool call the agent proposes, the Decider answer, and what the cascade did.")

if not os.path.exists(PATH):
    st.info("No decisions yet. Run `python -m agent.demo` or `python -m agent.main`, then refresh.")
    st.stop()

df = pd.read_json(PATH, lines=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Decisions", len(df))
c2.metric("Allowed", int((df.action == "allow").sum()))
c3.metric("Blocked", int((df.action == "block").sum()))
c4.metric("Median Decider latency (ms)", round(float(df.latency_ms.median()), 1))

left, right = st.columns(2)
left.subheader("Lanes chosen")
left.bar_chart(df.lane.value_counts())
right.subheader("Final actions")
right.bar_chart(df.action.value_counts())

st.subheader("Latest decisions")
cols = ["user_message", "tool", "p_grounded", "p_injected", "confidence", "lane", "action", "reason"]
st.dataframe(df[cols].tail(50).iloc[::-1], use_container_width=True)
if st.button("Refresh"):
    st.rerun()
