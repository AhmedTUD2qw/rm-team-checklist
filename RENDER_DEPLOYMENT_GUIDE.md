# دليل نشر المشروع على Render

## المتطلبات المسبقة
- حساب على [Render](https://render.com)
- حساب GitHub لرفع الكود

## خطوات النشر

### 1. رفع الكود إلى GitHub
```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/employee-data-system.git
git push -u origin main
```

### 2. إنشاء قاعدة البيانات على Render

1. اذهب إلى [Render Dashboard](https://dashboard.render.com)
2. اضغط على "New +" واختر "PostgreSQL"
3. املأ البيانات التالية:
   - **Name**: `employee-data-db`
   - **Database**: `employee_data_system`
   - **User**: `admin`
   - **Region**: اختر الأقرب لك
   - **PostgreSQL Version**: 15
   - **Plan**: Free (للاختبار) أو Starter ($7/شهر للإنتاج)

4. اضغط "Create Database"
5. انتظر حتى تصبح قاعدة البيانات جاهزة (Status: Available)

### 3. إنشاء Web Service

1. في Render Dashboard، اضغط "New +" واختر "Web Service"
2. اربط حساب GitHub واختر المستودع
3. املأ البيانات التالية:
   - **Name**: `employee-data-system`
   - **Region**: نفس منطقة قاعدة البيانات
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_setup.py && gunicorn --bind 0.0.0.0:$PORT app:app`

### 4. إعداد Cloudinary (مطلوب)

قبل النشر، يجب إعداد Cloudinary لحفظ الصور وملفات Excel:

1. أنشئ حساب مجاني على [Cloudinary](https://cloudinary.com)
2. احصل على بيانات الاتصال من [Console](https://cloudinary.com/console):
   - Cloud Name
   - API Key  
   - API Secret

### 5. إعداد متغيرات البيئة

في صفحة Web Service، اذهب إلى "Environment":

1. **DATABASE_URL**: 
   - اضغط "Add from Database"
   - اختر `employee-data-db`
   - اختر "Internal Database URL"

2. **SECRET_KEY**:
   - اضغط "Generate"
   - سيتم إنشاء مفتاح عشوائي آمن

3. **FLASK_ENV**: `production`

4. **متغيرات Cloudinary**:
   - **CLOUDINARY_CLOUD_NAME**: اسم السحابة من Cloudinary
   - **CLOUDINARY_API_KEY**: مفتاح API من Cloudinary
   - **CLOUDINARY_API_SECRET**: المفتاح السري من Cloudinary

### 6. النشر

1. اضغط "Create Web Service"
2. انتظر حتى يكتمل البناء والنشر
3. ستحصل على رابط مثل: `https://employee-data-system.onrender.com`

⚠️ **مهم**: تأكد من إعداد Cloudinary قبل استخدام رفع الصور!

## معلومات تسجيل الدخول الافتراضية

بعد النشر الناجح، يمكنك تسجيل الدخول باستخدام:
- **اسم المستخدم**: Admin
- **كود الشركة**: ADMIN
- **كلمة المرور**: admin123

⚠️ **مهم**: غيّر كلمة مرور المشرف فور تسجيل الدخول الأول!

## الميزات المتوفرة

### ✅ التخزين الآمن
- قاعدة بيانات PostgreSQL منفصلة
- نسخ احتياطية تلقائية
- حماية من فقدان البيانات

### ✅ الأداء
- خادم Gunicorn للإنتاج
- تحسينات الأداء
- SSL مجاني

### ✅ المراقبة
- سجلات مفصلة
- مراقبة الأداء
- تنبيهات الأخطاء

## استكشاف الأخطاء

### مشكلة في قاعدة البيانات
```bash
# تحقق من سجلات النشر
# في Render Dashboard > Web Service > Logs
```

### مشكلة في الاتصال
```bash
# تأكد من أن DATABASE_URL صحيح
# تحقق من حالة قاعدة البيانات (Available)
```

### إعادة النشر
```bash
git add .
git commit -m "Update deployment"
git push origin main
# سيتم إعادة النشر تلقائياً
```

## التكاليف المتوقعة

### الخطة المجانية
- Web Service: مجاني (مع قيود)
- PostgreSQL: مجاني (1GB، محدود)
- مناسب للاختبار فقط

### الخطة المدفوعة (موصى بها للإنتاج)
- Web Service: $7/شهر
- PostgreSQL: $7/شهر
- المجموع: $14/شهر

## النسخ الاحتياطية

Render يقوم بعمل نسخ احتياطية تلقائية لقاعدة البيانات:
- نسخة يومية لآخر 7 أيام
- نسخة أسبوعية لآخر 4 أسابيع
- يمكن استعادة البيانات من أي نسخة احتياطية

## الأمان

### SSL/TLS
- شهادة SSL مجانية تلقائياً
- تشفير جميع البيانات المنقولة

### قاعدة البيانات
- اتصال مشفر بقاعدة البيانات
- عزل الشبكة
- مصادقة قوية

## الدعم الفني

في حالة وجود مشاكل:
1. تحقق من سجلات Render
2. راجع وثائق Render
3. تواصل مع دعم Render

---

🎉 **مبروك! مشروعك الآن منشور على Render مع حماية كاملة للبيانات**