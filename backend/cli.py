
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

def scan_pii(text: str):
    """Scan for PII"""
    # PII scan is currently part of prompt scan in this API version, 
    # but we can call it explicitly or filter results.
    # For now, we reuse prompt scan but focus on PII signals.
    url = f"{API_BASE}/scan/prompt"
    payload = {"prompt": text, "metadata": {"source": "cli-pii"}}
    
    try:
        print(f"{BLUE}Scanning for PII...{RESET}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Check specific PII signals
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
        import base64
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
    
    # scan-pii
    p_pii = subparsers.add_parser("scan-pii", help="Scan text for PII leakage")
    p_pii.add_argument("text", help="The text to scan for PII")
    
    # scan-image
    p_image = subparsers.add_parser("scan-image", help="Scan image for deepfake traces")
    p_image.add_argument("path", help="Path to image file")

    args = parser.parse_args()

    if args.command == "scan-prompt":
        scan_prompt(args.text)
    elif args.command == "scan-output":
        scan_output(args.text, args.prompt)
    elif args.command == "scan-pii":
        scan_pii(args.text)
    elif args.command == "scan-image":
        scan_image(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
