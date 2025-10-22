import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime
import tempfile
from werkzeug.utils import secure_filename
import pandas as pd

# إعداد Cloudinary
def configure_cloudinary():
    """Configure Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )

def upload_image_to_cloudinary(file, folder="employee_data_images"):
    """
    رفع صورة إلى Cloudinary
    
    Args:
        file: ملف الصورة
        folder: مجلد التخزين في Cloudinary
    
    Returns:
        dict: معلومات الصورة المرفوعة أو None في حالة الخطأ
    """
    try:
        configure_cloudinary()
        
        # إنشاء اسم فريد للملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        public_id = f"{folder}/{timestamp}_{filename.split('.')[0]}"
        
        # رفع الصورة
        result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            folder=folder,
            resource_type="image",
            format="jpg",  # تحويل جميع الصور إلى JPG لتوفير المساحة
            quality="auto:good",  # ضغط تلقائي للصور
            fetch_format="auto",
            transformation=[
                {'width': 1200, 'height': 1200, 'crop': 'limit'},  # تحديد الحد الأقصى للحجم
                {'quality': 'auto:good'}
            ]
        )
        
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result['format'],
            'width': result['width'],
            'height': result['height'],
            'bytes': result['bytes']
        }
        
    except Exception as e:
        print(f"خطأ في رفع الصورة إلى Cloudinary: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def upload_excel_to_cloudinary(file_path, filename, folder="employee_data_exports"):
    """
    رفع ملف Excel إلى Cloudinary
    
    Args:
        file_path: مسار الملف المحلي
        filename: اسم الملف
        folder: مجلد التخزين في Cloudinary
    
    Returns:
        dict: معلومات الملف المرفوع أو None في حالة الخطأ
    """
    try:
        configure_cloudinary()
        
        # إنشاء اسم فريد للملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        public_id = f"{folder}/{timestamp}_{filename.split('.')[0]}"
        
        # رفع ملف Excel
        result = cloudinary.uploader.upload(
            file_path,
            public_id=public_id,
            folder=folder,
            resource_type="raw",  # للملفات غير الصور
            use_filename=True,
            unique_filename=True
        )
        
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result.get('format', 'xlsx'),
            'bytes': result['bytes']
        }
        
    except Exception as e:
        print(f"خطأ في رفع ملف Excel إلى Cloudinary: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def delete_file_from_cloudinary(public_id, resource_type="image"):
    """
    حذف ملف من Cloudinary
    
    Args:
        public_id: معرف الملف في Cloudinary
        resource_type: نوع الملف (image أو raw)
    
    Returns:
        bool: True إذا تم الحذف بنجاح
    """
    try:
        configure_cloudinary()
        
        result = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        
        return result.get('result') == 'ok'
        
    except Exception as e:
        print(f"خطأ في حذف الملف من Cloudinary: {e}")
        return False

def get_cloudinary_images_list(folder="employee_data_images", max_results=100):
    """
    الحصول على قائمة الصور من Cloudinary
    
    Args:
        folder: مجلد البحث
        max_results: عدد النتائج الأقصى
    
    Returns:
        list: قائمة الصور
    """
    try:
        configure_cloudinary()
        
        result = cloudinary.api.resources(
            type="upload",
            prefix=folder,
            max_results=max_results,
            resource_type="image"
        )
        
        return result.get('resources', [])
        
    except Exception as e:
        print(f"خطأ في الحصول على قائمة الصور: {e}")
        return []

def create_temp_excel_file(data, filename):
    """
    إنشاء ملف Excel مؤقت
    
    Args:
        data: البيانات لكتابتها في Excel
        filename: اسم الملف
    
    Returns:
        str: مسار الملف المؤقت
    """
    try:
        # إنشاء ملف مؤقت
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        # كتابة البيانات إلى Excel
        if isinstance(data, dict):
            # إذا كانت البيانات dictionary مع عدة sheets
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # إذا كانت البيانات DataFrame واحد
            data.to_excel(temp_path, index=False)
        
        return temp_path
        
    except Exception as e:
        print(f"خطأ في إنشاء ملف Excel مؤقت: {e}")
        return None

def cleanup_temp_file(file_path):
    """
    حذف الملف المؤقت
    
    Args:
        file_path: مسار الملف المؤقت
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"خطأ في حذف الملف المؤقت: {e}")
    return False

def is_cloudinary_configured():
    """
    التحقق من إعداد Cloudinary
    
    Returns:
        bool: True إذا كان Cloudinary مُعد بشكل صحيح
    """
    required_vars = [
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY', 
        'CLOUDINARY_API_SECRET'
    ]
    
    return all(os.getenv(var) for var in required_vars)