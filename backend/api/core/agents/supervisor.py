"""
api/core/agents/supervisor.py
==============================
Supervisor Agent — Phase 9.

The Supervisor is the entry point for the multi-agent system.
It decides which specialist agents to invoke, runs them,
collects their outputs, and synthesizes a final unified response.

Responsibilities:
  1. Read the user question and create an execution plan
  2. Select which specialist agents are relevant
  3. Run selected agents (sequentially — Python async not required)
  4. Collect all AgentResult objects
  5. Build a synthesis prompt from all agent insights
  6. Call Groq to write the final unified answer
  7. Return structured response with agent outputs + synthesis

Agent selection strategy:
  Keyword-based routing — same philosophy as the orchestrator in Phase 2.
  Fast, deterministic, zero LLM cost for routing.
  General questions activate ALL agents for maximum coverage.

Place this file at: backend/api/core/agents/supervisor.py
"""

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from groq import APIConnectionError, APIStatusError, RateLimitError

from api.core.agents.base_agent import AgentResult
from api.core.agents.salary_agent import SalaryAgent
from api.core.agents.skills_agent import SkillsAgent
from api.core.agents.hiring_agent import HiringAgent
from api.core.agents.disruption_agent import DisruptionAgent
from api.core.agents.forecast_agent import ForecastAgent
from api.core.groq_client import get_groq_client, get_groq_model

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT REGISTRY
# =============================================================================

# All available specialist agents — add new ones here as you build them
ALL_AGENTS = {
    "salary":       SalaryAgent(),
    "skills":       SkillsAgent(),
    "hiring":       HiringAgent(),
    "ai_disruption": DisruptionAgent(),
    "forecast":     ForecastAgent(),
}


# =============================================================================
# AGENT SELECTION (keyword routing)
# =============================================================================

AGENT_KEYWORDS = {
    "salary":        ["salary", "pay", "compensation", "earn", "wage", "income", "highest paid"],
    "skills":        ["skill", "learn", "technology", "python", "sql", "ai skill", "trending", "course"],
    "hiring":        ["hiring", "job posting", "demand", "remote", "recruitment", "industry", "country"],
    "ai_disruption": ["automat", "ai risk", "safe", "disruption", "replaced", "robot", "future safe"],
    "forecast":      ["predict", "forecast", "future", "2025", "2026", "next year", "trend", "will be"],
}


def select_agents(question: str) -> list[str]:
    """
    Decides which agents to activate based on question keywords.

    Returns a list of agent keys from ALL_AGENTS.
    If no keywords match, activates ALL agents (general question = full analysis).

    This is the Supervisor's planning step — zero LLM cost.
    """
    question_lower = question.lower()
    selected = []

    for agent_key, keywords in AGENT_KEYWORDS.items():
        if any(kw in question_lower for kw in keywords):
            selected.append(agent_key)

    # General question or no matches → run all agents
    if not selected:
        selected = list(ALL_AGENTS.keys())
        logger.info("[SUPERVISOR] No specific keywords — activating all agents.")
    else:
        logger.info(f"[SUPERVISOR] Selected agents: {selected}")

    return selected


# =============================================================================
# SYNTHESIS PROMPT
# =============================================================================

SUPERVISOR_SYSTEM_PROMPT = """You are a Chief AI Workforce Intelligence Officer
synthesizing insights from multiple specialist analytics agents.

You have received structured intelligence reports from specialist agents
covering: salary data, skill trends, hiring patterns, AI disruption risk,
and market forecasts.

Your task:
1. Synthesize all agent insights into one coherent, expert response
2. Lead with the insight most relevant to the user's specific question
3. Connect insights across domains where they reinforce each other
4. Be specific — use the exact numbers from the agent reports
5. End with one clear, actionable recommendation
6. Total length: 200–300 words maximum
7. Write in confident executive prose — no bullet points
"""


def build_synthesis_prompt(
    question: str,
    agent_results: list[AgentResult],
) -> str:
    """
    Builds the user message for the synthesis Groq call.
    Formats all successful agent insights as a structured briefing.
    """
    lines = [f"User question: {question}\n"]
    lines.append("=== SPECIALIST AGENT REPORTS ===\n")

    for result in agent_results:
        if not result.success:
            lines.append(f"[{result.agent_name}] FAILED: {result.error}\n")
            continue

        lines.append(f"[{result.agent_name} — {result.domain.upper()}]")
        for insight in result.insights:
            lines.append(f"  • {insight}")
        lines.append("")

    lines.append(
        "Synthesize these agent reports into one unified expert answer "
        "that directly addresses the user's question."
    )
    return "\n".join(lines)


# =============================================================================
# SUPERVISOR RESULT
# =============================================================================

@dataclass
class SupervisorResult:
    """
    The complete output from the multi-agent system.

    synthesis:       The Groq-written unified answer.
    agent_outputs:   Individual results from each specialist agent.
    execution_plan:  Which agents were selected and why.
    agents_run:      Count of agents that ran successfully.
    agents_failed:   Count of agents that failed.
    tokens_used:     Groq tokens for the synthesis call.
    model:           The model used.
    """
    synthesis:      str
    agent_outputs:  list[dict]
    execution_plan: list[str]
    agents_run:     int
    agents_failed:  int
    tokens_used:    int
    model:          str


# =============================================================================
# SUPERVISOR RUN
# =============================================================================

def run_supervisor(question: str, db: Session) -> SupervisorResult:
    """
    Main entry point for the multi-agent system.

    Steps:
      1. Select relevant agents (keyword routing — free)
      2. Run each selected agent via safe_run() (DB queries)
      3. Collect results, count successes/failures
      4. Build synthesis prompt from all insights
      5. Call Groq once for the final unified answer
      6. Return SupervisorResult

    Args:
        question: The user's natural language question.
        db:       SQLAlchemy session for all agent DB queries.

    Returns:
        SupervisorResult with synthesis + full agent outputs.
    """
    client = get_groq_client()
    model  = get_groq_model()

    # Step 1: Agent selection
    selected_keys  = select_agents(question)
    execution_plan = [f"Activate {k} agent" for k in selected_keys]

    # Step 2: Run selected agents
    logger.info(f"[SUPERVISOR] Running {len(selected_keys)} agents for: '{question[:60]}...'")

    agent_results: list[AgentResult] = []
    for key in selected_keys:
        agent  = ALL_AGENTS[key]
        result = agent.safe_run(question=question, db=db)
        agent_results.append(result)
        status = "✓" if result.success else "✗"
        logger.info(f"[SUPERVISOR] {status} {agent.name} | insights={len(result.insights)}")

    # Step 3: Count outcomes
    agents_run    = sum(1 for r in agent_results if r.success)
    agents_failed = sum(1 for r in agent_results if not r.success)

    # Step 4: Build synthesis prompt
    synthesis_prompt = build_synthesis_prompt(question, agent_results)

    # Step 5: Groq synthesis call
    logger.info(f"[SUPERVISOR] Synthesizing {agents_run} agent reports with Groq...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
                {"role": "user",   "content": synthesis_prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        synthesis   = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

    except (RateLimitError, APIConnectionError, APIStatusError) as e:
        # If Groq fails, fall back to concatenated insights (no synthesis)
        synthesis = "\n\n".join(
            f"{r.agent_name}: " + " ".join(r.insights)
            for r in agent_results if r.success
        )
        tokens_used = 0
        logger.warning(f"[SUPERVISOR] Groq synthesis failed: {e} — using raw insights")

    # Step 6: Format agent outputs for the API response
    agent_outputs = [
        {
            "agent_name": r.agent_name,
            "domain":     r.domain,
            "success":    r.success,
            "insights":   r.insights,
            "error":      r.error,
        }
        for r in agent_results
    ]

    logger.info(
        f"[SUPERVISOR] Complete | agents_run={agents_run} | "
        f"agents_failed={agents_failed} | tokens={tokens_used}"
    )

    return SupervisorResult(
        synthesis      = synthesis,
        agent_outputs  = agent_outputs,
        execution_plan = execution_plan,
        agents_run     = agents_run,
        agents_failed  = agents_failed,
        tokens_used    = tokens_used,
        model          = model,
    )