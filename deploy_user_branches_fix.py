#!/usr/bin/env python3
"""
Production deployment fix for user_branches table
This script should be run on Render to fix the missing table
"""

import os
import sys

def main():
    """Main deployment fix function"""
    print("🚀 Production fix for user_branches table...")
    
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
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_branches'
            );
        """)
        
        exists = cursor.fetchone()[0]
        if exists:
            print("ℹ️ user_branches table already exists")
            conn.close()
            return True
        
        print("🔧 Creating user_branches table...")
        
        # Create user_branches table for PostgreSQL
        cursor.execute('''
            CREATE TABLE user_branches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                branch_name VARCHAR(200) NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, branch_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ user_branches table created successfully!")
        print("🎉 Production fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)