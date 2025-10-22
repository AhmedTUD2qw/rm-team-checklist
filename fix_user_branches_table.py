#!/usr/bin/env python3
"""
Emergency fix to add missing user_branches table to production database
"""

import os
import sys
from database_config import get_database_connection

def add_user_branches_table():
    """Add the missing user_branches table"""
    print("🔧 Adding missing user_branches table...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Check if table already exists
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_branches'
                );
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user_branches';
            """)
        
        exists = cursor.fetchone()
        if exists and (exists[0] if db_type == 'postgresql' else exists):
            print("ℹ️ user_branches table already exists")
            conn.close()
            return True
        
        # Create user_branches table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE user_branches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    branch_name VARCHAR(200) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, branch_name)
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE user_branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    branch_name TEXT NOT NULL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, branch_name)
                )
            ''')
        
        conn.commit()
        conn.close()
        print("✅ user_branches table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user_branches table: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Emergency fix for user_branches table...")
    if add_user_branches_table():
        print("🎉 Fix completed successfully!")
    else:
        print("❌ Fix failed!")
        sys.exit(1)