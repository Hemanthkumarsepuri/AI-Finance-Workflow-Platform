import streamlit as st

# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_session():

    default_values = {

        "logged_in": False,

        "user_id": None,

        "employee_id": "",

        "employee_name": "",

        "email": "",

        "role": "",

        "department": "",

        "project_name": "",

        "manager_employee_id": "",

        "delivery_manager_employee_id": "",

        "uploader_key": 0
    }

    for key, value in default_values.items():

        if key not in st.session_state:

            st.session_state[key] = value

# =========================================================
# LOGIN SCREEN
# =========================================================

def login_screen(

    session,

    User
):

    st.subheader(
        "Enterprise Login"
    )

    username = st.text_input(
        "Employee ID / Username"
    )

    password = st.text_input(

        "Password",

        type="password"
    )

    if st.button(
        "Login"
    ):

        # =================================================
        # USER VALIDATION
        # =================================================

        user = session.query(
            User
        ).filter_by(
            employee_id=username
        ).first()

        # =================================================
        # DEMO PASSWORD STRATEGY
        # =================================================
        # Temporary:
        # employee_id acts as password
        #
        # Future:
        # LDAP / OAuth / SSO / Azure AD
        # =================================================

        if user:

            if password == user.employee_id:

                # =========================================
                # SESSION ENRICHMENT
                # =========================================

                st.session_state.logged_in = True

                st.session_state.user_id = user.id

                st.session_state.employee_id = (
                    user.employee_id
                )

                st.session_state.employee_name = (
                    user.employee_name
                )

                st.session_state.email = (
                    user.email
                )

                st.session_state.role = (
                    user.role
                )

                st.session_state.department = (
                    user.department
                )

                st.session_state.project_name = (
                    user.project_name
                )

                st.session_state.manager_employee_id = (
                    user.manager_employee_id
                )

                st.session_state.delivery_manager_employee_id = (
                    user.delivery_manager_employee_id
                )

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
                "Invalid Employee ID"
            )

# =========================================================
# SIDEBAR
# =========================================================

def sidebar_logout():

    st.sidebar.success(
        f"""
Logged in as:
{st.session_state.employee_name}
        """
    )

    st.sidebar.info(
        f"""
Role:
{st.session_state.role}
        """
    )

    st.sidebar.info(
        f"""
Project:
{st.session_state.project_name}
        """
    )

    st.sidebar.info(
        f"""
Department:
{st.session_state.department}
        """
    )

    # =====================================================
    # HIERARCHY VISIBILITY
    # =====================================================

    if st.session_state.manager_employee_id:

        st.sidebar.caption(
            f"""
Manager:
{st.session_state.manager_employee_id}
            """
        )

    if st.session_state.delivery_manager_employee_id:

        st.sidebar.caption(
            f"""
Delivery Manager:
{st.session_state.delivery_manager_employee_id}
            """
        )

    # =====================================================
    # LOGOUT
    # =====================================================

    if st.sidebar.button(
        "Logout"
    ):

        session_keys = list(
            st.session_state.keys()
        )

        for key in session_keys:

            del st.session_state[key]

        st.rerun()

# =========================================================
# USER SEEDING
# =========================================================
# Creates demo enterprise hierarchy users.
#
# Run once during app startup if users missing.
# =========================================================

def seed_demo_users(

    session,

    User
):

    existing_users = session.query(
        User
    ).count()

    if existing_users > 0:

        return

    demo_users = [

        User(

            employee_id="EMP1001",

            employee_name="Rahul Employee",

            email="rahul@company.com",

            role="employee",

            department="Engineering",

            project_name="Cloud Migration",

            manager_employee_id="MGR2001",

            delivery_manager_employee_id="DM3001"
        ),

        User(

            employee_id="MGR2001",

            employee_name="Priya Manager",

            email="priya@company.com",

            role="Manager",

            department="Engineering",

            project_name="Cloud Migration",

            manager_employee_id="DM3001",

            delivery_manager_employee_id="DM3001"
        ),

        User(

            employee_id="DM3001",

            employee_name="Arun Delivery Manager",

            email="arun@company.com",

            role="Delivery Manager",

            department="Engineering",

            project_name="Cloud Migration"
        ),

        User(

            employee_id="FIN4001",

            employee_name="Finance Admin",

            email="finance@company.com",

            role="Finance Admin",

            department="Finance",

            project_name="Finance Governance"
        )
    ]

    session.add_all(
        demo_users
    )

    session.commit()