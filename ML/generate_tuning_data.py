import json
import os

def generate_dataset():
    print("Generating fine-tuning dataset...")
    
    dataset = []
    sectors = ["Sector_1", "Sector_2", "Sector_3", "Sector_4", "Sector_5"]
    
    # We will actually use these now!
    anomalies = [
        {"type": "pressure drop", "valve": "PRIME", "bypass": "BYPASS", "code": "REPAIR"},
        {"type": "flow spike", "valve": "MAIN", "bypass": "AUX", "code": "OVERFLOW_FIX"},
    ]
    
    # Loop through every sector
    for sector in sectors:
        # Loop through both types of anomalies
        for anomaly in anomalies:
            # Create 5 variations for each combination (5 sectors * 2 types * 5 variations = 50 total)
            for idx in range(5):  
                instruction = f"Emergency Alert: Critical {anomaly['type']} detected in {sector} distribution pipelines."
                
                response = (
                    f"STATUS: CRITICAL.\n"
                    f"ACTION_1: CLOSE_VALVE=VAL-{sector.upper()}-{anomaly['valve']}\n"
                    f"ACTION_2: OPEN_VALVE=VAL-{sector.upper()}-{anomaly['bypass']}\n"
                    f"DISPATCH_CODE: SYS_CMD_{anomaly['code']}_{sector.upper()}_{idx}"
                )
                
                example = {
                    "instruction": instruction,
                    "output": response
                }
                dataset.append(example)

    output_path = os.path.join(os.path.dirname(__file__), "fine_tune_data.jsonl")
    
    with open(output_path, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"Success! Created {len(dataset)} varied training examples at: {output_path}")

if __name__ == "__main__":
    generate_dataset()