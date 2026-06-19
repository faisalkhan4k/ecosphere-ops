import streamlit as st
import os
import sys
import json
import io



# Locate our orchestrator class
sys.path.append(os.path.dirname(__file__))
from orchestrator import EcosphereMCPOrchestrator

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="Ecosphere Ops Control Center", page_icon="⚡", layout="wide")

st.title("⚡ Ecosphere Ops: Multi-Agent MCP Control Center")
st.markdown("Automated Infrastructure Remediation Loop Tracking (XGBoost + Cerebras + Ollama)")
st.write("---")

# Initialize our orchestrator instance
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = EcosphereMCPOrchestrator()

# --- SIDEBAR: CONTROL & TELEMETRY INJECTION ---
st.sidebar.header("🚨 Telemetry Injection Panel")

alert_profile = st.sidebar.selectbox(
    "Select Incident Profile Alert Text:",
    [
        "CRITICAL TELEMETRY: Anomalous friction profile detected in Sector_4 line manifolds.",
        "WARNING: Minor pressure fluctuations observed in Sector_4 pipeline junctions.",
        "SYSTEM HEALTH CHECK: Standard periodic maintenance scan sequence active."
    ]
)

input_psi = st.sidebar.slider("Current Telemetry Line Pressure (PSI):", min_value=10.0, max_value=60.0, value=34.2, step=0.1)

trigger_loop = st.sidebar.button("Run Multi-Agent Incident Response", type="primary")

# --- MAIN LAYOUT: SPLIT COLS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🖥️ Live Agent Processing Logs")
    log_area = st.empty()
    log_area.info("Awaiting telemetry incident injection execution...")

    if trigger_loop:
        with st.spinner("Executing autonomous agent loop..."):
            # Capture standard output stream to print terminal logs live into the UI!
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                # Trigger the real agent orchestration process
                st.session_state.orchestrator.run_incident_response(alert_profile, input_psi)
                captured_logs = buffer.getvalue()
            except Exception as e:
                captured_logs = f"An error occurred: {str(e)}"
            finally:
                sys.stdout = old_stdout
            
            # Format and display the terminal logs nicely
            log_area.text_area("Console Stream Output:", value=captured_logs, height=450)

with col2:
    st.subheader("🔒 Active Hardware State Register")
    
    # Read the simulation JSON file to display real active states
    state_file_path = os.path.join(os.path.dirname(__file__), "system_hardware_state.json")
    
    if os.path.exists(state_file_path):
        with open(state_file_path, "r") as f:
            current_hardware_state = json.load(f)
        
        # Display clean visual alert cards based on state values
        sector_status = current_hardware_state.get("Sector_4", {}).get("status", "UNKNOWN")
        valve_status = current_hardware_state.get("Sector_4", {}).get("valve_V-S4-01", "UNKNOWN")
        sensor_status = current_hardware_state.get("Sensor_Deployment", {}).get("ultrasonic_active", False)
        
        if sector_status == "ISOLATED":
            st.error(f"🔴 Sector 4 Status: {sector_status}")
        else:
            st.success(f"🟢 Sector 4 Status: {sector_status}")
            
        st.metric(label="Main Valve V-S4-01 Position", value=valve_status)
        
        if sensor_status:
            st.warning("📡 Supplemental Ultrasonic Diagnostic Array: ACTIVATED")
        else:
            st.info("📡 Supplemental Ultrasonic Diagnostic Array: OFF")
            
        st.write("### Raw Hardware State JSON Vector:")
        st.json(current_hardware_state)
    else:
        st.warning("Hardware environment simulation database file not detected.")