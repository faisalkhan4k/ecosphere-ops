import numpy as np
import pandas as pd
import os

# Set seed for reproducibility
np.random.seed(42)

def generate_city_sensor_data(num_records=1000):
    print("Generating smart city sensor telemetry data...")
    
    # Generate continuous timestamps
    timestamps = pd.date_range(start="2026-01-01", periods=num_records, freq="h")
    
    # Normal baseline metrics for a city water node
    flow_rate = np.random.normal(loc=50.0, scale=4.0, size=num_records)  # Liters per second
    pressure = np.random.normal(loc=3.5, scale=0.2, size=num_records)    # Bars
    
    # Create a DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps,
        "sector_id": "Sector_4",
        "flow_rate_lps": flow_rate,
        "pressure_bar": pressure,
        "anomaly": 0  # 0 means normal, 1 means leak/breakdown
    })
    
    # Inject deliberate anomalies (e.g., pipe bursts)
    # A burst causes flow rate to spike (water rushing out) and pressure to drop sharply
    anomaly_indices = [150, 151, 152, 450, 451, 452, 780, 781, 782, 783]
    
    for idx in anomaly_indices:
        df.loc[idx, "flow_rate_lps"] = np.random.normal(loc=85.0, scale=3.0)
        df.loc[idx, "pressure_bar"] = np.random.normal(loc=1.2, scale=0.1)
        df.loc[idx, "anomaly"] = 1
        
    return df

if __name__ == "__main__":
    data = generate_city_sensor_data()
    
    # Make sure we save it inside the ML folder
    output_path = os.path.join(os.path.dirname(__file__), "water_sensors.csv")
    data.to_csv(output_path, index=False)
    print(f"Success! Generated data and saved to: {output_path}")
    print(f"Total anomalies injected: {data['anomaly'].sum()}")