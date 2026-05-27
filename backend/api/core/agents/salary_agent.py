"""
api/core/agents/salary_agent.py
================================
Salary Specialist Agent — Phase 9.

Queries salary KPIs and returns structured salary insights.
Place this file at: backend/api/core/agents/salary_agent.py
"""

from sqlalchemy.orm import Session

from api.core.agents.base_agent import BaseAgent, AgentResult
from api.services import salary as salary_service


class SalaryAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "SalaryAgent"

    @property
    def domain(self) -> str:
        return "salary"

    def run(self, question: str, db: Session) -> AgentResult:
        top_roles     = salary_service.get_top_paying_roles(db, year=2024, limit=3)
        top_countries = salary_service.get_top_paying_countries(db, year=2024, limit=3)
        trends        = salary_service.get_salary_trends(db, start_year=2022, end_year=2024)

        insights = []

        if top_roles:
            r = top_roles[0]
            insights.append(
                f"Highest paying role: {r['role_name']} ({r['seniority_level']}) "
                f"at ${r['avg_salary_usd']:,.2f} USD avg in 2024."
            )

        if top_countries:
            names = ", ".join(c["country_name"] for c in top_countries)
            insights.append(f"Top paying countries: {names}.")

        if len(trends) >= 2:
            latest = trends[-1]
            prev   = trends[-2]
            if latest["avg_salary_usd"] and prev["avg_salary_usd"]:
                growth = round(
                    (latest["avg_salary_usd"] - prev["avg_salary_usd"])
                    / prev["avg_salary_usd"] * 100, 1
                )
                insights.append(
                    f"Global salary grew {growth}% YoY to "
                    f"${latest['avg_salary_usd']:,.2f} USD in 2024."
                )

        return AgentResult(
            agent_name=self.name,
            domain=self.domain,
            success=True,
            insights=insights,
            data={
                "top_roles":     top_roles[:3],
                "top_countries": top_countries[:3],
                "trends":        trends,
            },
        )