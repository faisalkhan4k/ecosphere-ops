# ⚡ Ecosphere Ops: Multi-Agent Automated MCP Control Center

This repository implements a resilient, closed-loop multi-agent automation platform for critical smart city infrastructure remediation. It utilizes a localized machine learning classifier alongside a hybrid multi-agent consensus architecture to ingest telemetry, override predictive errors via industrial guardrails, and dynamically isolate hardware hazards.

## Architecture Workflow

* **Input:** Raw sensor alert logs and real-time line pressure (PSI) inputs.
* **Tool 1 (Local ML):** A localized `XGBoost` classifier (`leak_detector_model.pkl`) evaluates incoming data to output an initial safety prediction.
* **State Intercept (Guardrail):** A deterministic python safety loop intercepts the pipeline. If telemetry tolerances are crossed, it overrides a false-negative ML output live.
* **Agent 1 (Cloud LLM):** `Cerebras Cloud API` acts as the Master Architect, ingesting the alert and generating a high-level tactical response strategy.
* **Agent 2 (Local LLM):** A local `Ollama Qwen` instance acts as the Action Specialist, translating the high-level strategy into strict technical instructions.
* **State Transfer (Regex & I/O Tools):** Pre-compiled regular expressions strip conversational text, handing raw variables to local execution tools to dynamically modify state registers (`system_hardware_state.json`).
* **Governance (MLflow MLOps):** Every single run lifecycle automatically syncs inputs, latencies, and execution summaries to a localized `MLflow` SQLite backend for audit tracking.
