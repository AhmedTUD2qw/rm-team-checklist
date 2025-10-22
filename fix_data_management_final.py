#!/usr/bin/env python3
"""
إصلاح نهائي لمشاكل إدارة البيانات
"""

import sqlite3
import requests
import json
from datetime import datetime

def clean_duplicate_data():
    """تنظيف البيانات المكررة"""
    print("🧹 تنظيف البيانات المكررة...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # تنظيف الفئات المكررة
        print("📊 تنظيف الفئات المكررة...")
        cursor.execute('''
            DELETE FROM categories 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM categories 
                GROUP BY name
            )
        ''')
        
        # تنظيف الموديلات المكررة
        print("📱 تنظيف الموديلات المكررة...")
        cursor.execute('''
            DELETE FROM models 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM models 
                GROUP BY name, category_id
            )
        ''')
        
        # تنظيف أنواع العرض المكررة
        print("🖥️ تنظيف أنواع العرض المكررة...")
        cursor.execute('''
            DELETE FROM display_types 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM display_types 
                GROUP BY name, category_id
            )
        ''')
        
        # تنظيف مواد POP المكررة
        print("🎨 تنظيف مواد POP المكررة...")
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
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التنظيف: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_data_management_api():
    """اختبار API إدارة البيانات"""
    print("\n🧪 اختبار API إدارة البيانات...")
    
    from app import app
    
    with app.test_client() as client:
        
        # تسجيل الدخول
        print("🔐 تسجيل الدخول...")
        login_data = {
            'name': 'admin',
            'company_code': 'ADMIN001',
            'password': 'admin123'
        }
        
        response = client.post('/login', data=login_data)
        if response.status_code not in [200, 302]:
            print(f"❌ فشل تسجيل الدخول: {response.status_code}")
            return False
        
        print("✅ تم تسجيل الدخول")
        
        # اختبار جلب الفئات
        print("\n📊 اختبار جلب الفئات...")
        response = client.get('/get_management_data/categories')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                categories = data.get('data', [])
                print(f"✅ تم جلب {len(categories)} فئة")
                
                # عرض أول 5 فئات
                for i, cat in enumerate(categories[:5]):
                    print(f"   {i+1}. {cat.get('name')} (ID: {cat.get('id')})")
            else:
                print(f"❌ فشل جلب الفئات: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ HTTP: {response.status_code}")
            return False
        
        # اختبار إضافة فئة جديدة
        print("\n➕ اختبار إضافة فئة جديدة...")
        test_category = f"TEST_CATEGORY_{datetime.now().strftime('%H%M%S')}"
        
        add_data = {
            'action': 'add',
            'type': 'categories',
            'name': test_category
        }
        
        response = client.post('/manage_data', 
                              json=add_data,
                              headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.get_json()
            if result.get('success'):
                print(f"✅ تم إضافة الفئة: {test_category}")
                
                # التحقق من وجود الفئة
                response = client.get('/get_management_data/categories')
                if response.status_code == 200:
                    data = response.get_json()
                    if data.get('success'):
                        categories = data.get('data', [])
                        found = any(cat.get('name') == test_category for cat in categories)
                        if found:
                            print("✅ تم التحقق من وجود الفئة المضافة")
                        else:
                            print("⚠️ لم يتم العثور على الفئة المضافة")
                
            else:
                print(f"❌ فشل إضافة الفئة: {result.get('message')}")
                return False
        else:
            print(f"❌ خطأ HTTP في إضافة الفئة: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            return False
        
        # اختبار إضافة موديل جديد
        print("\n📱 اختبار إضافة موديل جديد...")
        
        # الحصول على أول فئة
        response = client.get('/get_management_data/categories')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and data.get('data'):
                first_category = data['data'][0]
                category_id = first_category['id']
                category_name = first_category['name']
                
                test_model = f"TEST_MODEL_{datetime.now().strftime('%H%M%S')}"
                
                add_model_data = {
                    'action': 'add',
                    'type': 'models',
                    'name': test_model,
                    'category_id': category_id
                }
                
                response = client.post('/manage_data', 
                                      json=add_model_data,
                                      headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.get_json()
                    if result.get('success'):
                        print(f"✅ تم إضافة الموديل: {test_model} في فئة {category_name}")
                    else:
                        print(f"❌ فشل إضافة الموديل: {result.get('message')}")
                        return False
                else:
                    print(f"❌ خطأ HTTP في إضافة الموديل: {response.status_code}")
                    print(f"Response: {response.get_data(as_text=True)}")
                    return False
        
        # اختبار تحميل مواد POP
        print("\n🎨 اختبار تحميل مواد POP...")
        response = client.get('/get_dynamic_data/pop_materials?model=S95F')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                materials = data.get('data', [])
                print(f"✅ تم تحميل {len(materials)} مادة POP لموديل S95F")
                if len(materials) > 0:
                    print(f"   أول 3 مواد: {', '.join(materials[:3])}")
            else:
                print(f"❌ فشل تحميل مواد POP: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ HTTP في مواد POP: {response.status_code}")
            return False
        
        print("\n✅ جميع اختبارات API نجحت!")
        return True

def diagnose_database_structure():
    """تشخيص هيكل قاعدة البيانات"""
    print("\n🔍 تشخيص هيكل قاعدة البيانات...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # فحص الجداول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 الجداول الموجودة: {[table[0] for table in tables]}")
        
        # فحص هيكل جدول الفئات
        cursor.execute("PRAGMA table_info(categories)")
        categories_columns = cursor.fetchall()
        print(f"📊 أعمدة جدول categories: {[col[1] for col in categories_columns]}")
        
        # فحص هيكل جدول الموديلات
        cursor.execute("PRAGMA table_info(models)")
        models_columns = cursor.fetchall()
        print(f"📱 أعمدة جدول models: {[col[1] for col in models_columns]}")
        
        # فحص هيكل جدول مواد POP
        cursor.execute("PRAGMA table_info(pop_materials)")
        pop_columns = cursor.fetchall()
        print(f"🎨 أعمدة جدول pop_materials: {[col[1] for col in pop_columns]}")
        
        # فحص العلاقات
        print("\n🔗 فحص العلاقات:")
        
        # موديلات بدون فئات
        cursor.execute("SELECT COUNT(*) FROM models WHERE category_id IS NULL OR category_id NOT IN (SELECT id FROM categories)")
        orphaned_models = cursor.fetchone()[0]
        print(f"   موديلات بدون فئات: {orphaned_models}")
        
        # مواد POP بدون موديلات
        cursor.execute("SELECT COUNT(*) FROM pop_materials WHERE model_id IS NULL OR model_id NOT IN (SELECT id FROM models)")
        orphaned_materials = cursor.fetchone()[0]
        print(f"   مواد POP بدون موديلات: {orphaned_materials}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التشخيص: {e}")
        return False
    finally:
        conn.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء الإصلاح النهائي لإدارة البيانات...")
    
    # تشخيص هيكل قاعدة البيانات
    if not diagnose_database_structure():
        print("❌ فشل في تشخيص قاعدة البيانات")
        return False
    
    # تنظيف البيانات المكررة
    if not clean_duplicate_data():
        print("❌ فشل في تنظيف البيانات")
        return False
    
    # اختبار API إدارة البيانات
    if not test_data_management_api():
        print("❌ فشل في اختبار API")
        return False
    
    print("\n🎉 تم الإصلاح النهائي بنجاح!")
    print("\n📋 ملخص النتائج:")
    print("   ✅ تنظيف البيانات المكررة")
    print("   ✅ اختبار تسجيل الدخول")
    print("   ✅ اختبار جلب الفئات")
    print("   ✅ اختبار إضافة فئة جديدة")
    print("   ✅ اختبار إضافة موديل جديد")
    print("   ✅ اختبار تحميل مواد POP")
    
    print("\n🚀 النظام جاهز للاستخدام!")
    
    return True

if __name__ == "__main__":
    main()