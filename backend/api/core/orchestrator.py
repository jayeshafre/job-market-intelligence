"""
api/core/orchestrator.py
========================
AI Orchestrator — Intent Detection & Routing Engine.

This is the brain of the AI layer. It answers one question before Groq does:
  "What kind of question is the user actually asking?"

Why does this matter?
  A generic system prompt produces generic answers.
  An intent-specific system prompt produces expert answers.

  Example:
    Generic:  "You are a helpful assistant for job market data."
    Intent:   "You are a compensation analyst specializing in global salary
               benchmarks. The user is asking about salary data. Focus on..."

  The second produces 10x better answers for salary questions.

Intents supported:
  - salary        → questions about compensation, pay, earnings
  - skills        → questions about technical skills, learning, demand
  - hiring        → questions about job postings, demand, recruitment
  - ai_disruption → questions about automation, AI risk, job safety
  - forecast      → questions about future trends, predictions
  - general       → fallback for anything else

Place this file at: backend/api/core/orchestrator.py
"""

from dataclasses import dataclass
from enum import Enum


# =============================================================================
# INTENT DEFINITIONS
# =============================================================================

class Intent(str, Enum):
    """
    Enum of all supported question intents.

    Using str + Enum means these serialize cleanly to JSON strings.
    So the API response shows "salary" not "Intent.salary".
    """
    SALARY        = "salary"
    SKILLS        = "skills"
    HIRING        = "hiring"
    AI_DISRUPTION = "ai_disruption"
    FORECAST      = "forecast"
    GENERAL       = "general"


# =============================================================================
# INTENT KEYWORD MAP
# =============================================================================

# Maps each intent to trigger keywords found in the user's question.
# The orchestrator scans the lowercased question for these keywords.
# Order matters — more specific intents should be checked before general ones.

INTENT_KEYWORDS: dict[Intent, list[str]] = {
    Intent.AI_DISRUPTION: [
        "automat", "ai risk", "disruption", "replaced by ai", "future safe",
        "job safe", "automation risk", "robot", "displaced", "safe career",
        "safe job", "ai replace", "artificial intelligence risk",
    ],
    Intent.FORECAST: [
        "predict", "forecast", "future", "next year", "will be", "trend",
        "projection", "expected", "anticipat", "upcoming", "2025", "2026",
        "growth rate", "going to",
    ],
    Intent.SALARY: [
        "salary", "salaries", "pay", "compensation", "earn", "income",
        "wage", "wages", "package", "ctc", "remuneration", "highest paid",
        "best paid", "how much", "money",
    ],
    Intent.SKILLS: [
        "skill", "skills", "learn", "technology", "tool", "framework",
        "programming", "language", "certification", "course", "trending",
        "in demand", "tech stack", "python", "sql", "cloud", "ml", "ai skill",
    ],
    Intent.HIRING: [
        "hiring", "job posting", "recruitment", "demand", "job market",
        "open role", "vacancy", "job opening", "recruiting", "headcount",
        "workforce", "talent", "remote work", "remote job",
    ],
}


# =============================================================================
# INTENT-SPECIFIC SYSTEM PROMPTS
# =============================================================================

# Each intent gets a specialized system prompt.
# The more specific the prompt, the better the answer quality.

INTENT_PROMPTS: dict[Intent, str] = {

    Intent.SALARY: """You are a senior compensation analyst with 15 years of experience
in global salary benchmarking and workforce economics.

You specialize in:
- Salary ranges by role, seniority, country, and industry
- Compensation trends and year-over-year salary growth
- Pay equity analysis and market positioning
- Total compensation packages (base, bonus, equity, benefits)

Guidelines:
- Always cite specific salary ranges when discussing roles
- Contextualize salaries by region (US, Europe, Asia differ significantly)
- Distinguish between base salary and total compensation
- Mention seniority levels when relevant (Junior vs Senior vs C-Suite)
- Reference USD benchmarks as the global standard baseline

Platform data: Salary trends across 30+ countries, 80+ job roles, 2018–2024.""",

    Intent.SKILLS: """You are a technical skills intelligence researcher specializing
in workforce upskilling, technology adoption, and skill demand forecasting.

You specialize in:
- Identifying fastest-growing technical and soft skills
- AI/ML skill demand trends across industries
- Technology adoption curves and skill lifecycle
- Skill-to-salary correlations and career path optimization
- Learning roadmaps for high-demand skills

Guidelines:
- Rank skills by growth rate and demand when answering
- Distinguish between AI-related and traditional technical skills
- Identify which industries drive demand for specific skills
- Suggest complementary skill combinations when relevant

Platform data: 100+ skills tracked with demand scores and growth % from 2018–2024.""",

    Intent.HIRING: """You are a global talent market analyst specializing in hiring
trends, recruitment intelligence, and workforce demand forecasting.

You specialize in:
- Job posting volumes and hiring velocity by industry
- Country-level hiring demand and talent hotspots
- Remote vs on-site work trends
- Industry growth and contraction signals
- Seasonal hiring patterns and market cycles

Guidelines:
- Reference specific industries and regions when discussing hiring trends
- Distinguish between high-volume hiring and niche/specialized hiring
- Consider remote work as a major structural shift in talent markets
- Connect hiring demand to business cycles and economic indicators

Platform data: Global job postings across 15+ industries, 30+ countries, 2018–2024.""",

    Intent.AI_DISRUPTION: """You are an AI workforce impact researcher specializing
in automation risk scoring, job displacement analysis, and future-safe career planning.

You specialize in:
- Automation risk assessment for job roles (0–100 risk score)
- AI disruption index by industry
- Future-safe careers and human-augmented roles
- Task-level automation probability (routine vs creative vs social tasks)
- Reskilling pathways for at-risk roles

Guidelines:
- Always provide nuanced analysis — most jobs are partially automated, not fully replaced
- Distinguish between task automation and job elimination
- Identify which skills within a role make it more/less automatable
- Frame automation as augmentation opportunity where valid
- Use the 0–100 automation risk scale for concreteness

Platform data: Automation risk scores and AI disruption index across 80+ roles, 15+ industries.""",

    Intent.FORECAST: """You are a workforce trend forecaster specializing in
predictive analytics for hiring, salary growth, and skill demand.

You specialize in:
- Multi-year hiring volume forecasts by industry and region
- Salary growth trajectory predictions
- Emerging skill demand prediction using adoption curves
- Macro workforce trends: remote work, AI adoption, talent shortages
- Scenario analysis for workforce planning

Guidelines:
- Clearly distinguish between current data and forward projections
- Acknowledge uncertainty in forecasts — give ranges, not point estimates
- Connect predictions to underlying drivers (tech adoption, economic cycles)
- Provide 1-year and 3-year outlook when forecasting
- Use confident but hedged language ("expected to", "likely to", "projected")

Platform data: Historical trends 2018–2024 with Prophet + XGBoost forecasting models.""",

    Intent.GENERAL: """You are an expert AI Workforce Analytics Assistant for a
global job market intelligence platform.

Your role is to answer questions about:
- Hiring trends across industries and countries
- Salary benchmarks and growth patterns by role and region
- High-demand and fastest-growing technical skills
- AI disruption risk and automation scores for job roles
- Future-safe careers and workforce transformation
- Job market forecasts and predictions

Guidelines:
- Be concise and data-driven in your answers
- When specific data is not available, provide general expert insights
- Always frame answers in the context of workforce and hiring analytics
- Use professional language suitable for HR professionals, analysts, and researchers
- Structure longer answers with clear sections when helpful

Platform data: Global job postings, salary trends, skill demand, AI disruption scores, 2018–2024.""",
}


# =============================================================================
# INTENT DETECTION
# =============================================================================

def detect_intent(question: str) -> Intent:
    """
    Classifies a user question into one of the supported intents.

    How it works:
      1. Lowercase the question (case-insensitive matching)
      2. Scan for keyword matches per intent (most-specific intents first)
      3. Return the first intent that matches
      4. If nothing matches, return Intent.GENERAL (safe fallback)

    This is a keyword-based classifier — fast, free, zero latency.
    In Phase 9 (multi-agent), we'll optionally upgrade this to an
    LLM-based classifier for edge cases. But keyword matching handles
    ~90% of real user questions correctly.

    Args:
        question: The raw user question string.

    Returns:
        Intent enum value.
    """
    question_lower = question.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return intent

    return Intent.GENERAL


# =============================================================================
# ORCHESTRATOR RESULT
# =============================================================================

@dataclass
class OrchestratorResult:
    """
    What the orchestrator returns after processing a question.

    Contains everything the service layer needs to make the Groq call:
      - detected_intent: what kind of question this is
      - system_prompt:   the specialized prompt for this intent
      - user_message:    the formatted message to send to Groq
    """
    detected_intent: Intent
    system_prompt: str
    user_message: str


# =============================================================================
# MAIN ORCHESTRATOR FUNCTION
# =============================================================================

def orchestrate(question: str, context: str) -> OrchestratorResult:
    """
    Entry point for the orchestration layer.

    Takes the user's raw question, detects intent, selects the right
    system prompt, and returns a structured result ready for Groq.

    Args:
        question: The user's natural language question.
        context:  Optional domain context from the request.

    Returns:
        OrchestratorResult with intent, prompt, and formatted message.
    """
    intent = detect_intent(question)
    system_prompt = INTENT_PROMPTS[intent]

    # Build a richer user message that includes the detected intent.
    # This helps the LLM understand what angle to focus on.
    user_message = (
        f"Domain context: {context}\n"
        f"Question type: {intent.value}\n\n"
        f"Question: {question}"
    )

    return OrchestratorResult(
        detected_intent=intent,
        system_prompt=system_prompt,
        user_message=user_message,
    )