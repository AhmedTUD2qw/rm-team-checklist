#!/usr/bin/env python3
"""
Fix all remaining SQLite syntax issues in app.py
This script will replace all ? placeholders with proper database-agnostic syntax
"""

import re

def fix_database_syntax():
    """Fix all database syntax issues in app.py"""
    print("🔧 Fixing all database syntax issues...")
    
    # Read the current app.py file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    
    # Pattern 1: Simple execute with ? placeholders
    # Replace cursor.execute('...?...', (...)) with proper syntax
    def replace_execute_pattern(match):
        nonlocal changes_made
        changes_made += 1
        
        full_match = match.group(0)
        query = match.group(1)
        params = match.group(2) if match.group(2) else ''
        
        # Count placeholders
        placeholder_count = query.count('?')
        
        if placeholder_count > 0:
            # Replace with database-agnostic syntax
            new_query = query.replace('?', '{placeholder}')
            
            # Build the replacement
            replacement = f"cursor.execute(f'{new_query}'.format(placeholder=placeholder){params}"
            return replacement
        
        return full_match
    
    # Pattern for cursor.execute with ? placeholders
    pattern1 = r"cursor\.execute\(['\"]([^'\"]*\?[^'\"]*)['\"]([^)]*)\)"
    content = re.sub(pattern1, replace_execute_pattern, content)
    
    # Pattern 2: c.execute patterns
    def replace_c_execute_pattern(match):
        nonlocal changes_made
        changes_made += 1
        
        full_match = match.group(0)
        query = match.group(1)
        params = match.group(2) if match.group(2) else ''
        
        # Count placeholders
        placeholder_count = query.count('?')
        
        if placeholder_count > 0:
            # Replace with database-agnostic syntax
            new_query = query.replace('?', '{placeholder}')
            
            # Build the replacement
            replacement = f"c.execute(f'{new_query}'.format(placeholder=placeholder){params}"
            return replacement
        
        return full_match
    
    # Pattern for c.execute with ? placeholders
    pattern2 = r"c\.execute\(['\"]([^'\"]*\?[^'\"]*)['\"]([^)]*)\)"
    content = re.sub(pattern2, replace_c_execute_pattern, content)
    
    # Add placeholder variable definition at the beginning of functions that need it
    function_patterns = [
        r"(def \w+\([^)]*\):.*?)(conn, db_type = get_db_connection\(\))",
        r"(def \w+\([^)]*\):.*?)(conn, db_type = get_database_connection\(\))"
    ]
    
    for pattern in function_patterns:
        def add_placeholder_var(match):
            return match.group(1) + match.group(2) + "\n        placeholder = '%s' if db_type == 'postgresql' else '?'"
        
        content = re.sub(pattern, add_placeholder_var, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {changes_made} database syntax issues")
    return changes_made > 0

if __name__ == "__main__":
    if fix_database_syntax():
        print("🎉 All database syntax issues fixed!")
    else:
        print("ℹ️ No syntax issues found to fix")