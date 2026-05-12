import streamlit as st

from config import (

    APP_TITLE,

    APP_LAYOUT,

    PRIMARY_COLOR,

    SECONDARY_COLOR,

    BACKGROUND_COLOR,

    SIDEBAR_COLOR
)

# =========================================================
# UI SETUP
# =========================================================

def setup_ui():

    st.set_page_config(

        page_title=APP_TITLE,

        layout=APP_LAYOUT
    )

    st.markdown(f"""

    <style>

    .main {{
        background-color: {BACKGROUND_COLOR};
    }}

    h1, h2, h3 {{
        color: {SECONDARY_COLOR};
    }}

    [data-testid="metric-container"] {{
        background-color: #111827;
        border: 1px solid #1E3A5F;
        padding: 15px;
        border-radius: 14px;
    }}

    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_COLOR};
    }}

    </style>

    """, unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

def render_header():

    st.markdown(f"""

    <div style="
    background: linear-gradient(90deg,#1E293B,#134E4A);
    padding:20px;
    border-radius:16px;
    margin-bottom:20px;
    ">

    <h1 style="
    color:white;
    text-align:center;
    ">

    {APP_TITLE}

    </h1>

    <p style="
    color:#CBD5E1;
    text-align:center;
    font-size:18px;
    ">

    AI-Powered Finance Workflow Automation Platform

    </p>

    </div>

    """, unsafe_allow_html=True)