"""
api/database.py
===============
Database connection layer.

Responsibilities:
  1. Create the SQLAlchemy engine (one per application)
  2. Create the SessionLocal factory (one session per request)
  3. Expose the declarative Base (all ORM models inherit from this)
  4. Provide get_db() — the FastAPI dependency injected into every route

Industry pattern: "Unit of Work"
  Each HTTP request gets ONE database session.
  The session is committed on success, rolled back on failure, always closed.
  This prevents connection leaks that bring production DBs to their knees.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator

from api.config import get_settings

settings = get_settings()


# =============================================================================
# 1. ENGINE
# =============================================================================
# The engine is the actual connection manager.
# create_engine() does NOT open a connection — it just configures the pool.
# Real connections are opened lazily (on first query).

engine = create_engine(
    url=settings.database_url,

    # ── Connection Pool Settings ───────────────────────────────────────────
    # pool_size: persistent connections always kept alive
    # max_overflow: burst connections allowed beyond pool_size (temporarily)
    # Total max connections = pool_size + max_overflow = 15 (default config)
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,

    # pool_timeout: max seconds to wait when pool is exhausted before error
    pool_timeout=settings.DB_POOL_TIMEOUT,

    # pool_recycle: recycle connections older than N seconds
    # Prevents "server closed the connection unexpectedly" after long idle
    pool_recycle=settings.DB_POOL_RECYCLE,

    # pool_pre_ping: sends "SELECT 1" before each checkout to test liveness
    # Catches stale/dead connections BEFORE your query hits them — critical
    pool_pre_ping=True,

    # echo: set True to print every SQL query to stdout (only in debug mode)
    echo=settings.APP_DEBUG,
)


# =============================================================================
# 2. SESSION FACTORY
# =============================================================================
# SessionLocal is a CLASS (factory), not a session instance.
# Calling SessionLocal() creates a new session.

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # We manage transactions manually (best practice)
    autoflush=False,    # We flush manually before queries when needed
    expire_on_commit=False,  # Returned objects stay accessible after commit
)


# =============================================================================
# 3. DECLARATIVE BASE
# =============================================================================
# All ORM model classes (in models/) inherit from this Base.
# SQLAlchemy uses Base.metadata to track all registered tables.

class Base(DeclarativeBase):
    """
    Project-wide SQLAlchemy declarative base.
    All ORM models inherit from this class.
    
    Using the new SQLAlchemy 2.0 style (DeclarativeBase) instead of the
    legacy declarative_base() function — more type-safe and future-proof.
    """
    pass


# =============================================================================
# 4. DATABASE DEPENDENCY (FastAPI Dependency Injection)
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    How it works:
      1. A new Session is created when the request begins
      2. The session is yielded to the route handler
      3. The route handler does its DB work
      4. On success → session is automatically closed
      5. On exception → session is rolled back then closed

    Usage in any router:
        @router.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            results = db.query(MyModel).all()

    The `try/finally` ensures the session is ALWAYS closed — even if an
    exception is raised mid-request. No connection leaks.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# =============================================================================
# 5. CONNECTION TEST UTILITY
# =============================================================================

def test_connection() -> dict:
    """
    Verifies the database connection is alive.
    Called once at application startup in main.py.
    Returns a status dict consumed by the /health endpoint.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
        return {
            "status": "connected",
            "database": settings.DB_NAME,
            "host": settings.DB_HOST,
            "pg_version": version,
        }
    except Exception as exc:
        return {
            "status": "error",
            "database": settings.DB_NAME,
            "host": settings.DB_HOST,
            "error": str(exc),
        }