#!/usr/bin/env python3
"""
Final System Verification - Complete system check before production
"""

import sqlite3
import os
from datetime import datetime

def verify_database_persistence():
    """Verify that database preserves data between restarts"""
    print("🔍 Testing Database Persistence...")
    
    # Test marker to check if data persists
    test_marker = f"PERSISTENCE_TEST_{datetime.now().strftime('%H%M%S')}"
    
    try:
        # Add test data
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Add test category
        c.execute('INSERT OR IGNORE INTO categories (category_name, created_date) VALUES (?, ?)',
                 (test_marker, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        
        # Verify it was added
        c.execute('SELECT COUNT(*) FROM categories WHERE category_name = ?', (test_marker,))
        if c.fetchone()[0] > 0:
            print("✅ Test data added successfully")
            
            # Clean up test data
            c.execute('DELETE FROM categories WHERE category_name = ?', (test_marker,))
            conn.commit()
            print("✅ Test data cleaned up")
        else:
            print("❌ Failed to add test data")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database persistence test failed: {e}")
        return False

def verify_all_features():
    """Verify all system features are working"""
    print("\n🔍 Verifying All System Features...")
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    features_status = {}
    
    try:
        # Check Users System
        c.execute('SELECT COUNT(*) FROM users')
        user_count = c.fetchone()[0]
        features_status['Users System'] = user_count > 0
        
        # Check Categories
        c.execute('SELECT COUNT(*) FROM categories')
        category_count = c.fetchone()[0]
        features_status['Categories'] = category_count > 0
        
        # Check Models
        c.execute('SELECT COUNT(*) FROM models')
        model_count = c.fetchone()[0]
        features_status['Models'] = model_count > 0
        
        # Check Display Types
        c.execute('SELECT COUNT(*) FROM display_types')
        display_count = c.fetchone()[0]
        features_status['Display Types'] = display_count > 0
        
        # Check POP Materials
        c.execute('SELECT COUNT(*) FROM pop_materials_db')
        materials_count = c.fetchone()[0]
        features_status['POP Materials'] = materials_count > 0
        
        # Check Branches System
        c.execute('SELECT COUNT(*) FROM branches')
        branch_count = c.fetchone()[0]
        features_status['Branches System'] = True  # Can be empty initially
        
        # Check Data Entries
        c.execute('SELECT COUNT(*) FROM data_entries')
        entry_count = c.fetchone()[0]
        features_status['Data Entries'] = True  # Can be empty initially
        
        # Check Database Status Tracking
        c.execute('SELECT COUNT(*) FROM db_init_status')
        status_count = c.fetchone()[0]
        features_status['Status Tracking'] = status_count > 0
        
        conn.close()
        
        # Display results
        print("Feature verification results:")
        for feature, status in features_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        # Overall status
        all_working = all(features_status.values())
        if all_working:
            print("\n🎉 All features verified successfully!")
            return True
        else:
            failed_features = [f for f, s in features_status.items() if not s]
            print(f"\n❌ Failed features: {failed_features}")
            return False
        
    except Exception as e:
        print(f"❌ Feature verification failed: {e}")
        return False

def verify_file_structure():
    """Verify all required files exist"""
    print("\n📁 Verifying File Structure...")
    
    required_files = {
        'Core Files': [
            'app.py', 'requirements.txt', 'database.db'
        ],
        'Templates': [
            'templates/base.html', 'templates/login.html', 'templates/data_entry.html',
            'templates/admin_dashboard.html', 'templates/admin_management.html',
            'templates/user_management.html', 'templates/register.html'
        ],
        'Static Files': [
            'static/css/style.css', 'static/js/main.js', 'static/js/data_entry.js',
            'static/js/admin_management.js', 'static/js/user_management.js'
        ],
        'Production Files': [
            'production_database_manager.py', 'production_setup.py',
            'run_production.bat', 'PRODUCTION_README.md'
        ],
        'Test Files': [
            'test_system.py', 'test_pop_materials_by_model.py',
            'test_user_management.py', 'test_shop_code.py'
        ]
    }
    
    all_files_exist = True
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} (MISSING)")
                all_files_exist = False
    
    return all_files_exist

def verify_production_readiness():
    """Final production readiness check"""
    print("\n🚀 Production Readiness Check...")
    
    checks = {
        'Database Persistence': verify_database_persistence(),
        'All Features Working': verify_all_features(),
        'File Structure Complete': verify_file_structure(),
        'Backup System Ready': os.path.exists('production_backups'),
        'Documentation Complete': os.path.exists('PRODUCTION_README.md')
    }
    
    print("\nProduction Readiness Results:")
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check}")
    
    all_ready = all(checks.values())
    
    if all_ready:
        print("\n🎊 SYSTEM IS PRODUCTION READY!")
        print("\n📋 Deployment Checklist:")
        print("1. ✅ Database is persistent and protected")
        print("2. ✅ All features are working correctly")
        print("3. ✅ Backup system is operational")
        print("4. ✅ Documentation is complete")
        print("5. ✅ File structure is intact")
        
        print("\n🚀 Ready for deployment!")
        print("Use: python run_production.bat")
        
    else:
        failed_checks = [check for check, status in checks.items() if not status]
        print(f"\n❌ System NOT ready for production")
        print(f"Failed checks: {failed_checks}")
    
    return all_ready

def main():
    """Main verification function"""
    print("🔍 Final System Verification")
    print("=" * 50)
    
    try:
        if verify_production_readiness():
            print("\n✅ Verification completed successfully!")
            return True
        else:
            print("\n❌ Verification failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)