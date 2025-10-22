#!/usr/bin/env python3
"""
الحل النهائي الفوري - إصلاح مشكلة PostgreSQL
"""

def create_ultimate_js_fix():
    """إنشاء ملف JavaScript نهائي يحل المشكلة"""
    print("🔧 إنشاء الحل النهائي...")
    
    ultimate_js = '''
// ULTIMATE FIX - Override everything
console.log("🚀 ULTIMATE JavaScript Fix Loaded");

// Complete override of handleFormSubmit
window.handleFormSubmit = function(e) {
    console.log("🔧 ULTIMATE handleFormSubmit called");
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Get form values
    const itemId = document.getElementById('item-id').value;
    const dataType = document.getElementById('data-type').value;
    const itemName = document.getElementById('item-name').value;
    
    console.log("📊 Form values:", {itemId, dataType, itemName});
    
    // Build data object
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName.trim()
    };
    
    if (itemId) {
        data.id = parseInt(itemId);
    }
    
    // Handle category_id for models, display_types, pop_materials
    if (dataType === 'models' || dataType === 'display_types') {
        const categorySelect = document.getElementById('item-category');
        if (categorySelect && categorySelect.value) {
            data.category_id = parseInt(categorySelect.value);
            console.log("📊 Category ID:", data.category_id);
        }
    }
    
    // Handle model_id for pop_materials
    if (dataType === 'pop_materials') {
        const modelSelect = document.getElementById('item-model');
        if (modelSelect && modelSelect.value) {
            data.model_id = parseInt(modelSelect.value);
            console.log("📱 Model ID:", data.model_id);
        }
    }
    
    console.log("📤 Final data to send:", JSON.stringify(data, null, 2));
    
    // Validate data before sending
    if (!data.name) {
        alert('❌ Name is required');
        return;
    }
    
    if (dataType !== 'categories' && !data.category_id) {
        alert('❌ Category is required');
        return;
    }
    
    if (dataType === 'pop_materials' && !data.model_id) {
        alert('❌ Model is required');
        return;
    }
    
    // Send request
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log("📥 Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        console.log("📥 Response data:", result);
        if (result.success) {
            alert('✅ ' + result.message);
            closeModal();
            // Reload the current tab data
            if (typeof loadData === 'function') {
                loadData(dataType);
            } else {
                location.reload();
            }
        } else {
            alert('❌ Error: ' + result.message);
        }
    })
    .catch(error => {
        console.error('❌ Request failed:', error);
        alert('❌ Request failed: ' + error.message);
    });
};

// Override when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 ULTIMATE: DOM loaded, overriding form handler");
    
    const form = document.getElementById('dataForm');
    if (form) {
        // Remove all existing listeners
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        // Add our ultimate handler
        newForm.addEventListener('submit', window.handleFormSubmit);
        console.log("✅ ULTIMATE form handler attached");
    }
    
    // Also override any existing handleFormSubmit function
    setTimeout(() => {
        const form = document.getElementById('dataForm');
        if (form) {
            form.onsubmit = window.handleFormSubmit;
            console.log("✅ ULTIMATE: Form onsubmit overridden");
        }
    }, 1000);
});

// Override after 2 seconds to be absolutely sure
setTimeout(() => {
    const form = document.getElementById('dataForm');
    if (form) {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', window.handleFormSubmit);
        console.log("✅ ULTIMATE: Final override complete");
    }
}, 2000);
'''
    
    with open('static/js/ultimate_admin_fix.js', 'w', encoding='utf-8') as f:
        f.write(ultimate_js)
    
    print("✅ تم إنشاء الحل النهائي")

def update_template():
    """تحديث template لاستخدام الحل النهائي"""
    print("🔧 تحديث template...")
    
    # قراءة الملف الحالي
    with open('templates/admin_management.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة الحل النهائي
    if 'ultimate_admin_fix.js' not in content:
        content = content.replace(
            '<script src="{{ url_for(\'static\', filename=\'js/emergency_admin_fix.js\') }}"></script>',
            '''<script src="{{ url_for('static', filename='js/emergency_admin_fix.js') }}"></script>
<script src="{{ url_for('static', filename='js/ultimate_admin_fix.js') }}"></script>'''
        )
        
        with open('templates/admin_management.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم تحديث template")
    else:
        print("ℹ️ Template محدث مسبقاً")

def fix_app_py_postgresql():
    """إصلاح app.py للتعامل مع PostgreSQL بشكل صحيح"""
    print("🔧 إصلاح app.py للتعامل مع PostgreSQL...")
    
    # قراءة الملف
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة معالجة أفضل للأخطاء في manage_data
    if 'except psycopg2.Error as e:' not in content:
        # البحث عن دالة manage_data وإضافة معالجة أفضل للأخطاء
        old_error_handling = '''        except Exception as e:
            conn.rollback()
            raise e'''
        
        new_error_handling = '''        except Exception as e:
            conn.rollback()
            print(f"Database error in manage_data: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500'''
        
        if old_error_handling in content:
            content = content.replace(old_error_handling, new_error_handling)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ تم إصلاح معالجة الأخطاء في app.py")
        else:
            print("ℹ️ معالجة الأخطاء محدثة مسبقاً")

def main():
    """تشغيل الحل النهائي"""
    print("🚀 بدء الحل النهائي الفوري...")
    
    # إنشاء ملف JavaScript نهائي
    create_ultimate_js_fix()
    
    # تحديث template
    update_template()
    
    # إصلاح app.py
    fix_app_py_postgresql()
    
    print("\n🎉 تم تطبيق الحل النهائي!")
    print("\n📋 الإصلاحات:")
    print("   ✅ JavaScript نهائي يتعامل مع IDs بشكل صحيح")
    print("   ✅ تحويل القيم إلى integers")
    print("   ✅ التحقق من صحة البيانات قبل الإرسال")
    print("   ✅ معالجة أفضل للأخطاء")
    
    return True

if __name__ == "__main__":
    main()