#!/usr/bin/env python3
"""
إصلاح شامل لمشاكل تحميل البيانات
"""

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def fix_database_schema():
    """إصلاح مخطط قاعدة البيانات"""
    print("🔧 إصلاح مخطط قاعدة البيانات...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود الجداول والأعمدة المطلوبة
        
        # إصلاح جدول المستخدمين
        print("👤 إصلاح جدول المستخدمين...")
        
        # التحقق من الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'username' not in columns:
            # إضافة الأعمدة المفقودة
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN username TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN employee_name TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN employee_code TEXT')
                
                # نسخ البيانات من الأعمدة القديمة
                cursor.execute('''UPDATE users SET 
                    username = name,
                    password_hash = password,
                    employee_name = name,
                    employee_code = company_code
                    WHERE username IS NULL''')
                
                print("✅ تم إضافة الأعمدة الجديدة لجدول المستخدمين")
            except Exception as e:
                print(f"⚠️ خطأ في إضافة الأعمدة: {e}")
        
        # التأكد من وجود مستخدم إداري
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("👤 إنشاء مستخدم إداري...")
            admin_password = generate_password_hash('admin123')
            
            try:
                cursor.execute('''INSERT INTO users 
                    (username, password_hash, employee_name, employee_code, is_admin, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    ('admin', admin_password, 'System Administrator', 'ADMIN001', True, 
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                print("✅ تم إنشاء المستخدم الإداري (admin/admin123)")
            except:
                # Fallback للمخطط القديم
                cursor.execute('''INSERT INTO users 
                    (name, company_code, password, is_admin, created_date) 
                    VALUES (?, ?, ?, ?, ?)''',
                    ('admin', 'ADMIN001', admin_password, True, 
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                print("✅ تم إنشاء المستخدم الإداري (admin/admin123) - مخطط قديم")
        
        # التحقق من بيانات POP Materials
        print("📊 التحقق من بيانات POP Materials...")
        
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        if pop_count == 0:
            print("📊 تعبئة بيانات POP Materials الافتراضية...")
            populate_pop_materials(cursor)
        
        conn.commit()
        print("✅ تم إصلاح مخطط قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def populate_pop_materials(cursor):
    """تعبئة بيانات POP Materials الافتراضية"""
    
    # بيانات POP Materials حسب الموديل
    pop_materials_by_model = {
        'S95F': [
            'AI topper', 'OLED Topper', 'Glare Free', 'New Topper', '165 HZ Side POP',
            'Category POP', 'Samsung OLED Topper', '165 HZ & joy stick indicator',
            'AI Topper Gaming', 'Side POP', 'Specs Card', 'Why OLED side POP'
        ],
        'S90F': [
            'AI topper', 'OLED Topper', 'Glare Free', 'New Topper', 'Side POP',
            'Category POP', 'Samsung OLED Topper', 'Specs Card'
        ],
        'S85F': [
            'AI topper', 'OLED Topper', 'New Topper', 'Side POP', 'Specs Card'
        ],
        'QN90F': [
            'AI topper', 'Lockup Topper', 'Screen POP', 'New Topper', 'Glare Free', 'Specs Card'
        ],
        'QN85F': [
            'AI topper', 'Lockup Topper', 'Screen POP', 'New Topper', 'Specs Card'
        ],
        'QN80F': [
            'AI topper', 'Screen POP', 'New Topper', 'Specs Card'
        ],
        'QN70F': [
            'AI topper', 'Screen POP', 'New Topper', 'Specs Card'
        ],
        'Q8F': [
            'AI topper', 'Samsung QLED Topper', 'Screen POP', 'New Topper', 'Specs Card', 'QLED Topper'
        ],
        'Q7F': [
            'AI topper', 'Samsung QLED Topper', 'Screen POP', 'New Topper', 'Specs Card'
        ],
        'U8000': [
            'UHD topper', 'Samsung UHD topper', 'Screen POP', 'New Topper', 'Specs Card',
            'AI topper', 'Samsung Lockup Topper', 'Inch Logo side POP'
        ],
        '100"/98"': [
            'UHD topper', 'Samsung UHD topper', 'Screen POP', 'New Topper', 'Specs Card'
        ],
        'The Frame': [
            'Side POP', 'Matte Display', 'Category POP', 'Frame Bezel'
        ],
        'WD25DB8995': [
            'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
            'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
            'Ecobubble POP', 'Ecco Bubble', 'AI Ecco Bubble', '20 Years Warranty',
            'New Arrival', 'Samsung Brand/Tech Topper'
        ],
        'WD21D6400': [
            'PODs (Door)', 'POD (Top)', 'POD (Front)', 'AI Home POP', 'AI Home',
            'AI control panel', 'Capacity (Kg)', 'Filter', 'Ecobubble POP',
            '20 Years Warranty', 'Samsung Brand/Tech Topper'
        ],
        'RS70F': [
            'Samsung Brand/Tech Topper', 'Main POD', '20 Years Warranty',
            'Twin Cooling Plus™', 'Smart Conversion™', 'Digital Inverter™',
            'SpaceMax™', 'Tempered Glass', 'Power Freeze', 'Big Vegetable Box', 'Organize Big Bin'
        ]
    }
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for model_name, materials in pop_materials_by_model.items():
        # الحصول على معرف الموديل
        cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
        model_result = cursor.fetchone()
        
        if model_result:
            model_id = model_result[0]
            
            for material in materials:
                try:
                    # إدراج في الجدول الجديد
                    cursor.execute('''INSERT OR IGNORE INTO pop_materials 
                        (name, model_id, created_at) VALUES (?, ?, ?)''',
                        (material, model_id, current_time))
                    
                    # إدراج في الجدول القديم للتوافق
                    cursor.execute('''INSERT OR IGNORE INTO pop_materials_db 
                        (material_name, model_name, category_name, created_date) 
                        SELECT ?, ?, c.name, ?
                        FROM models m JOIN categories c ON m.category_id = c.id 
                        WHERE m.id = ?''',
                        (material, model_name, current_time, model_id))
                except Exception as e:
                    print(f"⚠️ خطأ في إدراج المادة {material} للموديل {model_name}: {e}")
    
    print("✅ تم تعبئة بيانات POP Materials")

def test_data_loading():
    """اختبار تحميل البيانات"""
    print("🧪 اختبار تحميل البيانات...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # اختبار تحميل الفئات
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        print(f"📊 الفئات: {categories_count}")
        
        # اختبار تحميل الموديلات
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        print(f"📱 الموديلات: {models_count}")
        
        # اختبار تحميل أنواع العرض
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        print(f"🖥️ أنواع العرض: {display_count}")
        
        # اختبار تحميل مواد POP
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        print(f"🎨 مواد POP: {pop_count}")
        
        # اختبار تحميل مواد POP لموديل محدد
        cursor.execute('''SELECT pm.name FROM pop_materials pm 
                         JOIN models m ON pm.model_id = m.id 
                         WHERE m.name = ? LIMIT 5''', ('S95F',))
        materials = cursor.fetchall()
        print(f"🎨 مواد POP لموديل S95F: {len(materials)} مواد")
        for material in materials:
            print(f"   - {material[0]}")
        
        # اختبار المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"👥 المستخدمين: {users_count}")
        
        print("✅ اختبار تحميل البيانات مكتمل!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار البيانات: {e}")
        return False
    finally:
        conn.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إصلاح مشاكل تحميل البيانات...")
    
    # إصلاح مخطط قاعدة البيانات
    if not fix_database_schema():
        print("❌ فشل في إصلاح قاعدة البيانات")
        return False
    
    # اختبار تحميل البيانات
    if not test_data_loading():
        print("❌ فشل في اختبار البيانات")
        return False
    
    print("\n🎉 تم إصلاح جميع مشاكل تحميل البيانات بنجاح!")
    print("\n📋 ملخص الإصلاحات:")
    print("   ✅ إصلاح مخطط قاعدة البيانات")
    print("   ✅ إضافة المستخدم الإداري")
    print("   ✅ تعبئة بيانات POP Materials")
    print("   ✅ اختبار تحميل البيانات")
    print("\n🔑 بيانات تسجيل الدخول للمدير:")
    print("   المستخدم: admin")
    print("   كلمة المرور: admin123")
    
    return True

if __name__ == "__main__":
    main()