#!/usr/bin/env python3
"""
Render deployment setup script
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
from datetime import datetime
from werkzeug.security import generate_password_hash

def setup_postgres_database():
    """Setup PostgreSQL database for production"""
    print("🔧 Setting up PostgreSQL database for Render...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return False
    
    try:
        # Parse database URL
        url = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Create tables
        create_tables(cursor)
        
        # Initialize default data
        initialize_default_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("✅ PostgreSQL database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_tables(cursor):
    """Create all required tables"""
    print("📋 Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            company_code TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Data entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_entries (
            id SERIAL PRIMARY KEY,
            employee_name TEXT NOT NULL,
            employee_code TEXT NOT NULL,
            branch TEXT NOT NULL,
            shop_code TEXT,
            model TEXT NOT NULL,
            display_type TEXT NOT NULL,
            selected_materials TEXT,
            unselected_materials TEXT,
            images TEXT,
            date TIMESTAMP NOT NULL
        )
    ''')
    
    # Branches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id SERIAL PRIMARY KEY,
            branch_name TEXT NOT NULL,
            shop_code TEXT NOT NULL,
            employee_code TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            UNIQUE(branch_name, employee_code),
            UNIQUE(shop_code, employee_code)
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            category_name TEXT NOT NULL UNIQUE,
            created_date TIMESTAMP NOT NULL
        )
    ''')
    
    # Models table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            model_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            UNIQUE(model_name, category_name)
        )
    ''')
    
    # Display types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS display_types (
            id SERIAL PRIMARY KEY,
            display_type_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            UNIQUE(display_type_name, category_name)
        )
    ''')
    
    # POP materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pop_materials_db (
            id SERIAL PRIMARY KEY,
            material_name TEXT NOT NULL,
            model_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            UNIQUE(material_name, model_name)
        )
    ''')
    
    # User branches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_branches (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, branch_name)
        )
    ''')
    
    # Database status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS db_init_status (
            id SERIAL PRIMARY KEY,
            component TEXT NOT NULL UNIQUE,
            initialized BOOLEAN DEFAULT FALSE,
            last_update TIMESTAMP NOT NULL
        )
    ''')
    
    print("✅ Tables created successfully")

def initialize_default_data(cursor):
    """Initialize default system data"""
    print("📊 Initializing default data...")
    
    current_time = datetime.now()
    
    # Create admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, company_code, password, is_admin, created_date) 
            VALUES (%s, %s, %s, %s, %s)
        ''', ('Admin', 'ADMIN', admin_password, True, current_time))
        print("✅ Admin user created")
    
    # Initialize categories
    categories = ['OLED', 'Neo QLED', 'QLED', 'UHD', 'LTV', 'BESPOKE COMBO', 
                 'BESPOKE Front', 'Front', 'TL', 'SBS', 'TMF', 'BMF', 'Local TMF']
    
    for category in categories:
        cursor.execute('''
            INSERT INTO categories (category_name, created_date) 
            VALUES (%s, %s) ON CONFLICT (category_name) DO NOTHING
        ''', (category, current_time))
    
    print("✅ Default categories initialized")
    
    # Mark initialization as complete
    cursor.execute('''
        INSERT INTO db_init_status (component, initialized, last_update) 
        VALUES (%s, %s, %s) ON CONFLICT (component) DO UPDATE SET 
        initialized = EXCLUDED.initialized, last_update = EXCLUDED.last_update
    ''', ('render_setup', True, current_time))

if __name__ == "__main__":
    print("🚀 Starting Render deployment setup...")
    
    if setup_postgres_database():
        print("🎉 Render setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Render setup failed!")
        sys.exit(1)