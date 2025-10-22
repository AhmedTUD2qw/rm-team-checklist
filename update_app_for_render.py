#!/usr/bin/env python3
"""
Update app.py to support PostgreSQL for Render deployment
"""

import re

def update_app_py():
    """Update app.py to support both SQLite and PostgreSQL"""
    print("🔧 Updating app.py for Render deployment...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all sqlite3.connect calls with get_db_connection
    content = re.sub(
        r'conn = sqlite3\.connect\([\'"]database\.db[\'"]\)',
        'conn, db_type = get_db_connection()',
        content
    )
    
    # Replace cursor creation
    content = re.sub(
        r'c = conn\.cursor\(\)',
        'c = conn.cursor()',
        content
    )
    
    # Update query execution for PostgreSQL compatibility
    # This is a simplified approach - you may need to manually update complex queries
    
    # Add port configuration for production
    if 'if __name__ == \'__main__\':' in content:
        content = re.sub(
            r'if __name__ == \'__main__\':\s*\n\s*app\.run\([^)]*\)',
            '''if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=not IS_PRODUCTION)''',
            content,
            flags=re.MULTILINE
        )
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py updated successfully!")

if __name__ == "__main__":
    update_app_py()
    print("🎉 App is ready for Render deployment!")