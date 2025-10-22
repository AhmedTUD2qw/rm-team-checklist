#!/usr/bin/env python3
"""
الحل الشامل والنهائي - إصلاح جميع المشاكل
"""

import sqlite3
import os
from datetime import datetime

def reset_everything():
    """إعادة تعيين كل شيء من الصفر"""
    print("🚨 إعادة تعيين شاملة من الصفر...")
    
    # حذف قاعدة البيانات
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("🗑️ تم حذف قاعدة البيانات القديمة")
    
    # إنشاء قاعدة بيانات جديدة ونظيفة
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # إنشاء الجداول
        cursor.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            employee_code TEXT UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
        
        cursor.execute('''CREATE TABLE display_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
        
        cursor.execute('''CREATE TABLE pop_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )''')
        
        cursor.execute('''CREATE TABLE data_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            employee_name TEXT NOT NULL,
            employee_code TEXT NOT NULL,
            branch_name TEXT NOT NULL,
            shop_code TEXT,
            category TEXT NOT NULL,
            model TEXT NOT NULL,
            display_type TEXT NOT NULL,
            selected_materials TEXT,
            missing_materials TEXT,
            image_urls TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        cursor.execute('''CREATE TABLE branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE user_branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, branch_name)
        )''')
        
        # إضافة المستخدم الإداري
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        cursor.execute('''INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) 
                         VALUES (?, ?, ?, ?, ?)''',
                      ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
        
        # إضافة فئات أساسية فقط
        categories = ['OLED', 'QLED', 'UHD']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for category in categories:
            cursor.execute('INSERT INTO categories (name, created_at) VALUES (?, ?)',
                          (category, current_time))
        
        # إضافة موديلات أساسية
        models_data = {
            'OLED': ['S95F'],
            'QLED': ['Q8F'],
            'UHD': ['U8000']
        }
        
        for category_name, model_list in models_data.items():
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                for model_name in model_list:
                    cursor.execute('INSERT INTO models (name, category_id, created_at) VALUES (?, ?, ?)',
                                 (model_name, category_id, current_time))
        
        # إضافة أنواع عرض أساسية
        display_types = ['Highlight Zone', 'Fixtures']
        for category_name in categories:
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                for display_name in display_types:
                    cursor.execute('INSERT INTO display_types (name, category_id, created_at) VALUES (?, ?, ?)',
                                 (display_name, category_id, current_time))
        
        # إضافة مواد POP أساسية
        s95f_materials = ['AI topper', 'OLED Topper', 'Side POP']
        cursor.execute('SELECT id FROM models WHERE name = ?', ('S95F',))
        s95f_result = cursor.fetchone()
        if s95f_result:
            s95f_id = s95f_result[0]
            for material in s95f_materials:
                cursor.execute('INSERT INTO pop_materials (name, model_id, created_at) VALUES (?, ?, ?)',
                             (material, s95f_id, current_time))
        
        conn.commit()
        
        # إحصائيات
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM models")
        models_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pop_materials")
        pop_count = cursor.fetchone()[0]
        
        print(f"✅ قاعدة بيانات جديدة:")
        print(f"   📊 الفئات: {categories_count}")
        print(f"   📱 الموديلات: {models_count}")
        print(f"   🖥️ أنواع العرض: {display_count}")
        print(f"   🎨 مواد POP: {pop_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_super_simple_js():
    """إنشاء JavaScript بسيط جداً وفعال"""
    print("🔧 إنشاء JavaScript بسيط وفعال...")
    
    simple_js = '''
// SUPER SIMPLE JavaScript Fix
console.log("🔧 SUPER SIMPLE JavaScript loaded");

// Simple form handler
function handleFormSubmit(e) {
    e.preventDefault();
    console.log("📝 Form submitted");
    
    // Get form elements directly
    const itemId = document.getElementById('item-id').value || '';
    const dataType = document.getElementById('data-type').value || '';
    const itemName = document.getElementById('item-name').value || '';
    
    console.log("Form data:", {itemId, dataType, itemName});
    
    // Build request data
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName.trim()
    };
    
    if (itemId) {
        data.id = parseInt(itemId);
    }
    
    // Handle category for models/display_types/pop_materials
    if (dataType === 'models' || dataType === 'display_types') {
        const categorySelect = document.getElementById('item-category');
        if (categorySelect && categorySelect.value) {
            data.category_id = parseInt(categorySelect.value);
            console.log("Category ID:", data.category_id);
        } else {
            alert('❌ Please select a category');
            return;
        }
    }
    
    // Handle model for pop_materials
    if (dataType === 'pop_materials') {
        const modelSelect = document.getElementById('item-model');
        if (modelSelect && modelSelect.value) {
            data.model_id = parseInt(modelSelect.value);
            console.log("Model ID:", data.model_id);
        } else {
            alert('❌ Please select a model');
            return;
        }
    }
    
    // Validate
    if (!data.name) {
        alert('❌ Name is required');
        return;
    }
    
    console.log("Sending:", JSON.stringify(data, null, 2));
    
    // Send request
    fetch('/manage_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log("Response:", result);
        if (result.success) {
            alert('✅ ' + result.message);
            closeModal();
            location.reload();
        } else {
            alert('❌ ' + result.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert('❌ Network error');
    });
}

// Attach handler when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 Attaching form handler");
    const form = document.getElementById('dataForm');
    if (form) {
        form.onsubmit = handleFormSubmit;
        console.log("✅ Form handler attached");
    }
});
'''
    
    with open('static/js/super_simple_admin.js', 'w', encoding='utf-8') as f:
        f.write(simple_js)
    
    print("✅ تم إنشاء JavaScript بسيط")

def update_template_final():
    """تحديث template نهائي"""
    print("🔧 تحديث template نهائي...")
    
    # قراءة الملف
    with open('templates/admin_management.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استبدال جميع ملفات JavaScript بملف واحد بسيط
    new_scripts = '''{% block scripts %}
<script src="{{ url_for('static', filename='js/super_simple_admin.js') }}"></script>
{% endblock %}'''
    
    # البحث عن block scripts واستبداله
    import re
    pattern = r'{% block scripts %}.*?{% endblock %}'
    content = re.sub(pattern, new_scripts, content, flags=re.DOTALL)
    
    with open('templates/admin_management.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم تحديث template")

def main():
    """تشغيل الحل الشامل"""
    print("🚀 بدء الحل الشامل والنهائي...")
    
    # إعادة تعيين كل شيء
    if not reset_everything():
        print("❌ فشل في إعادة التعيين")
        return False
    
    # إنشاء JavaScript بسيط
    create_super_simple_js()
    
    # تحديث template
    update_template_final()
    
    print("\n🎉 تم تطبيق الحل الشامل!")
    print("\n📋 ما تم عمله:")
    print("   ✅ إعادة تعيين قاعدة البيانات بالكامل")
    print("   ✅ بيانات أساسية فقط (3 فئات، 3 موديلات)")
    print("   ✅ JavaScript بسيط وفعال")
    print("   ✅ template محدث")
    
    return True

if __name__ == "__main__":
    main()