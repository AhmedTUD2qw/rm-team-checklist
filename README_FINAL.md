# نظام بيانات الموظفين - Employee Data System
## مع دعم Cloudinary والنشر الاحترافي

نظام شامل لإدارة بيانات الموظفين ومواد POP مع تخزين سحابي آمن ونشر احترافي.

## 🚀 الميزات الرئيسية

### 👥 إدارة المستخدمين
- تسجيل دخول آمن للموظفين والمشرفين
- إدارة الأذونات والصلاحيات
- تتبع نشاط المستخدمين

### 📊 إدارة البيانات
- تسجيل بيانات المنتجات والمواد
- إدارة الفروع وأكواد المتاجر
- تصنيف المنتجات والموديلات

### 🖼️ رفع الصور (Cloudinary)
- رفع آمن إلى السحابة
- ضغط وتحسين تلقائي
- وصول سريع عبر CDN عالمي
- حماية من فقدان الصور

### 📈 التقارير والتصدير
- تصدير البيانات إلى Excel
- حفظ التقارير في السحابة
- فلترة وبحث متقدم
- إحصائيات مفصلة

### 📱 متوافق مع الجوال
- تصميم متجاوب
- يعمل على جميع الأجهزة
- واجهة سهلة الاستخدام

## 🛠️ التقنيات المستخدمة

### Backend
- **Python 3.11+**
- **Flask** - إطار العمل الرئيسي
- **PostgreSQL** - قاعدة البيانات (الإنتاج)
- **SQLite** - قاعدة البيانات (التطوير)
- **Gunicorn** - خادم الإنتاج

### Frontend
- **HTML5 & CSS3**
- **JavaScript (ES6+)**
- **Bootstrap** - التصميم المتجاوب
- **Font Awesome** - الأيقونات

### Cloud Services
- **Cloudinary** - تخزين الصور والملفات
- **Render** - منصة النشر
- **PostgreSQL** - قاعدة البيانات السحابية

## 📦 التثبيت والتشغيل

### المتطلبات
- Python 3.11+
- pip
- Git

### التثبيت المحلي
```bash
# استنساخ المشروع
git clone https://github.com/yourusername/employee-data-system.git
cd employee-data-system

# إنشاء بيئة افتراضية
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد متغيرات البيئة
cp .env.example .env
# حرر ملف .env وأضف بيانات Cloudinary

# تشغيل المشروع
python app.py
```

### الوصول للتطبيق
- افتح المتصفح على: `http://localhost:5000`
- تسجيل دخول المشرف: `Admin / ADMIN / admin123`

## ☁️ إعداد Cloudinary

### 1. إنشاء حساب
1. اذهب إلى [cloudinary.com](https://cloudinary.com)
2. أنشئ حساب مجاني
3. احصل على بيانات الاتصال من Dashboard

### 2. إعداد متغيرات البيئة
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. اختبار الإعداد
```bash
python test_cloudinary.py
```

## 🚀 النشر على Render

### الإعداد السريع
1. **رفع الكود إلى GitHub**
2. **إنشاء PostgreSQL database على Render**
3. **إنشاء Web Service وربطه بـ GitHub**
4. **إعداد متغيرات البيئة**
5. **النشر التلقائي**

### الأدلة المفصلة
- 📖 `RENDER_DEPLOYMENT_GUIDE.md` - دليل النشر خطوة بخطوة
- ☁️ `CLOUDINARY_SETUP_GUIDE.md` - دليل إعداد Cloudinary
- 🎯 `FINAL_DEPLOYMENT_SUMMARY.md` - الملخص النهائي

## 💰 التكاليف

### مجاني (للاختبار)
- Render: مجاني مع قيود
- PostgreSQL: 1GB مجاني
- Cloudinary: 25GB مجاني
- **المجموع: $0/شهر**

### احترافي (للإنتاج)
- Render Web Service: $7/شهر
- Render PostgreSQL: $7/شهر
- Cloudinary: مجاني (25GB كافية)
- **المجموع: $14/شهر**

## 🔐 الأمان

### الحماية المطبقة
- ✅ تشفير كلمات المرور
- ✅ جلسات آمنة
- ✅ SSL/TLS تلقائي
- ✅ حماية من SQL Injection
- ✅ تخزين آمن في السحابة
- ✅ نسخ احتياطية تلقائية

## 📊 المراقبة

### المتاح
- سجلات مفصلة في Render
- إحصائيات Cloudinary
- مراقبة الأداء
- تنبيهات الأخطاء

## 🧪 الاختبار

### اختبارات متوفرة
```bash
# اختبار النظام الأساسي
python test_system.py

# اختبار إدارة المستخدمين
python test_user_management.py

# اختبار أكواد المتاجر
python test_shop_code.py

# اختبار Cloudinary
python test_cloudinary.py

# فحص جاهزية النشر
python check_render_readiness.py
```

## 📞 الدعم

### للمساعدة
1. راجع الأدلة في المجلد
2. تحقق من سجلات الأخطاء
3. راجع وثائق Render و Cloudinary

### المساهمة
نرحب بالمساهمات! يرجى:
1. Fork المشروع
2. إنشاء branch جديد
3. إضافة التحسينات
4. إرسال Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف LICENSE للتفاصيل.

---

## 🎯 الخلاصة

مشروع متكامل وجاهز للإنتاج مع:
- ✅ تخزين آمن في السحابة
- ✅ نشر احترافي
- ✅ أداء عالي
- ✅ أمان متقدم
- ✅ سهولة الاستخدام

**🚀 ابدأ الآن واستمتع بنظام إدارة بيانات احترافي!**