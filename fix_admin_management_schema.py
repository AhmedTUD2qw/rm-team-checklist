#!/usr/bin/env python3
"""
إصلاح مشاكل إدارة البيانات - توحيد النسخة القديمة والجديدة
"""

import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    """إصلاح بنية قاعدة البيانات"""
    print("🔧 إصلاح بنية قاعدة البيانات...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. إنشاء جدول pop_materials إذا لم يكن موجوداً
    print("📋 إنشاء جدول pop_materials...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pop_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id)
            )
        ''')
        print("  ✅ جدول pop_materials تم إنشاؤه")
    except Exception as e:
        print(f"  ❌ خطأ في إنشاء pop_materials: {e}")
    
    # 2. نسخ البيانات من pop_materials_db إلى pop_materials
    print("📋 نسخ البيانات من pop_materials_db...")
    try:
        # فحص إذا كان pop_materials فارغ
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        if pop_count == 0:
            # نسخ البيانات
            cursor.execute('''
                INSERT INTO pop_materials (name, created_at)
                SELECT DISTINCT material_name, created_date 
                FROM pop_materials_db 
                WHERE material_name IS NOT NULL
            ''')
            print(f"  ✅ تم نسخ البيانات إلى pop_materials")
        else:
            print(f"  ✅ pop_materials يحتوي على {pop_count} عنصر")
    except Exception as e:
        print(f"  ❌ خطأ في نسخ البيانات: {e}")
    
    # 3. إضافة أعمدة النسخة الجديدة للجداول الموجودة
    tables_to_update = [
        ('categories', 'name', 'category_name'),
        ('models', 'name', 'model_name'),
        ('display_types', 'name', 'display_type_name')
    ]
    
    for table, new_col, old_col in tables_to_update:
        print(f"📋 تحديث جدول {table}...")
        try:
            # إضافة العمود الجديد
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {new_col} TEXT')
            print(f"  ✅ تم إضافة عمود {new_col}")
        except:
            print(f"  ✅ عمود {new_col} موجود مسبقاً")
        
        try:
            # نسخ البيانات من العمود القديم للجديد
            cursor.execute(f'UPDATE {table} SET {new_col} = {old_col} WHERE {new_col} IS NULL')
            print(f"  ✅ تم نسخ البيانات من {old_col} إلى {new_col}")
        except Exception as e:
            print(f"  ❌ خطأ في نسخ البيانات: {e}")
    
    # 4. إضافة أعمدة created_at للجداول
    for table in ['categories', 'models', 'display_types']:
        try:
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN created_at TEXT')
            print(f"  ✅ تم إضافة عمود created_at لجدول {table}")
        except:
            print(f"  ✅ عمود created_at موجود مسبقاً في {table}")
        
        try:
            # نسخ البيانات من created_date إلى created_at
            cursor.execute(f'UPDATE {table} SET created_at = created_date WHERE created_at IS NULL')
            print(f"  ✅ تم نسخ التواريخ في {table}")
        except Exception as e:
            print(f"  ❌ خطأ في نسخ التواريخ: {e}")
    
    # 5. إضافة أعمدة category_id و model_id للعلاقات
    print("📋 إضافة أعمدة العلاقات...")
    
    # إضافة category_id للنماذج
    try:
        cursor.execute('ALTER TABLE models ADD COLUMN category_id INTEGER')
        print("  ✅ تم إضافة category_id للنماذج")
    except:
        print("  ✅ category_id موجود مسبقاً في النماذج")
    
    # إضافة category_id لأنواع العرض
    try:
        cursor.execute('ALTER TABLE display_types ADD COLUMN category_id INTEGER')
        print("  ✅ تم إضافة category_id لأنواع العرض")
    except:
        print("  ✅ category_id موجود مسبقاً في أنواع العرض")
    
    # تحديث العلاقات
    print("📋 تحديث العلاقات...")
    try:
        # تحديث category_id في النماذج
        cursor.execute('''
            UPDATE models 
            SET category_id = (
                SELECT c.id FROM categories c 
                WHERE c.category_name = models.category_name 
                   OR c.name = models.category_name
                LIMIT 1
            )
            WHERE category_id IS NULL
        ''')
        
        # تحديث category_id في أنواع العرض
        cursor.execute('''
            UPDATE display_types 
            SET category_id = (
                SELECT c.id FROM categories c 
                WHERE c.category_name = display_types.category_name 
                   OR c.name = display_types.category_name
                LIMIT 1
            )
            WHERE category_id IS NULL
        ''')
        
        print("  ✅ تم تحديث العلاقات")
    except Exception as e:
        print(f"  ❌ خطأ في تحديث العلاقات: {e}")
    
    conn.commit()
    conn.close()
    print("✅ تم إصلاح بنية قاعدة البيانات")

def verify_fix():
    """التحقق من الإصلاح"""
    print("\n🔍 التحقق من الإصلاح...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # فحص الجداول والأعمدة
    tables_to_check = ['categories', 'models', 'display_types', 'pop_materials']
    
    for table in tables_to_check:
        print(f"\n📋 فحص {table}:")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"  ✅ الأعمدة ({len(columns)}):")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # عد الصفوف
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ عدد الصفوف: {count}")
            
        except Exception as e:
            print(f"  ❌ خطأ: {e}")
    
    # فحص العلاقات
    print(f"\n📋 فحص العلاقات:")
    try:
        cursor.execute('''
            SELECT m.name, c.name 
            FROM models m 
            JOIN categories c ON m.category_id = c.id 
            LIMIT 3
        ''')
        relations = cursor.fetchall()
        if relations:
            print("  ✅ علاقات النماذج تعمل:")
            for rel in relations:
                print(f"    - {rel[0]} -> {rel[1]}")
        else:
            print("  ⚠️ لا توجد علاقات للنماذج")
    except Exception as e:
        print(f"  ❌ خطأ في علاقات النماذج: {e}")
    
    try:
        cursor.execute('''
            SELECT dt.name, c.name 
            FROM display_types dt 
            JOIN categories c ON dt.category_id = c.id 
            LIMIT 3
        ''')
        relations = cursor.fetchall()
        if relations:
            print("  ✅ علاقات أنواع العرض تعمل:")
            for rel in relations:
                print(f"    - {rel[0]} -> {rel[1]}")
        else:
            print("  ⚠️ لا توجد علاقات لأنواع العرض")
    except Exception as e:
        print(f"  ❌ خطأ في علاقات أنواع العرض: {e}")
    
    conn.close()

def main():
    print("🔧 إصلاح مشاكل إدارة البيانات")
    print("=" * 50)
    
    # إنشاء نسخة احتياطية
    print("💾 إنشاء نسخة احتياطية...")
    try:
        import shutil
        backup_name = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('database.db', backup_name)
        print(f"  ✅ تم إنشاء نسخة احتياطية: {backup_name}")
    except Exception as e:
        print(f"  ⚠️ تحذير: فشل في إنشاء النسخة الاحتياطية: {e}")
    
    fix_database_schema()
    verify_fix()
    
    print("\n" + "=" * 50)
    print("✅ انتهى الإصلاح")
    print("🚀 يمكنك الآن تشغيل التطبيق واختبار إدارة البيانات")

if __name__ == '__main__':
    main()