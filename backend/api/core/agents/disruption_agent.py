"""
api/core/agents/disruption_agent.py
=====================================
AI Disruption Specialist Agent — Phase 9.
Place this file at: backend/api/core/agents/disruption_agent.py
"""

from sqlalchemy.orm import Session

from api.core.agents.base_agent import BaseAgent, AgentResult
from api.services import ai_impact as ai_impact_service


class DisruptionAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "DisruptionAgent"

    @property
    def domain(self) -> str:
        return "ai_disruption"

    def run(self, question: str, db: Session) -> AgentResult:
        at_risk      = ai_impact_service.get_disruption_scores(db, year=2024, limit=3)
        safe_careers = ai_impact_service.get_future_safe_careers(db, year=2024, limit=3)
        by_industry  = ai_impact_service.get_disruption_by_industry(db, year=2024)

        insights = []

        if at_risk:
            highest = at_risk[0]
            insights.append(
                f"Highest automation risk role: {highest['role_name']} "
                f"(risk score: {highest['avg_automation_risk']}/100)."
            )

        if safe_careers:
            safest = safe_careers[0]
            insights.append(
                f"Safest career from AI: {safest['role_name']} "
                f"(future-safe score: {safest['avg_future_safe_score']}/100)."
            )
            names = ", ".join(r["role_name"] for r in safe_careers)
            insights.append(f"Top safe careers: {names}.")

        if by_industry:
            most_disrupted = by_industry[0]
            least_disrupted = by_industry[-1]
            insights.append(
                f"Most disrupted industry: {most_disrupted['industry_name']} "
                f"(avg risk: {most_disrupted['avg_automation_risk']}/100)."
            )
            insights.append(
                f"Least disrupted industry: {least_disrupted['industry_name']} "
                f"(avg risk: {least_disrupted['avg_automation_risk']}/100)."
            )

        return AgentResult(
            agent_name=self.name,
            domain=self.domain,
            success=True,
            insights=insights,
            data={
                "at_risk":      at_risk,
                "safe_careers": safe_careers,
                "by_industry":  by_industry[:5],
            },
        )