"""
api/
====
FastAPI application package.

Package structure:
  api/config.py      → Settings management (pydantic-settings)
  api/database.py    → Engine, SessionLocal, Base, get_db
  api/models/        → SQLAlchemy ORM models (8 tables)
  api/schemas/       → Pydantic request/response schemas
  api/routers/       → FastAPI route handlers (added in Phase 2)
"""