#!/usr/bin/env python3
"""
Check if the project is ready for Render deployment
"""

import os
import sys

def check_required_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        'requirements.txt',
        'app.py',
        'init_database.py',
        'database_config.py',
        'cloudinary_config.py',
        '.gitignore',
        'render.yaml'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_requirements_txt():
    """Check requirements.txt content"""
    print("\n🔍 Checking requirements.txt...")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_packages = [
            'Flask',
            'psycopg2-binary',
            'cloudinary',
            'gunicorn',
            'openpyxl'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            if package.lower() in content.lower():
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING")
                missing_packages.append(package)
        
        return len(missing_packages) == 0
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_app_py_production_ready():
    """Check if app.py is production ready"""
    print("\n🔍 Checking app.py production readiness...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('DATABASE_URL', 'PostgreSQL support'),
            ('IS_PRODUCTION', 'Production detection'),
            ('initialize_database', 'Database initialization'),
            ('gunicorn', 'WSGI server ready'),
            ('psycopg2', 'PostgreSQL driver')
        ]
        
        all_good = True
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - MISSING")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("❌ app.py not found")
        return False

def check_database_config():
    """Check database configuration"""
    print("\n🔍 Checking database configuration...")
    
    try:
        with open('database_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('get_database_connection', 'Database connection function'),
            ('psycopg2', 'PostgreSQL support'),
            ('DATABASE_URL', 'Environment variable support'),
            ('execute_query', 'Query execution function')
        ]
        
        all_good = True
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - MISSING")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("❌ database_config.py not found")
        return False

def check_cloudinary_config():
    """Check Cloudinary configuration"""
    print("\n🔍 Checking Cloudinary configuration...")
    
    try:
        with open('cloudinary_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('CLOUDINARY_CLOUD_NAME', 'Cloud name configuration'),
            ('CLOUDINARY_API_KEY', 'API key configuration'),
            ('upload_image_to_cloudinary', 'Image upload function'),
            ('is_cloudinary_configured', 'Configuration check function')
        ]
        
        all_good = True
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - MISSING")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("❌ cloudinary_config.py not found")
        return False

def check_static_files():
    """Check static files structure"""
    print("\n🔍 Checking static files...")
    
    required_dirs = [
        'static',
        'static/css',
        'static/js',
        'static/uploads',
        'templates'
    ]
    
    required_files = [
        'static/css/style.css',
        'static/js/data_entry.js',
        'templates/base.html',
        'templates/login.html',
        'templates/data_entry.html',
        'templates/admin_dashboard.html'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def check_environment_variables():
    """Check environment variables setup"""
    print("\n🔍 Checking environment variables...")
    
    # Check .env file (for development)
    env_vars = [
        'SECRET_KEY',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]
    
    if os.path.exists('.env'):
        print("✅ .env file exists (for development)")
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            for var in env_vars:
                if var in env_content:
                    print(f"✅ {var} configured")
                else:
                    print(f"⚠️ {var} not found in .env")
        except:
            print("⚠️ Could not read .env file")
    else:
        print("ℹ️ .env file not found (normal for production)")
    
    print("\n📝 Required environment variables for Render:")
    for var in env_vars:
        print(f"   • {var}")
    print("   • DATABASE_URL (will be set by Render)")
    
    return True

def main():
    """Run all deployment readiness checks"""
    print("🚀 Checking Render Deployment Readiness")
    print("=" * 50)
    
    checks = [
        check_required_files,
        check_requirements_txt,
        check_app_py_production_ready,
        check_database_config,
        check_cloudinary_config,
        check_static_files,
        check_environment_variables
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 PROJECT IS READY FOR RENDER DEPLOYMENT!")
        print("\n✅ All checks passed:")
        print("   • All required files present")
        print("   • Dependencies configured")
        print("   • Production settings ready")
        print("   • Database support enabled")
        print("   • Cloudinary integration ready")
        print("   • Static files organized")
        
        print("\n🚀 Next steps:")
        print("   1. Push code to GitHub")
        print("   2. Create Render account")
        print("   3. Create PostgreSQL database")
        print("   4. Create Web Service")
        print("   5. Set environment variables")
        print("   6. Deploy!")
        
        print("\n📖 Follow the guide: RENDER_DEPLOYMENT_QUICK_GUIDE.md")
        
    else:
        print("❌ PROJECT NOT READY FOR DEPLOYMENT!")
        print("\nPlease fix the issues above before deploying.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)