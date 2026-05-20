"""
api/core/smart_alerts.py
=========================
Smart Alert Scanner — Phase 5.

Scans your KPI data and fires alerts when thresholds are crossed.
Zero LLM calls — this is pure data intelligence, not generative AI.

Why no LLM here?
  Alerts must be deterministic. If a skill grows >100%, the alert
  ALWAYS fires. You can't have an LLM deciding whether to alert —
  it might say "yes" one time and "no" another for the same data.
  Rule-based systems are the right tool for threshold alerting.

Alert severity levels:
  critical  → immediate action needed (automation risk > 85)
  warning   → worth investigating (skill growth > 100%)
  info      → notable trend (remote work > 50%)

Alert categories:
  skill_surge      → a skill growing explosively
  automation_risk  → a role/industry crossing risk threshold
  salary_shift     → significant salary movement
  hiring_surge     → explosive hiring growth in a segment
  remote_shift     → remote work crossing meaningful threshold

Real companies that use this pattern:
  PagerDuty    → infrastructure threshold alerts
  Datadog      → metric anomaly detection
  Tableau      → data-driven notifications
  LinkedIn     → "Your profile views spiked 3x this week"

Place this file at: backend/api/core/smart_alerts.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.services import skills as skills_service
from api.services import ai_impact as ai_impact_service
from api.services import workforce as workforce_service
from api.services import salary as salary_service

logger = logging.getLogger(__name__)


# =============================================================================
# ALERT DATA CLASS
# =============================================================================

@dataclass
class Alert:
    """
    A single smart alert object.

    severity:   critical | warning | info
    category:   skill_surge | automation_risk | salary_shift |
                hiring_surge | remote_shift
    title:      Short alert headline (shown in notification)
    message:    Full alert explanation with the specific data point
    data_point: The raw number that triggered the alert
    entity:     The skill / role / industry / country that triggered it
    """
    severity:   str
    category:   str
    title:      str
    message:    str
    data_point: float
    entity:     str


# =============================================================================
# THRESHOLD CONFIGURATION
# =============================================================================

# All thresholds in one place — easy to tune without touching logic.
# In production these would come from a config file or database settings table.

THRESHOLDS = {
    "skill_growth_critical":     100.0,   # >100% YoY growth → critical surge
    "skill_growth_warning":       50.0,   # >50% YoY growth  → notable surge
    "automation_risk_critical":   80.0,   # >80/100 risk score → critical
    "automation_risk_warning":    65.0,   # >65/100 risk score → warning
    "future_safe_low_warning":    40.0,   # <40/100 safe score → warning
    "remote_pct_info":            45.0,   # >45% remote → structural shift info
    "salary_growth_info":          8.0,   # >8% YoY growth → notable
    "hiring_volume_info":      50_000,    # total postings crossing threshold
}


# =============================================================================
# INDIVIDUAL SCANNERS
# =============================================================================

def scan_skill_alerts(db: Session) -> list[Alert]:
    """Scans skill demand data for growth anomalies."""
    alerts = []
    try:
        skills = skills_service.get_top_growing_skills(db, year=2024, limit=20)
        for skill in skills:
            growth = float(skill.get("growth_pct") or 0)
            name   = skill.get("skill_name", "Unknown")

            if growth >= THRESHOLDS["skill_growth_critical"]:
                alerts.append(Alert(
                    severity="critical",
                    category="skill_surge",
                    title=f"Explosive skill surge: {name}",
                    message=(
                        f"{name} has grown {growth:.1f}% YoY — this is an extraordinary "
                        f"demand signal. Roles requiring this skill are likely commanding "
                        f"significant salary premiums right now."
                    ),
                    data_point=growth,
                    entity=name,
                ))
            elif growth >= THRESHOLDS["skill_growth_warning"]:
                alerts.append(Alert(
                    severity="warning",
                    category="skill_surge",
                    title=f"High-growth skill detected: {name}",
                    message=(
                        f"{name} is growing at {growth:.1f}% YoY. "
                        f"Early movers who acquire this skill now will have a "
                        f"competitive advantage within 12–18 months."
                    ),
                    data_point=growth,
                    entity=name,
                ))
    except Exception as e:
        logger.warning(f"[ALERTS] scan_skill_alerts failed: {e}")

    return alerts


def scan_automation_risk_alerts(db: Session) -> list[Alert]:
    """Scans AI disruption data for high-risk roles and industries."""
    alerts = []
    try:
        # Check high-risk roles
        roles = ai_impact_service.get_disruption_scores(db, year=2024, limit=10)
        for role in roles:
            risk  = float(role.get("avg_automation_risk") or 0)
            safe  = float(role.get("avg_future_safe") or 0)
            name  = role.get("role_name", "Unknown")

            if risk >= THRESHOLDS["automation_risk_critical"]:
                alerts.append(Alert(
                    severity="critical",
                    category="automation_risk",
                    title=f"Critical automation risk: {name}",
                    message=(
                        f"{name} has an automation risk score of {risk:.0f}/100. "
                        f"Workers in this role should prioritize upskilling into "
                        f"adjacent human-augmented areas immediately."
                    ),
                    data_point=risk,
                    entity=name,
                ))
            elif risk >= THRESHOLDS["automation_risk_warning"]:
                alerts.append(Alert(
                    severity="warning",
                    category="automation_risk",
                    title=f"Elevated automation risk: {name}",
                    message=(
                        f"{name} has an automation risk score of {risk:.0f}/100 "
                        f"with a future-safe score of {safe:.0f}/100. "
                        f"Strategic upskilling is recommended."
                    ),
                    data_point=risk,
                    entity=name,
                ))

        # Check industries
        industries = ai_impact_service.get_disruption_by_industry(db, year=2024)
        for ind in industries:
            risk = float(ind.get("avg_automation_risk") or 0)
            name = ind.get("industry_name", "Unknown")

            if risk >= THRESHOLDS["automation_risk_critical"]:
                alerts.append(Alert(
                    severity="critical",
                    category="automation_risk",
                    title=f"Industry-wide disruption alert: {name}",
                    message=(
                        f"The {name} industry shows an avg automation risk of "
                        f"{risk:.0f}/100 across all tracked roles. "
                        f"Workforce transformation planning is urgently needed."
                    ),
                    data_point=risk,
                    entity=name,
                ))

    except Exception as e:
        logger.warning(f"[ALERTS] scan_automation_risk_alerts failed: {e}")

    return alerts


def scan_remote_work_alerts(db: Session) -> list[Alert]:
    """Flags if remote work share crosses the structural shift threshold."""
    alerts = []
    try:
        remote = workforce_service.get_remote_stats(db, year=2024)
        pct    = float(remote.get("remote_pct") or 0)

        if pct >= THRESHOLDS["remote_pct_info"]:
            alerts.append(Alert(
                severity="info",
                category="remote_shift",
                title=f"Remote work at {pct:.1f}% — structural shift confirmed",
                message=(
                    f"{pct:.1f}% of all 2024 job postings are remote. "
                    f"This indicates a permanent structural shift in talent markets. "
                    f"Geographic salary arbitrage opportunities are significant."
                ),
                data_point=pct,
                entity="Global workforce",
            ))
    except Exception as e:
        logger.warning(f"[ALERTS] scan_remote_work_alerts failed: {e}")

    return alerts


def scan_salary_alerts(db: Session) -> list[Alert]:
    """Flags notable salary growth signals."""
    alerts = []
    try:
        trends = salary_service.get_salary_trends(db, start_year=2023, end_year=2024)
        if len(trends) >= 2:
            latest = trends[-1]
            prev   = trends[-2]

            if latest.get("avg_salary_usd") and prev.get("avg_salary_usd"):
                growth = round(
                    (latest["avg_salary_usd"] - prev["avg_salary_usd"])
                    / prev["avg_salary_usd"] * 100, 1
                )
                if growth >= THRESHOLDS["salary_growth_info"]:
                    alerts.append(Alert(
                        severity="info",
                        category="salary_shift",
                        title=f"Global salary growth: +{growth}% YoY",
                        message=(
                            f"Global average salary grew {growth}% YoY to "
                            f"${latest['avg_salary_usd']:,.2f} USD in 2024. "
                            f"This outpaces typical inflation and signals strong "
                            f"talent demand across tracked markets."
                        ),
                        data_point=growth,
                        entity="Global salary average",
                    ))
    except Exception as e:
        logger.warning(f"[ALERTS] scan_salary_alerts failed: {e}")

    return alerts


# =============================================================================
# MAIN SCANNER
# =============================================================================

def run_smart_alerts(db: Session) -> dict:
    """
    Runs all alert scanners and returns a unified alert report.

    Each scanner is independent — if one fails, others still run.
    This is the same resilience pattern used in production monitoring systems.

    Returns:
        dict with keys:
          alerts         → list of Alert dicts sorted by severity
          alert_count    → total number of alerts
          critical_count → number of critical alerts
          warning_count  → number of warning alerts
          info_count     → number of info alerts
          scanned_at     → ISO timestamp
    """
    logger.info("[ALERTS] Running smart alert scan...")

    all_alerts: list[Alert] = []
    all_alerts.extend(scan_skill_alerts(db))
    all_alerts.extend(scan_automation_risk_alerts(db))
    all_alerts.extend(scan_remote_work_alerts(db))
    all_alerts.extend(scan_salary_alerts(db))

    # Sort: critical first, then warning, then info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    all_alerts.sort(key=lambda a: severity_order.get(a.severity, 99))

    # Count by severity
    critical = sum(1 for a in all_alerts if a.severity == "critical")
    warning  = sum(1 for a in all_alerts if a.severity == "warning")
    info     = sum(1 for a in all_alerts if a.severity == "info")

    logger.info(
        f"[ALERTS] Scan complete. total={len(all_alerts)} "
        f"critical={critical} warning={warning} info={info}"
    )

    return {
        "alerts": [
            {
                "severity":   a.severity,
                "category":   a.category,
                "title":      a.title,
                "message":    a.message,
                "data_point": a.data_point,
                "entity":     a.entity,
            }
            for a in all_alerts
        ],
        "alert_count":    len(all_alerts),
        "critical_count": critical,
        "warning_count":  warning,
        "info_count":     info,
        "scanned_at":     datetime.now(timezone.utc).isoformat(),
    }