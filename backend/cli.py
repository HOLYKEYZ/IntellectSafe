
import argparse
import requests
import json
import sys
import os
import base64
from typing import Optional

# Configuration
API_BASE = "http://localhost:8001/api/v1"

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner():
    """Print the cool ASCII banner"""
    banner = f"""{CYAN}
    ██╗███╗   ██╗████████╗███████╗██╗     ██╗     ███████╗ ██████╗████████╗
    ██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ██╔════╝██╔════╝╚══██╔══╝
    ██║██╔██╗ ██║   ██║   █████╗  ██║     ██║     █████╗  ██║        ██║   
    ██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║     ██╔══╝  ██║        ██║   
    ██║██║ ╚████║   ██║   ███████╗███████╗███████╗███████╗╚██████╗   ██║   
    ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝   
    {RESET}{MAGENTA}                        SAFE  •  SECURE  •  CONTROLLED{RESET}
    """
    print(banner)

def print_result(verdict: str, score: float, explanation: str):
    """Print formatted scan result"""
    color = GREEN
    if verdict == "blocked":
        color = RED
    elif verdict == "flagged":
        color = YELLOW
    
    print(f"\n{BLUE}--- Scan Results ---{RESET}")
    print(f"Verdict: {BOLD}{color}{verdict.upper()}{RESET}")
    print(f"Risk Score: {color}{score}/100{RESET}")
    print(f"Explanation: {explanation}\n")

def scan_prompt(text: str):
    """Scan a prompt for injection"""
    url = f"{API_BASE}/scan/prompt"
    payload = {"prompt": text, "metadata": {"source": "cli"}}
    
    try:
        print(f"{BLUE}Scanning prompt...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print_result(data["verdict"], data["risk_score"], data["explanation"])
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def scan_output(text: str, prompt: str):
    """Scan output for safety"""
    url = f"{API_BASE}/scan/output"
    payload = {"output": text, "original_prompt": prompt, "metadata": {"source": "cli"}}
    
    try:
        print(f"{BLUE}Scanning output...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print_result(data["verdict"], data["risk_score"], data["explanation"])
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def scan_pii(text: str):
    """Scan for PII"""
    url = f"{API_BASE}/scan/prompt"
    payload = {"prompt": text, "metadata": {"source": "cli-pii"}}
    
    try:
        print(f"{BLUE}Scanning for PII...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        signals = data.get("signals", {})
        pii_found = signals.get("pii_detected", False)
        
        if pii_found:
            print_result("BLOCKED", data["risk_score"], "Personally Identifiable Information (PII) detected.")
        else:
            print_result("ALLOWED", 0.0, "No PII detected.")
            
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def scan_image(image_path: str):
    """Scan image for deepfake"""
    url = f"{API_BASE}/scan/content"
    
    if not os.path.exists(image_path):
        print(f"{RED}Error: File not found: {image_path}{RESET}")
        return

    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        payload = {
            "content_type": "image", 
            "content": encoded_string,
            "metadata": {"source": "cli"}
        }
        
        print(f"{BLUE}Scanning image for deepfakes...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print_result(data["verdict"], data["risk_score"], data["explanation"])
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def agent_authorize(agent_id: str, action_type: str, session: str):
    """Authorize an agent action"""
    url = f"{API_BASE}/agent/authorize"
    payload = {
        "agent_id": agent_id,
        "session_id": session,
        "action_type": action_type,
        "requested_action": {"command": "cli_test"}, # Placeholder, allows flexible testing
        "requested_scope": {"allow": True}
    }
    
    try:
        print(f"{MAGENTA}Requesting authorization for Agent {agent_id}...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        status_color = GREEN if data["authorized"] else RED
        status_text = "AUTHORIZED" if data["authorized"] else "DENIED"
        
        print(f"\n{BLUE}--- Agent Authorization ---{RESET}")
        print(f"Status: {BOLD}{status_color}{status_text}{RESET}")
        print(f"Action ID: {data['action_id']}")
        print(f"Reasoning: {data['reasoning']}\n")
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def agent_history(agent_id: str):
    """Get agent action history"""
    url = f"{API_BASE}/agent/history/{agent_id}"
    
    try:
        print(f"{MAGENTA}Fetching history for Agent {agent_id}...{RESET}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n{BLUE}--- Agent History ({data['total_actions']} actions) ---{RESET}")
        for action in data["actions"][:5]: # Show last 5
            status = "✅" if action["authorized"] else "❌"
            print(f"{status} [{action['created_at']}] {action['action_type']} (Risk: {action['risk_score']})")
        print("")
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def health_check():
    """Check API health"""
    print(f"{BLUE}Checking IntellectSafe API status...{RESET}")
    try:
        response = requests.get(f"http://localhost:8001/") # Root endpoint usually has message or docs
        if response.status_code == 200:
             print(f"{GREEN}✓ API is ONLINE at {API_BASE}{RESET}")
        else:
             print(f"{YELLOW}⚠ API responded with {response.status_code}{RESET}")
    except:
        print(f"{RED}✗ API is OFFLINE. Is the backend running?{RESET}")

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="IntellectSafe CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scanners
    p_prompt = subparsers.add_parser("scan-prompt", help="Scan prompt for injection")
    p_prompt.add_argument("text", help="Prompt text")

    p_output = subparsers.add_parser("scan-output", help="Scan output for safety")
    p_output.add_argument("text", help="Output text")
    p_output.add_argument("--prompt", default="", help="Original prompt")
    
    p_pii = subparsers.add_parser("scan-pii", help="Scan for PII")
    p_pii.add_argument("text", help="Text to scan")
    
    p_image = subparsers.add_parser("scan-image", help="Scan deepfake image")
    p_image.add_argument("path", help="Image path")

    # Agent Control
    p_auth = subparsers.add_parser("agent-auth", help="Authorize agent action")
    p_auth.add_argument("agent_id", help="Agent ID")
    p_auth.add_argument("action", help="Action type (e.g. file_read)")
    p_auth.add_argument("--session", default="cli-session", help="Session ID")
    
    p_hist = subparsers.add_parser("agent-history", help="Get agent history")
    p_hist.add_argument("agent_id", help="Agent ID")
    
    # System
    subparsers.add_parser("health", help="Check system status")

    args = parser.parse_args()

    if args.command == "scan-prompt":
        scan_prompt(args.text)
    elif args.command == "scan-output":
        scan_output(args.text, args.prompt)
    elif args.command == "scan-pii":
        scan_pii(args.text)
    elif args.command == "scan-image":
        scan_image(args.path)
    elif args.command == "agent-auth":
        agent_authorize(args.agent_id, args.action, args.session)
    elif args.command == "agent-history":
        agent_history(args.agent_id)
    elif args.command == "health":
        health_check()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
