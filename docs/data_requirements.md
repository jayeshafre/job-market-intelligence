# Data Requirements — Job Market Intelligence Platform

## What Data Do We Need?

### Table 1: job_postings
The core fact table. Every row = one job posting.

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| job_id | VARCHAR | Unique job identifier | Dataset |
| job_title | VARCHAR | Job title / role name | Dataset |
| company_name | VARCHAR | Hiring company | Dataset |
| country | VARCHAR | Country of job location | Dataset |
| city | VARCHAR | City (nullable) | Dataset |
| is_remote | BOOLEAN | Remote work flag | Dataset |
| industry | VARCHAR | Industry sector | Dataset |
| posted_date | DATE | When job was posted | Dataset |
| salary_min | NUMERIC | Min salary offered | Dataset |
| salary_max | NUMERIC | Max salary offered | Dataset |
| salary_currency | VARCHAR | Currency code (USD, EUR) | Dataset |
| experience_level | VARCHAR | Junior / Mid / Senior | Dataset |
| employment_type | VARCHAR | Full-time / Part-time / Contract | Dataset |

---

### Table 2: skills
Normalized skill mentions. One row per skill per job posting.

| Column | Type | Description |
|--------|------|-------------|
| skill_id | SERIAL | Auto-incremented PK |
| job_id | VARCHAR | FK → job_postings |
| skill_name | VARCHAR | e.g. Python, SQL, AWS |
| skill_category | VARCHAR | Programming / Cloud / Soft skill |

---

### Table 3: ai_impact
One row per role category with AI disruption scoring.

| Column | Type | Description |
|--------|------|-------------|
| role_category | VARCHAR | Grouped job category |
| automation_risk_score | NUMERIC(5,2) | 0-100 risk score |
| ai_disruption_index | NUMERIC(5,2) | Industry disruption % |
| risk_tier | VARCHAR | Low / Medium / High |
| assessed_date | DATE | When score was calculated |

---

### Table 4: salary_benchmarks
Monthly aggregated salary data for trend analysis.

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | SERIAL | PK |
| role_name | VARCHAR | Standardized role name |
| country | VARCHAR | Country |
| year_month | DATE | First day of month |
| median_salary_usd | NUMERIC | Converted to USD |
| p25_salary_usd | NUMERIC | 25th percentile |
| p75_salary_usd | NUMERIC | 75th percentile |
| sample_size | INTEGER | Count of records |

---

## Data Quality Rules (Our Acceptance Criteria)
- No nulls in: job_id, job_title, country, posted_date
- salary_min must be <= salary_max
- posted_date must be between 2018-01-01 and today
- automation_risk_score must be between 0 and 100
- All salary values converted to USD before storage