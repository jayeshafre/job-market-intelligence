"""
api/core/agents/base_agent.py
==============================
Base Agent Interface — Phase 9.

Every specialist agent inherits from BaseAgent.
This enforces a consistent interface across all agents:
  - Every agent has a name and domain
  - Every agent implements run(question, db) → AgentResult
  - Every agent returns the same structured output shape

Why a base class?
  The Supervisor Agent loops over a list of agents and calls run()
  on each one. If every agent has a different method signature,
  the supervisor can't treat them uniformly.

  This is the same pattern used in:
    LangChain  → BaseTool with _run() method
    AutoGen    → ConversableAgent with generate_reply()
    CrewAI     → Agent with execute_task()

  We're implementing the same architectural principle from scratch.

Place this file at: backend/api/core/agents/base_agent.py
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


# =============================================================================
# AGENT RESULT
# =============================================================================

@dataclass
class AgentResult:
    """
    Standardized output from every specialist agent.

    Every agent returns this exact shape — the supervisor
    can collect results without knowing which agent produced them.

    agent_name:  Which agent produced this result (e.g. "SalaryAgent")
    domain:      The domain this agent covers (e.g. "salary")
    success:     True if the agent completed without error
    insights:    List of key insight strings (shown in the final response)
    data:        Raw data dict for the supervisor to synthesize from
    error:       Error message if success=False
    """
    agent_name: str
    domain:     str
    success:    bool
    insights:   list[str]    = field(default_factory=list)
    data:       dict         = field(default_factory=dict)
    error:      str          = ""


# =============================================================================
# BASE AGENT
# =============================================================================

class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents.

    Subclasses must implement:
      - name:   str property
      - domain: str property
      - run(question, db) → AgentResult

    The run() method should:
      1. Query relevant data from the warehouse via existing service functions
      2. Extract the most important insights as plain strings
      3. Return an AgentResult with insights + raw data
      4. NEVER raise exceptions — catch all errors and return success=False
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent display name (e.g. 'SalaryAgent')"""
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this agent covers (e.g. 'salary')"""
        ...

    @abstractmethod
    def run(self, question: str, db: Session) -> AgentResult:
        """
        Execute the agent's analysis and return structured results.

        Args:
            question: The user's original question (for context).
            db:       SQLAlchemy session for warehouse queries.

        Returns:
            AgentResult — always returns, never raises.
        """
        ...

    def safe_run(self, question: str, db: Session) -> AgentResult:
        """
        Wrapper around run() that guarantees no exceptions escape.
        The supervisor calls safe_run() — not run() directly.

        If run() raises for any reason, returns a failed AgentResult
        with the error message. The supervisor handles partial failures
        gracefully — other agents still run and contribute.
        """
        try:
            return self.run(question, db)
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                domain=self.domain,
                success=False,
                error=str(e),
            )