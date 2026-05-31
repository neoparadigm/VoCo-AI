"""
Enterprise tools for VoCo agents.
Each tool queries a mock enterprise data source.
MCP-compatible pattern — replace with real API calls in production.
Uses crewai's @tool decorator (not langchain Tool).
"""

import json
import os
from crewai.tools import tool

# Resolve mock data path relative to project root
_HERE = os.path.dirname(os.path.abspath(__file__))
_MOCK_PATH = os.path.join(_HERE, "..", "..", "mock_data", "incidents.json")

with open(_MOCK_PATH, "r") as f:
    _mock = json.load(f)

_incidents = _mock.get("incidents", [])


def _find_incident(query: str) -> list:
    """Find relevant incidents based on keyword match."""
    q = query.lower()
    matches = []
    for inc in _incidents:
        title = inc.get("title", "").lower()
        key = inc.get("scenario_key", "").lower()
        if any(k in q for k in ["all", "everything", "latest", "current"]):
            matches.append(inc)
        elif key in q:
            matches.append(inc)
        elif "provision" in q and "provision" in title:
            matches.append(inc)
        elif "dns" in q and "dns" in title:
            matches.append(inc)
        elif "migrat" in q and "migrat" in title:
            matches.append(inc)
        elif "security" in q and "security" in title.lower():
            matches.append(inc)
        elif "region" in q and "region" in inc.get("region", "").lower():
            matches.append(inc)
    return matches if matches else _incidents


@tool("ServiceNow")
def servicenow_tool(query: str) -> str:
    """Query ServiceNow for incidents, tickets, SLA data, and business impact."""
    incidents = _find_incident(query)
    return json.dumps([i.get("servicenow", {}) for i in incidents], indent=2)


@tool("M365Metrics")
def m365_tool(query: str) -> str:
    """Query M365 for enrollment metrics, failure rates, and error distribution."""
    incidents = _find_incident(query)
    return json.dumps([i.get("m365", {}) for i in incidents if i.get("m365")], indent=2)


@tool("IntuneStatus")
def intune_tool(query: str) -> str:
    """Query Intune for device states, provisioning status, and retry logs."""
    incidents = _find_incident(query)
    return json.dumps([i.get("intune", {}) for i in incidents if i.get("intune")], indent=2)


@tool("InfraMetrics")
def metrics_tool(query: str) -> str:
    """Query infrastructure metrics: DNS latency, network health, failover state."""
    incidents = _find_incident(query)
    return json.dumps([i.get("network_metrics", {}) for i in incidents if i.get("network_metrics")], indent=2)


@tool("IncidentContext")
def context_tool(query: str) -> str:
    """Query incident context: timeline, alerts, team communication, sentiment."""
    incidents = _find_incident(query)
    return json.dumps([i.get("incident_context", {}) for i in incidents if i.get("incident_context")], indent=2)


all_tools = [servicenow_tool, m365_tool, intune_tool, metrics_tool, context_tool]
