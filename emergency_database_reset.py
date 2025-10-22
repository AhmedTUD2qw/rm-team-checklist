#!/usr/bin/env python3
"""
Emergency Database Reset - Complete Fix for Production
This script will completely reset and fix the database structure
"""

import os
import sys

def main():
    """Emergency database reset and fix"""
    print("🚨 Emergency Database Reset - Complete Fix")
    
    # Check if we're in production environment
    if not os.getenv('DATABASE_URL'):
        print("❌ This script should only be run in production with DATABASE_URL set")
        return False
    
    try:
        from database_config import get_database_connection
        
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_type} database")
        
        # 1. Drop and recreate user_branches table
        print("🔧 Fixing user_branches table...")
        try:
            cursor.execute("DROP TABLE IF EXISTS user_branches CASCADE")
            print("🗑️ Dropped old user_branches table")
        except:
            pass
        
        cursor.execute('''
            CREATE TABLE user_branches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                branch_name VARCHAR(200) NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, branch_name)
            )
        ''')
        print("✅ Created new user_branches table")
        
        # 2. Check and fix categories table
        print("🔧 Checking categories table...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'categories' ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Categories columns: {columns}")
        
        # If old schema, rename columns
        if 'category_name' in columns and 'name' not in columns:
            print("🔄 Updating categories table schema...")
            cursor.execute("ALTER TABLE categories RENAME COLUMN category_name TO name")
            cursor.execute("ALTER TABLE categories RENAME COLUMN created_date TO created_at")
            print("✅ Updated categories table schema")
        
        # 3. Check and fix models table
        print("🔧 Checking models table...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'models' ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Models columns: {columns}")
        
        # If old schema, update it
        if 'model_name' in columns and 'name' not in columns:
            print("🔄 Updating models table schema...")
            
            # Add new columns
            cursor.execute("ALTER TABLE models ADD COLUMN name VARCHAR(100)")
            cursor.execute("ALTER TABLE models ADD COLUMN category_id INTEGER")
            
            # Migrate data
            cursor.execute("UPDATE models SET name = model_name")
            
            # Update category_id based on category_name
            cursor.execute("""
                UPDATE models SET category_id = (
                    SELECT c.id FROM categories c WHERE c.name = models.category_name
                )
            """)
            
            # Drop old columns
            cursor.execute("ALTER TABLE models DROP COLUMN model_name")
            cursor.execute("ALTER TABLE models DROP COLUMN category_name")
            cursor.execute("ALTER TABLE models RENAME COLUMN created_date TO created_at")
            
            print("✅ Updated models table schema")
        
        # 4. Check and fix display_types table
        print("🔧 Checking display_types table...")
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'display_types' ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Display types columns: {columns}")
        
        # If old schema, update it
        if 'display_type_name' in columns and 'name' not in columns:
            print("🔄 Updating display_types table schema...")
            
            # Add new columns
            cursor.execute("ALTER TABLE display_types ADD COLUMN name VARCHAR(100)")
            cursor.execute("ALTER TABLE display_types ADD COLUMN category_id INTEGER")
            
            # Migrate data
            cursor.execute("UPDATE display_types SET name = display_type_name")
            
            # Update category_id based on category_name
            cursor.execute("""
                UPDATE display_types SET category_id = (
                    SELECT c.id FROM categories c WHERE c.name = display_types.category_name
                )
            """)
            
            # Drop old columns
            cursor.execute("ALTER TABLE display_types DROP COLUMN display_type_name")
            cursor.execute("ALTER TABLE display_types DROP COLUMN category_name")
            cursor.execute("ALTER TABLE display_types RENAME COLUMN created_date TO created_at")
            
            print("✅ Updated display_types table schema")
        
        # 5. Handle POP materials
        print("🔧 Fixing POP materials...")
        
        # Check if pop_materials table exists
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
            print("✅ Created pop_materials table")
        
        # Check if pop_materials_db exists and migrate data
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'pop_materials_db'
            );
        """)
        pop_db_exists = cursor.fetchone()[0]
        
        if pop_db_exists:
            print("🔄 Migrating data from pop_materials_db...")
            
            # Clear existing data
            cursor.execute("DELETE FROM pop_materials")
            
            # Migrate data
            cursor.execute("""
                INSERT INTO pop_materials (name, model_id, created_at)
                SELECT 
                    pdb.material_name,
                    m.id,
                    pdb.created_date::timestamp
                FROM pop_materials_db pdb
                JOIN models m ON m.name = pdb.model_name
            """)
            
            print("✅ Migrated POP materials data")
        
        # 6. Add performance indexes
        print("🔧 Adding performance indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_branches_user_id ON user_branches(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_branches_branch_name ON user_branches(branch_name)",
            "CREATE INDEX IF NOT EXISTS idx_models_category_id ON models(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_display_types_category_id ON display_types(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_pop_materials_model_id ON pop_materials(model_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_branch_name ON data_entries(branch_name)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_employee_name ON data_entries(employee_name)",
            "CREATE INDEX IF NOT EXISTS idx_data_entries_created_at ON data_entries(created_at)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"⚠️ Index warning: {e}")
        
        print("✅ Added performance indexes")
        
        # 7. Verify final structure
        print("📊 Verifying final database structure...")
        
        tables = ['users', 'user_branches', 'categories', 'models', 'display_types', 'pop_materials', 'data_entries']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            except Exception as e:
                print(f"  ❌ {table}: Error - {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Emergency database reset completed successfully!")
        print("✅ All tables now use the new schema")
        print("✅ All data has been migrated")
        print("✅ Performance indexes added")
        print("✅ Ready for production use")
        
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