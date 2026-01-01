import requests
import json

try:
    resp = requests.get("http://localhost:8001/api/v1/governance/risk/report", params={"days": 1}, timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data["summary"], indent=2))
        
        total = data.get("summary", {}).get("total_scans", 0)
        if total > 0:
            print("SUCCESS: Data found.")
        else:
            print("FAILURE: No data found.")
    else:
        print(f"Error: {resp.status_code}")
except Exception as e:
    print(f"Exception: {e}")
