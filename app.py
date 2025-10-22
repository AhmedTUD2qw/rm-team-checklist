from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

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

# Production database initialization will be done after function definitions

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
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            employee_name VARCHAR(100) NOT NULL,
            employee_code VARCHAR(50) UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            employee_code TEXT UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
    
    # Categories table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
    
    # Models table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
    
    # Display types table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS display_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS display_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
    
    # POP materials table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS pop_materials (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            model_id INTEGER REFERENCES models(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS pop_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )''')
    
    # Data entries table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS data_entries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            employee_name VARCHAR(100) NOT NULL,
            employee_code VARCHAR(50) NOT NULL,
            branch_name VARCHAR(200) NOT NULL,
            shop_code VARCHAR(50),
            category VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            display_type VARCHAR(100) NOT NULL,
            selected_materials TEXT,
            missing_materials TEXT,
            image_urls TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS data_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            employee_name TEXT NOT NULL,
            employee_code TEXT NOT NULL,
            branch_name TEXT NOT NULL,
            shop_code TEXT,
            category TEXT NOT NULL,
            model TEXT NOT NULL,
            display_type TEXT NOT NULL,
            selected_materials TEXT,
            missing_materials TEXT,
            image_urls TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
    
    # Branches table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS branches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
    
    # User branches table
    if db_type == 'postgresql':
        c.execute('''CREATE TABLE IF NOT EXISTS user_branches (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            branch_name VARCHAR(200) NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, branch_name)
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS user_branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, branch_name)
        )''')
    
    conn.commit()
    
    # Initialize default data
    initialize_default_data(c, conn, db_type)
    
    conn.close()

def initialize_default_data(cursor, conn, db_type):
    """Initialize default data"""
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    placeholder = '%s' if db_type == 'postgresql' else '?'
    
    # Check if admin user exists
    if db_type == 'postgresql':
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = true')
    else:
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        print("🔧 Creating admin user...")
        admin_password = generate_password_hash('admin123')
        cursor.execute(f'INSERT INTO users (username, password_hash, employee_name, employee_code, is_admin) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                     ('admin', admin_password, 'System Administrator', 'ADMIN001', True))
        print("✅ Admin user created (admin/admin123)")
    
    # Initialize categories
    categories = [
        'OLED', 'Neo QLED', 'QLED', 'UHD', 'LTV',
        'BESPOKE COMBO', 'BESPOKE Front', 'Front', 'TL', 'SBS', 'TMF', 'BMF', 'Local TMF'
    ]
    
    for category in categories:
        if db_type == 'postgresql':
            cursor.execute(f'INSERT INTO categories (name, created_at) VALUES ({placeholder}, {placeholder}) ON CONFLICT (name) DO NOTHING',
                          (category, current_time))
        else:
            cursor.execute(f'INSERT OR IGNORE INTO categories (name, created_at) VALUES ({placeholder}, {placeholder})',
                          (category, current_time))
    
    conn.commit()

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        name = request.form['name']
        company_code = request.form['company_code']
        password = request.form['password']
        remember_me = 'remember_me' in request.form
        
        user = execute_query('SELECT * FROM users WHERE username = ? AND employee_code = ?', 
                            (name, company_code), fetch_one=True)
        
        if user and check_password_hash(user[2], password):  # user[2] is password_hash
            session['user_id'] = user[0]
            session['user_name'] = user[1]  # username
            session['employee_name'] = user[3]  # employee_name
            session['company_code'] = user[4]  # employee_code
            session['is_admin'] = user[5]  # is_admin
            session.permanent = remember_me
            
            if user[5]:  # is_admin
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('data_entry'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Login error: {e}")
        flash('Login error occurred. Please try again.')
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

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        # Get basic data for dashboard
        conn, db_type = get_db_connection()
        c = conn.cursor()
        
        # Get all data entries
        c.execute('SELECT * FROM data_entries ORDER BY created_at DESC LIMIT 100')
        data_entries = c.fetchall()
        
        # Get unique values for filters
        employees = list(set([entry[1] for entry in data_entries if entry[1]]))  # employee_name
        branches = list(set([entry[3] for entry in data_entries if entry[3]]))   # branch_name
        models = list(set([entry[6] for entry in data_entries if entry[6]]))     # model
        
        conn.close()
        
        # Create filters object
        filters = {
            'employee': '',
            'branch': '',
            'model': '',
            'date_from': '',
            'date_to': ''
        }
        
        return render_template('admin_dashboard.html', 
                             data_entries=data_entries,
                             employees=employees,
                             branches=branches,
                             models=models,
                             filters=filters)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        # Return simple dashboard without data
        return render_template('admin_dashboard.html', 
                             data_entries=[],
                             employees=[],
                             branches=[],
                             models=[],
                             filters={'employee': '', 'branch': '', 'model': '', 'date_from': '', 'date_to': ''})

@app.route('/admin_management')
def admin_management():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('admin_management.html')

# Data loading routes
@app.route('/get_dynamic_data/<data_type>')
def get_dynamic_data(data_type):
    """Get dynamic data from database for frontend"""
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if data_type == 'categories':
            c.execute('SELECT name FROM categories ORDER BY name')
            data = [row[0] for row in c.fetchall()]
        
        elif data_type == 'models':
            category = request.args.get('category', '')
            if category:
                # Get category ID first
                c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                cat_result = c.fetchone()
                if cat_result:
                    c.execute(f'SELECT name FROM models WHERE category_id = {placeholder} ORDER BY name', (cat_result[0],))
                    data = [row[0] for row in c.fetchall()]
                else:
                    data = []
            else:
                c.execute('SELECT name FROM models ORDER BY name')
                data = [row[0] for row in c.fetchall()]
        
        elif data_type == 'display_types':
            category = request.args.get('category', '')
            if category:
                # Get category ID first
                c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                cat_result = c.fetchone()
                if cat_result:
                    c.execute(f'SELECT name FROM display_types WHERE category_id = {placeholder} ORDER BY name', (cat_result[0],))
                    data = [row[0] for row in c.fetchall()]
                else:
                    data = []
            else:
                data = []
        
        elif data_type == 'pop_materials':
            model = request.args.get('model', '')
            if model:
                # Get model ID first
                c.execute(f'SELECT id FROM models WHERE name = {placeholder}', (model,))
                model_result = c.fetchone()
                if model_result:
                    c.execute(f'SELECT name FROM pop_materials WHERE model_id = {placeholder} ORDER BY name', (model_result[0],))
                    data = [row[0] for row in c.fetchall()]
                else:
                    data = []
            else:
                data = []
        
        conn.close()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        print(f"Error in get_dynamic_data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin management routes
@app.route('/get_management_data/<data_type>')
def get_management_data(data_type):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn, db_type = get_db_connection()
        c = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        if data_type == 'categories':
            c.execute('SELECT id, name, created_at FROM categories ORDER BY name')
            rows = c.fetchall()
            data = [{'id': row[0], 'name': row[1], 'created_at': str(row[2]) if row[2] else 'N/A'} for row in rows]
        
        elif data_type == 'models':
            category = request.args.get('category', '')
            if category:
                c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                cat_result = c.fetchone()
                if cat_result:
                    c.execute(f'SELECT m.id, m.name, c.name as category_name, m.created_at FROM models m JOIN categories c ON m.category_id = c.id WHERE m.category_id = {placeholder} ORDER BY m.name', (cat_result[0],))
                    rows = c.fetchall()
                    data = [{'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
                else:
                    data = []
            else:
                c.execute('SELECT m.id, m.name, c.name as category_name, m.created_at FROM models m JOIN categories c ON m.category_id = c.id ORDER BY m.name')
                rows = c.fetchall()
                data = [{'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
        
        elif data_type == 'display_types':
            category = request.args.get('category', '')
            if category:
                c.execute(f'SELECT id FROM categories WHERE name = {placeholder}', (category,))
                cat_result = c.fetchone()
                if cat_result:
                    c.execute(f'SELECT dt.id, dt.name, c.name as category_name, dt.created_at FROM display_types dt JOIN categories c ON dt.category_id = c.id WHERE dt.category_id = {placeholder} ORDER BY dt.name', (cat_result[0],))
                    rows = c.fetchall()
                    data = [{'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
                else:
                    data = []
            else:
                c.execute('SELECT dt.id, dt.name, c.name as category_name, dt.created_at FROM display_types dt JOIN categories c ON dt.category_id = c.id ORDER BY dt.name')
                rows = c.fetchall()
                data = [{'id': row[0], 'name': row[1], 'category': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
        
        elif data_type == 'pop_materials':
            model = request.args.get('model', '')
            if model:
                c.execute(f'SELECT id FROM models WHERE name = {placeholder}', (model,))
                model_result = c.fetchone()
                if model_result:
                    c.execute(f'SELECT pm.id, pm.name, m.name as model_name, pm.created_at FROM pop_materials pm JOIN models m ON pm.model_id = m.id WHERE pm.model_id = {placeholder} ORDER BY pm.name', (model_result[0],))
                    rows = c.fetchall()
                    data = [{'id': row[0], 'name': row[1], 'model': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
                else:
                    data = []
            else:
                c.execute('SELECT pm.id, pm.name, m.name as model_name, pm.created_at FROM pop_materials pm JOIN models m ON pm.model_id = m.id ORDER BY pm.name')
                rows = c.fetchall()
                data = [{'id': row[0], 'name': row[1], 'model': row[2], 'created_at': str(row[3]) if row[3] else 'N/A'} for row in rows]
        
        conn.close()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        print(f"Error in get_management_data: {e}")
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
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            if action == 'add':
                if data_type == 'categories':
                    name = data.get('name', '').strip()
                    if not name:
                        return jsonify({'success': False, 'message': 'Category name is required'}), 400
                    
                    cursor.execute(f'SELECT COUNT(*) FROM categories WHERE name = {placeholder}', (name,))
                    if cursor.fetchone()[0] > 0:
                        return jsonify({'success': False, 'message': 'Category already exists'}), 400
                    
                    cursor.execute(f'INSERT INTO categories (name, created_at) VALUES ({placeholder}, {placeholder})',
                                 (name, current_time))
                    conn.commit()
                    return jsonify({'success': True, 'message': 'Category added successfully'})
                
                elif data_type == 'models':
                    name = data.get('name', '').strip()
                    category_id = data.get('category_id')
                    
                    if not name or not category_id:
                        return jsonify({'success': False, 'message': 'Model name and category are required'}), 400
                    
                    cursor.execute(f'SELECT COUNT(*) FROM models WHERE name = {placeholder} AND category_id = {placeholder}', 
                                 (name, category_id))
                    if cursor.fetchone()[0] > 0:
                        return jsonify({'success': False, 'message': 'Model already exists in this category'}), 400
                    
                    cursor.execute(f'INSERT INTO models (name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                                 (name, category_id, current_time))
                    conn.commit()
                    return jsonify({'success': True, 'message': 'Model added successfully'})
                
                elif data_type == 'display_types':
                    name = data.get('name', '').strip()
                    category_id = data.get('category_id')
                    
                    if not name or not category_id:
                        return jsonify({'success': False, 'message': 'Display type name and category are required'}), 400
                    
                    cursor.execute(f'INSERT INTO display_types (name, category_id, created_at) VALUES ({placeholder}, {placeholder}, {placeholder})',
                                 (name, category_id, current_time))
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
            
            elif action == 'edit':
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
            
            elif action == 'delete':
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
            
            else:
                return jsonify({'success': False, 'message': 'Invalid action'}), 400
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in manage_data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/export_excel')
def export_excel():
    """Export data to Excel with images"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    
    try:
        # Simple Excel export for now
        conn, db_type = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM data_entries ORDER BY created_at DESC')
        data = c.fetchall()
        conn.close()
        
        # Create simple Excel file
        import pandas as pd
        from io import BytesIO
        
        df = pd.DataFrame(data, columns=[
            'ID', 'User ID', 'Employee Name', 'Employee Code', 'Branch Name', 
            'Shop Code', 'Category', 'Model', 'Display Type', 'Selected Materials', 
            'Missing Materials', 'Image URLs', 'Created At'
        ])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data Entries', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'data_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        flash(f'Export error: {str(e)}')
        return redirect(url_for('admin_dashboard'))

@app.route('/export_excel_simple')
def export_excel_simple():
    """Simple Excel export"""
    return redirect(url_for('export_excel'))

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete data entry"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'DELETE FROM data_entries WHERE id = {placeholder}', (entry_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Entry deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/download_image/<filename>')
def download_image(filename):
    """Download image file"""
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Initialize production database after all functions are defined
if IS_PRODUCTION:
    try:
        print("🔧 Initializing production database...")
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        if db_type == 'postgresql':
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                employee_name VARCHAR(100) NOT NULL,
                employee_code VARCHAR(50) UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
        
        conn.commit()
        conn.close()
        print("✅ Production database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)