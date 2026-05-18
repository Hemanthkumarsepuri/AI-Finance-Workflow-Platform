import pandas as pd
import streamlit as st

# =========================================================
# ENTERPRISE FILTER ENGINE
# =========================================================
# Supports:
# - Global search
# - Workflow filtering
# - AI governance filtering
# - SLA visibility
# - Operational intelligence
# - Enterprise analytics readiness
# =========================================================

def apply_invoice_filters(
    dataframe
):

    st.subheader(
        "Enterprise Search & Operational Filters"
    )

    if dataframe.empty:

        st.warning(
            "No invoice data available."
        )

        return dataframe

    filtered_df = dataframe.copy()

    # =====================================================
    # GLOBAL SEARCH
    # =====================================================

    search_text = st.text_input(

        "Global Search",

        placeholder="""
Search vendor, invoice, employee,
project, category, workflow...
        """
    )

    # =====================================================
    # FILTER LAYOUT
    # =====================================================

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # STATUS FILTER
    # =====================================================

    with col1:

        status_options = ["All"]

        if "Status" in filtered_df.columns:

            unique_status = sorted(

                filtered_df["Status"]
                .dropna()
                .astype(str)
                .unique()
            )

            status_options.extend(
                unique_status
            )

        selected_status = st.selectbox(

            "Approval Status",

            status_options
        )

    # =====================================================
    # BILL CATEGORY FILTER
    # =====================================================

    with col2:

        category_options = ["All"]

        if "Category" in filtered_df.columns:

            unique_categories = sorted(

                filtered_df["Category"]
                .dropna()
                .astype(str)
                .unique()
            )

            category_options.extend(
                unique_categories
            )

        selected_category = st.selectbox(

            "Bill Category",

            category_options
        )

    # =====================================================
    # WORKFLOW STAGE FILTER
    # =====================================================

    with col3:

        workflow_options = ["All"]

        if "Workflow Stage" in filtered_df.columns:

            unique_workflows = sorted(

                filtered_df["Workflow Stage"]
                .dropna()
                .astype(str)
                .unique()
            )

            workflow_options.extend(
                unique_workflows
            )

        selected_workflow = st.selectbox(

            "Workflow Stage",

            workflow_options
        )

    # =====================================================
    # SECOND ROW FILTERS
    # =====================================================

    col4, col5, col6 = st.columns(3)

    # =====================================================
    # EMPLOYEE FILTER
    # =====================================================

    with col4:

        employee_options = ["All"]

        if "Employee" in filtered_df.columns:

            unique_employees = sorted(

                filtered_df["Employee"]
                .dropna()
                .astype(str)
                .unique()
            )

            employee_options.extend(
                unique_employees
            )

        selected_employee = st.selectbox(

            "Employee",

            employee_options
        )

    # =====================================================
    # PROJECT FILTER
    # =====================================================

    with col5:

        project_options = ["All"]

        if "Project" in filtered_df.columns:

            unique_projects = sorted(

                filtered_df["Project"]
                .dropna()
                .astype(str)
                .unique()
            )

            project_options.extend(
                unique_projects
            )

        selected_project = st.selectbox(

            "Project",

            project_options
        )

    # =====================================================
    # SLA FILTER
    # =====================================================

    with col6:

        sla_options = ["All"]

        if "SLA Status" in filtered_df.columns:

            unique_sla = sorted(

                filtered_df["SLA Status"]
                .dropna()
                .astype(str)
                .unique()
            )

            sla_options.extend(
                unique_sla
            )

        selected_sla = st.selectbox(

            "SLA Status",

            sla_options
        )

    # =====================================================
    # THIRD ROW FILTERS
    # =====================================================

    col7, col8, col9 = st.columns(3)

    # =====================================================
    # AI RECOMMENDATION FILTER
    # =====================================================

    with col7:

        ai_options = ["All"]

        if "AI Recommendation" in filtered_df.columns:

            unique_ai = sorted(

                filtered_df["AI Recommendation"]
                .dropna()
                .astype(str)
                .unique()
            )

            ai_options.extend(
                unique_ai
            )

        selected_ai = st.selectbox(

            "AI Recommendation",

            ai_options
        )

    # =====================================================
    # DUPLICATE RISK FILTER
    # =====================================================

    with col8:

        risk_filter = st.selectbox(

            "Duplicate Risk",

            [

                "All",

                "High Risk",

                "Medium Risk",

                "Low Risk"
            ]
        )

    # =====================================================
    # SORTING
    # =====================================================

    with col9:

        sort_column = st.selectbox(

            "Sort By",

            filtered_df.columns.tolist()
        )

    # =====================================================
    # SORT ORDER
    # =====================================================

    sort_order = st.radio(

        "Sort Order",

        [

            "Ascending",

            "Descending"
        ],

        horizontal=True
    )

    # =====================================================
    # GLOBAL SEARCH LOGIC
    # =====================================================

    if search_text:

        search_text = (
            search_text.lower()
            .strip()
        )

        filtered_df = filtered_df[

            filtered_df.apply(

                lambda row:

                search_text in str(row)
                .lower(),

                axis=1
            )
        ]

    # =====================================================
    # STATUS FILTER LOGIC
    # =====================================================

    if (

        selected_status != "All"

        and "Status" in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Status"]
            == selected_status
        ]

    # =====================================================
    # CATEGORY FILTER LOGIC
    # =====================================================

    if (

        selected_category != "All"

        and "Category" in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Category"]
            == selected_category
        ]

    # =====================================================
    # WORKFLOW FILTER LOGIC
    # =====================================================

    if (

        selected_workflow != "All"

        and "Workflow Stage"
        in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Workflow Stage"]
            == selected_workflow
        ]

    # =====================================================
    # EMPLOYEE FILTER LOGIC
    # =====================================================

    if (

        selected_employee != "All"

        and "Employee"
        in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Employee"]
            == selected_employee
        ]

    # =====================================================
    # PROJECT FILTER LOGIC
    # =====================================================

    if (

        selected_project != "All"

        and "Project"
        in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Project"]
            == selected_project
        ]

    # =====================================================
    # SLA FILTER LOGIC
    # =====================================================

    if (

        selected_sla != "All"

        and "SLA Status"
        in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["SLA Status"]
            == selected_sla
        ]

    # =====================================================
    # AI FILTER LOGIC
    # =====================================================

    if (

        selected_ai != "All"

        and "AI Recommendation"
        in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["AI Recommendation"]
            == selected_ai
        ]

    # =====================================================
    # DUPLICATE RISK FILTER LOGIC
    # =====================================================

    if (

        risk_filter != "All"

        and "Duplicate Risk Score"
        in filtered_df.columns
    ):

        if risk_filter == "High Risk":

            filtered_df = filtered_df[

                filtered_df[
                    "Duplicate Risk Score"
                ] >= 0.80
            ]

        elif risk_filter == "Medium Risk":

            filtered_df = filtered_df[

                (

                    filtered_df[
                        "Duplicate Risk Score"
                    ] >= 0.40

                )

                &

                (

                    filtered_df[
                        "Duplicate Risk Score"
                    ] < 0.80
                )
            ]

        elif risk_filter == "Low Risk":

            filtered_df = filtered_df[

                filtered_df[
                    "Duplicate Risk Score"
                ] < 0.40
            ]

    # =====================================================
    # SORTING LOGIC
    # =====================================================

    ascending = (
        sort_order == "Ascending"
    )

    try:

        filtered_df = filtered_df.sort_values(

            by=sort_column,

            ascending=ascending
        )

    except Exception:

        pass

    # =====================================================
    # OPERATIONAL METRICS
    # =====================================================

    st.markdown("---")

    metric_col1, metric_col2, metric_col3, metric_col4 = (

        st.columns(4)
    )

    with metric_col1:

        st.metric(

            "Filtered Invoices",

            len(filtered_df)
        )

    with metric_col2:

        if "Amount" in filtered_df.columns:

            total_amount = (

                pd.to_numeric(

                    filtered_df["Amount"],

                    errors="coerce"
                )

                .fillna(0)

                .sum()
            )

            st.metric(

                "Total Amount",

                f"₹ {round(total_amount, 2)}"
            )

    with metric_col3:

        if "Duplicate Risk Score" in filtered_df.columns:

            high_risk_count = len(

                filtered_df[

                    filtered_df[
                        "Duplicate Risk Score"
                    ] >= 0.80
                ]
            )

            st.metric(

                "High Risk Invoices",

                high_risk_count
            )

    with metric_col4:

        if "SLA Status" in filtered_df.columns:

            breach_count = len(

                filtered_df[

                    filtered_df[
                        "SLA Status"
                    ] == "Breached"
                ]
            )

            st.metric(

                "SLA Breaches",

                breach_count
            )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    st.markdown("---")

    st.markdown(

        f"""
### Operational Results:
{len(filtered_df)} invoices found
        """
    )

    return filtered_df