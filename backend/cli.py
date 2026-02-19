
import argparse
import requests
import json
import sys
import os
from typing import Optional

# Configuration
API_BASE = "http://localhost:8001/api/v1"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_result(verdict: str, score: float, explanation: str):
    """Print formatted scan result"""
    color = GREEN
    if verdict == "blocked":
        color = RED
    elif verdict == "flagged":
        color = YELLOW
    
    print(f"\n{BLUE}--- Scan Results ---{RESET}")
    print(f"Verdict: {color}{verdict.upper()}{RESET}")
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

def main():
    parser = argparse.ArgumentParser(description="IntellectSafe CLI - AI Security Scanner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan-prompt
    p_prompt = subparsers.add_parser("scan-prompt", help="Scan a prompt for injection/jailbreaks")
    p_prompt.add_argument("text", help="The prompt text to scan")

    # scan-output
    p_output = subparsers.add_parser("scan-output", help="Scan LLM output for safety")
    p_output.add_argument("text", help="The output text to scan")
    p_output.add_argument("--prompt", default="", help="Original prompt context")

    args = parser.parse_args()

    if args.command == "scan-prompt":
        scan_prompt(args.text)
    elif args.command == "scan-output":
        scan_output(args.text, args.prompt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
