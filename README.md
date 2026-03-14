# 💰 Personal Finance Tracker

A clean, full-featured personal finance tracker built with Python and Streamlit. Log income and expenses, set budgets with alerts, and visualise your spending — all in a dark-themed dashboard.

## Features

- **Transaction logging** — log income and expenses with category, date, description, and payment method (cash or card)
- **Auto-categorisation** — assign transactions to predefined or custom categories
- **Budget alerts** — set monthly or weekly spending limits per category; get alerted at 80% and 100%
- **Dashboard** — income vs expenses summary, spending breakdown by category (donut chart), timeline bar chart, cash vs card breakdown
- **Monthly and weekly views** — filter all data by period
- **Category management** — add custom categories; delete unused ones (business rule: cannot delete a category with linked transactions)
- **Transaction history** — filter and delete transactions by type, category, and payment method

## Tech Stack

- **Python** — core language
- **Streamlit** — UI framework
- **SQLAlchemy** — ORM and database management
- **SQLite** — local relational database
- **Plotly** — interactive charts
- **Pandas** — data manipulation

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`. The database is created automatically on first run with default categories pre-loaded.

## Project Structure

```
finance_tracker/
├── app.py            # Streamlit UI and page routing
├── crud.py           # All database operations and business logic
├── database.py       # SQLAlchemy models and database initialisation
├── requirements.txt  # Python dependencies
└── README.md
```

## Business Logic

- Transactions cannot be assigned to a category of the wrong type (e.g. income transaction in an expense category)
- Categories with linked transactions cannot be deleted
- Budget alerts trigger at 80% (warning) and 100% (over limit)
- Amount must be positive and description must be non-empty

## Future Improvements

- Multi-user support with authentication
- Real-time bank sync via Open Banking / PSD2 API
- Export transactions to CSV
- Recurring transaction support
- Mobile-friendly PWA deployment
