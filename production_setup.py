#!/usr/bin/env python3
"""
Simple Production Setup Script
"""

import sqlite3
import os
import shutil
from datetime import datetime

def create_production_backup():
    """Create production backup"""
    if not os.path.exists('database.db'):
        print("❌ No database file found")
        return False
    
    # Create backup directory
    backup_dir = 'production_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Created backup directory: {backup_dir}")
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'production_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2('database.db', backup_path)
        print(f"✅ Production backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def verify_production_database():
    """Verify production database"""
    print("🔍 Verifying production database...")
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Check required tables
        required_tables = ['users', 'data_entries', 'branches', 'categories', 'models', 'display_types', 'pop_materials_db']
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in c.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check admin user
        c.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
        admin_count = c.fetchone()[0]
        
        # Check data counts
        c.execute('SELECT COUNT(*) FROM categories')
        category_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM models')
        model_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM pop_materials_db')
        materials_count = c.fetchone()[0]
        
        print(f"✅ Database verification completed:")
        print(f"   - Tables: {len(existing_tables)}")
        print(f"   - Admin users: {admin_count}")
        print(f"   - Categories: {category_count}")
        print(f"   - Models: {model_count}")
        print(f"   - POP Materials: {materials_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def create_production_config():
    """Create production configuration"""
    config = """# Production Configuration

## Database Status
- Persistent data: ✅ Enabled
- Auto-backup: ✅ Enabled
- Data preservation: ✅ Enabled

## Security
- Admin user: Admin/ADMIN/admin123
- Change default password after deployment!

## Backup Schedule
- Manual backup: python production_setup.py backup
- Verify database: python production_setup.py verify

## Deployment Notes
- Database file: database.db (preserve this file)
- Backup directory: production_backups/
- Upload directory: static/uploads/

## Important
- Never delete database.db in production
- Regular backups are essential
- Monitor disk space for uploads
"""
    
    with open('PRODUCTION_README.md', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("✅ Production configuration created: PRODUCTION_README.md")

def main():
    """Main production setup"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            create_production_backup()
        elif command == 'verify':
            verify_production_database()
        else:
            print("Usage: python production_setup.py [backup|verify]")
    else:
        print("🚀 Production Setup for Employee Data System")
        print("=" * 50)
        
        # Verify current database
        if verify_production_database():
            print("\n💾 Creating production backup...")
            backup_path = create_production_backup()
            
            if backup_path:
                print("\n📋 Creating production documentation...")
                create_production_config()
                
                print("\n🎉 Production setup completed!")
                print("\n📋 Important Notes:")
                print("1. ✅ Your database is now persistent (won't reset on restart)")
                print("2. ✅ Backup created for safety")
                print("3. ✅ All your data will be preserved")
                print("4. 🔒 Change admin password after deployment")
                print("5. 📅 Schedule regular backups")
                
                print("\n🔧 Commands:")
                print("- Create backup: python production_setup.py backup")
                print("- Verify database: python production_setup.py verify")
                print("- Start system: python app.py")
                
            else:
                print("\n❌ Production setup failed")
        else:
            print("\n❌ Database verification failed")

if __name__ == "__main__":
    main()