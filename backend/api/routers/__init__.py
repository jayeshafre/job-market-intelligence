"""
api/routers/__init__.py
=======================
Exports all routers. main.py imports from here.

Phase 2: workforce, salary, skills, ai_impact
Phase 3: analytics, forecast
"""

from api.routers import ai_impact, analytics, forecast, salary, skills, workforce

__all__ = ["workforce", "salary", "skills", "ai_impact", "analytics", "forecast"]