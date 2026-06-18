import os
import pickle
import numpy as np
from fastmcp import FastMCP

# 1. Initialize a clean, standalone MCP server instance
mcp = FastMCP("Leak-Detector-ML-Server")

# 2. Get the absolute path to your saved pickle file
MODEL_PATH = os.path.join(os.path.dirname(__file__),'..','ML', "leak_detector_model.pkl")

# 3. Load your trained XGBoost model right when the server boots up
try:
    with open(MODEL_PATH, "rb") as f:
        xgboost_model = pickle.load(f)
    print(f"[SUCCESS] Loaded {MODEL_PATH} into MCP memory.")
except Exception as e:
    print(f"[ERROR] Failed to load model file: {e}")
    xgboost_model = None

# 4. Turn your XGBoost model into an official open-protocol tool
@mcp.tool(
    name="predict_leak_risk",
    description="Takes live water pressure (PSI) and a secondary feature (e.g., historical average) to check for leaks using XGBoost."
)
def predict_leak_risk(current_psi: float, secondary_feature: float = 25.0) -> str:
    """
    Exposes the XGBoost model over standard MCP input/output streams.
    """
    if xgboost_model is None:
        return "ERROR: ML model artifact is not loaded on the server."
        
    try:
        # Pass BOTH features to match the expected shape of 2
        features = np.array([[current_psi, secondary_feature]])
        
        # Run real inference using your actual trained model weights!
        prediction = xgboost_model.predict(features)[0]
        
        return f"XGBOOST_ANALYSIS: Input_PSI={current_psi} | Prediction={prediction}"
        
    except Exception as e:
        return f"ERROR: Inference execution failed. Details: {str(e)}"
    
    
if __name__ == "__main__":
    # 5. Run the server over standard input/output (stdio)
    mcp.run()