#!/usr/bin/env python3
"""
Quick fix for all column name issues on Render
"""

import os

def fix_all_column_issues():
    """Fix all column name mismatches between SQLite and PostgreSQL"""
    print("🔧 Fixing all column name issues...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all remaining issues
    fixes = [
        # Export issues
        ('SELECT id, employee_name, employee_code, branch,', 'SELECT id, employee_name, employee_code, branch_name,'),
        ('unselected_materials, images, date', 'missing_materials, image_urls, created_at'),
        
        # Category issues  
        ('SELECT category_name FROM categories', 'SELECT name FROM categories'),
        ('category_name = ?', 'name = ?'),
        ('WHERE category_name =', 'WHERE name ='),
        
        # Model issues
        ('SELECT model_name FROM models', 'SELECT name FROM models'),
        ('WHERE model_name =', 'WHERE name ='),
        
        # Display type issues
        ('SELECT display_type_name FROM display_types', 'SELECT name FROM display_types'),
        ('WHERE display_type_name =', 'WHERE name ='),
        
        # POP materials issues
        ('SELECT material_name FROM pop_materials', 'SELECT name FROM pop_materials'),
        ('WHERE material_name =', 'WHERE name ='),
    ]
    
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Fixed: {old[:50]}...")
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ All column fixes applied!")
    return True

if __name__ == "__main__":
    fix_all_column_issues()