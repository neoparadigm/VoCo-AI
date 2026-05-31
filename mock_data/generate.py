#!/usr/bin/env python3
"""
VoCo Mock Data Generator
Anonymized enterprise incident scenarios for demo.
No real customer names. No real locations.
"""

import json
from datetime import datetime


def scenario_device_provisioning() -> dict:
    return {
        "id": "INC-2026-0847",
        "title": "Device Provisioning Cascade Failure",
        "scenario_key": "provisioning",
        "severity": "P1",
        "region": "Region-Alpha",
        "timestamp_start": "2026-05-29T08:04:00Z",
        "timestamp_resolved": "2026-05-29T14:07:00Z",
        "duration_minutes": 363,
        "servicenow": {
            "tickets": [
                {
                    "number": "INC0847891",
                    "priority": "P1",
                    "title": "Regional device provisioning outage",
                    "description": "87 devices stuck at Pending Activation since 08:04",
                    "created": "2026-05-29T08:04:00Z",
                    "resolved": "2026-05-29T14:07:00Z",
                    "affected_users": 87,
                    "business_impact": "Complete regional deployment halt",
                    "assignment_group": "Regional Platform Operations"
                },
                {
                    "number": "INC0847892",
                    "priority": "P2",
                    "title": "Enrollment timeouts in office cluster A",
                    "created": "2026-05-29T08:15:00Z",
                    "resolved": "2026-05-29T14:07:00Z",
                    "affected_users": 34
                },
                {
                    "number": "INC0847893",
                    "priority": "P2",
                    "title": "Deployment queue stalled in office cluster B",
                    "created": "2026-05-29T08:22:00Z",
                    "resolved": "2026-05-29T14:07:00Z",
                    "affected_users": 28
                }
            ],
            "total_p1": 1,
            "total_p2": 2,
            "sla_breach": True,
            "sla_target_hours": 4,
            "actual_resolution_hours": 6.05
        },
        "m365": {
            "failed_enrollments": 87,
            "enrollment_window": "15 minutes",
            "error_distribution": {
                "ENROLLMENT_TIMEOUT": 45,
                "DNS_RESOLUTION_FAILURE": 35,
                "NETWORK_UNREACHABLE": 7
            },
            "enrollment_error_rate_pct": 87,
            "total_attempted": 100
        },
        "intune": {
            "device_states": {
                "Pending_Activation": 87,
                "Failed": 0,
                "Enrolled": 0
            },
            "enrollment_timeout_seconds": 900,
            "network_check_enabled": True,
            "retry_log": [
                {"attempt": 1, "latency_ms": 3200, "status": "pending"},
                {"attempt": 2, "latency_ms": 2850, "status": "pending"},
                {"attempt": 3, "latency_ms": 4100, "status": "pending"}
            ]
        },
        "network_metrics": {
            "primary_dns_latency_ms": 3200,
            "dns_baseline_ms": 45,
            "latency_spike_multiplier": 71.1,
            "failover_threshold_ms": 5000,
            "failover_triggered": False,
            "backup_dns_configured": False,
            "correlation_to_enrollment_failure": 0.94,
            "confidence_score": 0.98
        },
        "incident_context": {
            "first_alert": "2026-05-29T08:09:00Z",
            "total_mentions": 47,
            "channels": ["#incidents", "#platform-ops", "#escalation"],
            "sentiment_timeline": [
                {"time": "08:09", "sentiment": "critical"},
                {"time": "09:30", "sentiment": "investigating"},
                {"time": "12:00", "sentiment": "escalated"},
                {"time": "14:00", "sentiment": "resolving"},
                {"time": "14:07", "sentiment": "resolved"}
            ]
        },
        "root_cause_analysis": {
            "primary_cause": "DNS service degradation in regional datacenter",
            "contributing_factors": [
                "Cloud failover threshold set to 5000ms (too high for enrollment context)",
                "Device enrollment retry logic marginal under 3.2s DNS latency",
                "No backup DNS provider configured for region",
                "Network degradation not auto-detected before retry exhaustion"
            ],
            "correlation_score": 0.94,
            "confidence": "High",
            "reasoning_chain": [
                "OBSERVE: 87 devices stuck in 15-min window starting 08:04",
                "CORRELATE: DNS latency 3200ms vs baseline 45ms (71x spike), correlation 0.94",
                "ANALYZE: Failover threshold 5000ms > spike 3200ms, so failover never triggered",
                "ANALYZE: Enrollment timeout 900s with repeated 3.2s DNS lookups creates cascade",
                "CONCLUDE: Primary DNS degraded, failover too slow to protect enrollment flow",
                "RECOMMEND: Lower threshold + add backup DNS + workaround policy override"
            ]
        },
        "remediation": {
            "immediate": {
                "action": "Deploy enrollment policy override (disable network verification check)",
                "time_to_implement_minutes": 30,
                "recovery_time_minutes": 15,
                "devices_recovered": 87
            },
            "same_day": {
                "action": "Lower cloud failover threshold from 5000ms to 1000ms",
                "time_hours": 2,
                "risk": "Low"
            },
            "this_sprint": {
                "action": "Add redundant DNS provider for all regions",
                "story_points": 13,
                "deadline": "2026-06-15"
            }
        }
    }


def scenario_dns_failover() -> dict:
    return {
        "id": "INC-2026-0612",
        "title": "DNS Failover Degradation in Remote Datacenter",
        "scenario_key": "dns_failover",
        "severity": "P1",
        "region": "Remote-Datacenter-Beta",
        "timestamp_start": "2026-03-15T02:17:00Z",
        "timestamp_resolved": "2026-03-15T04:32:00Z",
        "duration_minutes": 135,
        "context": "Enterprise deploying mobile device management to 5000+ distributed users. Hybrid DNS (on-prem primary + cloud fallback). Primary DNS lost connectivity during maintenance window.",
        "servicenow": {
            "tickets": [
                {
                    "number": "INC0612441",
                    "priority": "P1",
                    "title": "Remote datacenter enrollment outage",
                    "description": "2847 devices unable to complete enrollment",
                    "affected_users": 2847
                },
                {
                    "number": "INC0612442",
                    "priority": "P1",
                    "title": "DNS resolution failures across all device types",
                    "affected_users": 2847
                }
            ],
            "total_p1": 2,
            "total_p2": 5,
            "incident_response_time_minutes": 8,
            "root_cause_identification_minutes": 45
        },
        "network_architecture": {
            "primary_dns": "On-premises primary (192.168.1.x)",
            "failover_dns": "Public fallback (external DNS)",
            "failover_strategy": "Manual (not automated)",
            "failover_timeout_seconds": 30,
            "issue": "30s timeout too long for device enrollment flow (900s total)"
        },
        "impact": {
            "devices_affected": 2847,
            "business_hours_lost": 2.25,
            "estimated_productivity_loss_usd": 67000
        },
        "root_cause_analysis": {
            "primary_cause": "Primary DNS connectivity loss with 30-second failover timeout exceeding safe enrollment window",
            "contributing_factors": [
                "Failover detection timeout 30s (safe for web, too long for enrollment)",
                "No automatic failover — requires manual intervention",
                "No local DNS redundancy configured at datacenter",
                "Primary DNS health monitoring not alerting proactively"
            ],
            "correlation_score": 0.97,
            "confidence": "High",
            "reasoning_chain": [
                "OBSERVE: 2847 enrollment failures beginning 02:17, all same error class",
                "CORRELATE: Primary DNS offline at 02:17:00Z, enrollment failures at 02:17:15Z (15s lag)",
                "ANALYZE: 30s failover timeout means 30s of DNS failure before fallback engaged",
                "ANALYZE: Device enrollment retry budget consumed during 30s timeout window",
                "CONCLUDE: Manual failover + 30s timeout incompatible with enrollment flow timing",
                "RECOMMEND: Reduce failover timeout to 5s, automate failover, add local redundancy"
            ]
        },
        "remediation": {
            "immediate": {"action": "Manual DNS failover to public fallback", "time_minutes": 5},
            "same_day": {"action": "Reduce failover timeout from 30s to 5s", "time_hours": 1},
            "this_sprint": {
                "action": "Implement automated DNS failover with health monitoring",
                "story_points": 8
            }
        }
    }


def scenario_cloud_migration() -> dict:
    return {
        "id": "MIG-2026-0089",
        "title": "Cloud Migration Blocked: Security Compliance Failure",
        "scenario_key": "migration",
        "severity": "P0 (Program Critical)",
        "type": "Migration Blocker",
        "program": "Legacy API Deprecation (Oct 2026 hard deadline)",
        "timestamp": "2026-05-20T09:00:00Z",
        "migration_scope": {
            "total_api_calls_annually": 817000000,
            "applications_affected": 234,
            "teams_involved": 12,
            "timeline_remaining_days": 133,
            "deadline": "2026-10-01T23:59:59Z"
        },
        "blocker": {
            "issue_id": "SEC-2026-004781",
            "title": "Service Principal Credentials Exposed in Batch Migration Scripts",
            "severity": "High",
            "description": "Batch migration scripts store API credentials in plaintext config files. Security audit found 34 exposed credentials across 12 teams.",
            "affected_components": [
                "Legacy API Sync Service",
                "Data Migration Batch Job",
                "Authorization Delegation Service"
            ],
            "risk": "Unauthorized access to 817M annual API calls"
        },
        "migration_status": {
            "phase_1_assessment": {"status": "complete", "apps_ready": 67},
            "phase_2_pilot": {"status": "in_progress", "apps_migrated": 12, "apps_total": 234},
            "phase_3_production": {"status": "BLOCKED", "blocker": "SEC-2026-004781"},
            "phase_4_decommission": {"status": "pending"}
        },
        "servicenow": {
            "tickets": [
                {
                    "number": "SEC0004781",
                    "priority": "P0",
                    "title": "Critical: Credential exposure in migration pipeline",
                    "description": "34 service principal credentials exposed",
                    "created": "2026-05-20T09:00:00Z"
                }
            ],
            "risk_assessment": "High",
            "compliance_impact": "SOC2, ISO27001 violations possible"
        },
        "impact": {
            "if_unresolved_by_oct_2026": "817M API calls stop working - complete system outage",
            "estimated_cost_of_failure_usd": 5000000,
            "days_remaining": 133
        },
        "root_cause_analysis": {
            "primary_cause": "Batch migration scripts using static credential files without secrets management",
            "contributing_factors": [
                "No secrets scanning in CI/CD pipeline",
                "Teams used quickstart templates without security review",
                "No mandatory credential vault policy for migration projects",
                "Security review gating not enforced until Phase 3"
            ],
            "correlation_score": 0.99,
            "confidence": "High",
            "reasoning_chain": [
                "OBSERVE: Phase 3 blocked - security audit found 34 exposed credentials",
                "CORRELATE: All exposures trace to batch job config files in same template",
                "ANALYZE: Teams used unreviewed quickstart template with static credential pattern",
                "ANALYZE: CI/CD pipeline lacks secrets scanning, so issue undetected until audit",
                "CONCLUDE: Systemic issue - template problem, not isolated developer error",
                "RECOMMEND: Credential rotation + vault migration + CI/CD secrets scanner + template fix"
            ]
        },
        "remediation": {
            "week_1": {
                "action": "Rotate all 34 exposed credentials",
                "action2": "Deploy secrets scanning to CI/CD pipeline",
                "days": 7
            },
            "week_2_to_4": {
                "action": "Migrate all batch jobs to credential vault",
                "action2": "Update migration template with secure credential pattern",
                "days": 21
            },
            "week_5_onward": {
                "action": "Resume Phase 3 production migration",
                "action2": "Accelerate remaining 222 applications",
                "days_available": 98
            }
        },
        "critical_path": {
            "milestone_security_clear": "2026-06-15",
            "milestone_50pct_migrated": "2026-08-01",
            "milestone_95pct_migrated": "2026-09-15",
            "hard_deadline": "2026-10-01"
        }
    }


def generate():
    data = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "note": "All data is anonymized. No real customer names, no real locations.",
            "scenarios": 3
        },
        "incidents": [
            scenario_device_provisioning(),
            scenario_dns_failover(),
            scenario_cloud_migration()
        ]
    }
    with open("mock_data/incidents.json", "w") as f:
        json.dump(data, f, indent=2)
    print("mock_data/incidents.json generated")
    print("  Scenario 1: Device provisioning (87 devices, DNS issue)")
    print("  Scenario 2: DNS failover (2847 devices, remote datacenter)")
    print("  Scenario 3: Cloud migration blocker (817M API calls at risk)")


if __name__ == "__main__":
    generate()
