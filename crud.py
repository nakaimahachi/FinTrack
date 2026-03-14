from database import get_supabase
from datetime import date, timedelta
import pandas as pd
import hashlib


# ── AUTH ──

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str) -> tuple[bool, str]:
    sb = get_supabase()
    # Check if email already exists
    existing = sb.table("users").select("id").eq("email", email).execute()
    if existing.data:
        return False, "An account with this email already exists."
    sb.table("users").insert({
        "name": name,
        "email": email,
        "password_hash": hash_password(password)
    }).execute()
    return True, "Account created successfully!"


def login_user(email: str, password: str):
    sb = get_supabase()
    result = sb.table("users").select("*").eq("email", email).eq(
        "password_hash", hash_password(password)
    ).execute()
    if result.data:
        return result.data[0]
    return None


def get_all_users():
    sb = get_supabase()
    result = sb.table("users").select("id, name, email").execute()
    return result.data or []


# ── CATEGORIES ──

DEFAULT_CATEGORIES = [
    {"name": "Salary", "type": "income"},
    {"name": "Freelance", "type": "income"},
    {"name": "Other Income", "type": "income"},
    {"name": "Groceries", "type": "expense"},
    {"name": "Rent", "type": "expense"},
    {"name": "Transport", "type": "expense"},
    {"name": "Eating Out", "type": "expense"},
    {"name": "Entertainment", "type": "expense"},
    {"name": "Health", "type": "expense"},
    {"name": "Clothing", "type": "expense"},
    {"name": "Subscriptions", "type": "expense"},
    {"name": "Other Expense", "type": "expense"},
]


def get_all_categories(user_id: int):
    sb = get_supabase()
    result = sb.table("categories").select("*").or_(
        f"user_id.eq.{user_id},is_default.eq.true"
    ).execute()
    return result.data or []


def get_categories_by_type(user_id: int, type_: str):
    cats = get_all_categories(user_id)
    return [c for c in cats if c["type"] == type_]


def add_category(user_id: int, name: str, type_: str):
    sb = get_supabase()
    sb.table("categories").insert({
        "user_id": user_id,
        "name": name,
        "type": type_,
        "is_default": False
    }).execute()


def delete_category(user_id: int, category_id: int) -> tuple[bool, str]:
    sb = get_supabase()
    # Check if category is default
    cat = sb.table("categories").select("*").eq("id", category_id).execute()
    if cat.data and cat.data[0].get("is_default"):
        return False, "Cannot delete a default category."
    # Check for linked transactions
    txs = sb.table("transactions").select("id").eq(
        "category_id", category_id).eq("user_id", user_id).execute()
    if txs.data:
        return False, f"Cannot delete: {len(txs.data)} transaction(s) linked to this category."
    sb.table("categories").delete().eq("id", category_id).eq("user_id", user_id).execute()
    return True, "Category deleted."


# ── TRANSACTIONS ──

def add_transaction(user_id: int, amount: float, description: str,
                    tx_date: date, payment_method: str, category_id: int):
    sb = get_supabase()
    sb.table("transactions").insert({
        "user_id": user_id,
        "amount": amount,
        "description": description,
        "date": str(tx_date),
        "payment_method": payment_method,
        "category_id": category_id
    }).execute()


def delete_transaction(tx_id: int, user_id: int):
    sb = get_supabase()
    sb.table("transactions").delete().eq("id", tx_id).eq("user_id", user_id).execute()


def get_transactions_df(user_id: int = None, period: str = "monthly",
                        year: int = None, month: int = None) -> pd.DataFrame:
    sb = get_supabase()
    today = date.today()
    year = year or today.year
    month = month or today.month

    query = sb.table("transactions").select(
        "*, categories(name, type)"
    )

    if user_id:
        query = query.eq("user_id", user_id)

    if period == "monthly":
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        query = query.gte("date", str(start)).lte("date", str(end))
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        query = query.gte("date", str(start)).lte("date", str(today))

    result = query.order("date", desc=True).execute()

    if not result.data:
        return pd.DataFrame()

    rows = []
    for tx in result.data:
        cat = tx.get("categories") or {}
        rows.append({
            "id": tx["id"],
            "user_id": tx["user_id"],
            "date": tx["date"],
            "description": tx["description"],
            "category": cat.get("name", "Unknown"),
            "type": cat.get("type", "expense"),
            "payment_method": tx["payment_method"],
            "amount": tx["amount"],
        })
    return pd.DataFrame(rows)


# ── BUDGETS ──

def set_budget(user_id: int, category_id: int, limit: float, period: str):
    sb = get_supabase()
    existing = sb.table("budgets").select("id").eq(
        "user_id", user_id).eq("category_id", category_id).eq("period", period).execute()
    if existing.data:
        sb.table("budgets").update({"amount_limit": limit}).eq("id", existing.data[0]["id"]).execute()
    else:
        sb.table("budgets").insert({
            "user_id": user_id,
            "category_id": category_id,
            "amount_limit": limit,
            "period": period
        }).execute()


def get_budgets(user_id: int):
    sb = get_supabase()
    result = sb.table("budgets").select("*, categories(name)").eq("user_id", user_id).execute()
    return result.data or []


def get_budget_alerts(user_id: int, period: str = "monthly"):
    budgets = get_budgets(user_id)
    today = date.today()
    df = get_transactions_df(user_id=user_id, period=period,
                              year=today.year, month=today.month)
    alerts = []
    for b in budgets:
        if b["period"] != period:
            continue
        cat_name = b["categories"]["name"] if b.get("categories") else "Unknown"
        if df.empty:
            spent = 0.0
        else:
            spent = df[(df["category"] == cat_name) & (df["type"] == "expense")]["amount"].sum()
        pct = (spent / b["amount_limit"] * 100) if b["amount_limit"] > 0 else 0
        alerts.append({
            "category": cat_name,
            "spent": spent,
            "limit": b["amount_limit"],
            "pct": pct,
            "period": period,
            "status": "over" if pct >= 100 else "warning" if pct >= 80 else "ok"
        })
    return sorted(alerts, key=lambda x: x["pct"], reverse=True)


# ── SUMMARY ──

def get_summary(user_id: int = None, period: str = "monthly",
                year: int = None, month: int = None):
    today = date.today()
    df = get_transactions_df(user_id=user_id, period=period,
                              year=year or today.year, month=month or today.month)
    if df.empty:
        return {"income": 0, "expenses": 0, "balance": 0, "df": df}
    income = df[df["type"] == "income"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    return {"income": income, "expenses": expenses,
            "balance": income - expenses, "df": df}
