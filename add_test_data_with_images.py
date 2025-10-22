#!/usr/bin/env python3
"""
إضافة بيانات تجريبية مع صور للاختبار
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def add_test_data():
    """إضافة بيانات تجريبية مع صور"""
    print("📊 إضافة بيانات تجريبية مع صور...")
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # إضافة مستخدم تجريبي إذا لم يكن موجوداً
        c.execute('SELECT COUNT(*) FROM users WHERE company_code = ?', ('TEST001',))
        if c.fetchone()[0] == 0:
            test_password = generate_password_hash('test123')
            c.execute('''INSERT INTO users (name, company_code, password, is_admin) 
                         VALUES (?, ?, ?, ?)''',
                     ('Test Employee', 'TEST001', test_password, False))
            print("✅ تم إضافة مستخدم تجريبي: Test Employee / TEST001 / test123")
        
        # إضافة فرع تجريبي
        c.execute('''INSERT OR IGNORE INTO branches (branch_name, shop_code, employee_code, created_date) 
                     VALUES (?, ?, ?, ?)''',
                 ('Test Branch Cairo', 'TB001', 'TEST001', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # بيانات تجريبية مع روابط صور من Cloudinary (عامة)
        test_entries = [
            {
                'employee_name': 'Test Employee',
                'employee_code': 'TEST001',
                'branch': 'Test Branch Cairo',
                'shop_code': 'TB001',
                'model': 'OLED - Samsung S95F',
                'display_type': 'Highlight Zone',
                'selected_materials': 'AI topper,OLED Topper,Glare Free',
                'unselected_materials': 'Screen POP,Gaming Features',
                'images': 'https://res.cloudinary.com/demo/image/upload/sample.jpg,https://res.cloudinary.com/demo/image/upload/sample2.jpg',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'employee_name': 'Test Employee',
                'employee_code': 'TEST001',
                'branch': 'Test Branch Cairo',
                'shop_code': 'TB001',
                'model': 'Neo QLED - Samsung QN90',
                'display_type': 'Fixtures',
                'selected_materials': 'Neo Quantum Processor,Gaming Hub,Premium Features',
                'unselected_materials': 'Basic Features',
                'images': 'https://res.cloudinary.com/demo/image/upload/sample3.jpg',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'employee_name': 'Test Employee',
                'employee_code': 'TEST001',
                'branch': 'Test Branch Cairo',
                'shop_code': 'TB001',
                'model': 'QLED - Samsung Q8F',
                'display_type': 'Multi Brand Zone',
                'selected_materials': 'QLED Topper,Smart Features,Performance Card',
                'unselected_materials': '',
                'images': '',  # بدون صور
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        # إضافة البيانات
        for entry in test_entries:
            c.execute('''INSERT INTO data_entries 
                        (employee_name, employee_code, branch, shop_code, model, display_type, 
                         selected_materials, unselected_materials, images, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (entry['employee_name'], entry['employee_code'], entry['branch'], 
                      entry['shop_code'], entry['model'], entry['display_type'],
                      entry['selected_materials'], entry['unselected_materials'], 
                      entry['images'], entry['date']))
        
        conn.commit()
        conn.close()
        
        print(f"✅ تم إضافة {len(test_entries)} إدخال تجريبي")
        print("\n📋 البيانات المضافة:")
        for i, entry in enumerate(test_entries, 1):
            images_count = len(entry['images'].split(',')) if entry['images'] else 0
            print(f"  {i}. {entry['model']} - {images_count} صور")
        
        print("\n🎯 الآن يمكنك:")
        print("1. تشغيل التطبيق: python app.py")
        print("2. تسجيل الدخول كمشرف: Admin / ADMIN / admin123")
        print("3. اختبار التصدير المحسن مع الصور")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة البيانات: {e}")
        return False

if __name__ == "__main__":
    success = add_test_data()
    if success:
        print("\n🎉 تم إضافة البيانات التجريبية بنجاح!")
    else:
        print("\n❌ فشل في إضافة البيانات التجريبية!")