from dotenv import dotenv_values
from pathlib import Path

env = dotenv_values(Path("../.env"))
keys = ["OPEN_AI_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "GROK_API_KEY", "COHERE_AI_API_KEY", "ANTHROPIC_API_KEY"]
for k in keys:
    val = env.get(k, "")
    print(f"{k}: len={len(val)}, empty={len(val) == 0}")
