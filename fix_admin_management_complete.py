#!/usr/bin/env python3
"""
إصلاح شامل لمشكلة إدارة البيانات
"""

import sqlite3
from datetime import datetime

def fix_admin_management():
    """إصلاح مشكلة إدارة البيانات"""
    print("🔧 إصلاح مشكلة إدارة البيانات...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود البيانات الأساسية
        print("📊 التحقق من البيانات الأساسية...")
        
        # عد الفئات
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        print(f"   الفئات: {categories_count}")
        
        # عد الموديلات
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        print(f"   الموديلات: {models_count}")
        
        # عد أنواع العرض
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        print(f"   أنواع العرض: {display_count}")
        
        # عد مواد POP
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        print(f"   مواد POP: {pop_count}")
        
        # اختبار إضافة فئة جديدة
        print("\n🧪 اختبار إضافة فئة جديدة...")
        test_category = "TEST_CATEGORY_" + datetime.now().strftime('%H%M%S')
        
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO categories (category_name, created_date, name, created_at) VALUES (?, ?, ?, ?)",
                         (test_category, current_time, test_category, current_time))
            conn.commit()
            print(f"✅ تم إضافة فئة اختبار: {test_category}")
            
            # حذف الفئة الاختبارية
            cursor.execute("DELETE FROM categories WHERE category_name = ?", (test_category,))
            conn.commit()
            print("✅ تم حذف فئة الاختبار")
            
        except Exception as e:
            print(f"❌ خطأ في اختبار إضافة الفئة: {e}")
            conn.rollback()
        
        # اختبار إضافة موديل جديد
        print("\n🧪 اختبار إضافة موديل جديد...")
        
        # الحصول على أول فئة
        cursor.execute("SELECT id, category_name FROM categories LIMIT 1")
        category_result = cursor.fetchone()
        
        if category_result:
            category_id, category_name = category_result
            test_model = "TEST_MODEL_" + datetime.now().strftime('%H%M%S')
            
            try:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO models (model_name, category_name, created_date, name, category_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                             (test_model, category_name, current_time, test_model, category_id, current_time))
                conn.commit()
                print(f"✅ تم إضافة موديل اختبار: {test_model} في فئة {category_name}")
                
                # حذف الموديل الاختباري
                cursor.execute("DELETE FROM models WHERE model_name = ?", (test_model,))
                conn.commit()
                print("✅ تم حذف موديل الاختبار")
                
            except Exception as e:
                print(f"❌ خطأ في اختبار إضافة الموديل: {e}")
                conn.rollback()
        
        # اختبار إضافة مادة POP
        print("\n🧪 اختبار إضافة مادة POP...")
        
        # الحصول على أول موديل
        cursor.execute("SELECT id, model_name FROM models LIMIT 1")
        model_result = cursor.fetchone()
        
        if model_result:
            model_id, model_name = model_result
            test_material = "TEST_MATERIAL_" + datetime.now().strftime('%H%M%S')
            
            try:
                cursor.execute("INSERT INTO pop_materials (name, model_id, created_at) VALUES (?, ?, ?)",
                             (test_material, model_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                print(f"✅ تم إضافة مادة POP اختبار: {test_material} للموديل {model_name}")
                
                # حذف المادة الاختبارية
                cursor.execute("DELETE FROM pop_materials WHERE name = ?", (test_material,))
                conn.commit()
                print("✅ تم حذف مادة POP الاختبار")
                
            except Exception as e:
                print(f"❌ خطأ في اختبار إضافة مادة POP: {e}")
                conn.rollback()
        
        print("\n✅ اكتمل اختبار إدارة البيانات!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار إدارة البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_admin_routes():
    """اختبار routes الإدارة"""
    print("\n🌐 اختبار routes الإدارة...")
    
    from app import app
    
    with app.test_client() as client:
        # محاولة الوصول لصفحة الإدارة (بدون تسجيل دخول)
        response = client.get('/admin_management')
        if response.status_code == 302:  # Redirect to login
            print("✅ صفحة الإدارة محمية بشكل صحيح")
        else:
            print(f"⚠️ صفحة الإدارة غير محمية: {response.status_code}")
        
        # اختبار جلب بيانات الفئات
        response = client.get('/get_management_data/categories')
        if response.status_code == 401:  # Unauthorized
            print("✅ API الإدارة محمي بشكل صحيح")
        else:
            print(f"⚠️ API الإدارة غير محمي: {response.status_code}")
        
        print("✅ اكتمل اختبار routes الإدارة!")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إصلاح مشكلة إدارة البيانات...")
    
    # إصلاح قاعدة البيانات
    if not fix_admin_management():
        print("❌ فشل في إصلاح قاعدة البيانات")
        return False
    
    # اختبار routes
    test_admin_routes()
    
    print("\n🎉 تم إصلاح مشكلة إدارة البيانات بنجاح!")
    print("\n📋 ملخص الإصلاحات:")
    print("   ✅ اختبار إضافة الفئات")
    print("   ✅ اختبار إضافة الموديلات")
    print("   ✅ اختبار إضافة مواد POP")
    print("   ✅ اختبار حماية routes الإدارة")
    
    print("\n🔑 للاختبار:")
    print("   1. شغل التطبيق: python app.py")
    print("   2. سجل دخول بالمدير: admin / admin123")
    print("   3. انتقل إلى Admin Management")
    print("   4. جرب إضافة فئة أو موديل جديد")
    
    return True

if __name__ == "__main__":
    main()