#!/usr/bin/env python3
"""
Database initialization script for production deployment
"""

import os
import sys
from database_config import get_database_connection, execute_query, convert_sqlite_to_postgres_query

def create_tables():
    """Create all required tables"""
    print("🔧 Creating database tables...")
    
    conn, db_type = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    employee_name VARCHAR(100) NOT NULL,
                    employee_code VARCHAR(50) UNIQUE NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    employee_code TEXT UNIQUE NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Branches table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS branches (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Categories table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Models table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category_id INTEGER REFERENCES categories(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

        # Display types table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS display_types (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category_id INTEGER REFERENCES categories(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS display_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

        # POP materials table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pop_materials (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    model_id INTEGER REFERENCES models(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pop_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    model_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            ''')

        # User branches table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_branches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    branch_name VARCHAR(200) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, branch_name)
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    branch_name TEXT NOT NULL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, branch_name)
                )
            ''')

        # Data entries table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_entries (
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
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_entries (
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
                )
            ''')

        conn.commit()
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_admin_user():
    """Create default admin user"""
    print("👤 Creating admin user...")
    
    from werkzeug.security import generate_password_hash
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute("SELECT id FROM users WHERE username = %s" if db_type == 'postgresql' else "SELECT id FROM users WHERE username = ?", ('admin',))
        if cursor.fetchone():
            print("ℹ️ Admin user already exists")
            conn.close()
            return True
        
        # Create admin user
        password_hash = generate_password_hash('admin123')
        
        if db_type == 'postgresql':
            cursor.execute('''
                INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin', password_hash, 'System Administrator', 'ADMIN001', True))
        else:
            cursor.execute('''
                INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', password_hash, 'System Administrator', 'ADMIN001', True))
        
        conn.commit()
        conn.close()
        print("✅ Admin user created successfully!")
        print("📝 Login credentials: admin / admin123")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def populate_default_data():
    """Populate default categories, models, and materials"""
    print("📊 Populating default data...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Categories
        categories = [
            'OLED', 'Neo QLED', 'QLED', 'UHD', 'LTV',
            'BESPOKE COMBO', 'BESPOKE Front', 'Front', 'TL', 'SBS', 'TMF', 'BMF', 'Local TMF'
        ]
        
        for category in categories:
            try:
                if db_type == 'postgresql':
                    cursor.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (category,))
                else:
                    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            except:
                pass
        
        # Models for each category
        models_data = {
            'OLED': ['S95F', 'S90F', 'S85F'],
            'Neo QLED': ['QN90', 'QN85F', 'QN80F', 'QN70F'],
            'QLED': ['Q8F', 'Q7F'],
            'UHD': ['U8000', '100"/98"'],
            'LTV': ['The Frame'],
            'BESPOKE COMBO': ['WD25DB8995', 'WD21D6400'],
            'BESPOKE Front': ['WW11B1944DGB'],
            'Front': ['WW11B1534D', 'WW90CGC', 'WW4040', 'WW4020'],
            'TL': ['WA19CG6886', 'Local TL'],
            'SBS': ['RS70F'],
            'TMF': ['Bespoke', 'TMF Non-Bespoke', 'TMF'],
            'BMF': ['(Bespoke, BMF)', '(Non-Bespoke, BMF)'],
            'Local TMF': ['Local TMF']
        }
        
        for category_name, model_list in models_data.items():
            # Get category ID
            cursor.execute("SELECT id FROM categories WHERE name = %s" if db_type == 'postgresql' else "SELECT id FROM categories WHERE name = ?", (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                
                for model_name in model_list:
                    try:
                        if db_type == 'postgresql':
                            cursor.execute("INSERT INTO models (name, category_id) VALUES (%s, %s)", (model_name, category_id))
                        else:
                            cursor.execute("INSERT INTO models (name, category_id) VALUES (?, ?)", (model_name, category_id))
                    except:
                        pass
        
        # Display types
        display_types_data = {
            'OLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'Neo QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'UHD': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'LTV': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
            'BESPOKE COMBO': ['POP Out', 'POP Inner', 'POP'],
            'BESPOKE Front': ['POP Out', 'POP Inner', 'POP'],
            'Front': ['POP Out', 'POP Inner', 'POP'],
            'TL': ['POP Out', 'POP Inner', 'POP'],
            'SBS': ['POP Out', 'POP Inner', 'POP'],
            'TMF': ['POP Out', 'POP Inner', 'POP'],
            'BMF': ['POP Out', 'POP Inner', 'POP'],
            'Local TMF': ['POP Out', 'POP Inner', 'POP']
        }
        
        for category_name, display_list in display_types_data.items():
            cursor.execute("SELECT id FROM categories WHERE name = %s" if db_type == 'postgresql' else "SELECT id FROM categories WHERE name = ?", (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                
                for display_name in display_list:
                    try:
                        if db_type == 'postgresql':
                            cursor.execute("INSERT INTO display_types (name, category_id) VALUES (%s, %s)", (display_name, category_id))
                        else:
                            cursor.execute("INSERT INTO display_types (name, category_id) VALUES (?, ?)", (display_name, category_id))
                    except:
                        pass
        
        conn.commit()
        conn.close()
        print("✅ Default data populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating default data: {e}")
        return False

def initialize_database():
    """Initialize complete database"""
    print("🚀 Initializing database for production...")
    
    try:
        # Test database connection
        conn, db_type = get_database_connection()
        print(f"✅ Database connection successful! Type: {db_type}")
        conn.close()
        
        # Create tables
        if not create_tables():
            return False
        
        # Create admin user
        if not create_admin_user():
            return False
        
        # Populate default data
        if not populate_default_data():
            return False
        
        print("🎉 Database initialization completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ All tables created")
        print("   ✅ Admin user created (admin/admin123)")
        print("   ✅ Default data populated")
        print("   ✅ Ready for production!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    initialize_database()