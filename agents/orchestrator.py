import os
import sys
import re
import json
import time
import mlflow
from dotenv import load_dotenv

import sys
import io

original_builtin_print = print

def safe_print(*args, **kwargs):
    """Custom print wrapper that safely encodes special cloud chars to UTF-8
    without causing infinite recursion loop crashes."""
    try:
        msg = " ".join(map(str, args))
        # Safely encode to utf-8 and write straight to the active console buffer
        sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b'\n')
        sys.stdout.flush()
    except (AttributeError, ValueError):
        # Fallback to the ORIGINAL python printer so we never infinite-loop
        original_builtin_print(*args, **kwargs)

# Reassign print globally for this file execution path
print = safe_print

# Ensure python can locate our gateway layer
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gateway.llm_gateway import route_llm_request
from leak_detector_server import predict_leak_risk

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class EcosphereMCPOrchestrator:
    def __init__(self):
        self.state_file = os.path.join(os.path.dirname(__file__), "system_hardware_state.json")
        self._initialize_hardware_state()
        
        # Configure MLflow to track our operational production deployment loops
        
        mlflow.set_tracking_uri("sqlite:///mlflows.db")
        mlflow.set_experiment("Ecosphere_Ops_Production_Orchestration")

    def _initialize_hardware_state(self):
        default_state = {
            "Sector_4": {"status": "OPERATIONAL", "valve_V-S4-01": "OPEN"},
            "Sensor_Deployment": {"ultrasonic_active": False}
        }
        with open(self.state_file, "w") as f:
            json.dump(default_state, f, indent=4)
        print("[SYSTEM] Hardware environment simulation reset to default baseline.")

    def parse_specialist_payload(self, raw_text: str) -> dict:
        commands = {"isolate_sector": None, "target_valve": None, "deploy_sensor": None}
        sector_match = re.search(r"(?:Sector\s*|SECTOR_)(\d+)", raw_text, re.IGNORECASE)
        valve_match = re.search(r"(?:valve\s*|VALVE=)(V-[A-Z0-9-]+)", raw_text, re.IGNORECASE)
        sensor_match = re.search(r"(ultasonic|ultrasonic|AE sensors|sensor)", raw_text, re.IGNORECASE)

        if sector_match: commands["isolate_sector"] = int(sector_match.group(1))
        if valve_match: commands["target_valve"] = valve_match.group(1).upper()
        if sensor_match: commands["deploy_sensor"] = "ULTRASONIC_AE"
        return commands

    def execute_hardware_overrides(self, parsed_actions: dict) -> str:
        """Takes structured dict and patches local system state files."""
        print("\n[EXECUTION ENGINE] Initiating physical infrastructure overrides...")
        with open(self.state_file, "r") as f:
            current_state = json.load(f)

        actions_taken = []

        if parsed_actions["isolate_sector"] and parsed_actions["target_valve"]:
            sector_key = f"Sector_{parsed_actions['isolate_sector']}"
            valve_key = f"valve_{parsed_actions['target_valve']}"
            if sector_key in current_state:
                current_state[sector_key]["status"] = "ISOLATED"
                current_state[sector_key][valve_key] = "CLOSED"
                log_msg = f"Sector {parsed_actions['isolate_sector']} isolated via closing {valve_key}"
                actions_taken.append(log_msg)
                print(f" [CRITICAL ACTION] {log_msg}")

        if parsed_actions["deploy_sensor"] == "ULTRASONIC_AE":
            current_state["Sensor_Deployment"]["ultrasonic_active"] = True
            log_msg = "Activated supplemental ultrasonic acoustic emissions diagnostic array"
            actions_taken.append(log_msg)
            print(f" [CRITICAL ACTION] {log_msg}")

        if actions_taken:
            with open(self.state_file, "w") as f:
                json.dump(current_state, f, indent=4)
            print("[EXECUTION ENGINE SUCCESS] Local hardware configuration strings successfully patched.")
            return "; ".join(actions_taken)
        else:
            print("[EXECUTION ENGINE WARNING] No executable patterns identified.")
            return "No actions executed"

    def run_incident_response(self, alert_text: str, telemetry_psi: float):
        print(f"\n==================================================")
        print(f"🚨 NEW SYSTEM ALERT INGESTED: {alert_text}")
        print(f"==================================================")

        # Force clear any leaked background runs hanging in the session cache
        if mlflow.active_run():
            mlflow.end_run()

        # Start a clean, tracked transaction block
        active_run = mlflow.start_run(run_name="Incident_Response_Telemetry_Event")
        try:
            # Log variables immediately to the database
            mlflow.log_param("input_telemetry_psi", telemetry_psi)
            mlflow.log_param("alert_incident_profile", alert_text)

            # 1. XGBoost Predictor Tool Run
            print("\n[STEP 1] Orchestrator invoking Local XGBoost MCP Server Tool...")
            ml_tool_result = predict_leak_risk(current_psi=telemetry_psi, secondary_feature=25.0)
            print(f"[MCP TOOL RESPONSE] -> {ml_tool_result}")
            mlflow.log_param("xgboost_tool_raw_output", ml_tool_result)

            # Guardrail calculation
            is_model_safe = "Prediction=0" in ml_tool_result
            guardrail_triggered = False
            if is_model_safe and (telemetry_psi > 30.0 or "CRITICAL" in alert_text.upper()):
                guardrail_triggered = True
                print("\n⚠️ [GUARDRAIL TRIGGERED] Telemetry limits violated!")
                mlflow.log_param("guardrail_override_activated", "TRUE")
            else:
                mlflow.log_param("guardrail_override_activated", "FALSE")

            # 2. Cerebras Master Planner Run
            print("\n[STEP 2] Routing context to Master Orchestrator (Cerebras Cloud)...")
            guardrail_context = "CRITICAL DIRECTIVE: The ML prediction model returned a potential False Negative." if guardrail_triggered else ""
            orchestrator_prompt = (
                "[SYSTEM CONTEXT]\n"
                "You are the Lead Reliability Architect for an automated infrastructure control loop.\n"
                "Analyze the operational inputs below and synthesize a high-level containment strategy.\n\n"
                "[CRITICAL DIRECTIVE]\n"
                f"{guardrail_context if guardrail_triggered else 'Evaluate if current system parameters match the incident profile.'}\n\n"
                "[INPUT PARAMETERS]\n"
                f"- Ingested Alert: {alert_text}\n"
                f"- ML Model Diagnostic: {ml_tool_result}\n\n"
                "[RESPONSE REQUIREMENT]\n"
                "Provide a strict, bulleted 2-sentence tactical synthesis for the engineering team. No conversational filler."
            )            
            start_cerebras = time.time()
            synthesis = route_llm_request(orchestrator_prompt, model_type="general")
            cerebras_latency = time.time() - start_cerebras
            print(f"[CEREBRAS ANALYSIS]:\n{synthesis}\n")
            mlflow.log_metric("latency_cerebras_seconds", float(cerebras_latency))

            # 3. Ollama Technical Sub-Agent Run
            print("[STEP 3] Routing context to Technical Specialist Sub-Agent (Ollama)...")
            specialist_prompt = (
                "[SYSTEM CONTEXT]\n"
                "You are a machine-instruction translation engine for industrial hardware actuators.\n\n"
                "[INPUT ANALYSIS CONTEXT]\n"
                f"{synthesis}\n\n"
                "[STRICT FORMAT REQUIREMENT]\n"
                "You must output exactly two lines using the following format keys. Substitute the brackets with the values identified from the analysis context. Do not write an introductory text or conversational sign-off.\n\n"
                "SECTOR: [Insert Sector Number Only, e.g., 4]\n"
                "VALVE: [Insert Alphanumeric Valve ID Only, e.g., V-S4-01]"
            )
            
            start_ollama = time.time()
            raw_specialist_output = route_llm_request(specialist_prompt, model_type="specialist")
            ollama_latency = time.time() - start_ollama
            print(f"[LOCAL BASE QWEN OUTPUT]:\n{raw_specialist_output}\n")
            mlflow.log_metric("latency_ollama_seconds", float(ollama_latency))

            # 4. Intercept and Parse Text into Machine Instructions
            parsed_actions = self.parse_specialist_payload(raw_specialist_output)
            
            # 5. Run and track Hardware Overrides
            execution_summary = self.execute_hardware_overrides(parsed_actions)
            mlflow.log_param("executed_mitigation_actions", execution_summary)
            
            print("\n==================================================")
            print("[STATUS] Run block finished successfully.")
            print("==================================================")

        except Exception as e:
            print(f"❌ [PIPELINE ERROR] Critical error during tracking: {str(e)}")
            raise e
        finally:
            # THIS FORCE FLUSHES THE METRICS TO SQLITE DISK BEFORE WE EXIT
            print("[MLFLOW] Safely closing active session and flushing tables...")
            mlflow.end_run()

if __name__ == "__main__":
    live_alert = "CRITICAL TELEMETRY: Anomalous friction profile detected in Sector_4 line manifolds."
    live_psi = 34.2
    
    manager = EcosphereMCPOrchestrator()
    manager.run_incident_response(live_alert, live_psi)