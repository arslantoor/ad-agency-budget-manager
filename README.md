# Ad Agency Budget Manager API

This project is a budget management system for an Ad Agency. It handles:
- Daily and Monthly budget tracking
- Campaign state changes based on budget status
- Dayparting for campaigns (active during specific hours)
- Automatic reset of budgets daily/monthly
- FastAPI auto-generated docs

---

## 🔧 Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic (DB migrations)
- SQLite (default DB, easily swappable)

---

## 🗂 Project Structure

```bash
app/
│
├── api/
│ └── v1/
│ ├── routes_brand.py
│ ├── routes_budget.py
│ ├── routes_campaign.py
│ └── routes_spend_log.py
│
├── crud/
│ ├── crud_brand.py
│ └── ...
│
├── core/
│ └── config.py
│
├── db/
│ ├── base.py
│ ├── session.py
│ └── init_db.py
│
├── models/
│ ├── brand.py
│ ├── budget.py
│ ├── campaign.py
│ └── spend_log.py
│
├── schemas/
│ ├── brand.py
│ ├── budget.py
│ ├── campaign.py
│ └── spend_log.py
│
└── services/
└── budget_service.py

alembic/
├── versions/
├── env.py
└── script.py.mako

main.py
```
## 🚀 Running the Project
### 1. 📦 Install Dependencies

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

##  🗃️ Set Up DB & Run Migrations
```bash
alembic revision --autogenerate -m "Recreate initial migration"
alembic upgrade head
```
## ▶️ Start FastAPI App
```bash
uvicorn main:app --reload

```
## 📄 Open API Docs
Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

## ✅ Alembic Commands
Initialize (already done in setup):
```commandline
alembic init alembic // Initialize (already done in setup):
alembic revision --autogenerate -m "your message" // Create a new migration:
alembic upgrade head // Run migrations:
alembic downgrade -1 // Downgrade last migration:

```
## ✍️ Author Notes
Adheres to SOLID principles via service layers, clear routing, and decoupled logic.

Uses API versioning in the routing layer for scalable design.