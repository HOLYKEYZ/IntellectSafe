"""
Architecture Diagram Generator
------------------------------
Generates a visual representation of the IntellectSafe architecture using the `diagrams` library.

Usage:
    pip install diagrams
    python generate_architecture.py

Requirements:
    - Graphviz installed on the system (brew install graphviz / choco install graphviz)
    - pip install diagrams
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User, Client
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.security import Vault
from diagrams.programming.framework import FastAPI
from diagrams.saas.chat import Slack  # Placeholder for Chat App
from diagrams.generic.os import Ubuntu
from diagrams.custom import Custom
import os
import shutil
import sys

# Auto-detect Graphviz on Windows
if os.name == 'nt':
    possible_paths = [
        r"C:\Program Files\Graphviz\bin",
        r"C:\Program Files (x86)\Graphviz\bin",
        os.path.expanduser(r"~\AppData\Local\Programs\Graphviz\bin"),
    ]
    
    # Check if 'dot' is already in PATH
    if not shutil.which("dot"):
        for path in possible_paths:
            if os.path.exists(os.path.join(path, "dot.exe")):
                print(f"✅ Found Graphviz at {path}, adding to PATH...")
                os.environ["PATH"] += os.pathsep + path
                break


def generate_diagram():
    # Nodes
    with Diagram("IntellectSafe Architecture", show=False, filename="intellectsafe_architecture", direction="LR"):
        
        user = User("User / Agent")
        
        with Cluster("IntellectSafe Platform"):
            
            with Cluster("Edge Layer"):
                proxy = Server("Universal Proxy\n(Intercept & Auth)")
                auth = Vault("Auth & API Keys")
            
            with Cluster("Safety Pipeline"):
                with Cluster("Level 1: Prompt Shield"):
                    injection_detect = Server("Injection Detector")
                    pii_scrub = Server("PII Scrubber")
                    
                with Cluster("Level 4: LLM Council (Consensus)"):
                    # Representing the multi-model voting
                    gemini = Server("Gemini 1.5")
                    llama = Server("Llama 3")
                    claude = Server("Claude 3")
                    council = [gemini, llama, claude]
                    
                with Cluster("Level 2: Output Guard"):
                    output_scan = Server("Hallucination/Safety Check")

            with Cluster("Storage & Logs"):
                db = PostgreSQL("PostgreSQL\n(Risk Scores & Logs)")
                cache = Redis("Redis\n(Rate Limit & Queue)")

        # Upstream
        upstream_llm = Server("Upstream Provider\n(OpenAI/Anthropic/Google)")

        # Flow
        user >> Edge(label="1. Request") >> proxy
        proxy >> Edge(label="2. Validate") >> auth
        proxy >> Edge(label="3. Scan Prompt") >> injection_detect
        
        # Council Voting
        injection_detect >> Edge(label="4. Vote") >> gemini
        injection_detect >> Edge(label="4. Vote") >> llama
        injection_detect >> Edge(label="4. Vote") >> claude
        
        # Consensus
        council >> Edge(label="5. Consensus Reached") >> upstream_llm
        
        # Response Flow
        upstream_llm >> Edge(label="6. Raw Response") >> output_scan
        
        output_scan >> Edge(label="7. Log Event") >> db
        proxy >> Edge(label="Rate Limit") >> cache
        
        output_scan >> Edge(label="8. Safe Response") >> user

if __name__ == "__main__":
    try:
        print("Generating diagram...")
        generate_diagram()
        print("✅ Diagram generated: intellectsafe_architecture.png")
    except Exception as e:
        if "make sure the Graphviz executables are on your systems' PATH" in str(e):
            print("\n❌ ERROR: Graphviz executable not found!")
            print("To generate the diagram, you need to install Graphviz and add it to your PATH.")
            print("\nWindows (via Winget - Recommended):")
            print("  winget install Graphviz.Graphviz")
            print("\nWindows (via Chocolatey):")
            print("  choco install graphviz")
            print("\nWindows (Manual):")
            print("  1. Download installer from https://graphviz.org/download/")
            print("  2. Run installer and select 'Add Graphviz to the system PATH for all users'")
            print("\nMac:")
            print("  brew install graphviz")
            print("\nLinux:")
            print("  sudo apt-get install graphviz")
        else:
            raise e
