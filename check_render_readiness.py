#!/usr/bin/env python3
"""
Check if the project is ready for Render deployment
"""

import os
import sys

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'render.yaml',
        'render_setup.py',
        'cloudinary_config.py',
        'excel_export_enhanced.py',
        '.gitignore',
        'RENDER_DEPLOYMENT_GUIDE.md',
        'CLOUDINARY_SETUP_GUIDE.md',
        'EXCEL_EXPORT_GUIDE.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (MISSING)")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_requirements():
    """Check if requirements.txt has all needed packages"""
    print("\n📦 Checking requirements.txt...")
    
    required_packages = [
        'Flask',
        'Werkzeug', 
        'pandas',
        'openpyxl',
        'Pillow',
        'psycopg2-binary',
        'python-dotenv',
        'gunicorn',
        'cloudinary',
        'requests'
    ]
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_packages = []
        for package in required_packages:
            if package.lower() in content.lower():
                print(f"✅ {package}")
            else:
                print(f"❌ {package} (MISSING)")
                missing_packages.append(package)
        
        return len(missing_packages) == 0
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_app_configuration():
    """Check if app.py is configured for production"""
    print("\n⚙️ Checking app.py configuration...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'Environment variables': 'os.getenv' in content,
            'Database connection function': 'get_db_connection' in content,
            'PostgreSQL support': 'psycopg2' in content,
            'Production port': 'PORT' in content and '0.0.0.0' in content,
            'Production mode': 'IS_PRODUCTION' in content,
            'Cloudinary integration': 'cloudinary_config' in content and 'upload_image_to_cloudinary' in content,
            'Enhanced Excel export': 'excel_export_enhanced' in content and 'export_enhanced_excel_with_cloudinary' in content
        }
        
        all_good = True
        for check, passed in checks.items():
            if passed:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("❌ app.py not found")
        return False

def check_render_config():
    """Check render.yaml configuration"""
    print("\n🔧 Checking render.yaml...")
    
    try:
        with open('render.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            'services:',
            'type: web',
            'buildCommand:',
            'startCommand:',
            'databases:',
            'databaseName:'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section in content:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} (MISSING)")
                missing_sections.append(section)
        
        return len(missing_sections) == 0
        
    except FileNotFoundError:
        print("❌ render.yaml not found")
        return False

def main():
    """Main check function"""
    print("🔍 Checking Render Deployment Readiness")
    print("=" * 50)
    
    checks = [
        ("Required Files", check_files),
        ("Requirements", check_requirements), 
        ("App Configuration", check_app_configuration),
        ("Render Configuration", check_render_config)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 PROJECT IS READY FOR RENDER DEPLOYMENT!")
        print("\n📋 Next Steps:")
        print("1. Push code to GitHub")
        print("2. Create PostgreSQL database on Render")
        print("3. Create Web Service on Render")
        print("4. Configure environment variables")
        print("5. Deploy!")
        print("\n📖 See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions")
        return True
    else:
        print("❌ PROJECT IS NOT READY FOR DEPLOYMENT")
        print("\n🔧 Please fix the failed checks above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)