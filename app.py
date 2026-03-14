import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date
from crud import (
    login_user, register_user, get_all_users,
    get_all_categories, get_categories_by_type,
    add_transaction, delete_transaction, get_transactions_df,
    add_category, delete_category,
    set_budget, get_budgets, get_budget_alerts,
    get_summary
)

st.set_page_config(
    page_title="FinTrack",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None


LOGIN_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Ephesis&display=swap" rel="stylesheet">
<style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton, .stDeployButton { display: none !important; }

    /* Do NOT hide sidebar/collapsedControl here.
       That was leaking into the post-login app view. */

    .block-container {
        padding-top: 2rem !important;
    }

    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(160deg, #0a0015 0%, #12002e 50%, #0a0a1a 100%) !important;
    }

    .logo-wrap {
        display: flex;
        justify-content: center;
        margin-bottom: 8px;
    }

    .login-title {
        font-family: 'Ephesis', cursive !important;
        font-size: 96px;
        font-weight: 400;
        background: linear-gradient(135deg, #f5d782, #c9960c, #f5d782);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        line-height: 1.15;
    }

    .gold-divider {
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #c9960c, transparent);
        margin: 8px auto 16px auto;
    }

    .login-subtitle {
        color: #7c6a9e;
        text-align: center;
        font-size: 11px;
        margin-bottom: 28px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    [data-testid="stTabs"] button {
        color: #7c6a9e !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #f5d782 !important;
        border-bottom: 2px solid #c9960c !important;
    }

    label {
        color: #9e8fc0 !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #8B6914, #c9960c, #f5d782) !important;
        color: #0a0015 !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }

    .stButton > button *,
    .stButton > button span,
    .stButton > button p {
        color: #0a0015 !important;
    }

    .stForm {
        background: transparent !important;
        border: none !important;
    }
</style>
"""

APP_CSS = """
<style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton, .stDeployButton { display: none !important; }

    .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    [data-testid="stSidebar"] {
        display: block !important;
        background: linear-gradient(180deg, #0f0020, #1a0035) !important;
        border-right: 1px solid #2a1040 !important;
    }

    [data-testid="stSidebar"] * {
        color: #d4b8f0 !important;
    }

    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        background: linear-gradient(135deg, #8B6914, #c9960c) !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        border: none !important;
    }

    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="collapsedControl"] button svg {
        fill: #0a0015 !important;
        color: #0a0015 !important;
    }

    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(160deg, #0a0015 0%, #12002e 50%, #0a0a1a 100%) !important;
    }

    .metric-card {
        background: linear-gradient(135deg, #0f0020, #1a0035);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2a0050;
        border-top: 2px solid #c9960c;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #7c6a9e;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        margin-top: 6px;
    }

    .income { color: #4ade80; }
    .expense { color: #f87171; }
    .balance-pos { color: #f5d782; }
    .balance-neg { color: #f87171; }

    .alert-over {
        background: #3b1212;
        border-left: 4px solid #f87171;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 6px 0;
    }

    .alert-warning {
        background: #1a1200;
        border-left: 4px solid #c9960c;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 6px 0;
    }

    .alert-ok {
        background: #0a1f0a;
        border-left: 4px solid #4ade80;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 6px 0;
    }

    h1, h2, h3 {
        color: #f5d782 !important;
        letter-spacing: 1px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #8B6914, #c9960c, #f5d782) !important;
        color: #0a0015 !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }

    .stButton > button *,
    .stButton > button span,
    .stButton > button p {
        color: #0a0015 !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #8B6914, #f5d782) !important;
    }
</style>
"""

LOGO_HTML = """
<div class="logo-wrap">
    <svg width="52" height="46" viewBox="0 0 52 46" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="1" y="28" width="9" height="16" rx="1.5" fill="url(#gold1)"/>
        <rect x="14" y="18" width="9" height="26" rx="1.5" fill="url(#gold1)"/>
        <rect x="27" y="8" width="9" height="36" rx="1.5" fill="url(#gold1)"/>
        <rect x="40" y="0" width="9" height="44" rx="1.5" fill="url(#gold1)"/>
        <line x1="1" y1="44" x2="50" y2="44" stroke="#c9960c" stroke-width="1.5" stroke-linecap="round"/>
        <defs>
            <linearGradient id="gold1" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
                <stop offset="0%" stop-color="#f5d782"/>
                <stop offset="100%" stop-color="#8B6914"/>
            </linearGradient>
        </defs>
    </svg>
</div>
<div class="login-title">FinTrack</div>
<div class="gold-divider"></div>
<div class="login-subtitle">your family finance companion</div>
"""


def show_login():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(LOGO_HTML, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submitted:
                    user = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Your full name")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
                password2 = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submitted:
                    if not name or not email or not password:
                        st.error("Please fill in all fields.")
                    elif password != password2:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success, msg = register_user(name, email, password)
                        if success:
                            st.success(msg + " Please sign in.")
                        else:
                            st.error(msg)


def show_app():
    user = st.session_state.user
    today = date.today()

    st.markdown(APP_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 📊 FinTrack")
        st.markdown(f"👤 **{user['name']}**")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            [
                "Dashboard",
                "Family Summary",
                "Add Transaction",
                "Budgets",
                "Manage Categories",
                "All Transactions",
            ],
        )

        st.markdown("---")
        st.markdown("### View Period")

        period = st.selectbox("Period", ["monthly", "weekly"])

        selected_month = st.selectbox(
            "Month",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda m: date(2000, m, 1).strftime("%B"),
        )

        year_options = list(range(2023, today.year + 1))
        selected_year = st.selectbox(
            "Year",
            year_options,
            index=year_options.index(today.year),
        )

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if page == "Dashboard":
        st.markdown("# Dashboard")
        try:
            summary = get_summary(
                user_id=user["id"],
                period=period,
                year=selected_year,
                month=selected_month,
            )
        except Exception:
            summary = {"income": 0, "expenses": 0, "balance": 0, "df": pd.DataFrame()}

        df = summary["df"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Income</div><div class="metric-value income">€{summary["income"]:,.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Expenses</div><div class="metric-value expense">€{summary["expenses"]:,.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            bal_class = "balance-pos" if summary["balance"] >= 0 else "balance-neg"
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Balance</div><div class="metric-value {bal_class}">€{summary["balance"]:,.2f}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        alerts = []
        try:
            alerts = get_budget_alerts(user["id"], period=period)
        except Exception:
            pass

        if alerts:
            st.markdown("### Budget Alerts")
            for a in alerts:
                icon = "🔴" if a["status"] == "over" else "🟡" if a["status"] == "warning" else "🟢"
                st.markdown(
                    f'<div class="alert-{a["status"]}">{icon} <strong>{a["category"]}</strong> — €{a["spent"]:.2f} / €{a["limit"]:.2f} ({a["pct"]:.0f}%)</div>',
                    unsafe_allow_html=True,
                )
                st.progress(min(a["pct"] / 100, 1.0))
            st.markdown("<br>", unsafe_allow_html=True)

        if not df.empty:
            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown("### Spending by Category")
                exp_df = df[df["type"] == "expense"]
                if not exp_df.empty:
                    cat_totals = exp_df.groupby("category")["amount"].sum().reset_index()
                    fig = px.pie(
                        cat_totals,
                        values="amount",
                        names="category",
                        color_discrete_sequence=[
                            "#f5d782", "#c9960c", "#8B6914",
                            "#4ade80", "#f87171", "#a78bda", "#60a5fa"
                        ],
                        hole=0.45,
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="white",
                        margin=dict(t=20, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_r:
                st.markdown("### Income vs Expenses")
                df_chart = df.copy()
                df_chart["date"] = pd.to_datetime(df_chart["date"])
                timeline = df_chart.groupby(["date", "type"])["amount"].sum().reset_index()

                fig2 = px.bar(
                    timeline,
                    x="date",
                    y="amount",
                    color="type",
                    color_discrete_map={"income": "#4ade80", "expense": "#f87171"},
                    barmode="group",
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    xaxis=dict(gridcolor="#1a0035"),
                    yaxis=dict(gridcolor="#1a0035"),
                    margin=dict(t=20, b=20),
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### Cash vs Card")
            method_df = df.groupby("payment_method")["amount"].sum().reset_index()
            fig3 = px.bar(
                method_df,
                x="payment_method",
                y="amount",
                color="payment_method",
                color_discrete_map={"cash": "#f5d782", "card": "#8B6914"},
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=False,
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown("### Recent Transactions")
            display = df[["date", "description", "category", "type", "payment_method", "amount"]].head(10).copy()
            display["amount"] = display.apply(
                lambda r: f"+€{r['amount']:.2f}" if r["type"] == "income" else f"-€{r['amount']:.2f}",
                axis=1,
            )
            st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet. Add one to get started!")

    elif page == "Family Summary":
        st.markdown("# Family Summary")
        users = get_all_users()

        try:
            family_summary = get_summary(period=period, year=selected_year, month=selected_month)
        except Exception:
            family_summary = {"income": 0, "expenses": 0, "balance": 0, "df": pd.DataFrame()}

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Family Income</div><div class="metric-value income">€{family_summary["income"]:,.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Family Expenses</div><div class="metric-value expense">€{family_summary["expenses"]:,.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            bal = family_summary["balance"]
            bal_class = "balance-pos" if bal >= 0 else "balance-neg"
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Family Balance</div><div class="metric-value {bal_class}">€{bal:,.2f}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Per Member Breakdown")

        for u in users:
            try:
                s = get_summary(user_id=u["id"], period=period, year=selected_year, month=selected_month)
            except Exception:
                s = {"income": 0, "expenses": 0, "balance": 0}

            with st.expander(f"👤 {u['name']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Income", f"€{s['income']:,.2f}")
                c2.metric("Expenses", f"€{s['expenses']:,.2f}")
                c3.metric("Balance", f"€{s['balance']:,.2f}")

        if not family_summary["df"].empty:
            st.markdown("### Family Spending by Category")
            exp = family_summary["df"][family_summary["df"]["type"] == "expense"]

            if not exp.empty:
                cat_totals = exp.groupby("category")["amount"].sum().reset_index()
                fig = px.pie(
                    cat_totals,
                    values="amount",
                    names="category",
                    color_discrete_sequence=["#f5d782", "#c9960c", "#8B6914", "#4ade80", "#f87171", "#a78bda"],
                    hole=0.45,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    margin=dict(t=20, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

    elif page == "Add Transaction":
        st.markdown("# Add Transaction")

        tx_type = st.selectbox("Type", ["expense", "income"])
        cats = get_categories_by_type(user["id"], tx_type)
        cat_map = {c["name"]: c["id"] for c in cats}

        with st.form("add_tx_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                category_name = st.selectbox("Category", list(cat_map.keys()) if cat_map else ["No categories"])
                amount_input = st.text_input("Amount (€)", placeholder="e.g. 45.50")

            with col2:
                description = st.text_input("Description", placeholder="e.g. Lidl grocery run")
                tx_date = st.date_input("Date", value=today)
                payment_method = st.selectbox("Payment Method", ["card", "cash"])

            submitted = st.form_submit_button("Add Transaction", use_container_width=True, type="primary")

            if submitted:
                try:
                    amount = float(amount_input)
                except (ValueError, TypeError):
                    amount = -1

                if not description.strip():
                    st.error("Please enter a description.")
                elif amount <= 0:
                    st.error("Please enter a valid amount greater than zero.")
                elif not cat_map:
                    st.error("No categories available.")
                else:
                    add_transaction(
                        user["id"],
                        amount,
                        description.strip(),
                        tx_date,
                        payment_method,
                        cat_map[category_name],
                    )
                    st.success(f"Added: {description} — €{amount:.2f}")

                    if tx_type == "expense":
                        try:
                            alerts = get_budget_alerts(user["id"], period="monthly")
                            for a in alerts:
                                if a["category"] == category_name and a["status"] != "ok":
                                    icon = "🔴" if a["status"] == "over" else "🟡"
                                    st.warning(f"{icon} Budget alert for **{category_name}**: {a['pct']:.0f}% used")
                        except Exception:
                            pass

    elif page == "Budgets":
        st.markdown("# Budgets")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Set a Budget")
            with st.form("budget_form", clear_on_submit=True):
                expense_cats = get_categories_by_type(user["id"], "expense")
                cat_map = {c["name"]: c["id"] for c in expense_cats}

                cat_name = st.selectbox("Category", list(cat_map.keys()))
                limit_input = st.text_input("Budget Limit (€)", placeholder="e.g. 200.00")
                period_choice = st.selectbox("Period", ["monthly", "weekly"])
                submitted = st.form_submit_button("Set Budget", use_container_width=True, type="primary")

                if submitted:
                    try:
                        limit = float(limit_input)
                    except (ValueError, TypeError):
                        limit = -1

                    if limit <= 0:
                        st.error("Please enter a valid budget limit.")
                    else:
                        set_budget(user["id"], cat_map[cat_name], limit, period_choice)
                        st.success(f"Budget set: €{limit:.2f} {period_choice} for {cat_name}")

        with col2:
            st.markdown("### Current Budgets")
            try:
                budgets = get_budgets(user["id"])
                if budgets:
                    for b in budgets:
                        cat_name = b["categories"]["name"] if b.get("categories") else "Unknown"
                        st.markdown(f"**{cat_name}** — €{b['amount_limit']:.2f} / {b['period']}")
                else:
                    st.info("No budgets set yet.")
            except Exception:
                st.info("No budgets set yet.")

        st.markdown("### Budget Status")
        for p in ["monthly", "weekly"]:
            try:
                alerts = get_budget_alerts(user["id"], period=p)
                if alerts:
                    st.markdown(f"**{p.capitalize()}**")
                    for a in alerts:
                        icon = "🔴" if a["status"] == "over" else "🟡" if a["status"] == "warning" else "🟢"
                        st.markdown(
                            f'<div class="alert-{a["status"]}">{icon} <strong>{a["category"]}</strong> — €{a["spent"]:.2f} / €{a["limit"]:.2f} ({a["pct"]:.0f}%)</div>',
                            unsafe_allow_html=True,
                        )
                        st.progress(min(a["pct"] / 100, 1.0))
            except Exception:
                pass

    elif page == "Manage Categories":
        st.markdown("# Manage Categories")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Add Category")
            with st.form("add_cat_form", clear_on_submit=True):
                new_cat_name = st.text_input("Category Name")
                new_cat_type = st.selectbox("Type", ["expense", "income"])
                submitted = st.form_submit_button("Add", use_container_width=True, type="primary")

                if submitted:
                    if not new_cat_name.strip():
                        st.error("Please enter a name.")
                    else:
                        add_category(user["id"], new_cat_name.strip(), new_cat_type)
                        st.success(f"Category '{new_cat_name}' added.")
                        st.rerun()

        with col2:
            st.markdown("### Your Categories")
            cats = get_all_categories(user["id"])

            for cat in cats:
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(cat["name"])
                c2.write(f"{'🟢' if cat['type'] == 'income' else '🔴'} {cat['type']}")

                if not cat.get("is_default"):
                    if c3.button("🗑️", key=f"del_{cat['id']}"):
                        ok, msg = delete_category(user["id"], cat["id"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    c3.write("Default")

    elif page == "All Transactions":
        st.markdown("# All Transactions")

        try:
            df = get_transactions_df(
                user_id=user["id"],
                period=period,
                year=selected_year,
                month=selected_month,
            )
        except Exception:
            df = pd.DataFrame()

        if df.empty:
            st.info("No transactions for this period.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                type_filter = st.selectbox("Type", ["all", "income", "expense"])
            with col2:
                method_filter = st.selectbox("Method", ["all", "card", "cash"])
            with col3:
                cat_filter = st.selectbox("Category", ["all"] + sorted(df["category"].unique().tolist()))

            filtered = df.copy()
            if type_filter != "all":
                filtered = filtered[filtered["type"] == type_filter]
            if method_filter != "all":
                filtered = filtered[filtered["payment_method"] == method_filter]
            if cat_filter != "all":
                filtered = filtered[filtered["category"] == cat_filter]

            st.markdown(f"**{len(filtered)} transaction(s)** — Total: €{filtered['amount'].sum():.2f}")

            for _, row in filtered.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
                c1.write(str(row["date"]))
                c2.write(row["description"])
                c3.write(row["category"])
                c4.write(f"{'🟢 +' if row['type'] == 'income' else '🔴 -'}€{row['amount']:.2f}")

                if c5.button("🗑️", key=f"del_tx_{row['id']}"):
                    delete_transaction(row["id"], user["id"])
                    st.rerun()


if st.session_state.user is None:
    show_login()
else:
    show_app()
