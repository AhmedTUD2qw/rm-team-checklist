#!/usr/bin/env python3
"""
Comprehensive database fix for Render deployment
This script fixes all database-related issues in production
"""

import os
import sys

def main():
    """Main fix function"""
    print("🚀 Comprehensive Render database fix...")
    
    # Check if we're in production environment
    if not os.getenv('DATABASE_URL'):
        print("❌ This script should only be run in production with DATABASE_URL set")
        return False
    
    try:
        # Import here to avoid issues if modules aren't available
        from database_config import get_database_connection
        
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_type} database")
        
        # 1. Check and create user_branches table if missing
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
        
        # 2. Check and create missing indexes for performance
        print("🔧 Creating performance indexes...")
        
        # Index on user_branches for faster lookups
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_branches_user_id 
                ON user_branches(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_branches_branch_name 
                ON user_branches(branch_name)
            ''')
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
        
        # Index on data_entries for faster filtering
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_data_entries_branch_name 
                ON data_entries(branch_name)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_data_entries_employee_name 
                ON data_entries(employee_name)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_data_entries_created_at 
                ON data_entries(created_at)
            ''')
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
        
        # 3. Verify all required tables exist
        print("🔧 Verifying all required tables...")
        required_tables = [
            'users', 'user_branches', 'categories', 'models', 
            'display_types', 'pop_materials', 'data_entries'
        ]
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            if exists:
                print(f"✅ {table} table exists")
            else:
                print(f"❌ {table} table missing!")
        
        # 4. Check for data consistency
        print("🔧 Checking data consistency...")
        
        # Check if we have categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"📊 Categories: {cat_count}")
        
        # Check if we have models
        cursor.execute("SELECT COUNT(*) FROM models")
        model_count = cursor.fetchone()[0]
        print(f"📊 Models: {model_count}")
        
        # Check if we have users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Users: {user_count}")
        
        conn.commit()
        conn.close()
        
        print("✅ All database fixes completed successfully!")
        print("🎉 Production database is now ready!")
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