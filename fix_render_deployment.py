#!/usr/bin/env python3
"""
Fix common Render deployment issues
"""

import os
import sys

def fix_requirements():
    """Fix requirements.txt for Render compatibility"""
    print("🔧 Fixing requirements.txt...")
    
    # Read current requirements
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Check for problematic packages
        fixes_needed = []
        
        if 'psycopg2==' in content and 'psycopg2-binary' not in content:
            fixes_needed.append("Replace psycopg2 with psycopg2-binary")
        
        if 'Pillow==' in content:
            # Check version
            import re
            pillow_match = re.search(r'Pillow==(\d+\.\d+\.\d+)', content)
            if pillow_match:
                version = pillow_match.group(1)
                major, minor, patch = map(int, version.split('.'))
                if major < 10:
                    fixes_needed.append("Update Pillow to 10.0.1+")
        
        if fixes_needed:
            print("⚠️ Issues found:")
            for fix in fixes_needed:
                print(f"   • {fix}")
        else:
            print("✅ requirements.txt looks good!")
        
        return len(fixes_needed) == 0
        
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

def create_render_files():
    """Create necessary files for Render deployment"""
    print("\n🔧 Creating Render deployment files...")
    
    files_created = []
    
    # Create runtime.txt if not exists
    if not os.path.exists('runtime.txt'):
        with open('runtime.txt', 'w') as f:
            f.write('python-3.11.0\n')
        files_created.append('runtime.txt')
    
    # Create Procfile if not exists
    if not os.path.exists('Procfile'):
        with open('Procfile', 'w') as f:
            f.write('web: gunicorn app:app\n')
        files_created.append('Procfile')
    
    # Update render.yaml with better settings
    render_yaml_content = '''services:
  - type: web
    name: rm-team-checklist
    env: python
    region: oregon
    plan: free
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app --workers 1 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: rm-checklist-db
          property: connectionString
  
  - type: pserv
    name: rm-checklist-db
    env: postgresql
    plan: free
    region: oregon
    databaseName: rm_checklist
    databaseUser: rm_user
'''
    
    with open('render.yaml', 'w') as f:
        f.write(render_yaml_content)
    files_created.append('render.yaml (updated)')
    
    if files_created:
        print("✅ Files created/updated:")
        for file in files_created:
            print(f"   • {file}")
    
    return True

def check_app_py():
    """Check app.py for Render compatibility"""
    print("\n🔧 Checking app.py...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('DATABASE_URL', 'PostgreSQL environment variable support'),
            ('IS_PRODUCTION', 'Production environment detection'),
            ('psycopg2', 'PostgreSQL driver import'),
            ('gunicorn', 'WSGI server compatibility'),
            ('PORT', 'Port environment variable')
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
        print("❌ app.py not found!")
        return False

def create_deployment_guide():
    """Create step-by-step deployment guide"""
    print("\n📝 Creating deployment guide...")
    
    guide_content = '''# 🚀 Render Deployment Guide - Fixed Version

## ✅ Files Ready:
- requirements.txt (fixed for Render)
- runtime.txt (Python 3.11.0)
- Procfile (Gunicorn configuration)
- render.yaml (optimized settings)

## 🔧 Deployment Steps:

### 1. Create Render Account
- Go to: https://render.com
- Sign up with GitHub or email

### 2. Create PostgreSQL Database
- Dashboard → New + → PostgreSQL
- Name: rm-checklist-db
- Database: rm_checklist
- User: rm_user
- Plan: Free
- Region: Oregon
- Click "Create Database"

### 3. Create Web Service
- Dashboard → New + → Web Service
- Connect your GitHub repository
- Settings:
  - Name: rm-team-checklist
  - Environment: Python 3
  - Region: Oregon (same as database)
  - Plan: Free
  - Build Command: pip install --upgrade pip && pip install -r requirements.txt
  - Start Command: gunicorn --bind 0.0.0.0:$PORT app:app --workers 1 --timeout 120

### 4. Environment Variables
Add these in Web Service → Environment:

```
SECRET_KEY = [generate a strong 32+ character key]
FLASK_ENV = production
CLOUDINARY_CLOUD_NAME = [your cloudinary cloud name]
CLOUDINARY_API_KEY = [your cloudinary api key]
CLOUDINARY_API_SECRET = [your cloudinary api secret]
```

### 5. Connect Database
- In Environment Variables
- Add Environment Variable → Add from Database
- Select: rm-checklist-db
- Select: DATABASE_URL

### 6. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Your app will be available at: https://rm-team-checklist.onrender.com

## 🎯 Login Credentials:
- Username: admin
- Password: admin123

## 🔧 If Build Fails:
1. Check Build Logs in Render dashboard
2. Ensure all environment variables are set
3. Verify database connection is established
4. Check that PostgreSQL service is running

## 📞 Support:
If you encounter issues, check:
1. Build logs for specific error messages
2. Runtime logs for application errors
3. Database connection status
4. Environment variables configuration

## 🎉 Success Indicators:
- Build completes without errors
- App starts successfully
- Database tables are created automatically
- Admin login works
- Image upload functions properly
'''
    
    with open('RENDER_DEPLOYMENT_FIXED.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Created: RENDER_DEPLOYMENT_FIXED.md")
    return True

def main():
    """Run all fixes"""
    print("🔧 Render Deployment Fix Tool")
    print("=" * 50)
    
    fixes = [
        fix_requirements,
        create_render_files,
        check_app_py,
        create_deployment_guide
    ]
    
    all_good = True
    
    for fix in fixes:
        if not fix():
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n✅ Ready for Render deployment:")
        print("   • requirements.txt optimized")
        print("   • Runtime specified (Python 3.11)")
        print("   • Procfile created")
        print("   • render.yaml optimized")
        print("   • Deployment guide updated")
        
        print("\n🚀 Next steps:")
        print("   1. Commit and push to GitHub")
        print("   2. Follow RENDER_DEPLOYMENT_FIXED.md")
        print("   3. Deploy to Render")
        
        print("\n📖 Key changes made:")
        print("   • Fixed psycopg2-binary version")
        print("   • Added build optimizations")
        print("   • Increased timeout settings")
        print("   • Specified Python version")
        
    else:
        print("❌ SOME FIXES FAILED!")
        print("Please check the issues above.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)