#!/usr/bin/env python3
"""
حل طوارئ فوري لمشاكل Render
"""

import sqlite3
import os
from datetime import datetime

def emergency_database_reset():
    """إعادة تعيين قاعدة البيانات بالكامل"""
    print("🚨 إعادة تعيين قاعدة البيانات - حل الطوارئ...")
    
    # حذف قاعدة البيانات القديمة
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("🗑️ تم حذف قاعدة البيانات القديمة")
    
    # إنشاء قاعدة بيانات جديدة
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # إنشاء جدول المستخدمين
        cursor.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            employee_code TEXT UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # إنشاء جدول الفئات
        cursor.execute('''CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # إنشاء جدول الموديلات
        cursor.execute('''CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
        
        # إنشاء جدول مواد POP
        cursor.execute('''CREATE TABLE pop_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )''')
        
        print("✅ تم إنشاء الجداول الأساسية")
        
        # إضافة المستخدم الإداري
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        cursor.execute('''INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) 
                         VALUES (?, ?, ?, ?, ?)''',
                      ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
        print("👤 تم إنشاء المستخدم الإداري")
        
        # إضافة الفئات الأساسية فقط
        categories = ['OLED', 'Neo QLED', 'QLED']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for category in categories:
            cursor.execute('INSERT INTO categories (name, created_at) VALUES (?, ?)',
                          (category, current_time))
        
        print(f"📊 تم إضافة {len(categories)} فئة أساسية")
        
        # إضافة موديلات أساسية
        models_data = {
            'OLED': ['S95F', 'S90F'],
            'Neo QLED': ['QN90F', 'QN85F'],
            'QLED': ['Q8F', 'Q7F']
        }
        
        models_count = 0
        for category_name, model_list in models_data.items():
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                for model_name in model_list:
                    cursor.execute('INSERT INTO models (name, category_id, created_at) VALUES (?, ?, ?)',
                                 (model_name, category_id, current_time))
                    models_count += 1
        
        print(f"📱 تم إضافة {models_count} موديل أساسي")
        
        # إضافة مواد POP لموديل S95F فقط
        s95f_materials = [
            'AI topper', 'OLED Topper', 'Glare Free', 'New Topper', 'Side POP', 'Specs Card'
        ]
        
        cursor.execute('SELECT id FROM models WHERE name = ?', ('S95F',))
        s95f_result = cursor.fetchone()
        if s95f_result:
            s95f_id = s95f_result[0]
            for material in s95f_materials:
                cursor.execute('INSERT INTO pop_materials (name, model_id, created_at) VALUES (?, ?, ?)',
                             (material, s95f_id, current_time))
        
        print(f"🎨 تم إضافة {len(s95f_materials)} مادة POP")
        
        conn.commit()
        
        # إحصائيات نهائية
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        print(f"\n✅ قاعدة البيانات الجديدة جاهزة:")
        print(f"   📊 الفئات: {categories_count}")
        print(f"   📱 الموديلات: {models_count}")
        print(f"   🎨 مواد POP: {pop_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة التعيين: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_emergency_js():
    """إنشاء ملف JavaScript طوارئ"""
    print("🔧 إنشاء ملف JavaScript طوارئ...")
    
    emergency_js = '''// Emergency JavaScript Fix
console.log("🚨 Emergency JavaScript Fix Loaded");

function handleFormSubmit(e) {
    console.log("🔧 Emergency handleFormSubmit called");
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const itemId = formData.get('item-id') || document.getElementById('item-id').value;
    const dataType = formData.get('data-type') || document.getElementById('data-type').value;
    const itemName = formData.get('item-name') || document.getElementById('item-name').value;
    const itemCategory = formData.get('item-category') || document.getElementById('item-category').value;
    
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName
    };
    
    if (itemId) {
        data.id = itemId;
    }
    
    if (dataType !== 'categories') {
        data.category_id = itemCategory;
        
        if (dataType === 'pop_materials') {
            const itemModel = document.getElementById('item-model').value;
            data.model_id = itemModel;
        }
    }
    
    console.log("📤 Sending data:", JSON.stringify(data, null, 2));
    
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log("📥 Response:", data);
        if (data.success) {
            alert('✅ ' + data.message);
            closeModal();
            location.reload();
        } else {
            alert('❌ Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        alert('❌ Network error: ' + error.message);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dataForm');
    if (form) {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', handleFormSubmit);
        console.log("✅ Emergency form handler attached");
    }
});'''
    
    with open('static/js/emergency_admin_fix.js', 'w', encoding='utf-8') as f:
        f.write(emergency_js)
    
    print("✅ تم إنشاء ملف JavaScript الطوارئ")

def main():
    """تشغيل حل الطوارئ"""
    print("🚨 بدء حل الطوارئ الفوري...")
    
    # إعادة تعيين قاعدة البيانات
    if not emergency_database_reset():
        print("❌ فشل في إعادة تعيين قاعدة البيانات")
        return False
    
    # إنشاء ملف JavaScript طوارئ
    create_emergency_js()
    
    print("\n🎉 تم تطبيق حل الطوارئ بنجاح!")
    
    return True

if __name__ == "__main__":
    main()