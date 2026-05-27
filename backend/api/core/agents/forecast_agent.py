"""
api/core/agents/forecast_agent.py
===================================
Forecasting Specialist Agent — Phase 9.
Place this file at: backend/api/core/agents/forecast_agent.py
"""

from sqlalchemy.orm import Session

from api.core.agents.base_agent import BaseAgent, AgentResult
from api.services.ml import forecast_hiring, forecast_salary


class ForecastAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "ForecastAgent"

    @property
    def domain(self) -> str:
        return "forecast"

    def run(self, question: str, db: Session) -> AgentResult:
        hiring_fc = forecast_hiring(db, periods=2)
        salary_fc = forecast_salary(db, periods=2)

        insights = []

        if hiring_fc.get("forecast"):
            next_year = hiring_fc["forecast"][0]
            insights.append(
                f"Hiring forecast {next_year['year']}: "
                f"{next_year['predicted_value']:,.0f} postings predicted "
                f"(range: {next_year['lower_bound']:,.0f}–{next_year['upper_bound']:,.0f})."
            )

        if salary_fc.get("forecast"):
            next_year = salary_fc["forecast"][0]
            insights.append(
                f"Salary forecast {next_year['year']}: "
                f"${next_year['predicted_value']:,.2f} USD avg predicted "
                f"(range: ${next_year['lower_bound']:,.2f}–${next_year['upper_bound']:,.2f})."
            )

        if hiring_fc.get("forecast") and len(hiring_fc["forecast"]) > 1:
            yr2 = hiring_fc["forecast"][1]
            insights.append(
                f"2-year hiring outlook ({yr2['year']}): "
                f"{yr2['predicted_value']:,.0f} postings projected."
            )

        return AgentResult(
            agent_name=self.name,
            domain=self.domain,
            success=True,
            insights=insights,
            data={
                "hiring_forecast": hiring_fc,
                "salary_forecast": salary_fc,
            },
        )