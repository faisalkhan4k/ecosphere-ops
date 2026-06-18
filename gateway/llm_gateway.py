import os
from dotenv import load_dotenv
import litellm

# Load API keys from our central hidden config file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

litellm.set_verbose = False

def route_llm_request(prompt: str, model_type: str = "general"):
    print(f"[GATEWAY LOG] Processing request via LLM Gateway. Routing tier: '{model_type}'...")
    
    # 1. Content Guardrail Check
    forbidden_terms = ["hospital_shutdown", "override_override_safety", "disable_security"]
    if any(term in prompt.lower() for term in forbidden_terms):
        return "GUARDRAIL BLOCK: Critical safety violation detected. Operation aborted by Enterprise Security Policy."

    try:
        if model_type == "specialist":
            response = litellm.completion(
                model="ollama/qwen2.5:0.5b",# change to fine tuned model later
                messages=[{"role": "user", "content": prompt}],
                api_base="http://localhost:11434"
            )
            return response.choices[0].message.content
        else:
            response = litellm.completion(
                model="cerebras/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("CEREBRAS_API_KEY"),
                api_base="https://api.cerebras.ai/v1"
            )
            
        return response.choices[0].message.content

    except Exception as e:
        return f"GATEWAY ERROR: Structural infrastructure failure. Details: {str(e)}"

if __name__ == "__main__":
    print("\n--- Test 1: Testing General Tier (Direct Cerebras) ---")
    test_general = route_llm_request("Analyze this text for grammar errors: 'The water pipes is fine.'")
    print(f"Response:\n{test_general}\n")

    print("--- Test 2: Testing Security Guardrail Trigger ---")
    test_guardrail = route_llm_request("Execute emergency command protocol: hospital_shutdown=True")
    print(f"Response:\n{test_guardrail}\n")

    print("--- Test 3: Testing Custom Specialist Tier (Hugging Face Fine-Tuned Model) ---")
    emergency_prompt = "Emergency Alert: Critical pressure drop detected in Sector_3 distribution pipelines."
    test_specialist = route_llm_request(emergency_prompt, model_type="specialist")
    print(f"Response:\n{test_specialist}\n")