#!/usr/bin/env python3
"""
تشخيص مشاكل إدارة البيانات في Admin Management
"""

import os
import sys
import sqlite3
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql'):
        # Production PostgreSQL
        try:
            conn = psycopg2.connect(database_url)
            return conn, 'postgresql'
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return None, None
    else:
        # Local SQLite
        try:
            conn = sqlite3.connect('database.db')
            return conn, 'sqlite'
        except Exception as e:
            print(f"SQLite connection failed: {e}")
            return None, None

def check_table_structure():
    """فحص بنية الجداول"""
    print("🔍 فحص بنية الجداول...")
    
    conn, db_type = get_db_connection()
    if not conn:
        print("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    cursor = conn.cursor()
    
    # فحص الجداول المطلوبة
    tables_to_check = ['categories', 'models', 'display_types', 'pop_materials']
    
    for table in tables_to_check:
        print(f"\n📋 فحص جدول {table}:")
        
        try:
            if db_type == 'postgresql':
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
            else:
                cursor.execute(f"PRAGMA table_info({table})")
            
            columns = cursor.fetchall()
            if columns:
                print(f"  ✅ الجدول موجود مع {len(columns)} عمود:")
                for col in columns:
                    if db_type == 'postgresql':
                        print(f"    - {col[0]} ({col[1]})")
                    else:
                        print(f"    - {col[1]} ({col[2]})")
            else:
                print(f"  ❌ الجدول غير موجود أو فارغ")
                
        except Exception as e:
            print(f"  ❌ خطأ في فحص الجدول: {e}")
    
    conn.close()

def check_data_integrity():
    """فحص سلامة البيانات"""
    print("\n🔍 فحص سلامة البيانات...")
    
    conn, db_type = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    placeholder = '%s' if db_type == 'postgresql' else '?'
    
    # فحص الكاتجوريز
    print("\n📊 فحص الكاتجوريز:")
    try:
        # جرب النسخة الجديدة أولاً
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        print(f"  ✅ إجمالي الكاتجوريز: {count}")
        
        # فحص التكرار
        try:
            cursor.execute("SELECT name, COUNT(*) FROM categories GROUP BY name HAVING COUNT(*) > 1")
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"  ⚠️ كاتجوريز مكررة: {len(duplicates)}")
                for dup in duplicates[:5]:
                    print(f"    - {dup[0]}: {dup[1]} مرة")
            else:
                print("  ✅ لا توجد كاتجوريز مكررة")
        except:
            # جرب النسخة القديمة
            cursor.execute("SELECT category_name, COUNT(*) FROM categories GROUP BY category_name HAVING COUNT(*) > 1")
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"  ⚠️ كاتجوريز مكررة (نسخة قديمة): {len(duplicates)}")
            else:
                print("  ✅ لا توجد كاتجوريز مكررة (نسخة قديمة)")
                
    except Exception as e:
        print(f"  ❌ خطأ في فحص الكاتجوريز: {e}")
    
    # فحص النماذج
    print("\n📊 فحص النماذج:")
    try:
        cursor.execute("SELECT COUNT(*) FROM models")
        count = cursor.fetchone()[0]
        print(f"  ✅ إجمالي النماذج: {count}")
        
        # فحص العلاقات
        try:
            cursor.execute("""
                SELECT m.name, c.name 
                FROM models m 
                JOIN categories c ON m.category_id = c.id 
                LIMIT 5
            """)
            relations = cursor.fetchall()
            if relations:
                print(f"  ✅ العلاقات تعمل (نسخة جديدة):")
                for rel in relations:
                    print(f"    - {rel[0]} -> {rel[1]}")
            else:
                print("  ⚠️ لا توجد علاقات صحيحة")
        except:
            # جرب النسخة القديمة
            cursor.execute("SELECT model_name, category_name FROM models LIMIT 5")
            old_relations = cursor.fetchall()
            if old_relations:
                print(f"  ✅ البيانات موجودة (نسخة قديمة):")
                for rel in old_relations:
                    print(f"    - {rel[0]} -> {rel[1]}")
                    
    except Exception as e:
        print(f"  ❌ خطأ في فحص النماذج: {e}")
    
    # فحص أنواع العرض
    print("\n📊 فحص أنواع العرض:")
    try:
        cursor.execute("SELECT COUNT(*) FROM display_types")
        count = cursor.fetchone()[0]
        print(f"  ✅ إجمالي أنواع العرض: {count}")
        
        # فحص العلاقات
        try:
            cursor.execute("""
                SELECT dt.name, c.name 
                FROM display_types dt 
                JOIN categories c ON dt.category_id = c.id 
                LIMIT 5
            """)
            relations = cursor.fetchall()
            if relations:
                print(f"  ✅ العلاقات تعمل (نسخة جديدة):")
                for rel in relations:
                    print(f"    - {rel[0]} -> {rel[1]}")
            else:
                print("  ⚠️ لا توجد علاقات صحيحة")
        except:
            # جرب النسخة القديمة
            cursor.execute("SELECT display_type_name, category_name FROM display_types LIMIT 5")
            old_relations = cursor.fetchall()
            if old_relations:
                print(f"  ✅ البيانات موجودة (نسخة قديمة):")
                for rel in old_relations:
                    print(f"    - {rel[0]} -> {rel[1]}")
                    
    except Exception as e:
        print(f"  ❌ خطأ في فحص أنواع العرض: {e}")
    
    conn.close()

def test_api_endpoints():
    """اختبار API endpoints"""
    print("\n🔍 اختبار API endpoints...")
    
    import requests
    import json
    
    base_url = "http://localhost:5000"
    
    # اختبار تسجيل الدخول
    print("\n🔐 اختبار تسجيل الدخول:")
    try:
        session = requests.Session()
        login_data = {'name': 'admin', 'password': 'admin123'}
        response = session.post(f"{base_url}/login", data=login_data)
        
        if response.status_code == 200 and 'admin_dashboard' in response.url:
            print("  ✅ تسجيل الدخول نجح")
            
            # اختبار جلب البيانات
            endpoints_to_test = ['categories', 'models', 'display_types']
            
            for endpoint in endpoints_to_test:
                print(f"\n📡 اختبار {endpoint}:")
                try:
                    response = session.get(f"{base_url}/get_management_data/{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print(f"  ✅ {endpoint}: {len(data.get('data', []))} عنصر")
                        else:
                            print(f"  ❌ {endpoint}: {data.get('message', 'خطأ غير معروف')}")
                    else:
                        print(f"  ❌ {endpoint}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {endpoint}: {e}")
        else:
            print("  ❌ فشل تسجيل الدخول")
            
    except Exception as e:
        print(f"  ❌ خطأ في الاتصال: {e}")

def main():
    print("🔧 تشخيص مشاكل إدارة البيانات")
    print("=" * 50)
    
    check_table_structure()
    check_data_integrity()
    
    # اختبار API فقط إذا كان التطبيق يعمل محلياً
    if len(sys.argv) > 1 and sys.argv[1] == '--test-api':
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ انتهى التشخيص")

if __name__ == '__main__':
    main()