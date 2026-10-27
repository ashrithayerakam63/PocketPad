
import re
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px
import db

st.set_page_config(
    page_title="PocketPad",
    page_icon="💼",
    layout="wide"
)

db.init_db()

# ---------- DARK NAVY DESIGN ----------
NAVY = "#111827"
CARD = "#1F2937"
PURPLE = "#818CF8"
LIGHT_PURPLE = "#A5B4FC"
TEXT = "#F3F4F6"
MUTED = "#9CA3AF"
GREEN = "#6EE7B7"
RED = "#FCA5A5"
BORDER = "#374151"

st.markdown("""
<style>
/* Main background */
.stApp {
    background: #111827;
    color: #F3F4F6;
}

[data-testid="stHeader"] {
    background: #111827;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings and general text */
h1, h2, h3, h4, p, label,
.stMarkdown, .stCaption,
[data-testid="stWidgetLabel"] {
    color: #F3F4F6;
}

[data-testid="stCaptionContainer"] p {
    color: #9CA3AF;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0B1120;
    border-right: 1px solid #374151;
}

[data-testid="stSidebar"] * {
    color: #F3F4F6;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent;
    border-radius: 8px;
}

/* Cards and forms */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 14px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 16px;
}

[data-testid="stMetricLabel"] {
    color: #D1D5DB;
}

[data-testid="stMetricValue"] {
    color: #A5B4FC;
}

[data-testid="stMetricDelta"] {
    color: #6EE7B7;
}

/* Inputs and dropdowns */
input, textarea {
    background: #111827 !important;
    color: #F9FAFB !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] > div {
    background: #111827;
    color: #F9FAFB;
    border-color: #4B5563;
}

[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {
    background: #111827 !important;
    color: #F9FAFB !important;
}

/* Buttons */
div.stButton > button,
div.stFormSubmitButton > button {
    min-height: 42px;
    border-radius: 9px;
    font-weight: 600;
    border: 1px solid #6366F1;
    background: #4F46E5;
    color: white;
    transition: 0.2s ease;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #6366F1;
    border-color: #A5B4FC;
    color: white;
}

/* Links */
a {
    color: #A5B4FC !important;
}

/* Charts */
[data-testid="stPlotlyChart"] {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 8px;
}

/* Data tables */
[data-testid="stDataFrame"] {
    border: 1px solid #374151;
    border-radius: 10px;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Progress bar */
[data-testid="stProgressBar"] > div {
    background: #374151;
}

[data-testid="stProgressBar"] [role="progressbar"] > div {
    background: #818CF8;
}

/* Dividers */
hr {
    border-color: #374151;
}

/* Mobile layout */
@media (max-width: 640px) {
    .block-container {
        padding: 1rem 0.8rem;
    }

    [data-testid="stMetric"] {
        padding: 10px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Sign In"


def money(value):
    return f"₹{value:,.2f}"


def style_chart(fig):
    fig.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT),
        margin=dict(t=25, b=20, l=15, r=15),
        legend_title_text="",
        title_font_color=LIGHT_PURPLE
    )
    fig.update_xaxes(
        color=MUTED,
        gridcolor=BORDER,
        linecolor=BORDER
    )
    fig.update_yaxes(
        color=MUTED,
        gridcolor=BORDER,
        linecolor=BORDER
    )
    return fig


# ---------- SIGN IN / SIGN UP ----------
if st.session_state.user is None:

    st.markdown("# PocketPad 💼")
    st.caption("PERSONAL BUDGET TRACKER")
    st.divider()

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown("### Small steps. Better finances.")
        st.write(
            "Plan your monthly money, record daily transactions, "
            "and understand your spending."
        )
        st.markdown("**With PocketPad you can:**")
        st.markdown("""
        - Set a monthly income target
        - Choose an expense budget
        - Track income and expenses
        - View charts and transaction history
        """)

    with right:
        with st.container(border=True):

            if st.session_state.auth_page == "Sign Up":
                st.subheader("Create your account")
                st.caption("Get started with PocketPad.")

                with st.form("signup_form"):
                    name = st.text_input("Full name")
                    email = st.text_input("Email address")
                    password = st.text_input(
                        "Password", type="password"
                    )
                    confirm_password = st.text_input(
                        "Confirm password", type="password"
                    )

                    submitted = st.form_submit_button(
                        "Create Account",
                        use_container_width=True,
                        type="primary"
                    )

                    if submitted:
                        clean_name = name.strip()
                        clean_email = email.strip().lower()

                        if not clean_name or not clean_email:
                            st.error("Please fill in all fields.")
                        elif not re.fullmatch(
                            r"[^@\s]+@[^@\s]+\.[^@\s]+",
                            clean_email
                        ):
                            st.error("Enter a valid email address.")
                        elif len(password) < 8:
                            st.error(
                                "Password must have at least 8 characters."
                            )
                        elif password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            success = db.signup(
                                clean_name, clean_email, password
                            )

                            if success:
                                st.session_state.auth_page = "Sign In"
                                st.session_state.signup_message = (
                                    "Account created! Please sign in."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "This email is already registered."
                                )

                if st.button(
                    "Already registered? Sign In",
                    use_container_width=True
                ):
                    st.session_state.auth_page = "Sign In"
                    st.rerun()

            else:
                st.subheader("Welcome back")
                st.caption("Sign in to manage your money.")

                if "signup_message" in st.session_state:
                    st.success(
                        st.session_state.pop("signup_message")
                    )

                with st.form("login_form"):
                    email = st.text_input("Email address")
                    password = st.text_input(
                        "Password", type="password"
                    )

                    submitted = st.form_submit_button(
                        "Sign In",
                        use_container_width=True,
                        type="primary"
                    )

                    if submitted:
                        if not email.strip() or not password:
                            st.error("Enter your email and password.")
                        else:
                            user = db.login(email, password)

                            if user:
                                st.session_state.user = {
                                    "id": user[0],
                                    "name": user[1]
                                }
                                st.rerun()
                            else:
                                st.error("Incorrect email or password.")

                if st.button(
                    "New to PocketPad? Create Account",
                    use_container_width=True
                ):
                    st.session_state.auth_page = "Sign Up"
                    st.rerun()


# ---------- LOGGED-IN APPLICATION ----------
else:
    user = st.session_state.user
    user_id = user["id"]

    today = date.today()
    current_month = today.strftime("%Y-%m")
    month_label = today.strftime("%B %Y")

    plan = db.get_monthly_plan(user_id, current_month)

    # ---------- FIRST-TIME MONTHLY SETUP ----------
    if plan is None:
        st.markdown("# PocketPad 💼")
        st.caption("PERSONAL BUDGET TRACKER")
        st.divider()

        st.title("Plan your month")
        st.write(
            f"Welcome, {user['name']}! Before adding transactions, "
            f"set your financial targets for {month_label}."
        )

        with st.container(border=True):
            with st.form("monthly_setup_form"):
                expected_income = st.number_input(
                    "Expected monthly income (₹)",
                    min_value=0.0,
                    value=25000.0,
                    step=1000.0
                )

                expense_budget = st.number_input(
                    "Monthly expense budget (₹)",
                    min_value=0.0,
                    value=15000.0,
                    step=500.0
                )

                submitted = st.form_submit_button(
                    "Save Budget & Continue",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:
                    if expected_income <= 0:
                        st.error(
                            "Expected income must be greater than zero."
                        )
                    elif expense_budget <= 0:
                        st.error(
                            "Expense budget must be greater than zero."
                        )
                    else:
                        db.save_monthly_plan(
                            user_id,
                            current_month,
                            expected_income,
                            expense_budget
                        )
                        st.success("Your monthly plan has been saved!")
                        st.rerun()

        st.caption(
            "Your budget is saved to your account. "
            "You can update it later from Monthly Plan."
        )

        if st.button("Sign Out"):
            st.session_state.user = None
            st.rerun()

    # ---------- MAIN APP ----------
    else:
        with st.sidebar:
            st.markdown("# PocketPad 💼")
            st.caption("PERSONAL BUDGET TRACKER")
            st.divider()
            st.write(f"Welcome, {user['name']}!")
            st.caption(month_label)

            page = st.radio(
                "MENU",
                [
                    "Dashboard",
                    "Add Transaction",
                    "History",
                    "Monthly Plan"
                ]
            )

            st.divider()

            if st.button("Sign Out", use_container_width=True):
                st.session_state.user = None
                st.session_state.auth_page = "Sign In"
                st.rerun()

        records = db.get_transactions(user_id)

        df = pd.DataFrame(
            records,
            columns=["ID", "Date", "Category", "Amount", "Type"]
        )

        if not df.empty:
            df["Amount"] = pd.to_numeric(
                df["Amount"], errors="coerce"
            )
            df["Date"] = pd.to_datetime(
                df["Date"], errors="coerce"
            )
            df = df.dropna(subset=["Date", "Amount"])

        if not df.empty:
            month_df = df[
                df["Date"].dt.strftime("%Y-%m") == current_month
            ].copy()
        else:
            month_df = df.copy()

        actual_income = (
            month_df.loc[
                month_df["Type"] == "Income", "Amount"
            ].sum()
            if not month_df.empty else 0
        )

        spent = (
            month_df.loc[
                month_df["Type"] == "Expense", "Amount"
            ].sum()
            if not month_df.empty else 0
        )

        expected_income = float(plan[0])
        expense_budget = float(plan[1])
        remaining_budget = expense_budget - spent

        # ---------- DASHBOARD ----------
        if page == "Dashboard":
            st.title("Dashboard")
            st.caption(f"Your financial overview for {month_label}.")

            c1, c2, c3 = st.columns(3)
            c1.metric("Expected Income", money(expected_income))
            c2.metric("Actual Income", money(actual_income))
            c3.metric("Expense Budget", money(expense_budget))

            c4, c5 = st.columns(2)
            c4.metric("Spent This Month", money(spent))
            c5.metric(
                "Budget Remaining",
                money(remaining_budget),
                delta=(
                    "Within budget"
                    if remaining_budget >= 0
                    else "Over budget"
                ),
                delta_color=(
                    "normal" if remaining_budget >= 0 else "inverse"
                )
            )

            progress = min(spent / expense_budget, 1.0)
            st.write("Monthly budget used")
            st.progress(progress)
            st.caption(
                f"{(spent / expense_budget) * 100:.1f}% of your "
                "expense budget used."
            )

            if spent > expense_budget:
                st.warning(
                    "You have exceeded your monthly expense budget."
                )
            elif spent >= expense_budget * 0.8:
                st.warning(
                    "You have used 80% or more of your budget."
                )

            st.divider()

            if month_df.empty:
                st.info(
                    "No transactions for this month yet. "
                    "Choose Add Transaction to get started."
                )
            else:
                left, right = st.columns(2)

                with left:
                    st.subheader("Expense Breakdown")
                    expense_data = month_df[
                        month_df["Type"] == "Expense"
                    ]

                    if not expense_data.empty:
                        category_data = (
                            expense_data.groupby(
                                "Category", as_index=False
                            )["Amount"].sum()
                        )

                        fig = px.pie(
                            category_data,
                            names="Category",
                            values="Amount",
                            hole=0.45,
                            color_discrete_sequence=[
                                "#818CF8", "#A5B4FC", "#6366F1",
                                "#C4B5FD", "#60A5FA", "#6EE7B7",
                                "#FBBF24", "#F9A8D4"
                            ]
                        )
                        fig.update_traces(
                            textfont_color=TEXT,
                            marker=dict(
                                line=dict(color=CARD, width=2)
                            )
                        )
                        style_chart(fig)
                        st.plotly_chart(
                            fig, use_container_width=True
                        )
                    else:
                        st.info("Add an expense to see this chart.")

                with right:
                    st.subheader("Income vs Expenses")

                    chart_df = df.copy()
                    chart_df["Month"] = (
                        chart_df["Date"].dt.strftime("%Y-%m")
                    )

                    monthly_data = chart_df.pivot_table(
                        index="Month",
                        columns="Type",
                        values="Amount",
                        aggfunc="sum",
                        fill_value=0
                    ).reset_index()

                    for kind in ["Income", "Expense"]:
                        if kind not in monthly_data.columns:
                            monthly_data[kind] = 0

                    monthly_data = monthly_data.sort_values(
                        "Month"
                    ).tail(6)

                    melted = monthly_data.melt(
                        id_vars="Month",
                        value_vars=["Income", "Expense"],
                        var_name="Type",
                        value_name="Amount"
                    )

                    fig = px.bar(
                        melted,
                        x="Month",
                        y="Amount",
                        color="Type",
                        barmode="group",
                        color_discrete_map={
                            "Income": "#6EE7B7",
                            "Expense": "#FCA5A5"
                        }
                    )
                    style_chart(fig)
                    st.plotly_chart(
                        fig, use_container_width=True
                    )

                st.subheader("Recent Transactions")
                recent = df.sort_values(
                    ["Date", "ID"], ascending=False
                ).head(5).copy()

                recent["Date"] = recent["Date"].dt.strftime(
                    "%d %b %Y"
                )
                recent["Amount"] = recent["Amount"].apply(money)

                st.dataframe(
                    recent[["Date", "Category", "Type", "Amount"]],
                    use_container_width=True,
                    hide_index=True
                )

        # ---------- ADD TRANSACTION ----------
        elif page == "Add Transaction":
            st.title("Add Transaction")
            st.caption("Record your income and expenses.")

            with st.container(border=True):
                with st.form("transaction_form"):
                    transaction_date = st.date_input(
                        "Date",
                        value=today
                    )

                    transaction_type = st.radio(
                        "Transaction Type",
                        ["Expense", "Income"],
                        horizontal=True
                    )

                    if transaction_type == "Expense":
                        categories = [
                            "Food", "Transport", "Rent",
                            "Entertainment", "Shopping",
                            "Healthcare", "Education",
                            "Bills", "Others"
                        ]
                    else:
                        categories = [
                            "Salary", "Business", "Investment",
                            "Gift", "Other Income"
                        ]

                    category = st.selectbox("Category", categories)

                    amount = st.number_input(
                        "Amount (₹)",
                        min_value=0.0,
                        step=100.0,
                        format="%.2f"
                    )

                    note = st.text_input(
                        "Note (optional)",
                        placeholder="e.g. Groceries"
                    )

                    submitted = st.form_submit_button(
                        "Save Transaction",
                        use_container_width=True,
                        type="primary"
                    )

                    if submitted:
                        if amount <= 0:
                            st.error(
                                "Enter an amount greater than zero."
                            )
                        elif (
                            transaction_date.strftime("%Y-%m")
                            != current_month
                        ):
                            st.error(
                                "Please select a date in the current "
                                "month. You can still view older records "
                                "in History."
                            )
                        else:
                            # Notes are not stored in this database version.
                            db.add_transaction(
                                user_id,
                                transaction_date,
                                category,
                                amount,
                                transaction_type
                            )
                            st.success("Transaction saved successfully!")
                            st.rerun()

        # ---------- HISTORY ----------
        elif page == "History":
            st.title("Transaction History")
            st.caption("Search and manage your records.")

            if df.empty:
                st.info("No transactions found. Add one to get started.")
            else:
                a, b, c = st.columns(3)

                with a:
                    search = st.text_input("Search category")

                with b:
                    type_filter = st.selectbox(
                        "Type", ["All", "Income", "Expense"]
                    )

                with c:
                    category_filter = st.selectbox(
                        "Category",
                        ["All"] + sorted(
                            df["Category"].dropna().unique().tolist()
                        )
                    )

                filtered = df.copy()

                if search:
                    filtered = filtered[
                        filtered["Category"].str.contains(
                            search, case=False, na=False
                        )
                    ]

                if type_filter != "All":
                    filtered = filtered[
                        filtered["Type"] == type_filter
                    ]

                if category_filter != "All":
                    filtered = filtered[
                        filtered["Category"] == category_filter
                    ]

                display = filtered.sort_values(
                    ["Date", "ID"], ascending=False
                ).copy()

                display["Date"] = display["Date"].dt.strftime(
                    "%d %b %Y"
                )
                display["Amount"] = display["Amount"].apply(money)

                st.write(f"Transactions found: {len(display)}")

                st.dataframe(
                    display[
                        ["ID", "Date", "Category", "Type", "Amount"]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()
                st.subheader("Delete a transaction")

                if not filtered.empty:
                    selected_id = st.selectbox(
                        "Transaction ID",
                        filtered["ID"].astype(int).tolist()
                    )

                    confirm_delete = st.checkbox(
                        "I confirm that I want to delete this transaction."
                    )

                    if st.button(
                        "Delete Transaction",
                        type="primary"
                    ):
                        if confirm_delete:
                            db.delete_transaction(
                                int(selected_id), user_id
                            )
                            st.success("Transaction deleted.")
                            st.rerun()
                        else:
                            st.warning(
                                "Please confirm before deleting."
                            )

        # ---------- MONTHLY PLAN ----------
        elif page == "Monthly Plan":
            st.title("Monthly Plan")
            st.caption(f"Manage your targets for {month_label}.")

            with st.container(border=True):
                with st.form("edit_plan_form"):
                    new_income = st.number_input(
                        "Expected monthly income (₹)",
                        min_value=0.0,
                        value=expected_income,
                        step=1000.0
                    )

                    new_budget = st.number_input(
                        "Monthly expense budget (₹)",
                        min_value=0.0,
                        value=expense_budget,
                        step=500.0
                    )

                    submitted = st.form_submit_button(
                        "Update Monthly Plan",
                        use_container_width=True,
                        type="primary"
                    )

                    if submitted:
                        if new_income <= 0 or new_budget <= 0:
                            st.error(
                                "Income and budget must both be greater than zero."
                            )
                        else:
                            db.save_monthly_plan(
                                user_id,
                                current_month,
                                new_income,
                                new_budget
                            )
                            st.success("Monthly plan updated.")
                            st.rerun()
