import streamlit as st
import os
import requests

st.set_page_config(page_title="ClauseBreaker", page_icon="⚖️", layout="wide")

st.title("⚖️ ClauseBreaker")
st.write("App is running!")
st.write(f"Host: {os.environ.get('DATABRICKS_HOST', 'NOT SET')[:30]}")

user_input = st.text_input("Ask something:")
send = st.button("Send")

if send and user_input:
    st.write(f"You said: {user_input}")