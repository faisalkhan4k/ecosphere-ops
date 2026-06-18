import os
import sys
import subprocess
from dotenv import load_dotenv

# Ensure python can locate our gateway layer
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gateway.llm_gateway import route_llm_request

from leak_detector_server import predict_leak_risk

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class EcosphereMCPOrchestrator:
    def __init__(self):
        print("[ORCHESTRATOR] Initializing Multi-Agent MCP Control Loop...")

    def run_incident_response(self, alert_text: str, telemetry_psi: float):
        print(f"\n==================================================")
        print(f"🚨 NEW SYSTEM ALERT INGESTED: {alert_text}")
        print(f"==================================================")

        # STEP 1: Execute your local XGBoost MCP tool dynamically
        print("\n[STEP 1] Orchestrator invoking Local XGBoost MCP Server Tool...")
        ml_tool_result = predict_leak_risk(current_psi=telemetry_psi, secondary_feature=25.0)
        print(f"[MCP TOOL RESPONSE] -> {ml_tool_result}")

        # STEP 2: Feed the real ML data into the Cerebras Master Architect
        print("\n[STEP 2] Routing context to Master Orchestrator (Cerebras Cloud)...")
        orchestrator_prompt = (
            f"Review this critical infrastructure alert alongside our XGBoost leak prediction model output. "
            f"Provide a brief engineering synthesis of what the team needs to act on.\n\n"
            f"Alert Context: {alert_text}\n"
            f"ML Model Analysis: {ml_tool_result}"
        )
        synthesis = route_llm_request(orchestrator_prompt, model_type="general")
        print(f"[CEREBRAS ANALYSIS]:\n{synthesis}\n")

        # STEP 3: Pass that rich summary directly to the local Qwen specialist
        print("[STEP 3] Routing synthesized context to Technical Specialist Sub-Agent (Ollama)...")
        specialist_prompt = (
            f"Based on this synthesized analysis, generate the exact deterministic system control strings "
            f"required to isolate the anomaly.\n\n"
            f"Analysis Context: {synthesis}"
        )
        technical_codes = route_llm_request(specialist_prompt, model_type="specialist")
        print(f"[LOCAL QWEN PAYLOAD]:\n{technical_codes}\n")
        print("==================================================")

if __name__ == "__main__":
    # Simulate a real live operational pipeline failure event stream
    live_alert = "CRITICAL TELEMETRY: Anomalous friction profile detected in Sector_4 line manifolds."
    live_psi = 34.2  # High pressure reading to pass to your model
    
    manager = EcosphereMCPOrchestrator()
    manager.run_incident_response(live_alert, live_psi)