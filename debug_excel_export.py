#!/usr/bin/env python3
"""
تشخيص مفصل لتصدير Excel
"""

import sqlite3
from excel_export_enhanced import export_enhanced_excel_with_cloudinary

def debug_excel_export():
    """تشخيص مفصل لتصدير Excel"""
    print("🔍 تشخيص مفصل لتصدير Excel")
    print("=" * 50)
    
    try:
        # الحصول على البيانات
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''SELECT id, employee_name, employee_code, branch, shop_code, model, 
                            display_type, selected_materials, unselected_materials, images, date 
                     FROM data_entries ORDER BY date DESC''')
        entries = c.fetchall()
        conn.close()
        
        print(f"📊 تم العثور على {len(entries)} إدخال")
        
        # تحليل الصور
        total_images = 0
        cloudinary_images = 0
        local_images = 0
        missing_images = 0
        
        print("\n📋 تحليل الصور:")
        for i, entry in enumerate(entries, 1):
            images_data = entry[9] if entry[9] else ''
            if images_data:
                image_urls = [url.strip() for url in images_data.split(',') if url.strip()]
                total_images += len(image_urls)
                
                for image_url in image_urls:
                    if image_url.startswith('http'):
                        cloudinary_images += 1
                        print(f"  {i}. ✅ Cloudinary: {image_url[:50]}...")
                    else:
                        import os
                        local_path = os.path.join('static/uploads', image_url)
                        if os.path.exists(local_path):
                            local_images += 1
                            print(f"  {i}. ✅ Local: {image_url}")
                        else:
                            missing_images += 1
                            print(f"  {i}. ❌ Missing: {image_url}")
            else:
                print(f"  {i}. ⚪ No images: {entry[1]}")
        
        print(f"\n📊 ملخص الصور:")
        print(f"   - إجمالي الصور: {total_images}")
        print(f"   - Cloudinary: {cloudinary_images}")
        print(f"   - محلية موجودة: {local_images}")
        print(f"   - مفقودة: {missing_images}")
        
        # اختبار التصدير
        print(f"\n🖼️ اختبار التصدير المحسن...")
        result = export_enhanced_excel_with_cloudinary(entries)
        
        print(f"📊 نتيجة التصدير:")
        print(f"   - نجح: {result['success']}")
        print(f"   - الطريقة: {result.get('method', 'غير محدد')}")
        print(f"   - الرسالة: {result.get('message', 'لا توجد رسالة')}")
        
        if result['success']:
            if result['method'] == 'cloudinary':
                print(f"   - رابط Cloudinary: {result['url']}")
            else:
                file_size = len(result['data']) / 1024
                print(f"   - حجم الملف المحلي: {file_size:.1f} KB")
                
                # حفظ الملف للاختبار
                with open('debug_export.xlsx', 'wb') as f:
                    f.write(result['data'])
                print(f"   - تم حفظ الملف: debug_export.xlsx")
        else:
            print(f"   - خطأ: {result.get('error', 'خطأ غير معروف')}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ خطأ في التشخيص: {e}")
        return False

def test_cloudinary_status():
    """اختبار حالة Cloudinary"""
    print("\n☁️ اختبار حالة Cloudinary:")
    
    try:
        # تحميل متغيرات البيئة
        from dotenv import load_dotenv
        load_dotenv()
        
        from cloudinary_config import is_cloudinary_configured
        
        if is_cloudinary_configured():
            print("✅ Cloudinary مُعد بشكل صحيح")
            
            # اختبار الاتصال
            from cloudinary_config import configure_cloudinary
            import cloudinary.api
            
            configure_cloudinary()
            result = cloudinary.api.ping()
            
            if result.get('status') == 'ok':
                print("✅ الاتصال بـ Cloudinary ناجح")
                return True
            else:
                print("❌ فشل الاتصال بـ Cloudinary")
                return False
        else:
            print("❌ Cloudinary غير مُعد")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار Cloudinary: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧪 تشخيص شامل لتصدير Excel")
    print("=" * 60)
    
    # اختبار Cloudinary
    cloudinary_ok = test_cloudinary_status()
    
    # اختبار التصدير
    export_ok = debug_excel_export()
    
    print("\n" + "=" * 60)
    print("📊 ملخص التشخيص")
    print("=" * 60)
    
    print(f"Cloudinary: {'✅ يعمل' if cloudinary_ok else '❌ لا يعمل'}")
    print(f"تصدير Excel: {'✅ يعمل' if export_ok else '❌ لا يعمل'}")
    
    if cloudinary_ok and export_ok:
        print("\n🎉 كل شيء يعمل بشكل صحيح!")
        print("\n📋 التوصيات:")
        print("1. تحقق من ملف debug_export.xlsx")
        print("2. شغل التطبيق واختبر التصدير من Dashboard")
        print("3. أدخل بيانات جديدة مع صور")
    else:
        print("\n❌ هناك مشاكل تحتاج إصلاح")
        if not cloudinary_ok:
            print("🔧 أصلح إعدادات Cloudinary أولاً")
        if not export_ok:
            print("🔧 راجع أخطاء التصدير أعلاه")

if __name__ == "__main__":
    main()