#!/usr/bin/env python3
"""
فحص مخطط الجداول
"""

import sqlite3

def check_table_schema():
    """فحص مخطط جميع الجداول"""
    print("🔍 فحص مخطط الجداول...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    tables = ['categories', 'models', 'display_types', 'pop_materials', 'users']
    
    for table in tables:
        print(f"\n📋 جدول {table}:")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_table_schema()