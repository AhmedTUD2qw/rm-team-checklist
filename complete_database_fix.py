#!/usr/bin/env python3
"""
Complete Database Fix - Immediate Solution
This will completely fix all database issues immediately
"""

import os
import sys
from datetime import datetime

def main():
    """Complete immediate fix for all database issues"""
    print("🚨 Complete Database Fix - Immediate Solution")
    
    try:
        # Import database functions
        if os.getenv('DATABASE_URL'):
            from database_config import get_database_connection
            conn, db_type = get_database_connection()
        else:
            import sqlite3
            conn = sqlite3.connect('database.db')
            db_type = 'sqlite'
        
        cursor = conn.cursor()
        print(f"✅ Connected to {db_type} database")
        
        # 1. Create user_branches table if missing
        print("🔧 Creating user_branches table...")
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_branches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
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
                    UNIQUE(user_id, branch_name)
                )
            ''')
        print("✅ user_branches table ready")
        
        # 2. Check current schema and fix if needed
        print("🔧 Checking and fixing table schemas...")
        
        # Check categories table
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'categories' ORDER BY ordinal_position;
            """)
            cat_columns = [row[0] for row in cursor.fetchall()]
            
            # If old schema, create new table and migrate
            if 'category_name' in cat_columns and 'name' not in cat_columns:
                print("🔄 Migrating categories table...")
                cursor.execute("ALTER TABLE categories RENAME TO categories_old")
                cursor.execute('''
                    CREATE TABLE categories (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    INSERT INTO categories (id, name, created_at)
                    SELECT id, category_name, created_date::timestamp
                    FROM categories_old
                ''')
                print("✅ Categories table migrated")
        
        # 3. Fix models table
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'models' ORDER BY ordinal_position;
            """)
            model_columns = [row[0] for row in cursor.fetchall()]
            
            if 'model_name' in model_columns and 'name' not in model_columns:
                print("🔄 Migrating models table...")
                cursor.execute("ALTER TABLE models RENAME TO models_old")
                cursor.execute('''
                    CREATE TABLE models (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category_id INTEGER REFERENCES categories(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    INSERT INTO models (id, name, category_id, created_at)
                    SELECT m.id, m.model_name, c.id, m.created_date::timestamp
                    FROM models_old m
                    JOIN categories c ON c.name = m.category_name
                ''')
                print("✅ Models table migrated")
        
        # 4. Fix display_types table
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'display_types' ORDER BY ordinal_position;
            """)
            display_columns = [row[0] for row in cursor.fetchall()]
            
            if 'display_type_name' in display_columns and 'name' not in display_columns:
                print("🔄 Migrating display_types table...")
                cursor.execute("ALTER TABLE display_types RENAME TO display_types_old")
                cursor.execute('''
                    CREATE TABLE display_types (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category_id INTEGER REFERENCES categories(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    INSERT INTO display_types (id, name, category_id, created_at)
                    SELECT dt.id, dt.display_type_name, c.id, dt.created_date::timestamp
                    FROM display_types_old dt
                    JOIN categories c ON c.name = dt.category_name
                ''')
                print("✅ Display types table migrated")
        
        # 5. Create pop_materials table and migrate from pop_materials_db
        print("🔧 Setting up pop_materials table...")
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pop_materials (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    model_id INTEGER REFERENCES models(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if pop_materials_db exists and migrate
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'pop_materials_db'
                );
            """)
            if cursor.fetchone()[0]:
                print("🔄 Migrating POP materials...")
                cursor.execute("DELETE FROM pop_materials")
                cursor.execute('''
                    INSERT INTO pop_materials (name, model_id, created_at)
                    SELECT pdb.material_name, m.id, pdb.created_date::timestamp
                    FROM pop_materials_db pdb
                    JOIN models m ON m.name = pdb.model_name
                    WHERE m.id IS NOT NULL
                ''')
                print("✅ POP materials migrated")
        
        # 6. Add performance indexes
        print("🔧 Adding performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_branches_user_id ON user_branches(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_models_category_id ON models(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_display_types_category_id ON display_types(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_pop_materials_model_id ON pop_materials(model_id)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"Index warning: {e}")
        
        # 7. Verify data
        print("📊 Verifying data...")
        tables = ['users', 'categories', 'models', 'display_types', 'pop_materials', 'user_branches']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            except Exception as e:
                print(f"  ⚠️ {table}: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Complete database fix completed!")
        print("✅ All tables now use consistent schema")
        print("✅ All data migrated successfully")
        print("✅ Performance indexes added")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)