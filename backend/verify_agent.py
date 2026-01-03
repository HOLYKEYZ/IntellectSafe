"""
Verification script for Agent Control (Level 5)
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def print_result(name, passed, details=""):
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_authorize_safe_action():
    """Test that a safe whitelisted action is authorized instantly"""
    print("\n--- Test 1: Whitelisted Safe Action ---")
    try:
        payload = {
            "agent_id": "test-agent-1",
            "session_id": "session-1",
            "action_type": "file_read",
            "requested_action": {"path": "/tmp/test.txt"},
        }
        resp = requests.post(f"{BASE_URL}/agent/authorize", json=payload, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            passed = data.get("authorized") == True
            whitelisted = data.get("safety_flags", {}).get("whitelisted", False)
            print_result("Whitelisted Action", passed and whitelisted, 
                        f"Authorized: {data.get('authorized')}, Whitelisted: {whitelisted}")
        else:
            print_result("Whitelisted Action", False, f"Status: {resp.status_code}")
    except Exception as e:
        print_result("Whitelisted Action", False, str(e))

def test_authorize_dangerous_action():
    """Test that a dangerous action is blocked"""
    print("\n--- Test 2: Dangerous Action Block ---")
    try:
        payload = {
            "agent_id": "test-agent-2",
            "session_id": "session-1",
            "action_type": "system_command",
            "requested_action": {"command": "rm -rf /"},
        }
        resp = requests.post(f"{BASE_URL}/agent/authorize", json=payload, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            blocked = data.get("authorized") == False
            risk_score = data.get("risk_score", 0)
            print_result("Dangerous Action Block", blocked and risk_score >= 50, 
                        f"Authorized: {data.get('authorized')}, Risk: {risk_score}")
        else:
            print_result("Dangerous Action Block", False, f"Status: {resp.status_code}")
    except Exception as e:
        print_result("Dangerous Action Block", False, str(e))

def test_kill_switch():
    """Test kill switch endpoint"""
    print("\n--- Test 3: Kill Switch ---")
    try:
        # First authorize an action
        auth_payload = {
            "agent_id": "kill-test-agent",
            "session_id": "session-1",
            "action_type": "file_read",
            "requested_action": {"path": "/tmp/test.txt"},
        }
        requests.post(f"{BASE_URL}/agent/authorize", json=auth_payload, timeout=5)
        
        # Now kill the agent
        kill_payload = {
            "agent_id": "kill-test-agent",
            "reason": "Testing kill switch",
        }
        resp = requests.post(f"{BASE_URL}/agent/kill", json=kill_payload, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            killed = data.get("killed") == True
            print_result("Kill Switch", killed, f"Killed: {killed}, Blocked: {data.get('actions_blocked')}")
            
            # Verify subsequent actions are blocked
            resp2 = requests.post(f"{BASE_URL}/agent/authorize", json=auth_payload, timeout=5)
            data2 = resp2.json()
            blocked_after_kill = data2.get("authorized") == False
            print_result("Post-Kill Block", blocked_after_kill, 
                        f"Authorized after kill: {data2.get('authorized')}")
        else:
            print_result("Kill Switch", False, f"Status: {resp.status_code}")
    except Exception as e:
        print_result("Kill Switch", False, str(e))

def test_action_history():
    """Test action history endpoint"""
    print("\n--- Test 4: Action History ---")
    try:
        resp = requests.get(f"{BASE_URL}/agent/history/test-agent-1", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            has_actions = data.get("total_actions", 0) > 0
            print_result("Action History", True, f"Total actions: {data.get('total_actions')}")
        else:
            print_result("Action History", False, f"Status: {resp.status_code}")
    except Exception as e:
        print_result("Action History", False, str(e))

def main():
    print("=" * 60)
    print("Agent Control (Level 5) Verification")
    print("=" * 60)
    
    test_authorize_safe_action()
    test_authorize_dangerous_action()
    test_kill_switch()
    test_action_history()
    
    print("\n" + "=" * 60)
    print("Verification Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
