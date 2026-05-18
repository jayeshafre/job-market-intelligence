"""
CSV → PostgreSQL Loader
Loads all 8 synthetic CSV files into the data warehouse.
Run AFTER warehouse_schema.sql has been executed.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# ─── Connection ───────────────────────────────────────────────────────────────

DB_URL = (
    f"postgresql://{os.getenv('DB_USER', 'postgres')}"
    f":{os.getenv('DB_PASSWORD', 'postgres')}"
    f"@{os.getenv('DB_HOST', 'localhost')}"
    f":{os.getenv('DB_PORT', '5432')}"
    f"/{os.getenv('DB_NAME', 'job_market_db')}"
)
engine = create_engine(DB_URL)

# ─── Load Order (dimensions MUST load before facts) ───────────────────────────
# Foreign keys enforce this. Loading facts first = FK violation error.

LOAD_ORDER = [
    ("dim_country",        "data/synthetic/dim_country.csv"),
    ("dim_industry",       "data/synthetic/dim_industry.csv"),
    ("dim_job_role",       "data/synthetic/dim_job_role.csv"),
    ("dim_skill",          "data/synthetic/dim_skill.csv"),
    ("fact_job_postings",  "data/synthetic/fact_job_postings.csv"),
    ("fact_salary_trends", "data/synthetic/fact_salary_trends.csv"),
    ("fact_skill_demand",  "data/synthetic/fact_skill_demand.csv"),
    ("fact_ai_disruption", "data/synthetic/fact_ai_disruption.csv"),
]

# ─── Loader ───────────────────────────────────────────────────────────────────

def load_table(table_name: str, csv_path: str) -> None:
    print(f"Loading {table_name}...", end=" ", flush=True)

    df = pd.read_csv(csv_path)

    # Convert Python True/False strings → actual booleans
    for col in df.select_dtypes(include="object").columns:
        if df[col].dropna().isin(["True", "False"]).all():
            df[col] = df[col].map({"True": True, "False": False})

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",   # append = respect existing schema + data
        index=False,          # don't write pandas index as a column
        method="multi",       # batch insert — much faster than row-by-row
        chunksize=5000,       # 5,000 rows per batch
    )

    print(f"{len(df):,} rows loaded.")


def reset_sequences() -> None:
    """
    After bulk loading with explicit IDs, PostgreSQL sequences
    are still at 1. This resets them so future INSERTs don't conflict.
    """
    tables_with_serial = [
        "dim_country", "dim_industry", "dim_job_role", "dim_skill",
        "fact_job_postings", "fact_salary_trends",
        "fact_skill_demand", "fact_ai_disruption",
    ]
    with engine.connect() as conn:
        for table in tables_with_serial:
            conn.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', "
                f"(SELECT column_name FROM information_schema.columns "
                f"WHERE table_name='{table}' AND column_default LIKE 'nextval%' LIMIT 1)), "
                f"(SELECT MAX({table[table.rfind('_')+1:].rstrip('s')}_id) FROM {table}));"
            ))
        conn.commit()


def verify_load() -> None:
    print("\nVerification:")
    with engine.connect() as conn:
        for table, _ in LOAD_ORDER:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:<30} {count:>10,} rows")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Job Market DB — CSV Loader")
    print("=" * 50)

    for table_name, csv_path in LOAD_ORDER:
        load_table(table_name, csv_path)

    verify_load()
    print("\nAll tables loaded successfully.")