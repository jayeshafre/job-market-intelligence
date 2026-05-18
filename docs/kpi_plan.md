# KPI Plan — Job Market Intelligence Platform

## Platform North Star Question
> Which skills, roles, and countries lead global hiring in 2025–2026,
> and how will they change in the next 12 months?

---

## Module 1 — Workforce Analytics

| KPI | Formula | Target User | Update Frequency |
|-----|---------|-------------|-----------------|
| Monthly job posting volume | COUNT(job_postings) GROUP BY month | HR Researcher | Monthly |
| Country hiring demand index | job_count_country / total_jobs * 100 | Recruiter | Monthly |
| Remote vs onsite ratio | COUNT(remote) / COUNT(all) * 100 | Analyst | Monthly |
| Industry growth rate | (current_month - prev_month) / prev_month * 100 | Business Analyst | Monthly |

---

## Module 2 — Salary Intelligence

| KPI | Formula | Target User | Update Frequency |
|-----|---------|-------------|-----------------|
| Median salary by role | PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) | Student / Jobseeker | Monthly |
| Country salary percentile | NTILE(100) OVER (PARTITION BY country ORDER BY salary) | Analyst | Monthly |
| YoY salary growth | (current_year_median - prev_year_median) / prev_year_median * 100 | HR Researcher | Yearly |
| Experience premium ratio | senior_median_salary / junior_median_salary | Recruiter | Quarterly |

---

## Module 3 — Skill Intelligence

| KPI | Formula | Target User | Update Frequency |
|-----|---------|-------------|-----------------|
| Skill mention frequency | COUNT(skill_mentions) GROUP BY skill_name | Student | Monthly |
| Skill growth velocity | (current_count - prev_count) / prev_count * 100 | Analyst | Monthly |
| AI skill demand share | ai_skill_count / total_skill_mentions * 100 | Researcher | Monthly |
| Emerging skill index | skills appearing in top 20 for first time | Strategist | Quarterly |

---

## Module 4 — AI Impact Analytics

| KPI | Formula | Target User | Update Frequency |
|-----|---------|-------------|-----------------|
| Automation risk score | weighted score (0–100) per role category | Workforce Researcher | Quarterly |
| AI disruption index | % jobs in high-risk categories by industry | Business Analyst | Quarterly |
| Future-safe role count | COUNT(roles WHERE risk_score < 30) | Student | Quarterly |
| AI adoption rate | ai_related_jobs / total_jobs * 100 | Strategist | Monthly |

---

## Module 5 — Forecasting Engine

| KPI | Formula | Target User | Update Frequency |
|-----|---------|-------------|-----------------|
| 12-month hiring forecast | Prophet time-series model on job_postings | HR Researcher | Monthly |
| Salary growth projection | XGBoost regression on historical salary data | Analyst | Quarterly |
| Emerging skill prediction | NLP trend model on skill frequency time series | Student | Quarterly |
| Model accuracy (MAPE) | mean(|actual - predicted| / actual) * 100 | Data Engineer | Per model run |