#!/usr/bin/env python3
"""
Fix all SQL syntax issues in app.py
Replace all ? with proper database placeholders
"""

import re

def fix_sql_syntax():
    """Fix all SQL syntax issues"""
    print("🔧 Fixing all SQL syntax issues...")
    
    # Read app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all c.execute patterns with ? placeholders
    patterns_to_fix = [
        # Pattern: c.execute('...?...', (...))
        (r"c\.execute\('([^']*\?[^']*)', \(([^)]*)\)\)", r"c.execute(f'\1'.replace('?', placeholder), (\2))"),
        # Pattern: c.execute("...?...", (...))
        (r'c\.execute\("([^"]*\?[^"]*)", \(([^)]*)\)\)', r'c.execute(f"\1".replace("?", placeholder), (\2))'),
        # Pattern: cursor.execute('...?...', (...))
        (r"cursor\.execute\('([^']*\?[^']*)', \(([^)]*)\)\)", r"cursor.execute(f'\1'.replace('?', placeholder), (\2))"),
        # Pattern: cursor.execute("...?...", (...))
        (r'cursor\.execute\("([^"]*\?[^"]*)", \(([^)]*)\)\)', r'cursor.execute(f"\1".replace("?", placeholder), (\2))'),
    ]
    
    changes_made = 0
    
    # Apply fixes
    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"Fixed {len(matches)} SQL queries")
    
    # Add placeholder variable to functions that need it
    functions_needing_placeholder = [
        'manage_user', 'register', 'delete_entry', 'change_password', 
        'get_data', 'get_management_data'
    ]
    
    for func_name in functions_needing_placeholder:
        # Look for function definition
        func_pattern = rf"(def {func_name}\([^)]*\):.*?)(conn, db_type = get_db_connection\(\))"
        if re.search(func_pattern, content, re.DOTALL):
            # Add placeholder variable after db connection
            replacement = r"\1\2\n        placeholder = '%s' if db_type == 'postgresql' else '?'"
            content = re.sub(func_pattern, replacement, content, flags=re.DOTALL)
            print(f"Added placeholder variable to {func_name}")
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {changes_made} SQL syntax issues")
    return changes_made > 0

if __name__ == "__main__":
    if fix_sql_syntax():
        print("🎉 All SQL syntax issues fixed!")
    else:
        print("ℹ️ No SQL syntax issues found")