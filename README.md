# Adaptive Retry Circuit Breaker Skill for Autonomous Agents

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

Resilience and fault-tolerance engine protecting multi-agent pipelines from cascade outages, API rate limit exhaustion, and unstable external web services.

## Core Features
- **Finite State Machine**: Seamlessly manages `CLOSED`, `OPEN`, and `HALF_OPEN` states.
- **Exponential Backoff with Full Jitter**: Prevents thundering herd problems when upstream APIs recover.
- **Fail-Fast Defense**: Immediately rejects downstream requests when a service is degraded, preventing timeout latency spikes.

## MCP Server Integration
```bash
python mcp_server.py
```

### Available MCP Tools
- `check_execution_allowed`: Query if a target service endpoint is healthy and requests are permitted.
- `report_result`: Record success or failure to trigger state transitions.
- `get_breaker_state`: Get current breaker status, failure metrics, and recovery timers.
