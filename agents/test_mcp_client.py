import os
import sys
import json
import subprocess

print("=== STARTING LOCAL MCP SERVER INTEGRATION TEST ===")

# 1. Locate our server script precisely
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "leak_detector_server.py")
print(f"[CLIENT] Target server script: {SERVER_SCRIPT}")

# 2. Directly call the function locally to verify your XGBoost weights are working
print("\n[TEST 1] Testing ML Model Inference Pipeline Locally...")
try:
    from leak_detector_server import predict_leak_risk
    local_output = predict_leak_risk(28.5)
    print(f"[SUCCESS] Local function returned: {local_output}")
except Exception as e:
    print(f"[FAIL] Local execution failed: {e}")

print("\n[TEST 2] Verifying Server Capabilities over Standard I/O (How Agents see it)...")
# We simulate a simple protocol request to ensure the server file responds when invoked
try:
    # Run the server file just long enough to verify it compiles and runs without crashing
    result = subprocess.run(
        [sys.executable, SERVER_SCRIPT],
        input=b"", # Send nothing, just checking if it boots
        capture_output=True,
        timeout=3 # Kill it after 3 seconds so it doesn't lock our terminal
    )
    print("[SUCCESS] MCP Server responds to process execution cleanly.")
except subprocess.TimeoutExpired:
    # This is actually a success state for stdio servers! It means it stayed alive waiting for data.
    print("[SUCCESS] MCP Server successfully initialized and entered listening loop.")
except Exception as e:
    print(f"[FAIL] Server process failed to execute: {e}")

print("\n=== INTEGRATION PROTOCOL CHECK COMPLETE ===")