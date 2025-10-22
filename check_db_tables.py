#!/usr/bin/env python3
import sqlite3

# فحص قاعدة البيانات
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# جلب أسماء الجداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("الجداول الموجودة في database.db:")
for table in tables:
    print(f"- {table[0]}")
    
    # عد الصفوف في كل جدول
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  عدد الصفوف: {count}")
    except Exception as e:
        print(f"  خطأ في العد: {e}")

conn.close()