"""
Simple test to verify RAG pattern files are correctly seeded
Tests the JSON files directly without full app imports
"""

import json
from pathlib import Path

def test_rag_patterns():
    print("=" * 80)
    print("RAG SAFETY BRAIN - PATTERN FILE VERIFICATION")
    print("=" * 80)
    
    # Check if data directory exists
    data_dir = Path("./data/rag_fallback")
    if not data_dir.exists():
        print(f"\n❌ ERROR: Directory not found: {data_dir.absolute()}")
        return False
    
    # Get all JSON files
    pattern_files = list(data_dir.glob("*.json"))
    print(f"\n📂 Found {len(pattern_files)} pattern files in {data_dir.absolute()}\n")
    
    if len(pattern_files) == 0:
        print("❌ ERROR: No pattern files found!")
        return False
    
    # Analyze patterns
    patterns_by_category = {}
    patterns_by_bucket = {}
    user_research_count = 0
    
    for i, file_path in enumerate(pattern_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError("JSON root is not a dictionary")
            
            category = data.get('threat_category', 'unknown')
            metadata = data.get('metadata', {})
            if not isinstance(metadata, dict):
                raise ValueError("Metadata field is not a dictionary")
            
            bucket = metadata.get('bucket', 'unknown')
            source = data.get('source', 'unknown')
            subcategory = metadata.get('subcategory', 'unknown')
            severity = metadata.get('severity', 0)
            
            # Track categories and buckets
            patterns_by_category[category] = patterns_by_category.get(category, 0) + 1
            patterns_by_bucket[bucket] = patterns_by_bucket.get(bucket, 0) + 1
            
            # Count user research patterns
            if 'user_research' in source:
                user_research_count += 1
                marker = "🆕"
            else:
                marker = "📌"
            
            print(f"{marker} Pattern {i}: {subcategory}")
            print(f"   Category: {category} | Bucket: {bucket} | Severity: {severity}/5")
            print(f"   Source: {source}")
            print(f"   Content preview: {data.get('content', '')[:80]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}\n")
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n📊 Total Patterns: {len(pattern_files)}")
    print(f"🆕 User Research Patterns: {user_research_count}")
    print(f"📌 Original Patterns: {len(pattern_files) - user_research_count}")
    
    print(f"\n📂 Breakdown by Category:")
    for cat, count in sorted(patterns_by_category.items()):
        print(f"   {cat}: {count}")
    
    print(f"\n🪣 Breakdown by Bucket:")
    for bucket, count in sorted(patterns_by_bucket.items()):
        print(f"   {bucket}: {count}")
    
    # Verify critical buckets exist
    print(f"\n✅ Validation:")
    has_injection = patterns_by_bucket.get('injection', 0) > 0
    has_refusal = patterns_by_bucket.get('refusal', 0) > 0
    
    if has_injection:
        print(f"   ✓ INJECTION bucket found ({patterns_by_bucket['injection']} patterns)")
    else:
        print("   ✗ WARNING: No INJECTION patterns found!")
    
    if has_refusal:
        print(f"   ✓ REFUSAL bucket found ({patterns_by_bucket['refusal']} patterns)")
    else:
        print("   ℹ️  No REFUSAL patterns (optional)")
    
    print("\n" + "=" * 80)
    
    if has_injection:
        print("\n🎉 RAG Safety Brain is populated and ready!")
        print("\nNext steps:")
        print("1. Test via API: POST http://localhost:8001/api/v1/scan/prompt")
        print("2. Check Dashboard: http://localhost:5173")
        print("3. Add more patterns from your research")
        return True
    else:
        print("\n⚠️  RAG Safety Brain needs INJECTION patterns!")
        return False

if __name__ == "__main__":
    success = test_rag_patterns()
    exit(0 if success else 1)
