
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_frontier_models():
    print("=== FRONTIER MODEL PROXY VERIFICATION ===\n")
    
    frontier_tests = [
        {"id": "gpt-4o", "payload": "Say 'IntellectSafe secured OpenAI'"},
        {"id": "claude-3-5-sonnet", "payload": "Say 'IntellectSafe secured Anthropic'"},
        {"id": "grok-2", "payload": "Say 'IntellectSafe secured xAI'"},
        {"id": "copilot-secure-bridge", "payload": "Write a hello world in Python"}
    ]

    for test in frontier_tests:
        print(f"Testing Frontier Model: {test['id']}...")
        try:
            resp = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": test["id"],
                    "messages": [{"role": "user", "content": test["payload"]}]
                },
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                safety = data.get("intellectsafe", {})
                print(f"✅ SUCCESS: {test['id']} responded.")
                print(f"   Safety Status: {safety}")
                print(f"   Content Preview: {content[:40]}...")
            else:
                print(f"❌ FAILED: {test['id']} returned {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"‼️ ERROR testing {test['id']}: {e}")
        print("-" * 40)

if __name__ == "__main__":
    test_frontier_models()
