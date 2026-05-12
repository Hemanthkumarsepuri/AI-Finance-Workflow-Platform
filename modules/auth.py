import streamlit as st

from config import (

    ROLE_EMPLOYEE,

    ROLE_MANAGER,

    ROLE_FINANCE
)

# =========================================================
# USERS
# =========================================================

USERS = {

    "employee": {

        "password": "emp123",

        "role": ROLE_EMPLOYEE
    },

    "manager": {

        "password": "mgr123",

        "role": ROLE_MANAGER
    },

    "finance": {

        "password": "fin123",

        "role": ROLE_FINANCE
    }
}

# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_session():

    if "logged_in" not in st.session_state:

        st.session_state.logged_in = False

    if "username" not in st.session_state:

        st.session_state.username = ""

    if "role" not in st.session_state:

        st.session_state.role = ""

    if "uploader_key" not in st.session_state:

        st.session_state.uploader_key = 0

# =========================================================
# LOGIN SCREEN
# =========================================================

def login_screen():

    st.subheader(
        "Login"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username in USERS:

            if USERS[username]["password"] == password:

                st.session_state.logged_in = True

                st.session_state.username = username

                st.session_state.role = USERS[username]["role"]

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Password"
                )

        else:

            st.error(
                "Invalid Username"
            )

# =========================================================
# SIDEBAR
# =========================================================

def sidebar_logout():

    st.sidebar.success(
        f"Logged in as: {st.session_state.username}"
    )

    st.sidebar.info(
        f"Role: {st.session_state.role}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False

        st.session_state.username = ""

        st.session_state.role = ""

        st.rerun()