"""
api/core/groq_client.py
=======================
Groq API client — singleton pattern.

Why a singleton?
  Creating a new HTTP client on every request is wasteful (connection setup
  overhead). A singleton creates the client once at startup and reuses it
  across all requests — the same pattern used for database connection pools.

Place this file at: backend/api/core/groq_client.py
Create the folder:  backend/api/core/__init__.py  (empty file)
"""

import os
from functools import lru_cache
from api.config import get_settings

from groq import Groq


from api.config import get_settings

@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in your .env file.")
    return Groq(api_key=settings.GROQ_API_KEY)

def get_groq_model() -> str:
    return get_settings().GROQ_MODEL