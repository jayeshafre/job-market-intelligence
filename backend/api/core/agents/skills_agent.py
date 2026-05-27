"""
api/core/agents/skills_agent.py
================================
Skills Specialist Agent — Phase 9.
Place this file at: backend/api/core/agents/skills_agent.py
"""

from sqlalchemy.orm import Session

from api.core.agents.base_agent import BaseAgent, AgentResult
from api.services import skills as skills_service


class SkillsAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "SkillsAgent"

    @property
    def domain(self) -> str:
        return "skills"

    def run(self, question: str, db: Session) -> AgentResult:
        top_skills  = skills_service.get_top_growing_skills(db, year=2024, limit=5)
        ai_skills   = skills_service.get_ai_skills(db, year=2024, limit=3)
        by_category = skills_service.get_skills_by_category(db, year=2024)

        insights = []

        if top_skills:
            fastest = top_skills[0]
            insights.append(
                f"Fastest growing skill: {fastest['skill_name']} "
                f"at {fastest['growth_pct']}% YoY growth in 2024."
            )
            top_names = ", ".join(s["skill_name"] for s in top_skills[:3])
            insights.append(f"Top 3 skills by growth: {top_names}.")

        if ai_skills:
            ai_names = ", ".join(s["skill_name"] for s in ai_skills)
            insights.append(f"Top AI skills by demand: {ai_names}.")

        if by_category:
            top_cat = by_category[0]
            insights.append(
                f"Fastest growing skill category: {top_cat['skill_category']} "
                f"with {top_cat['avg_growth_pct']}% avg growth."
            )

        return AgentResult(
            agent_name=self.name,
            domain=self.domain,
            success=True,
            insights=insights,
            data={
                "top_skills":  top_skills,
                "ai_skills":   ai_skills,
                "by_category": by_category,
            },
        )