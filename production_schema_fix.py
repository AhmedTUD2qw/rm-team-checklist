#!/usr/bin/env python3
"""
Production schema fix - ensure correct database structure and data
"""

import os
import sys

def main():
    """Fix production database schema and data"""
    print("🚀 Production schema fix...")
    
    # Check if we're in production environment
    if not os.getenv('DATABASE_URL'):
        print("❌ This script should only be run in production with DATABASE_URL set")
        return False
    
    try:
        from database_config import get_database_connection
        
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_type} database")
        
        # 1. Ensure user_branches table exists
        print("🔧 Checking user_branches table...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_branches'
            );
        """)
        
        exists = cursor.fetchone()[0]
        if not exists:
            print("📝 Creating user_branches table...")
            cursor.execute('''
                CREATE TABLE user_branches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    branch_name VARCHAR(200) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, branch_name)
                )
            ''')
            print("✅ user_branches table created")
        else:
            print("ℹ️ user_branches table already exists")
        
        # 2. Check and fix categories table schema
        print("🔧 Checking categories table schema...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'categories' ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Categories columns: {columns}")
        
        # If using old schema, we need to work with it
        if 'category_name' in columns and 'name' not in columns:
            print("⚠️ Using old categories schema (category_name)")
        elif 'name' in columns:
            print("✅ Using new categories schema (name)")
        
        # 3. Check models table schema
        print("🔧 Checking models table schema...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'models' ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Models columns: {columns}")
        
        # 4. Check pop_materials table
        print("🔧 Checking pop_materials table...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'pop_materials'
            );
        """)
        
        pop_exists = cursor.fetchone()[0]
        if not pop_exists:
            print("📝 Creating pop_materials table...")
            cursor.execute('''
                CREATE TABLE pop_materials (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    model_id INTEGER REFERENCES models(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ pop_materials table created")
        
        # 5. Check if we have pop_materials_db (old schema)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'pop_materials_db'
            );
        """)
        
        pop_db_exists = cursor.fetchone()[0]
        if pop_db_exists:
            print("ℹ️ Found old pop_materials_db table")
            
            # Migrate data from old to new if new table is empty
            cursor.execute("SELECT COUNT(*) FROM pop_materials")
            new_count = cursor.fetchone()[0]
            
            if new_count == 0:
                print("📝 Migrating POP materials data...")
                # This would require complex migration logic
                print("⚠️ Manual data migration needed")
        
        # 6. Add performance indexes
        print("🔧 Adding performance indexes...")
        
        indexes_to_create = [
            "CREATE INDEX IF NOT EXISTS idx_user_branches_user_id ON user_branches(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_branches_branch_name ON user_branches(branch_name)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_branch_name ON data_entries(branch_name)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_employee_name ON data_entries(employee_name)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_created_at ON data_entries(created_at)",
        ]
        
        for index_sql in indexes_to_create:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index")
            except Exception as e:
                print(f"⚠️ Index creation warning: {e}")
        
        # 7. Verify data counts
        print("📊 Verifying data...")
        
        tables_to_check = ['users', 'categories', 'models', 'display_types', 'data_entries']
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Production schema fix completed!")
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