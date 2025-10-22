#!/usr/bin/env python3
"""
إصلاح أخطاء Render
"""

import os
from database_config import get_database_connection
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_render_database():
    """إصلاح قاعدة البيانات على Render"""
    print("🔧 إصلاح قاعدة البيانات على Render...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"📊 نوع قاعدة البيانات: {db_type}")
        
        # إنشاء الجداول إذا لم تكن موجودة
        if db_type == 'postgresql':
            # Users table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                employee_name VARCHAR(100) NOT NULL,
                employee_code VARCHAR(50) UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Categories table
            cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Models table
            cursor.execute('''CREATE TABLE IF NOT EXISTS models (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Display types table
            cursor.execute('''CREATE TABLE IF NOT EXISTS display_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # POP materials table
            cursor.execute('''CREATE TABLE IF NOT EXISTS pop_materials (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                model_id INTEGER REFERENCES models(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Data entries table
            cursor.execute('''CREATE TABLE IF NOT EXISTS data_entries (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                employee_name VARCHAR(100) NOT NULL,
                employee_code VARCHAR(50) NOT NULL,
                branch_name VARCHAR(200) NOT NULL,
                shop_code VARCHAR(50),
                category VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                display_type VARCHAR(100) NOT NULL,
                selected_materials TEXT,
                missing_materials TEXT,
                image_urls TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Branches table
            cursor.execute('''CREATE TABLE IF NOT EXISTS branches (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # User branches table
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_branches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                branch_name VARCHAR(200) NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, branch_name)
            )''')
        
        conn.commit()
        print("✅ تم إنشاء الجداول")
        
        # التحقق من وجود المستخدم الإداري
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = true')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("👤 إنشاء المستخدم الإداري...")
            admin_password = generate_password_hash('admin123')
            
            if db_type == 'postgresql':
                cursor.execute('''INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) 
                                 VALUES (%s, %s, %s, %s, %s)''',
                             ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
            else:
                cursor.execute('''INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) 
                                 VALUES (?, ?, ?, ?, ?)''',
                             ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
            
            conn.commit()
            print("✅ تم إنشاء المستخدم الإداري")
        
        # إضافة الفئات الافتراضية
        categories = [
            'OLED', 'Neo QLED', 'QLED', 'UHD', 'LTV',
            'BESPOKE COMBO', 'BESPOKE Front', 'Front', 'TL', 'SBS', 'TMF', 'BMF', 'Local TMF'
        ]
        
        current_time = datetime.now()
        
        for category in categories:
            try:
                if db_type == 'postgresql':
                    cursor.execute('INSERT INTO categories (name, created_at) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING',
                                 (category, current_time))
                else:
                    cursor.execute('INSERT OR IGNORE INTO categories (name, created_at) VALUES (?, ?)',
                                 (category, current_time.strftime('%Y-%m-%d %H:%M:%S')))
            except Exception as e:
                print(f"⚠️ خطأ في إضافة الفئة {category}: {e}")
        
        conn.commit()
        print("✅ تم إضافة الفئات الافتراضية")
        
        # إحصائيات
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        print(f"\n📊 إحصائيات قاعدة البيانات:")
        print(f"   👥 المستخدمين: {users_count}")
        print(f"   📊 الفئات: {categories_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_render_database()