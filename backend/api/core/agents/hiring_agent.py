"""
api/core/agents/hiring_agent.py
================================
Hiring Specialist Agent — Phase 9.
Place this file at: backend/api/core/agents/hiring_agent.py
"""

from sqlalchemy.orm import Session

from api.core.agents.base_agent import BaseAgent, AgentResult
from api.services import workforce as workforce_service


class HiringAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "HiringAgent"

    @property
    def domain(self) -> str:
        return "hiring"

    def run(self, question: str, db: Session) -> AgentResult:
        trends         = workforce_service.get_hiring_trends(db, start_year=2022, end_year=2024)
        top_industries = workforce_service.get_hiring_by_industry(db, year=2024, limit=3)
        top_countries  = workforce_service.get_hiring_by_country(db, year=2024, limit=3)
        remote         = workforce_service.get_remote_stats(db, year=2024)
        top_roles      = workforce_service.get_top_roles(db, year=2024, limit=3)

        insights = []

        if trends:
            latest = trends[-1]
            insights.append(
                f"Global hiring in 2024: {latest['total_postings']:,} postings, "
                f"avg salary ${latest['avg_salary_usd']:,.2f}."
            )

        if top_industries:
            names = ", ".join(i["industry_name"] for i in top_industries)
            insights.append(f"Top hiring industries: {names}.")

        if top_countries:
            names = ", ".join(c["country_name"] for c in top_countries)
            insights.append(f"Top hiring countries: {names}.")

        if remote:
            insights.append(
                f"Remote work: {remote['remote_pct']}% of all 2024 postings "
                f"({remote['remote_postings']:,} remote jobs)."
            )

        if top_roles:
            names = ", ".join(r["role_name"] for r in top_roles)
            insights.append(f"Most in-demand roles: {names}.")

        return AgentResult(
            agent_name=self.name,
            domain=self.domain,
            success=True,
            insights=insights,
            data={
                "trends":         trends,
                "top_industries": top_industries,
                "top_countries":  top_countries,
                "remote":         remote,
                "top_roles":      top_roles,
            },
        )