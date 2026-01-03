"""
Comprehensive API Key & Infrastructure Diagnostic Script
Tests all LLM providers and checks data setup.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def check_env_keys():
    """Check which API keys are set in environment"""
    print("\n" + "="*60)
    print("1. ENVIRONMENT VARIABLE CHECK")
    print("="*60)
    
    keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
    }
    
    for name, value in keys.items():
        if value:
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
            print(f"  [OK] {name}: {masked} (length: {len(value)})")
        else:
            print(f"  [X] {name}: NOT SET")
    
    return keys

def check_settings_loading():
    """Check if pydantic Settings loads the keys correctly"""
    print("\n" + "="*60)
    print("2. PYDANTIC SETTINGS LOADING")
    print("="*60)
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        settings_keys = {
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
            "DEEPSEEK_API_KEY": settings.DEEPSEEK_API_KEY,
            "GROQ_API_KEY": settings.GROQ_API_KEY,
            "COHERE_API_KEY": settings.COHERE_API_KEY,
        }
        
        for name, value in settings_keys.items():
            if value:
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
                print(f"  [OK] {name}: {masked}")
            else:
                print(f"  [X] {name}: None/Empty")
        
        return settings_keys
    except Exception as e:
        print(f"  ERROR loading settings: {e}")
        return None

def test_openai():
    """Test OpenAI API"""
    print("\n" + "="*60)
    print("3. TESTING OPENAI API")
    print("="*60)
    
    try:
        from openai import OpenAI
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.OPENAI_API_KEY:
            print("  [X] OPENAI_API_KEY not configured")
            return False
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test' only"}],
            max_tokens=5,
        )
        print(f"  [OK] OpenAI works! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"  [X] OpenAI FAILED: {e}")
        return False

def test_google():
    """Test Google Gemini API"""
    print("\n" + "="*60)
    print("4. TESTING GOOGLE GEMINI API")
    print("="*60)
    
    try:
        import google.generativeai as genai
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.GOOGLE_API_KEY:
            print("  [X] GOOGLE_API_KEY not configured")
            return False
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content("Say 'test' only")
        print(f"  [OK] Gemini works! Response: {response.text[:50]}")
        return True
    except Exception as e:
        print(f"  [X] Gemini FAILED: {e}")
        return False

def test_deepseek():
    """Test DeepSeek API"""
    print("\n" + "="*60)
    print("5. TESTING DEEPSEEK API")
    print("="*60)
    
    try:
        from openai import OpenAI
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.DEEPSEEK_API_KEY:
            print("  [X] DEEPSEEK_API_KEY not configured")
            return False
        
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Say 'test' only"}],
            max_tokens=5,
        )
        print(f"  [OK] DeepSeek works! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"  [X] DeepSeek FAILED: {e}")
        return False

def test_groq():
    """Test Groq API"""
    print("\n" + "="*60)
    print("6. TESTING GROQ API")
    print("="*60)
    
    try:
        from groq import Groq
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.GROQ_API_KEY:
            print("  [X] GROQ_API_KEY not configured")
            return False
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'test' only"}],
            max_tokens=5,
        )
        print(f"  [OK] Groq works! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"  [X] Groq FAILED: {e}")
        return False

def test_cohere():
    """Test Cohere API"""
    print("\n" + "="*60)
    print("7. TESTING COHERE API")
    print("="*60)
    
    try:
        import cohere
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.COHERE_API_KEY:
            print("  [X] COHERE_API_KEY not configured")
            return False
        
        co = cohere.Client(api_key=settings.COHERE_API_KEY)
        response = co.chat(
            model="command-r-plus",
            message="Say 'test' only",
        )
        print(f"  [OK] Cohere works! Response: {response.text[:50]}")
        return True
    except Exception as e:
        print(f"  [X] Cohere FAILED: {e}")
        return False

def check_chromadb():
    """Check ChromaDB setup"""
    print("\n" + "="*60)
    print("8. CHECKING CHROMADB")
    print("="*60)
    
    try:
        import chromadb
        from pathlib import Path
        
        chroma_path = Path("./chroma_db")
        if chroma_path.exists():
            print(f"  [OK] ChromaDB directory exists: {chroma_path.absolute()}")
            client = chromadb.PersistentClient(path=str(chroma_path))
            collections = client.list_collections()
            print(f"  [OK] Collections found: {len(collections)}")
            for col in collections:
                count = col.count()
                print(f"    - {col.name}: {count} documents")
        else:
            print(f"  [X] ChromaDB directory NOT found at {chroma_path.absolute()}")
            print("  --> Will create when RAG system initializes")
        
        return True
    except Exception as e:
        print(f"  [X] ChromaDB check FAILED: {e}")
        return False

def check_postgres():
    """Check PostgreSQL connection"""
    print("\n" + "="*60)
    print("9. CHECKING POSTGRESQL")
    print("="*60)
    
    try:
        from sqlalchemy import create_engine, text
        from app.core.config import get_settings
        settings = get_settings()
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM scan_requests"))
            count = result.scalar()
            print(f"  [OK] PostgreSQL connected!")
            print(f"  [OK] Total scan_requests: {count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM risk_scores"))
            count = result.scalar()
            print(f"  [OK] Total risk_scores: {count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM agent_actions"))
            count = result.scalar()
            print(f"  [OK] Total agent_actions: {count}")
        
        return True
    except Exception as e:
        print(f"  [X] PostgreSQL FAILED: {e}")
        return False

def check_alembic():
    """Check Alembic migrations"""
    print("\n" + "="*60)
    print("10. CHECKING ALEMBIC MIGRATIONS")
    print("="*60)
    
    try:
        from pathlib import Path
        import subprocess
        
        alembic_dir = Path("./alembic")
        if alembic_dir.exists():
            print(f"  [OK] Alembic directory exists")
            
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent)
            )
            if result.returncode == 0:
                current = result.stdout.strip()
                print(f"  [OK] Current migration: {current}")
            else:
                print(f"  [!] Alembic output: {result.stderr}")
        else:
            print(f"  [X] Alembic directory NOT found")
        
        return True
    except Exception as e:
        print(f"  [X] Alembic check FAILED: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  INTELLECTSAFE INFRASTRUCTURE DIAGNOSTIC")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
    load_dotenv()
    
    results = {}
    
    check_env_keys()
    check_settings_loading()
    results["openai"] = test_openai()
    results["google"] = test_google()
    results["deepseek"] = test_deepseek()
    results["groq"] = test_groq()
    results["cohere"] = test_cohere()
    check_chromadb()
    check_postgres()
    check_alembic()
    
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    working = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    print(f"\n  Working providers: {', '.join(working) if working else 'None'}")
    print(f"  Failed providers: {', '.join(failed) if failed else 'None'}")
    
    if failed:
        print("\n  RECOMMENDATIONS:")
        for provider in failed:
            if provider == "openai":
                print("    - Check OPENAI_API_KEY in .env (should start with 'sk-')")
            elif provider == "google":
                print("    - Check GOOGLE_API_KEY in .env")
            elif provider == "deepseek":
                print("    - Check DEEPSEEK_API_KEY in .env")
            elif provider == "groq":
                print("    - Check GROQ_API_KEY in .env (get from console.groq.com)")
            elif provider == "cohere":
                print("    - Check COHERE_API_KEY in .env")

if __name__ == "__main__":
    main()
