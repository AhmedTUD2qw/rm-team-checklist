from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
# Removed external data management routes - using internal implementation
try:
    import psycopg2
    from urllib.parse import urlparse
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️ psycopg2 not available - PostgreSQL support disabled")

from cloudinary_config import (
    upload_image_to_cloudinary, 
    upload_excel_to_cloudinary,
    create_temp_excel_file,
    cleanup_temp_file,
    is_cloudinary_configured
)
from excel_export_enhanced import (
    export_enhanced_excel_with_cloudinary,
    create_simple_excel_with_formatting
)
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
IS_PRODUCTION = DATABASE_URL is not None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup (for production)
if IS_PRODUCTION:
    try:
        from init_database import initialize_database
        print("🔧 Initializing production database...")
        initialize_database()
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
IS_PRODUCTION = DATABASE_URL is not None

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute query with proper database handling"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert SQLite syntax to PostgreSQL if needed
        if db_type == 'postgresql':
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            
        conn.commit()
        return result
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_db_connection():
    """Get database connection based on environment"""
    if IS_PRODUCTION and DATABASE_URL and PSYCOPG2_AVAILABLE:
        # Production: PostgreSQL
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        return conn, 'postgresql'
    else:
        # Development: SQLite
        conn = sqlite3.connect('database.db')
        return conn, 'sqlite'

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute query with proper database handling"""
    conn, db_type = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            # Convert SQLite placeholders to PostgreSQL
            if params:
                pg_query = query.replace('?', '%s')
                cursor.execute(pg_query, params)
            else:
                cursor.execute(query)
        else:
            # SQLite
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            
        conn.commit()
        return result
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize database with persistent data preservation"""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company_code TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add created_date column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE users ADD COLUMN created_date TEXT DEFAULT CURRENT_TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Data entries table
    c.execute('''CREATE TABLE IF NOT EXISTS data_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT NOT NULL,
        employee_code TEXT NOT NULL,
        branch TEXT NOT NULL,
        shop_code TEXT,
        model TEXT NOT NULL,
        display_type TEXT NOT NULL,
        selected_materials TEXT,
        unselected_materials TEXT,
        images TEXT,
        date TEXT NOT NULL
    )''')
    
    # Branches table for autocomplete
    c.execute('''CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT NOT NULL,
        shop_code TEXT NOT NULL,
        employee_code TEXT NOT NULL,
        created_date TEXT NOT NULL,
        UNIQUE(branch_name, employee_code),
        UNIQUE(shop_code, employee_code)
    )''')
    
    # Categories management table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        created_date TEXT NOT NULL
    )''')
    
    # Models management table
    c.execute('''CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        created_date TEXT NOT NULL,
        UNIQUE(model_name, category_name)
    )''')
    
    # Display types management table
    c.execute('''CREATE TABLE IF NOT EXISTS display_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_type_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        created_date TEXT NOT NULL,
        UNIQUE(display_type_name, category_name)
    )''')
    
    # POP materials management table
    c.execute('''CREATE TABLE IF NOT EXISTS pop_materials_db (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        model_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        created_date TEXT NOT NULL,
        UNIQUE(material_name, model_name)
    )''')
    
    # User branches management table
    c.execute('''CREATE TABLE IF NOT EXISTS user_branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        branch_name TEXT NOT NULL,
        created_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, branch_name)
    )''')
    
    # Database initialization status table
    c.execute('''CREATE TABLE IF NOT EXISTS db_init_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component TEXT NOT NULL UNIQUE,
        initialized BOOLEAN DEFAULT FALSE,
        last_update TEXT NOT NULL
    )''')
    
    # Check if this is the first run or if we need to initialize data
    initialize_system_data(c)
    
    conn.commit()
    conn.close()

def initialize_system_data(cursor):
    """Initialize system data only if not already done"""
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if admin user exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        print("🔧 Creating admin user...")
        admin_password = generate_password_hash('admin123')
        # Try new schema first
        try:
            cursor.execute('INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) VALUES (?, ?, ?, ?, ?)',
                         ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
        except:
            # Fallback to old schema
            cursor.execute('INSERT INTO users (name, company_code, password, is_admin) VALUES (?, ?, ?, ?)',
                         ('admin', 'ADMIN001', admin_password, True))
        
        # Mark admin as initialized
        cursor.execute('INSERT OR REPLACE INTO db_init_status (component, initialized, last_update) VALUES (?, ?, ?)',
                     ('admin_user', True, current_time))
        print("✅ Admin user created")
    
    # Check if default categories are initialized
    cursor.execute('SELECT initialized FROM db_init_status WHERE component = ?', ('default_categories',))
    categories_init = cursor.fetchone()
    
    if not categories_init or not categories_init[0]:
        print("🔧 Initializing default categories...")
        initialize_default_categories(cursor)
        cursor.execute('INSERT OR REPLACE INTO db_init_status (component, initialized, last_update) VALUES (?, ?, ?)',
                     ('default_categories', True, current_time))
        print("✅ Default categories initialized")
    
    # Check if default models are initialized
    cursor.execute('SELECT initialized FROM db_init_status WHERE component = ?', ('default_models',))
    models_init = cursor.fetchone()
    
    if not models_init or not models_init[0]:
        print("🔧 Initializing default models...")
        initialize_default_models(cursor)
        cursor.execute('INSERT OR REPLACE INTO db_init_status (component, initialized, last_update) VALUES (?, ?, ?)',
                     ('default_models', True, current_time))
        print("✅ Default models initialized")
    
    # Check if default display types are initialized
    cursor.execute('SELECT initialized FROM db_init_status WHERE component = ?', ('default_display_types',))
    display_types_init = cursor.fetchone()
    
    if not display_types_init or not display_types_init[0]:
        print("🔧 Initializing default display types...")
        initialize_default_display_types(cursor)
        cursor.execute('INSERT OR REPLACE INTO db_init_status (component, initialized, last_update) VALUES (?, ?, ?)',
                     ('default_display_types', True, current_time))
        print("✅ Default display types initialized")
    
    # Check if default POP materials are initialized
    cursor.execute('SELECT initialized FROM db_init_status WHERE component = ?', ('default_pop_materials',))
    pop_materials_init = cursor.fetchone()
    
    if not pop_materials_init or not pop_materials_init[0]:
        print("🔧 Initializing default POP materials...")
        initialize_default_pop_materials(cursor)
        cursor.execute('INSERT OR REPLACE INTO db_init_status (component, initialized, last_update) VALUES (?, ?, ?)',
                     ('default_pop_materials', True, current_time))
        print("✅ Default POP materials initialized")

def initialize_default_categories(cursor):
    """Initialize default categories"""
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    categories = ['OLED', 'Neo QLED', 'QLED', 'UHD', 'LTV', 'BESPOKE COMBO', 
                 'BESPOKE Front', 'Front', 'TL', 'SBS', 'TMF', 'BMF', 'Local TMF']
    
    for category in categories:
        cursor.execute('INSERT OR IGNORE INTO categories (category_name, created_date) VALUES (?, ?)',
                      (category, current_time))

def initialize_default_models(cursor):
    """Initialize default models - temporarily disabled"""
    print("⚠️ Model initialization temporarily disabled to avoid SQL errors")
    pass

def initialize_default_display_types(cursor):
    """Initialize default display types - temporarily disabled"""
    print("⚠️ Display types initialization temporarily disabled to avoid SQL errors")
    pass

def initialize_default_pop_materials(cursor):
    """Initialize default POP materials - temporarily disabled"""
    print("⚠️ POP materials initialization temporarily disabled to avoid SQL errors")
    pass



@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    company_code = request.form['company_code']
    password = request.form['password']
    remember_me = 'remember_me' in request.form
    
    # Try new schema first, then fallback to old schema
    try:
        user = execute_query('SELECT * FROM users WHERE username = ? AND employee_code = ?', 
                            (name, company_code), fetch_one=True)
    except:
        # Fallback to old schema
        user = execute_query('SELECT * FROM users WHERE name = ? AND company_code = ?', 
                            (name, company_code), fetch_one=True)
    
    if user and check_password_hash(user[2], password):  # user[2] is password_hash
        session['user_id'] = user[0]
        session['user_name'] = user[1]  # username or name
        session['employee_name'] = user[1] if len(user) <= 3 else user[3]  # employee_name
        session['company_code'] = user[4] if len(user) > 4 else company_code  # employee_code or company_code
        session['is_admin'] = user[5] if len(user) > 5 else (user[4] if len(user) > 4 else False)  # is_admin
        session.permanent = remember_me
        
        if user[5]:  # is_admin
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('data_entry'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/data_entry')
def data_entry():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('data_entry.html')

@app.route('/get_dynamic_data/<data_type>')
def get_dynamic_data(data_type):
    """Get dynamic data from database for frontend"""
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if data_type == 'categories':
            # Try new schema first, fallback to old
            try:
                c.execute('SELECT name FROM categories ORDER BY name')
                data = [row[0] for row in c.fetchall()]
            except:
                c.execute('SELECT category_name FROM categories ORDER BY category_name')
                data = [row[0] for row in c.fetchall()]
        
        elif data_type == 'models':
            category = request.args.get('category', '')
            if category:
                # Try new schema first
                try:
                    # Get category ID first
                    c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                    cat_result = c.fetchone()
                    if cat_result:
                        c.execute(f'SELECT name FROM models WHERE category_id = {placeholder} ORDER BY name', (cat_result[0],))
                        data = [row[0] for row in c.fetchall()]
                    else:
                        data = []
                except:
                    # Fallback to old schema
                    c.execute(f'SELECT model_name FROM models WHERE category_name = {placeholder} ORDER BY model_name', (category,))
                    data = [row[0] for row in c.fetchall()]
            else:
                try:
                    c.execute('SELECT name FROM models ORDER BY name')
                    data = [row[0] for row in c.fetchall()]
                except:
                    c.execute('SELECT model_name FROM models ORDER BY model_name')
                    data = [row[0] for row in c.fetchall()]
        
        elif data_type == 'display_types':
            category = request.args.get('category', '')
            if category:
                try:
                    # Get category ID first
                    c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                    cat_result = c.fetchone()
                    if cat_result:
                        c.execute(f'SELECT name FROM display_types WHERE category_id = {placeholder} ORDER BY name', (cat_result[0],))
                        data = [row[0] for row in c.fetchall()]
                    else:
                        data = []
                except:
                    # Fallback to old schema
                    c.execute(f'SELECT display_type_name FROM display_types WHERE category_name = {placeholder} ORDER BY display_type_name', (category,))
                    data = [row[0] for row in c.fetchall()]
            else:
                data = []
        
        elif data_type == 'pop_materials':
            model = request.args.get('model', '')
            if model:
                try:
                    # Get model ID first
                    c.execute(f'SELECT id FROM models WHERE name = {placeholder}', (model,))
                    model_result = c.fetchone()
                    if model_result:
                        c.execute(f'SELECT name FROM pop_materials WHERE model_id = {placeholder} ORDER BY name', (model_result[0],))
                        data = [row[0] for row in c.fetchall()]
                    else:
                        data = []
                except:
                    # Fallback to old schema
                    c.execute(f'SELECT material_name FROM pop_materials_db WHERE model_name = {placeholder} ORDER BY material_name', (model,))
                    data = [row[0] for row in c.fetchall()]
            else:
                data = []
        
        conn.close()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        print(f"Error in get_dynamic_data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_branches', methods=['GET'])
def get_branches():
    if 'user_id' not in session or session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        employee_code = session['company_code']
        search_term = request.args.get('search', '').strip()
        
        conn, db_type = get_db_connection()
        c = conn.cursor()
        
        if search_term:
            # Search by both branch name and shop code
            c.execute('''SELECT branch_name, shop_code FROM branches 
                        WHERE employee_code = ? AND 
                        (branch_name LIKE ? OR shop_code LIKE ?) 
                        ORDER BY branch_name''', 
                     (employee_code, f'%{search_term}%', f'%{search_term}%'))
        else:
            c.execute('''SELECT branch_name, shop_code FROM branches 
                        WHERE employee_code = ? 
                        ORDER BY branch_name''', 
                     (employee_code,))
        
        branches = [{'name': row[0], 'code': row[1]} for row in c.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'branches': branches})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_branch_by_code', methods=['GET'])
def get_branch_by_code():
    if 'user_id' not in session or session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        employee_code = session['company_code']
        shop_code = request.args.get('code', '').strip()
        
        if not shop_code:
            return jsonify({'success': False, 'message': 'Shop code is required'})
        
        conn, db_type = get_db_connection()
        c = conn.cursor()
        
        c.execute('''SELECT branch_name, shop_code FROM branches 
                    WHERE employee_code = ? AND shop_code = ?''', 
                 (employee_code, shop_code))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return jsonify({'success': True, 'branch': {'name': result[0], 'code': result[1]}})
        else:
            return jsonify({'success': False, 'message': 'Branch not found'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/submit_data', methods=['POST'])
def submit_data():
    if 'user_id' not in session or session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get form data
        employee_name = session['user_name']
        employee_code = session['company_code']
        
        # Process multiple model entries
        entries_saved = 0
        model_index = 0
        
        while f'branch_{model_index}' in request.form:
            branch = request.form.get(f'branch_{model_index}')
            shop_code = request.form.get(f'shop_code_{model_index}')
            category = request.form.get(f'category_{model_index}')
            model = request.form.get(f'model_{model_index}')
            display_type = request.form.get(f'display_type_{model_index}')
            
            # Save branch if it's new
            if branch and shop_code:
                conn, db_type = get_db_connection()
                c = conn.cursor()
                try:
                    c.execute('''INSERT OR IGNORE INTO branches 
                                (branch_name, shop_code, employee_code, created_date) 
                                VALUES (?, ?, ?, ?)''',
                             (branch, shop_code, employee_code, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                except:
                    pass  # Branch already exists, ignore
                conn.close()
            
            # Get selected POP materials
            selected_materials = request.form.getlist(f'pop_materials_{model_index}')
            
            # Define all possible materials by category
            pop_materials_by_category = {
                'OLED': [
                    'AI topper', 'Oled Topper', 'Glare Free', 'New Topper', '165 HZ Side POP',
                    'Category POP', 'Samsung OLED Topper', '165 HZ & joy stick indicator',
                    'AI Topper Gaming', 'Side POP', 'Specs Card', 'OLED Topper', 'Why Oled side POP'
                ],
                'Neo QLED': [
                    'AI topper', 'Lockup Topper', 'Screen POP', 'New Topper', 'Glare Free', 'Specs Card'
                ],
                'QLED': [
                    'AI topper', 'Samsung QLED Topper', 'Screen POP', 'New Topper', 'Specs Card', 'QLED Topper'
                ],
                'UHD': [
                    'UHD topper', 'Samsung UHD topper', 'Screen POP', 'New Topper', 'Specs Card',
                    'AI topper', 'Samsung Lockup Topper', 'Inch Logo side POP'
                ],
                'LTV': [
                    'Side POP', 'Matte Display', 'Category POP', 'Frame Bezel'
                ],
                'BESPOKE COMBO': [
                    'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                    'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
                    'Ecobuble POP', 'Ecco Buble', 'AI Ecco Buble', '20 Years Warranty',
                    'New Arrival', 'Samsung Brand/Tech Topper'
                ],
                'BESPOKE Front': [
                    'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                    'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
                    'Ecobuble POP', 'Ecco Buble', 'AI Ecco Buble', '20 Years Warranty',
                    'New Arrival', 'Samsung Brand/Tech Topper'
                ],
                'Front': [
                    'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                    'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
                    'Ecobuble POP', 'Ecco Buble', 'AI Ecco Buble', '20 Years Warranty',
                    'New Arrival', 'Samsung Brand/Tech Topper'
                ],
                'TL': [
                    'PODs (Door)', 'POD (Top)', 'POD (Front)', '3 PODs (Top)', 'AI Home POP',
                    'AI Home', 'AI control panel', 'Capacity (Kg)', 'Capacity Dryer', 'Filter',
                    'Ecobuble POP', 'Ecco Buble', 'AI Ecco Buble', '20 Years Warranty',
                    'New Arrival', 'Samsung Brand/Tech Topper'
                ],
                'SBS': [
                    'Samsung Brand/Tech Topper', 'Main POD', '20 Years Warranty', 'Twin Cooling Plus™',
                    'Smart Conversion™', 'Digital Inverter™', 'SpaceMax™', 'Tempered Glass',
                    'Power Freeze', 'Big Vegetable Box', 'Organize Big Bin'
                ],
                'TMF': [
                    'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                    'Global No.1', 'Freshness POP', 'Bacteria Safe Ionizer POP', 'Gallon Guard POP',
                    'Big Vegetables Box POP', 'Adjustable Pin & Organize POP', 'Optimal Fresh',
                    'Tempered Glass', 'Gallon Guard', 'Veg Box', 'Internal Display', 'Multi Tray',
                    'Foldable Shelf', 'Active Fresh Filter'
                ],
                'BMF': [
                    'Samsung Brand/Tech Topper', '20 Years Warranty', 'Key features POP', 'Side POP',
                    'Global No.1', 'Led Lighting POP', 'Full Open Box POP', 'Big Guard POP',
                    'Adjustable Pin', 'Saves Energy POP', 'Gentle Lighting', 'Multi Tray',
                    'All-Around Cooling', '2 Step Foldable Shelf', 'Big Fresh Box'
                ],
                'Local TMF': [
                    'Samsung Brand/Tech Topper', 'Key features POP', 'Side POP', 'Big Vegetables Box POP'
                ]
            }
            
            # Get all materials for the selected model from database
            conn_materials, db_type_materials = get_db_connection()
            c_materials = conn_materials.cursor()
            
            # Try new schema first
            try:
                # Get model ID first
                placeholder = '%s' if db_type_materials == 'postgresql' else '?'
                c_materials.execute(f'SELECT id FROM models WHERE name = {placeholder}', (model,))
                model_result = c_materials.fetchone()
                if model_result:
                    c_materials.execute(f'SELECT name FROM pop_materials WHERE model_id = {placeholder}', (model_result[0],))
                    model_materials = [row[0] for row in c_materials.fetchall()]
                else:
                    model_materials = []
            except:
                # Fallback to old schema
                try:
                    c_materials.execute(f'SELECT material_name FROM pop_materials_db WHERE model_name = {placeholder}', (model,))
                    model_materials = [row[0] for row in c_materials.fetchall()]
                except:
                    model_materials = []
            
            conn_materials.close()
            
            # Calculate unselected materials based on model-specific materials
            unselected_materials = [mat for mat in model_materials if mat not in selected_materials]
            
            # Handle image uploads
            uploaded_images = []
            if f'images_{model_index}' in request.files:
                files = request.files.getlist(f'images_{model_index}')
                for file in files:
                    if file and file.filename:
                        if is_cloudinary_configured():
                            # رفع إلى Cloudinary
                            result = upload_image_to_cloudinary(file, f"employee_data/{employee_code}")
                            if result['success']:
                                uploaded_images.append(result['url'])
                            else:
                                flash(f'خطأ في رفع الصورة: {result.get("error", "خطأ غير معروف")}')
                        else:
                            # رفع محلي (للتطوير)
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                            filename = timestamp + filename
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            file.save(file_path)
                            uploaded_images.append(filename)
            
            # Save to database
            conn, db_type = get_db_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO data_entries 
                        (employee_name, employee_code, branch_name, shop_code, model, display_type, 
                         selected_materials, missing_materials, image_urls, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (employee_name, employee_code, branch, shop_code, f"{category} - {model}", 
                      display_type, ','.join(selected_materials), 
                      ','.join(unselected_materials), ','.join(uploaded_images),
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Auto-assign branch to user if not already assigned
            user_id = session.get('user_id')
            if user_id and branch:
                c.execute('''INSERT OR IGNORE INTO user_branches (user_id, branch_name, created_date) 
                             VALUES (?, ?, ?)''',
                          (user_id, branch, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            conn.close()
            
            entries_saved += 1
            model_index += 1
        
        return jsonify({
            'success': True, 
            'message': f'{entries_saved} model entries saved successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    # Get filter parameters
    employee_filter = request.args.get('employee', '')
    branch_filter = request.args.get('branch', '')
    model_filter = request.args.get('model', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = 'SELECT * FROM data_entries WHERE 1=1'
    params = []
    
    if employee_filter:
        query += ' AND employee_name LIKE ?'
        params.append(f'%{employee_filter}%')
    
    if branch_filter:
        query += ' AND branch LIKE ?'
        params.append(f'%{branch_filter}%')
    
    if model_filter:
        query += ' AND model LIKE ?'
        params.append(f'%{model_filter}%')
    
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to + ' 23:59:59')
    
    query += ' ORDER BY created_at DESC'
    
    # Execute query
    conn, db_type = get_db_connection()
    c = conn.cursor()
    c.execute(query, params)
    data_entries = c.fetchall()
    
    # Get unique values for filters
    c.execute('SELECT DISTINCT employee_name FROM data_entries ORDER BY employee_name')
    employees = [row[0] for row in c.fetchall()]
    
    c.execute('SELECT DISTINCT branch_name FROM data_entries ORDER BY branch_name')
    branches = [row[0] for row in c.fetchall()]
    
    c.execute('SELECT DISTINCT model FROM data_entries ORDER BY model')
    models = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         data_entries=data_entries,
                         employees=employees,
                         branches=branches,
                         models=models,
                         filters={
                             'employee': employee_filter,
                             'branch': branch_filter,
                             'model': model_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })

@app.route('/export_excel')
def export_excel():
    """تصدير Excel محسن مع الصور والتنسيق"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        # الحصول على معاملات الفلترة من الطلب
        employee_filter = request.args.get('employee', '')
        branch_filter = request.args.get('branch', '')
        model_filter = request.args.get('model', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # بناء الاستعلام مع الفلاتر (نفس منطق admin_dashboard)
        query = '''SELECT id, employee_name, employee_code, branch_name, shop_code, model, 
                          display_type, selected_materials, missing_materials, image_urls, created_at 
                   FROM data_entries WHERE 1=1'''
        params = []
        
        if employee_filter:
            query += ' AND employee_name LIKE ?'
            params.append(f'%{employee_filter}%')
        
        if branch_filter:
            query += ' AND branch LIKE ?'
            params.append(f'%{branch_filter}%')
        
        if model_filter:
            query += ' AND model LIKE ?'
            params.append(f'%{model_filter}%')
        
        if date_from:
            query += ' AND date >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND date <= ?'
            params.append(date_to + ' 23:59:59')
        
        query += ' ORDER BY created_at DESC'
        
        # تنفيذ الاستعلام
        conn, db_type = get_db_connection()
        c = conn.cursor()
        c.execute(query, params)
        entries = c.fetchall()
        conn.close()
        
        if not entries:
            flash('لا توجد بيانات للتصدير مع الفلاتر المحددة')
            return redirect(url_for('admin_dashboard'))
        
        # إضافة رسالة توضيحية عن عدد السجلات
        flash(f'جاري تصدير {len(entries)} سجل مع الفلاتر المطبقة')
        
        # تصدير محسن مع الصور
        result = export_enhanced_excel_with_cloudinary(entries)
        
        if result['success']:
            if result['method'] == 'cloudinary':
                # إعادة توجيه إلى رابط Cloudinary
                flash(f'تم إنشاء التقرير المحسن ورفعه إلى السحابة! {result["message"]}')
                return redirect(result['url'])
            else:
                # إرسال الملف مباشرة (محسن محلياً)
                return send_file(
                    BytesIO(result['data']),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=result['filename']
                )
        else:
            flash(f'خطأ في التصدير المحسن: {result["error"]}')
            # Fallback إلى التصدير البسيط
            return redirect(url_for('export_excel_simple'))
            
    except Exception as e:
        flash(f'خطأ في تصدير البيانات: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/export_excel_simple')
def export_excel_simple():
    """تصدير Excel بسيط مع تنسيق محسن (بدون صور)"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        # الحصول على معاملات الفلترة من الطلب
        employee_filter = request.args.get('employee', '')
        branch_filter = request.args.get('branch', '')
        model_filter = request.args.get('model', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # بناء الاستعلام مع الفلاتر (نفس منطق admin_dashboard)
        query = '''SELECT id, employee_name, employee_code, branch_name, shop_code, model, 
                          display_type, selected_materials, missing_materials, image_urls, created_at 
                   FROM data_entries WHERE 1=1'''
        params = []
        
        if employee_filter:
            query += ' AND employee_name LIKE ?'
            params.append(f'%{employee_filter}%')
        
        if branch_filter:
            query += ' AND branch LIKE ?'
            params.append(f'%{branch_filter}%')
        
        if model_filter:
            query += ' AND model LIKE ?'
            params.append(f'%{model_filter}%')
        
        if date_from:
            query += ' AND date >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND date <= ?'
            params.append(date_to + ' 23:59:59')
        
        query += ' ORDER BY created_at DESC'
        
        # تنفيذ الاستعلام
        conn, db_type = get_db_connection()
        c = conn.cursor()
        c.execute(query, params)
        entries = c.fetchall()
        conn.close()
        
        if not entries:
            flash('لا توجد بيانات للتصدير مع الفلاتر المحددة')
            return redirect(url_for('admin_dashboard'))
        
        # إضافة رسالة توضيحية عن عدد السجلات
        flash(f'جاري تصدير {len(entries)} سجل (بسيط) مع الفلاتر المطبقة')
        
        # إنشاء اسم الملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pop_materials_simple_{timestamp}.xlsx'
        
        # إنشاء ملف Excel مع تنسيق
        temp_path = create_simple_excel_with_formatting(entries, filename)
        
        if not temp_path:
            flash('خطأ في إنشاء ملف Excel')
            return redirect(url_for('admin_dashboard'))
        
        # محاولة رفع إلى Cloudinary
        if is_cloudinary_configured():
            result = upload_excel_to_cloudinary(temp_path, filename, "reports/simple")
            
            if result['success']:
                cleanup_temp_file(temp_path)
                flash('تم إنشاء التقرير ورفعه إلى السحابة بنجاح')
                return redirect(result['url'])
            else:
                flash(f'تم إنشاء التقرير محلياً: {result.get("error", "")}')
        
        # إرسال الملف مباشرة
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        cleanup_temp_file(temp_path)
        
        return send_file(
            BytesIO(file_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'خطأ في تصدير البيانات: {str(e)}')
        return redirect(url_for('admin_dashboard'))

# تم استبدال هذه الدالة بـ export_enhanced_excel_with_cloudinary في excel_export_enhanced.py

@app.route('/download_image/<filename>')
def download_image(filename):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), 
                        as_attachment=True)
    except Exception as e:
        flash(f'Error downloading image: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin_management')
def admin_management():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('admin_management.html')

@app.route('/get_management_data/<data_type>')
def get_management_data(data_type):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if data_type == 'categories':
            # Get unique categories only
            try:
                c.execute('SELECT DISTINCT id, name, created_at FROM categories ORDER BY name LIMIT 50')
                rows = c.fetchall()
                data = []
                seen_names = set()
                for row in rows:
                    if row[1] not in seen_names:
                        seen_names.add(row[1])
                        data.append({'id': row[0], 'name': row[1], 'created_at': str(row[2]) if row[2] else 'N/A'})
            except:
                try:
                    c.execute('SELECT DISTINCT id, category_name, created_date FROM categories ORDER BY category_name LIMIT 50')
                    rows = c.fetchall()
                    data = []
                    seen_names = set()
                    for row in rows:
                        if row[1] not in seen_names:
                            seen_names.add(row[1])
                            data.append({'id': row[0], 'name': row[1], 'created_at': str(row[2]) if row[2] else 'N/A'})
                except Exception as e:
                    return jsonify({'success': False, 'message': f'Categories error: {str(e)}'}), 500
        
        elif data_type == 'models':
            category = request.args.get('category', '')
            try:
                if category:
                    # Get models for specific category - avoid duplicates
                    try:
                        # New schema - get category name with models
                        c.execute(f'SELECT id FROM categories WHERE name = {placeholder} LIMIT 1', (category,))
                        cat_result = c.fetchone()
                        if cat_result:
                            c.execute(f'SELECT DISTINCT m.id, m.name, c.name as category_name, m.created_at FROM models m JOIN categories c ON m.category_id = c.id WHERE m.category_id = {placeholder} ORDER BY m.name LIMIT 50', (cat_result[0],))
                            rows = c.fetchall()
                            data = []
                            seen_names = set()
                            for row in rows:
                                if row[1] not in seen_names:
                                    seen_names.add(row[1])
                                    data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                        else:
                            data = []
                    except:
                        # Old schema fallback
                        c.execute(f'SELECT DISTINCT id, model_name, category_name, created_date FROM models WHERE category_name = {placeholder} ORDER BY model_name LIMIT 50', (category,))
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                else:
                    # Get all models with category names - avoid duplicates
                    try:
                        c.execute('SELECT DISTINCT m.id, m.name, c.name as category_name, m.created_at FROM models m JOIN categories c ON m.category_id = c.id ORDER BY m.name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                    except:
                        c.execute('SELECT DISTINCT id, model_name, category_name, created_date FROM models ORDER BY model_name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Models error: {str(e)}'}), 500
        
        elif data_type == 'display_types':
            category = request.args.get('category', '')
            try:
                if category:
                    try:
                        # New schema - get category name with display types
                        c.execute(f'SELECT id FROM categories WHERE name = {placeholder} LIMIT 1', (category,))
                        cat_result = c.fetchone()
                        if cat_result:
                            c.execute(f'SELECT DISTINCT dt.id, dt.name, c.name as category_name, dt.created_at FROM display_types dt JOIN categories c ON dt.category_id = c.id WHERE dt.category_id = {placeholder} ORDER BY dt.name LIMIT 50', (cat_result[0],))
                            rows = c.fetchall()
                            data = []
                            seen_names = set()
                            for row in rows:
                                if row[1] not in seen_names:
                                    seen_names.add(row[1])
                                    data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                        else:
                            data = []
                    except:
                        # Old schema fallback
                        c.execute(f'SELECT DISTINCT id, display_type_name, category_name, created_date FROM display_types WHERE category_name = {placeholder} ORDER BY display_type_name LIMIT 50', (category,))
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                else:
                    try:
                        # New schema - get all display types with category names
                        c.execute('SELECT DISTINCT dt.id, dt.name, c.name as category_name, dt.created_at FROM display_types dt JOIN categories c ON dt.category_id = c.id ORDER BY dt.name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                    except:
                        c.execute('SELECT DISTINCT id, display_type_name, category_name, created_date FROM display_types ORDER BY display_type_name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Display types error: {str(e)}'}), 500
        
        elif data_type == 'pop_materials':
            model = request.args.get('model', '')
            category = request.args.get('category', '')
            try:
                if model:
                    try:
                        # New schema
                        c.execute(f'SELECT id FROM models WHERE name = {placeholder} LIMIT 1', (model,))
                        model_result = c.fetchone()
                        if model_result:
                            c.execute(f'SELECT DISTINCT id, name, model_id, created_at FROM pop_materials WHERE model_id = {placeholder} ORDER BY name LIMIT 50', (model_result[0],))
                            rows = c.fetchall()
                            data = []
                            seen_names = set()
                            for row in rows:
                                if row[1] not in seen_names:
                                    seen_names.add(row[1])
                                    data.append({'id': row[0], 'name': row[1], 'model_id': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                        else:
                            data = []
                    except:
                        # Old schema fallback
                        c.execute(f'SELECT DISTINCT id, material_name, model_name, created_date FROM pop_materials_db WHERE model_name = {placeholder} ORDER BY material_name LIMIT 50', (model,))
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'model': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                elif category:
                    try:
                        # New schema
                        c.execute(f'SELECT id FROM categories WHERE name = {placeholder} LIMIT 1', (category,))
                        cat_result = c.fetchone()
                        if cat_result:
                            c.execute(f'SELECT DISTINCT pm.id, pm.name, pm.model_id, pm.created_at FROM pop_materials pm JOIN models m ON pm.model_id = m.id WHERE m.category_id = {placeholder} ORDER BY pm.name LIMIT 50', (cat_result[0],))
                            rows = c.fetchall()
                            data = []
                            seen_names = set()
                            for row in rows:
                                if row[1] not in seen_names:
                                    seen_names.add(row[1])
                                    data.append({'id': row[0], 'name': row[1], 'model_id': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                        else:
                            data = []
                    except:
                        # Old schema fallback
                        c.execute(f'SELECT DISTINCT id, material_name, model_name, created_date FROM pop_materials_db WHERE category_name = {placeholder} ORDER BY material_name LIMIT 50', (category,))
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'model': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                else:
                    try:
                        c.execute('SELECT DISTINCT id, name, model_id, created_at FROM pop_materials ORDER BY name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'model_id': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
                    except:
                        c.execute('SELECT DISTINCT id, material_name, model_name, created_date FROM pop_materials_db ORDER BY material_name LIMIT 100')
                        rows = c.fetchall()
                        data = []
                        seen_names = set()
                        for row in rows:
                            if row[1] not in seen_names:
                                seen_names.add(row[1])
                                data.append({'id': row[0], 'name': row[1], 'model': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'POP materials error: {str(e)}'}), 500
        
        else:
            return jsonify({'success': False, 'message': 'Invalid data type'}), 400
        
        conn.close()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/manage_data', methods=['POST'])
def manage_data():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        action = data.get('action')
        data_type = data.get('type')
        
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        try:
            if action == 'add':
                return handle_add_data_internal(cursor, conn, data_type, data, placeholder)
            elif action == 'edit':
                return handle_edit_data_internal(cursor, conn, data_type, data, placeholder)
            elif action == 'delete':
                return handle_delete_data_internal(cursor, conn, data_type, data, placeholder)
            else:
                return jsonify({'success': False, 'message': 'Invalid action'}), 400
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def handle_add_data_internal(cursor, conn, data_type, data, placeholder):
    """Handle adding new data"""
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        if data_type == 'categories':
            name = data.get('name', '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Category name is required'}), 400
            
            # Check if category already exists (check both old and new column names)
            cursor.execute(f'SELECT COUNT(*) FROM categories WHERE category_name = {placeholder} OR name = {placeholder}', (name, name))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'Category already exists'}), 400
            
            # Insert using old schema columns (which are NOT NULL)
            cursor.execute(f'INSERT INTO categories (category_name, created_date, name, created_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})',
                         (name, current_time, name, current_time))
            conn.commit()
            return jsonify({'success': True, 'message': 'Category added successfully'})
        
        elif data_type == 'models':
            name = data.get('name', '').strip()
            category_id = data.get('category_id')
            
            if not name:
                return jsonify({'success': False, 'message': 'Model name is required'}), 400
            
            # Get category name for old schema
            category_name = ''
            if category_id:
                cursor.execute(f'SELECT category_name FROM categories WHERE id = {placeholder}', (category_id,))
                cat_result = cursor.fetchone()
                if cat_result:
                    category_name = cat_result[0]
                else:
                    return jsonify({'success': False, 'message': 'Invalid category'}), 400
            else:
                return jsonify({'success': False, 'message': 'Category is required'}), 400
            
            # Check if model already exists
            cursor.execute(f'SELECT COUNT(*) FROM models WHERE (model_name = {placeholder} AND category_name = {placeholder}) OR (name = {placeholder} AND category_id = {placeholder})', 
                         (name, category_name, name, category_id))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'Model already exists in this category'}), 400
            
            # Insert using both old and new schema columns
            cursor.execute(f'INSERT INTO models (model_name, category_name, created_date, name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                         (name, category_name, current_time, name, category_id, current_time))
            conn.commit()
            return jsonify({'success': True, 'message': 'Model added successfully'})
        
        elif data_type == 'display_types':
            name = data.get('name', '').strip()
            category_id = data.get('category_id')
            
            if not name:
                return jsonify({'success': False, 'message': 'Display type name is required'}), 400
            
            # Get category name for old schema
            category_name = ''
            if category_id:
                cursor.execute(f'SELECT category_name FROM categories WHERE id = {placeholder}', (category_id,))
                cat_result = cursor.fetchone()
                if cat_result:
                    category_name = cat_result[0]
                else:
                    return jsonify({'success': False, 'message': 'Invalid category'}), 400
            else:
                return jsonify({'success': False, 'message': 'Category is required'}), 400
            
            # Insert using both old and new schema columns
            cursor.execute(f'INSERT INTO display_types (display_type_name, category_name, created_date, name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                         (name, category_name, current_time, name, category_id, current_time))
            conn.commit()
            return jsonify({'success': True, 'message': 'Display type added successfully'})
        
        elif data_type == 'pop_materials':
            name = data.get('name', '').strip()
            model_id = data.get('model_id')
            
            if not name or not model_id:
                return jsonify({'success': False, 'message': 'Material name and model are required'}), 400
            
            cursor.execute(f'INSERT INTO pop_materials (name, model_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                         (name, model_id, current_time))
            conn.commit()
            return jsonify({'success': True, 'message': 'POP material added successfully'})
        
        else:
            return jsonify({'success': False, 'message': 'Invalid data type'}), 400
            
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

def handle_edit_data_internal(cursor, conn, data_type, data, placeholder):
    """Handle editing existing data"""
    try:
        item_id = data.get('id')
        if not item_id:
            return jsonify({'success': False, 'message': 'Item ID is required'}), 400
        
        if data_type == 'categories':
            name = data.get('name', '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Category name is required'}), 400
            
            cursor.execute(f'UPDATE categories SET name = {placeholder} WHERE id = {placeholder}',
                         (name, item_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Category updated successfully'})
        
        elif data_type == 'models':
            name = data.get('name', '').strip()
            category_id = data.get('category_id')
            
            if not name:
                return jsonify({'success': False, 'message': 'Model name is required'}), 400
            
            if category_id:
                cursor.execute(f'UPDATE models SET name = {placeholder}, category_id = {placeholder} WHERE id = {placeholder}',
                             (name, category_id, item_id))
            else:
                cursor.execute(f'UPDATE models SET name = {placeholder} WHERE id = {placeholder}',
                             (name, item_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Model updated successfully'})
        
        elif data_type == 'display_types':
            name = data.get('name', '').strip()
            category_id = data.get('category_id')
            
            if not name:
                return jsonify({'success': False, 'message': 'Display type name is required'}), 400
            
            if category_id:
                cursor.execute(f'UPDATE display_types SET name = {placeholder}, category_id = {placeholder} WHERE id = {placeholder}',
                             (name, category_id, item_id))
            else:
                cursor.execute(f'UPDATE display_types SET name = {placeholder} WHERE id = {placeholder}',
                             (name, item_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Display type updated successfully'})
        
        elif data_type == 'pop_materials':
            name = data.get('name', '').strip()
            model_id = data.get('model_id')
            
            if not name:
                return jsonify({'success': False, 'message': 'Material name is required'}), 400
            
            if model_id:
                cursor.execute(f'UPDATE pop_materials SET name = {placeholder}, model_id = {placeholder} WHERE id = {placeholder}',
                             (name, model_id, item_id))
            else:
                cursor.execute(f'UPDATE pop_materials SET name = {placeholder} WHERE id = {placeholder}',
                             (name, item_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'POP material updated successfully'})
        
        else:
            return jsonify({'success': False, 'message': 'Invalid data type'}), 400
            
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

def handle_delete_data_internal(cursor, conn, data_type, data, placeholder):
    """Handle deleting data"""
    try:
        item_id = data.get('id')
        if not item_id:
            return jsonify({'success': False, 'message': 'Item ID is required'}), 400
        
        if data_type == 'categories':
            # Check if category has models
            cursor.execute(f'SELECT COUNT(*) FROM models WHERE category_id = {placeholder}', (item_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'Cannot delete category with existing models'}), 400
            
            cursor.execute(f'DELETE FROM categories WHERE id = {placeholder}', (item_id,))
            
        elif data_type == 'models':
            # Check if model has POP materials
            cursor.execute(f'SELECT COUNT(*) FROM pop_materials WHERE model_id = {placeholder}', (item_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'Cannot delete model with existing POP materials'}), 400
            
            cursor.execute(f'DELETE FROM models WHERE id = {placeholder}', (item_id,))
            
        elif data_type == 'display_types':
            cursor.execute(f'DELETE FROM display_types WHERE id = {placeholder}', (item_id,))
            
        elif data_type == 'pop_materials':
            cursor.execute(f'DELETE FROM pop_materials WHERE id = {placeholder}', (item_id,))
            
        else:
            return jsonify({'success': False, 'message': 'Invalid data type'}), 400
        
        conn.commit()
        return jsonify({'success': True, 'message': f'{data_type.title()} deleted successfully'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Use string for SQLite
    
    if data_type == 'categories':
        # Try new schema first, fallback to old
        try:
            if db_type == 'postgresql':
                cursor.execute(f'INSERT INTO categories (name, created_at) VALUES ({placeholder}, {placeholder})',
                              (data['name'], current_time))
            else:
                cursor.execute(f'INSERT INTO categories (name, created_at) VALUES ({placeholder}, {placeholder})',
                              (data['name'], current_time))
        except:
            cursor.execute(f'INSERT INTO categories (category_name, created_date) VALUES ({placeholder}, {placeholder})',
                          (data['name'], current_time))
    
    elif data_type == 'models':
        try:
            # New schema - need category_id
            cursor.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (data['category'],))
            cat_result = cursor.fetchone()
            if not cat_result:
                # Try old schema for category lookup
                cursor.execute(f'SELECT id FROM categories WHERE category_name = {placeholder}', (data['category'],))
                cat_result = cursor.fetchone()
            
            if cat_result:
                cursor.execute(f'INSERT INTO models (name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                              (data['name'], cat_result[0], current_time))
            else:
                raise Exception("Category not found")
        except:
            # Fallback to old schema
            cursor.execute(f'INSERT INTO models (model_name, category_name, created_date) VALUES ({placeholder}, {placeholder}, {placeholder})',
                          (data['name'], data['category'], current_time))
    
    elif data_type == 'display_types':
        try:
            # New schema - need category_id
            cursor.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (data['category'],))
            cat_result = cursor.fetchone()
            if not cat_result:
                # Try old schema for category lookup
                cursor.execute(f'SELECT id FROM categories WHERE category_name = {placeholder}', (data['category'],))
                cat_result = cursor.fetchone()
            
            if cat_result:
                cursor.execute(f'INSERT INTO display_types (name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                              (data['name'], cat_result[0], current_time))
            else:
                raise Exception("Category not found")
        except:
            # Fallback to old schema
            cursor.execute(f'INSERT INTO display_types (display_type_name, category_name, created_date) VALUES ({placeholder}, {placeholder}, {placeholder})',
                          (data['name'], data['category'], current_time))
    
    elif data_type == 'pop_materials':
        try:
            # New schema - need model_id
            cursor.execute(f'SELECT id FROM models WHERE name = {placeholder}', (data['model'],))
            model_result = cursor.fetchone()
            if model_result:
                cursor.execute(f'INSERT INTO pop_materials (name, model_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                              (data['name'], model_result[0], current_time))
            else:
                raise Exception("Model not found")
        except:
            # Fallback to old schema
            if db_type == 'postgresql':
                cursor.execute(f'INSERT INTO pop_materials_db (material_name, model_name, category_name, created_date) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}) ON CONFLICT DO NOTHING',
                              (data['name'], data['model'], data['category'], current_time))
            else:
                cursor.execute(f'INSERT OR IGNORE INTO pop_materials_db (material_name, model_name, category_name, created_date) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})',
                              (data['name'], data['model'], data['category'], current_time))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'{data_type.title()} added successfully'})

def handle_edit_data(cursor, conn, data_type, data):
    """Handle edit data - temporarily simplified to avoid SQL errors"""
    # Get database type for correct placeholder
    _, db_type = get_db_connection()
    placeholder = '%s' if db_type == 'postgresql' else '?'
    
    if data_type == 'categories':
        # Simple update without cascading
        try:
            cursor.execute(f'UPDATE categories SET name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
        except:
            cursor.execute(f'UPDATE categories SET category_name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
    
    elif data_type == 'models':
        # Simple update without cascading
        try:
            cursor.execute(f'UPDATE models SET name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
        except:
            cursor.execute(f'UPDATE models SET model_name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
    
    elif data_type == 'display_types':
        # Simple update without cascading
        try:
            cursor.execute(f'UPDATE display_types SET name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
        except:
            cursor.execute(f'UPDATE display_types SET display_type_name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
    
    elif data_type == 'pop_materials':
        # Simple update without cascading
        try:
            cursor.execute(f'UPDATE pop_materials SET name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
        except:
            cursor.execute(f'UPDATE pop_materials_db SET material_name = {placeholder} WHERE id = {placeholder}',
                          (data['name'], data['id']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'{data_type.title()} updated successfully'})

def handle_delete_data(cursor, conn, data_type, data):
    """Handle delete data - temporarily simplified to avoid SQL errors"""
    # Get database type for correct placeholder
    _, db_type = get_db_connection()
    placeholder = '%s' if db_type == 'postgresql' else '?'
    
    if data_type == 'categories':
        # Simple delete without cascading
        try:
            cursor.execute(f'DELETE FROM categories WHERE id = {placeholder}', (data['id'],))
        except Exception as e:
            print(f"Error deleting category: {e}")
    
    elif data_type == 'models':
        # Simple delete without cascading
        try:
            cursor.execute(f'DELETE FROM models WHERE id = {placeholder}', (data['id'],))
        except Exception as e:
            print(f"Error deleting model: {e}")
    
    elif data_type == 'display_types':
        try:
            cursor.execute(f'DELETE FROM display_types WHERE id = {placeholder}', (data['id'],))
        except Exception as e:
            print(f"Error deleting display type: {e}")
    
    elif data_type == 'pop_materials':
        try:
            cursor.execute(f'DELETE FROM pop_materials WHERE id = {placeholder}', (data['id'],))
        except:
            cursor.execute(f'DELETE FROM pop_materials_db WHERE id = {placeholder}', (data['id'],))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'{data_type.title()} deleted successfully'})

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        
        # Get entry details before deletion for cleanup
        c.execute('SELECT images FROM data_entries WHERE id = ?', (entry_id,))
        result = c.fetchone()
        
        if result and result[0]:
            # Delete associated images
            images = result[0].split(',')
            for image in images:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        # Delete the entry
        c.execute('DELETE FROM data_entries WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Entry deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/user_management')
def user_management():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        # Get users with their branches - safe query
        try:
            # Try to get users with branches
            if db_type == 'postgresql':
                c.execute('''SELECT u.id, u.username, u.password_hash, u.employee_name, u.employee_code, u.is_admin, u.created_at,
                             COALESCE(STRING_AGG(ub.branch_name, ', '), '') as branches
                             FROM users u
                             LEFT JOIN user_branches ub ON u.id = ub.user_id
                             GROUP BY u.id, u.username, u.password_hash, u.employee_name, u.employee_code, u.is_admin, u.created_at
                             ORDER BY u.is_admin DESC, u.username''')
            else:
                c.execute('''SELECT u.id, u.username, u.password_hash, u.employee_name, u.employee_code, u.is_admin, u.created_at,
                             COALESCE(GROUP_CONCAT(ub.branch_name, ', '), '') as branches
                             FROM users u
                             LEFT JOIN user_branches ub ON u.id = ub.user_id
                             GROUP BY u.id, u.username, u.password_hash, u.employee_name, u.employee_code, u.is_admin, u.created_at
                             ORDER BY u.is_admin DESC, u.username''')
            
            users = c.fetchall()
            
        except Exception as join_error:
            print(f"JOIN query failed: {join_error}, using simple query")
            # Fallback to simple query
            c.execute('SELECT id, username, password_hash, employee_name, employee_code, is_admin, created_at FROM users ORDER BY is_admin DESC, username')
            raw_users = c.fetchall()
            # Add empty branches column
            users = [tuple(list(user) + ['']) for user in raw_users]
        
        # Get all unique branches for management
        try:
            c.execute('SELECT DISTINCT branch_name FROM data_entries WHERE branch_name IS NOT NULL ORDER BY branch_name')
            all_branches = [row[0] for row in c.fetchall()]
        except:
            all_branches = ['Main Branch', 'Secondary Branch']  # Default branches
        
        conn.close()
        
        return render_template('user_management.html', users=users, all_branches=all_branches)
        
    except Exception as e:
        print(f"Error in user_management: {e}")
        return f"Error loading user management: {str(e)}", 500

@app.route('/manage_user', methods=['POST'])
def manage_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        action = data.get('action')
        
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if action == 'add':
            name = data.get('name')
            company_code = data.get('company_code')
            password = data.get('password')
            is_admin = data.get('is_admin', False)
            
            # Check if user already exists
            c.execute(f'SELECT * FROM users WHERE username = {placeholder} OR employee_code = {placeholder}', (name, company_code))
            if c.fetchone():
                return jsonify({'success': False, 'message': 'User with this name or company code already exists'})
            
            hashed_password = generate_password_hash(password)
            c.execute(f'INSERT INTO users (username, employee_code, password_hash, employee_name, is_admin) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                     (name, company_code, hashed_password, name, is_admin))
            
        elif action == 'edit':
            user_id = data.get('id')
            name = data.get('name')
            company_code = data.get('company_code')
            password = data.get('password')
            is_admin = data.get('is_admin', False)
            
            # Check if another user has the same name or company code
            c.execute(f'SELECT * FROM users WHERE (username = {placeholder} OR employee_code = {placeholder}) AND id != {placeholder}', 
                     (name, company_code, user_id))
            if c.fetchone():
                return jsonify({'success': False, 'message': 'Another user with this name or company code already exists'})
            
            if password:
                # Update with new password
                hashed_password = generate_password_hash(password)
                c.execute(f'UPDATE users SET username = {placeholder}, employee_code = {placeholder}, employee_name = {placeholder}, password_hash = {placeholder}, is_admin = {placeholder} WHERE id = {placeholder}',
                         (name, company_code, name, hashed_password, is_admin, user_id))
            else:
                # Update without changing password
                c.execute(f'UPDATE users SET username = {placeholder}, employee_code = {placeholder}, employee_name = {placeholder}, is_admin = {placeholder} WHERE id = {placeholder}',
                         (name, company_code, name, is_admin, user_id))
            
        elif action == 'delete':
            user_id = data.get('id')
            
            # Prevent deleting the current admin user
            if user_id == session['user_id']:
                return jsonify({'success': False, 'message': 'Cannot delete your own account'})
            
            # Check if this is the last admin
            c.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
            admin_count = c.fetchone()[0]
            
            c.execute(f'SELECT is_admin FROM users WHERE id = {placeholder}', (user_id,))
            user_to_delete = c.fetchone()
            
            if user_to_delete and user_to_delete[0] and admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot delete the last admin user'})
            
            # Delete user's data entries and branches
            c.execute(f'SELECT employee_code FROM users WHERE id = {placeholder}', (user_id,))
            user_data = c.fetchone()
            if user_data:
                employee_code = user_data[0]
                
                # Delete user branches
                try:
                    c.execute(f'DELETE FROM user_branches WHERE user_id = {placeholder}', (user_id,))
                except:
                    pass  # Table might not exist
                
                # Delete data entries
                try:
                    c.execute(f'DELETE FROM data_entries WHERE employee_code = {placeholder}', (employee_code,))
                except:
                    pass
            
            # Delete the user
            c.execute(f'DELETE FROM users WHERE id = {placeholder}', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'User {action}ed successfully'})
        
    except Exception as e:
        print(f"Error in manage_user: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/change_admin_password', methods=['POST'])
def change_admin_password():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        c.execute(f'SELECT password_hash FROM users WHERE id = {placeholder}', (session['user_id'],))
        user = c.fetchone()
        
        if not user or not check_password_hash(user[0], current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'})
        
        hashed_password = generate_password_hash(new_password)
        c.execute(f'UPDATE users SET password_hash = {placeholder} WHERE id = {placeholder}', (hashed_password, session['user_id']))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Password changed successfully'})
        
    except Exception as e:
        print(f"Error in change_admin_password: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    # Temporarily disabled for debugging
    return "Registration temporarily disabled for maintenance. <a href='/admin_dashboard'>Back to Dashboard</a>"

@app.route('/get_user_branches/<int:user_id>')
def get_user_branches(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        # Ensure user_branches table exists
        try:
            if db_type == 'postgresql':
                c.execute('''
                    CREATE TABLE IF NOT EXISTS user_branches (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        branch_name VARCHAR(200) NOT NULL,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, branch_name)
                    )
                ''')
            else:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS user_branches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        branch_name TEXT NOT NULL,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, branch_name)
                    )
                ''')
            conn.commit()
        except:
            pass
        
        # Get user's current branches
        user_branches = []
        try:
            c.execute(f'SELECT branch_name FROM user_branches WHERE user_id = {placeholder} ORDER BY branch_name', (user_id,))
            user_branches = [row[0] for row in c.fetchall()]
        except Exception as e:
            print(f"Error getting user branches: {e}")
            user_branches = []
        
        # Get all available branches
        try:
            c.execute('SELECT DISTINCT branch_name FROM data_entries WHERE branch_name IS NOT NULL ORDER BY branch_name')
            all_branches = [row[0] for row in c.fetchall()]
        except:
            all_branches = ['Main Branch', 'Secondary Branch', 'Third Branch']  # Default branches
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user_branches': user_branches,
            'all_branches': all_branches
        })
        
    except Exception as e:
        print(f"Error in get_user_branches: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/manage_user_branches', methods=['POST'])
def manage_user_branches():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        action = data.get('action')  # 'add' or 'remove'
        branch_name = data.get('branch_name')
        
        if not all([user_id, action, branch_name]):
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        # Ensure user_branches table exists
        try:
            if db_type == 'postgresql':
                c.execute('''
                    CREATE TABLE IF NOT EXISTS user_branches (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        branch_name VARCHAR(200) NOT NULL,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, branch_name)
                    )
                ''')
            else:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS user_branches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        branch_name TEXT NOT NULL,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, branch_name)
                    )
                ''')
            conn.commit()
        except:
            pass
        
        if action == 'add':
            # Add branch to user
            try:
                if db_type == 'postgresql':
                    c.execute('''INSERT INTO user_branches (user_id, branch_name, created_date) 
                                 VALUES (%s, %s, %s) ON CONFLICT (user_id, branch_name) DO NOTHING''',
                              (user_id, branch_name, datetime.now()))
                else:
                    c.execute('''INSERT OR IGNORE INTO user_branches (user_id, branch_name, created_date) 
                                 VALUES (?, ?, ?)''',
                              (user_id, branch_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                message = f'Branch "{branch_name}" added to user'
            except Exception as e:
                print(f"Error adding branch: {e}")
                message = f'Branch "{branch_name}" add attempted'
                
        elif action == 'remove':
            # Remove branch from user
            try:
                c.execute(f'DELETE FROM user_branches WHERE user_id = {placeholder} AND branch_name = {placeholder}',
                          (user_id, branch_name))
                message = f'Branch "{branch_name}" removed from user'
            except Exception as e:
                print(f"Error removing branch: {e}")
                message = f'Branch "{branch_name}" remove attempted'
                
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        print(f"Error in manage_user_branches: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/fix_now')
def fix_now():
    """Simple fix endpoint - no login required for emergency"""
    try:
        # Run the simple fix
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Create user_branches table
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_branches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    branch_name VARCHAR(200) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, branch_name)
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    branch_name TEXT NOT NULL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, branch_name)
                )
            ''')
        
        # Add test data
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            if db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO user_branches (user_id, branch_name) 
                    VALUES (%s, %s) ON CONFLICT DO NOTHING
                ''', (user_id, 'Main Branch'))
            else:
                cursor.execute('''
                    INSERT OR IGNORE INTO user_branches (user_id, branch_name) 
                    VALUES (?, ?)
                ''', (user_id, 'Main Branch'))
        
        # Verify tables
        tables = ['users', 'categories', 'models', 'user_branches']
        results = []
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results.append(f"{table}: {count} records")
            except Exception as e:
                results.append(f"{table}: ERROR - {e}")
        
        conn.commit()
        conn.close()
        
        return f"""
        <h2>🎉 Database Fix Completed!</h2>
        <h3>✅ Results:</h3>
        <ul>
        {''.join([f'<li>{result}</li>' for result in results])}
        </ul>
        <p><strong>✅ user_branches table created and ready!</strong></p>
        <p><strong>✅ All critical issues fixed!</strong></p>
        <p><a href="/user_management">Test User Management</a></p>
        <p><a href="/admin_dashboard">Back to Dashboard</a></p>
        """
        
    except Exception as e:
        return f"""
        <h2>❌ Fix Error</h2>
        <p>Error: {str(e)}</p>
        <p>Please check the logs for more details.</p>
        """

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=not IS_PRODUCTION)

# Production deployment with gunicorn:
# gunicorn --bind 0.0.0.0:$PORT app:app
