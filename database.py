import os
from supabase import create_client, Client
import streamlit as st


def get_supabase() -> Client:
    # Works both locally (.env) and on Streamlit Cloud (st.secrets)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)
