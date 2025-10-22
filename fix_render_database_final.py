#!/usr/bin/env python3
"""
إصلاح نهائي لقاعدة بيانات Render
"""

from database_config import get_database_connection
from werkzeug.security import generate_password_hash
from datetime import datetime

def clean_render_database():
    """تنظيف قاعدة بيانات Render من البيانات المكررة"""
    print("🧹 تنظيف قاعدة بيانات Render...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"📊 نوع قاعدة البيانات: {db_type}")
        
        if db_type == 'postgresql':
            # PostgreSQL - حذف البيانات المكررة
            print("🗑️ حذف البيانات المكررة في PostgreSQL...")
            
            # حذف الفئات المكررة
            cursor.execute('''
                DELETE FROM categories 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM categories 
                    GROUP BY name
                )
            ''')
            
            # حذف الموديلات المكررة
            cursor.execute('''
                DELETE FROM models 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM models 
                    GROUP BY name, category_id
                )
            ''')
            
            # حذف أنواع العرض المكررة
            cursor.execute('''
                DELETE FROM display_types 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM display_types 
                    GROUP BY name, category_id
                )
            ''')
            
            # حذف مواد POP المكررة
            cursor.execute('''
                DELETE FROM pop_materials 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM pop_materials 
                    GROUP BY name, model_id
                )
            ''')
            
        else:
            # SQLite - نفس الاستعلامات
            print("🗑️ تنظيف البيانات المكررة في SQLite...")
            
            cursor.execute('''
                DELETE FROM categories 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM categories 
                    GROUP BY name
                )
            ''')
            
            cursor.execute('''
                DELETE FROM models 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM models 
                    GROUP BY name, category_id
                )
            ''')
            
            cursor.execute('''
                DELETE FROM display_types 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM display_types 
                    GROUP BY name, category_id
                )
            ''')
            
            cursor.execute('''
                DELETE FROM pop_materials 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM pop_materials 
                    GROUP BY name, model_id
                )
            ''')
        
        conn.commit()
        
        # إحصائيات بعد التنظيف
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        print(f"✅ تم التنظيف:")
        print(f"   📊 الفئات: {categories_count}")
        print(f"   📱 الموديلات: {models_count}")
        print(f"   🖥️ أنواع العرض: {display_count}")
        print(f"   🎨 مواد POP: {pop_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التنظيف: {e}")
        return False

def add_cleanup_flag():
    """إضافة علامة لمنع إعادة تشغيل populate_clean_data"""
    print("🏷️ إضافة علامة منع التكرار...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # إنشاء جدول للعلامات إذا لم يكن موجود
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_flags (
                    id SERIAL PRIMARY KEY,
                    flag_name VARCHAR(100) UNIQUE NOT NULL,
                    flag_value BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_flags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flag_name TEXT UNIQUE NOT NULL,
                    flag_value BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # إضافة علامة منع التكرار
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if db_type == 'postgresql':
            cursor.execute(f'''
                INSERT INTO system_flags (flag_name, flag_value) 
                VALUES ({placeholder}, {placeholder}) 
                ON CONFLICT (flag_name) DO UPDATE SET flag_value = EXCLUDED.flag_value
            ''', ('data_populated', True))
        else:
            cursor.execute(f'''
                INSERT OR REPLACE INTO system_flags (flag_name, flag_value) 
                VALUES ({placeholder}, {placeholder})
            ''', ('data_populated', True))
        
        conn.commit()
        conn.close()
        
        print("✅ تم إضافة علامة منع التكرار")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة العلامة: {e}")
        return False

def main():
    """تشغيل الإصلاح النهائي"""
    print("🚀 بدء الإصلاح النهائي لقاعدة بيانات Render...")
    
    # تنظيف البيانات المكررة
    if not clean_render_database():
        print("❌ فشل في تنظيف قاعدة البيانات")
        return False
    
    # إضافة علامة منع التكرار
    if not add_cleanup_flag():
        print("❌ فشل في إضافة علامة منع التكرار")
        return False
    
    print("\n🎉 تم الإصلاح النهائي لقاعدة البيانات!")
    print("\n📋 ما تم عمله:")
    print("   ✅ حذف جميع البيانات المكررة")
    print("   ✅ إضافة علامة منع التكرار")
    print("   ✅ قاعدة البيانات نظيفة ومرتبة")
    
    return True

if __name__ == "__main__":
    main()