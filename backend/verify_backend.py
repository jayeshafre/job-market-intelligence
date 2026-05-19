"""
verify_backend.py
=================
Pre-flight check — run this BEFORE starting the server.
Confirms every Phase 1 module imports cleanly and DB is reachable.

Run from inside the backend/ folder:
    cd backend
    python verify_backend.py
"""

import sys


def check(label: str, fn) -> bool:
    try:
        fn()
        print(f"  ✓  {label}")
        return True
    except Exception as exc:
        print(f"  ✗  {label}")
        print(f"       → {type(exc).__name__}: {exc}")
        return False


def main():
    print("\n" + "=" * 55)
    print("  Job Market API — Phase 1 Backend Verification")
    print("=" * 55)

    results = []

    # 1. Config
    results.append(check(
        "api.config — Settings loads from .env",
        lambda: __import__("api.config", fromlist=["get_settings"]).get_settings()
    ))

    # 2. Database module
    results.append(check(
        "api.database — Engine and SessionLocal created",
        lambda: __import__("api.database", fromlist=["engine", "SessionLocal"])
    ))

    # 3. ORM Models — dimensions
    results.append(check(
        "api.models.dimensions — DimCountry, DimIndustry, DimJobRole, DimSkill",
        lambda: __import__("api.models.dimensions", fromlist=[
            "DimCountry", "DimIndustry", "DimJobRole", "DimSkill"
        ])
    ))

    # 4. ORM Models — facts
    results.append(check(
        "api.models.facts — FactJobPostings, FactSalaryTrends, FactSkillDemand, FactAiDisruption",
        lambda: __import__("api.models.facts", fromlist=[
            "FactJobPostings", "FactSalaryTrends", "FactSkillDemand", "FactAiDisruption"
        ])
    ))

    # 5. Schemas
    results.append(check(
        "api.schemas — HealthResponse, APIResponse, ErrorResponse",
        lambda: __import__("api.schemas", fromlist=[
            "HealthResponse", "APIResponse", "ErrorResponse"
        ])
    ))

    # 6. Main app
    results.append(check(
        "main — FastAPI app instance loads",
        lambda: __import__("main", fromlist=["app"])
    ))

    # 7. DB connection (optional — skips gracefully if PostgreSQL isn't running)
    print("\n  Testing DB connection (requires PostgreSQL running):")
    try:
        from api.database import test_connection
        status = test_connection()
        if status["status"] == "connected":
            print(f"  ✓  Database — {status['database']}@{status['host']}")
            print(f"       PostgreSQL: {status.get('pg_version', '')[:50]}")
        else:
            print(f"  ⚠  Database — FAILED (is PostgreSQL running?)")
            print(f"       Error: {status.get('error', 'unknown')}")
            print(f"       (Safe to ignore if DB isn't started yet)")
    except Exception as exc:
        print(f"  ⚠  Database — {exc}")

    # Summary
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 55)
    print(f"  Import checks : {passed}/{total} passed")
    if passed == total:
        print("  All good! Start the server with:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("  Fix the errors above before starting the server.")
    print("=" * 55 + "\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()