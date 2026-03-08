import os

def apply_surgical_edits(content, edits):
    """Old substring-based logic from the bot (before my recent line-matching fix)"""
    new_content = content
    original_line_count = len(content.splitlines())
    for edit in edits:
        search = edit.get('search')
        replace = edit.get('replace')
        if search and search in new_content:
            search_lines = len(search.strip().splitlines())
            replace_lines = len(replace.strip().splitlines()) if replace else 0
            if search_lines > 5 and replace_lines < search_lines * 0.5:
                print(f"DEBUG: BLOCKED destructive edit - would delete {search_lines - replace_lines} lines")
                continue
            
            # The exact str.replace that caused the bug
            test_content = new_content.replace(search, replace, 1)
            new_line_count = len(test_content.splitlines())
            
            # Note: The 20% guard was not present when PR #8 ran!
            
            new_content = test_content
        else:
            print("DEBUG: Search block not found in file")
    return new_content

target_file = r"C:\Users\USER\Desktop\cursor file\AI-safety\README.md"
with open(target_file, "r", encoding="utf-8") as f:
    text = f.read()

# The edit exactly as modified by the Reviewer and sent to the pipeline in Cycle 1772671945
reviewer_corrected_edit = {
    "file": "README.md",
    "search": "git clone <repo-url>\ncd AI-safety",
    "replace": "git clone https://github.com/HOLYKEYZ/IntellectSafe\ncd IntellectSafe"
}

print(f"Original file lines: {len(text.splitlines())}")

# Test 1: Simulate the Reviewer's exact edit with the old substring matcher
result_text = apply_surgical_edits(text, [reviewer_corrected_edit])
print(f"Resulting file lines (Old Engine): {len(result_text.splitlines())}")
print(f"Net lines removed: {len(text.splitlines()) - len(result_text.splitlines())}")
