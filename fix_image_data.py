#!/usr/bin/env python3
"""
إصلاح بيانات الصور في قاعدة البيانات
"""

import sqlite3
import os

def fix_image_data():
    """إصلاح بيانات الصور المعطلة"""
    print("🔧 إصلاح بيانات الصور في قاعدة البيانات...")
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # الحصول على جميع الإدخالات مع الصور
        c.execute('SELECT id, employee_name, images FROM data_entries WHERE images IS NOT NULL AND images != ""')
        entries = c.fetchall()
        
        print(f"📊 تم العثور على {len(entries)} إدخال يحتوي على صور")
        
        fixed_count = 0
        removed_count = 0
        
        for entry_id, employee_name, images in entries:
            if not images:
                continue
                
            image_list = [img.strip() for img in images.split(',') if img.strip()]
            valid_images = []
            
            for image in image_list:
                if image.startswith('http'):
                    # Cloudinary image - keep it
                    valid_images.append(image)
                    print(f"✅ ID {entry_id}: Cloudinary image kept")
                else:
                    # Local image - check if exists
                    local_path = os.path.join('static/uploads', image)
                    if os.path.exists(local_path):
                        valid_images.append(image)
                        print(f"✅ ID {entry_id}: Local image exists: {image}")
                    else:
                        print(f"❌ ID {entry_id}: Local image missing: {image}")
                        removed_count += 1
            
            # Update the database with valid images only
            new_images = ','.join(valid_images) if valid_images else ''
            
            if new_images != images:
                c.execute('UPDATE data_entries SET images = ? WHERE id = ?', (new_images, entry_id))
                fixed_count += 1
                print(f"🔧 ID {entry_id}: Updated images for {employee_name}")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 ملخص الإصلاح:")
        print(f"   - إدخالات تم إصلاحها: {fixed_count}")
        print(f"   - صور تم إزالتها (مفقودة): {removed_count}")
        print(f"   - إدخالات سليمة: {len(entries) - fixed_count}")
        
        if fixed_count > 0:
            print("\n✅ تم إصلاح بيانات الصور بنجاح!")
        else:
            print("\n✅ جميع بيانات الصور سليمة!")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح البيانات: {e}")
        return False

def show_current_data():
    """عرض البيانات الحالية"""
    print("\n📋 البيانات الحالية:")
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute('SELECT id, employee_name, images FROM data_entries ORDER BY id DESC LIMIT 10')
        entries = c.fetchall()
        
        for entry_id, employee_name, images in entries:
            if images:
                image_count = len([img for img in images.split(',') if img.strip()])
                cloudinary_count = len([img for img in images.split(',') if img.strip().startswith('http')])
                local_count = image_count - cloudinary_count
                
                print(f"ID {entry_id}: {employee_name} - {image_count} صور ({cloudinary_count} Cloudinary, {local_count} محلية)")
            else:
                print(f"ID {entry_id}: {employee_name} - لا توجد صور")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في عرض البيانات: {e}")

def main():
    """الدالة الرئيسية"""
    print("🔧 أداة إصلاح بيانات الصور")
    print("=" * 50)
    
    # عرض البيانات الحالية
    show_current_data()
    
    # إصلاح البيانات
    success = fix_image_data()
    
    if success:
        # عرض البيانات بعد الإصلاح
        show_current_data()
        
        print("\n🚀 الخطوات التالية:")
        print("1. شغل التطبيق: python app.py")
        print("2. تحقق من عرض الصور في Dashboard")
        print("3. جرب التصدير المحسن")
        print("4. أدخل بيانات جديدة مع صور (ستُرفع إلى Cloudinary)")

if __name__ == "__main__":
    main()