"""
api/routers/__init__.py
=======================
Exports all routers so main.py has a single clean import.

Usage in main.py:
    from api.routers import workforce, salary, skills, ai_impact
"""

from api.routers import ai_impact, salary, skills, workforce

__all__ = ["workforce", "salary", "skills", "ai_impact"]