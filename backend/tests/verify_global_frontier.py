
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def verify_global_registry():
    print("=== GLOBAL FRONTIER REGISTRY VERIFICATION (2025/2026) ===\n")
    
    # 1. Test Model Listing
    print("Fetching Model Registry...")
    try:
        resp = requests.get(f"{BASE_URL}/v1/models")
        if resp.status_code == 200:
            models = [m["id"] for m in resp.json().get("data", [])]
            print(f"✅ REGISTRY OK. Found {len(models)} models.")
            for m in ["gpt-4.5-preview", "claude-3-7-sonnet", "deepseek-r1", "sonar-deep-research"]:
                if m in models:
                    print(f"   [+] Verified: {m}")
                else:
                    print(f"   [X] Missing: {m}")
        else:
            print(f"❌ FAILED to fetch registry: {resp.status_code}")
    except Exception as e:
        print(f"‼️ ERROR in registry check: {e}")

    # 2. Test Dynamic Routing Logic (Prefix Detection)
    test_cases = [
        {"model": "gpt-4.5-preview", "desc": "OpenAI Frontier"},
        {"model": "claude-3-7-sonnet", "desc": "Anthropic Frontier"},
        {"model": "deepseek-v3", "desc": "DeepSeek Frontier"},
        {"model": "sonar-deep-research", "desc": "Perplexity Frontier"}
    ]
    
    print("\nVerifying Prefix-Based Routing...")
    for case in test_cases:
        print(f"Testing {case['desc']} ({case['model']})...")
        try:
            # We use a short timeout because if it gets to upstream and fails with 402/429, 
            # it means our INTERNAL routing to the provider worked.
            resp = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": case["model"],
                    "messages": [{"role": "user", "content": "hi"}]
                },
                timeout=10
            )
            # If we get 402, 429, or 200, it means it reached the upstream correctly.
            if resp.status_code in [200, 402, 429]:
                 print(f"✅ ROUTING OK: Model reached upstream (Status: {resp.status_code})")
            else:
                 print(f"⚠️ ROUTING UNKNOWN: Received {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"‼️ ERROR in routing check: {e}")
        print("-" * 30)

if __name__ == "__main__":
    verify_global_registry()
