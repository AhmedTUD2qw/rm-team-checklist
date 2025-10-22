#!/usr/bin/env python3
"""
Production Setup Script - Prepares the system for production deployment
"""

import os
import sys
from production_database_manager import ProductionDatabaseManager

def setup_production_environment():
    """Setup production environment"""
    print("🚀 Setting up Production Environment")
    print("=" * 50)
    
    # Initialize production database manager
    manager = ProductionDatabaseManager()
    
    # Step 1: Initialize production database
    print("\n📊 Step 1: Database Initialization")
    if manager.initialize_production_database():
        print("✅ Production database initialized successfully")
    else:
        print("❌ Failed to initialize production database")
        return False
    
    # Step 2: Create initial backup
    print("\n💾 Step 2: Creating Initial Backup")
    backup_path = manager.create_backup('production_initial_backup.db')
    if backup_path:
        print(f"✅ Initial backup created: {backup_path}")
    else:
        print("❌ Failed to create initial backup")
    
    # Step 3: Verify database integrity
    print("\n🔍 Step 3: Database Integrity Check")
    if manager.verify_database_integrity():
        print("✅ Database integrity verified")
    else:
        print("❌ Database integrity check failed")
        return False
    
    # Step 4: Create production configuration
    print("\n⚙️ Step 4: Production Configuration")
    create_production_config()
    
    # Step 5: Setup backup schedule
    print("\n📅 Step 5: Backup Schedule Setup")
    setup_backup_schedule()
    
    print("\n🎉 Production setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Test the system: python app.py")
    print("2. Create regular backups: python production_database_manager.py")
    print("3. Monitor database integrity regularly")
    print("4. Deploy to production server")
    
    return True

def create_production_config():
    """Create production configuration file"""
    config_content = """# Production Configuration for Employee Data System

## Database Settings
- Database file: database.db
- Backup directory: database_backups
- Auto-backup: Enabled
- Backup retention: 30 days

## Security Settings
- Admin user: Admin/ADMIN
- Password policy: Minimum 6 characters
- Session timeout: 24 hours
- File upload limit: 16MB

## Performance Settings
- Max concurrent users: 50
- Database connection pool: 10
- File cleanup: Weekly

## Monitoring
- Database integrity check: Daily
- Backup verification: Weekly
- Log rotation: Monthly

## Maintenance Schedule
- Database optimization: Monthly
- Backup cleanup: Weekly
- System updates: As needed
"""
    
    with open('PRODUCTION_CONFIG.md', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Production configuration created: PRODUCTION_CONFIG.md")

def setup_backup_schedule():
    """Setup automated backup schedule"""
    backup_script = """#!/usr/bin/env python3
# Automated Backup Script
# Run this script daily via cron job or task scheduler

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_database_manager import ProductionDatabaseManager
from datetime import datetime

def daily_backup():
    manager = ProductionDatabaseManager()
    
    # Create daily backup
    timestamp = datetime.now().strftime('%Y%m%d')
    backup_name = f'daily_backup_{timestamp}.db'
    
    if manager.create_backup(backup_name):
        print(f"✅ Daily backup created: {backup_name}")
        
        # Cleanup old backups (keep 30 days)
        manager.cleanup_old_backups(30)
        
        # Verify database integrity
        if manager.verify_database_integrity():
            print("✅ Database integrity verified")
        else:
            print("❌ Database integrity check failed - manual intervention required")
    else:
        print("❌ Daily backup failed - manual intervention required")

if __name__ == "__main__":
    daily_backup()
"""
    
    with open('daily_backup.py', 'w', encoding='utf-8') as f:
        f.write(backup_script)
    
    print("✅ Backup script created: daily_backup.py")
    print("   Schedule this script to run daily via cron or task scheduler")

def create_deployment_guide():
    """Create deployment guide"""
    guide_content = """# Production Deployment Guide

## Prerequisites
- Python 3.7+
- Required packages: Flask, pandas, openpyxl, werkzeug
- Web server (optional): nginx, Apache
- Process manager (optional): gunicorn, uwsgi

## Deployment Steps

### 1. Server Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup directory structure
mkdir -p /var/www/employee-data-system
cd /var/www/employee-data-system

# Copy application files
cp -r * /var/www/employee-data-system/
```

### 2. Database Setup
```bash
# Initialize production database
python setup_production.py

# Verify setup
python production_database_manager.py
```

### 3. Security Configuration
- Change default admin password
- Setup SSL/HTTPS
- Configure firewall rules
- Setup user authentication

### 4. Web Server Configuration (nginx example)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /var/www/employee-data-system/static;
    }
}
```

### 5. Process Management (systemd example)
```ini
[Unit]
Description=Employee Data System
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/employee-data-system
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. Backup Schedule
```bash
# Add to crontab
0 2 * * * /usr/bin/python3 /var/www/employee-data-system/daily_backup.py
```

### 7. Monitoring
- Setup log monitoring
- Database integrity checks
- Performance monitoring
- Backup verification

## Post-Deployment
1. Test all functionality
2. Create admin users
3. Train end users
4. Setup monitoring alerts
5. Document procedures

## Maintenance
- Regular backups
- Database optimization
- Security updates
- Performance monitoring
"""
    
    with open('DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Deployment guide created: DEPLOYMENT_GUIDE.md")

def main():
    """Main setup function"""
    try:
        # Setup production environment
        if setup_production_environment():
            # Create additional documentation
            create_deployment_guide()
            
            print("\n🎊 Production setup completed successfully!")
            print("\nYour system is now ready for production deployment.")
            print("Please review the generated documentation files:")
            print("- PRODUCTION_CONFIG.md")
            print("- DEPLOYMENT_GUIDE.md")
            print("- daily_backup.py")
            
        else:
            print("\n❌ Production setup failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()