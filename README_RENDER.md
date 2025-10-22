# نظام بيانات الموظفين - Employee Data System

نظام شامل لإدارة بيانات الموظفين ومواد POP مع دعم النشر على Render.

## 🚀 النشر السريع على Render

### المتطلبات
- حساب [Render](https://render.com) مجاني
- حساب GitHub

### خطوات النشر

1. **رفع الكود إلى GitHub**
```bash
git init
git add .
git commit -m "Deploy to Render"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **إنشاء قاعدة البيانات**
   - اذهب إلى Render Dashboard
   - اضغط "New +" → "PostgreSQL"
   - Name: `employee-data-db`
   - اختر الخطة المناسبة

3. **إنشاء Web Service**
   - اضغط "New +" → "Web Service"
   - اربط GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python render_setup.py && gunicorn --bind 0.0.0.0:$PORT app:app`

4. **إعداد متغيرات البيئة**
   - `DATABASE_URL`: من قاعدة البيانات
   - `SECRET_KEY`: Generate جديد
   - `FLASK_ENV`: `production`

## 🔧 التطوير المحلي

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ ملف البيئة
cp .env.example .env

# تشغيل المشروع
python app.py
```

## 📊 الميزات

### للموظفين
- تسجيل بيانات المنتجات
- رفع الصور
- إدارة الفروع
- تتبع مواد POP

### للمشرفين
- لوحة تحكم شاملة
- إدارة المستخدمين
- تصدير البيانات إلى Excel
- إدارة الفئات والموديلات

## 🔐 تسجيل الدخول الافتراضي

**المشرف:**
- الاسم: Admin
- كود الشركة: ADMIN
- كلمة المرور: admin123

## 🛡️ الأمان

- تشفير كلمات المرور
- جلسات آمنة
- حماية من SQL Injection
- SSL/TLS على Render

## 📱 متوافق مع الجوال

النظام مصمم ليعمل بسلاسة على:
- الهواتف الذكية
- الأجهزة اللوحية
- أجهزة الكمبيوتر

## 🔄 النسخ الاحتياطية

- نسخ احتياطية تلقائية على Render
- حماية من فقدان البيانات
- استعادة سهلة

## 📞 الدعم الفني

للمساعدة أو الاستفسارات، راجع:
- `RENDER_DEPLOYMENT_GUIDE.md` - دليل النشر المفصل
- `USER_GUIDE.md` - دليل المستخدم
- سجلات Render للأخطاء

---

🎉 **مشروعك جاهز للنشر على Render!**