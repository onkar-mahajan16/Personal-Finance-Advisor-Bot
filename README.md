# Ledgerly: Personal Finance Advisor Bot

Flask + SQLAlchemy backend, vanilla JS dashboard, and an AI engine (Claude) with a built-in rule-based fallback.

## Run it

```bash
python -m venv venv
venv\Scripts\activate           # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env          # optional: add ANTHROPIC_API_KEY for AI advice
python app.py                   # http://127.0.0.1:5000
```

The SQLite database (`instance/finance.db`) is created on first run. Without an API key the
advisor uses the rule-based engine, so everything works offline.

## Deploy on Render

1. Push this project to a GitHub repository. Do not upload `.env`, the `venv` folder, or
   `instance/finance.db`; `.gitignore` excludes these local files.
2. In Render, choose **New → Blueprint**, connect the repository, and deploy the
   `render.yaml` blueprint. It creates a web service and a persistent PostgreSQL database.
3. Optionally add `ANTHROPIC_API_KEY` in the web service's Render environment settings to
   enable Claude advice. Without it, the rule-based advisor remains available.

The web service uses HTTPS-only session cookies and a Render-generated `SECRET_KEY`. The
PostgreSQL database uses Render's `basic-256mb` plan, which has a monthly charge; check
Render's current pricing before deploying. The free web service may sleep when idle.

## Structure

```
app.py               app factory, dashboard route
config.py            settings read from .env
models.py            User, Category, Income, Expense, Budget, SavingsGoal, MonthlyReport
services/budget.py   monthly summary, trend, budget generation (per profile type)
services/ai_engine.py  Claude insights + Q&A, rule-based fallback
services/reports.py  monthly report builder
routes/auth.py       register, login, logout
routes/api.py        JSON API used by the dashboard
templates/, static/  UI
```

## Profile logic

| Profile | Savings target | Income basis |
|---|---|---|
| Salaried | 20% | this month's income |
| Student | 10% | this month's allowance |
| Freelancer | 25% | 90% of the recent average (variable income), plus a 6-month emergency fund goal |
| Household | 15% | this month's combined income |

Budget limits start from your last three months of spending per category. If that exceeds
what's left after the savings target, discretionary categories are trimmed first.

## API (all under /api, login required)

| Method | Path | Purpose |
|---|---|---|
| GET/POST | /income, /expenses | list (`?month=YYYY-MM`) or add |
| DELETE | /income/<id>, /expenses/<id> | remove an entry |
| GET/POST | /categories | list or add |
| GET | /summary, /trend | month totals, six-month history |
| POST | /budget/generate | build the month's budget |
| PUT | /budget | edit one category limit |
| GET/POST/DELETE | /goals, /goals/<id>/contribute | savings goals |
| GET | /insights | health score, insights, tips |
| POST | /advisor/ask | free-form question |
| POST | /reports/generate; GET /reports, /reports/<month> | monthly reports |

## Before deploying

Set a strong `SECRET_KEY`, serve over HTTPS, use a production server (gunicorn) and add CSRF
protection (Flask-WTF) if you expose it publicly. AI advice is informational, not licensed
financial advice.

## Ideas for next steps

Predictive spending (moving averages or Prophet), recurring transactions, CSV import,
investment suggestions, multi-user households with shared access.
