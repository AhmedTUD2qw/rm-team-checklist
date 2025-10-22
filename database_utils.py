import sqlite3
from contextlib import contextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_cursor():
    """Database connection context manager"""
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def update_category(id, new_name):
    """Update category with proper cascading updates"""
    try:
        with get_db_cursor() as cursor:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Update category
            cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (new_name, id)
            )
            
            if cursor.rowcount == 0:
                raise ValueError(f"Category with ID {id} not found")
            
            # Update related models
            cursor.execute(
                "UPDATE models SET category_name = ? WHERE category_id = ?",
                (new_name, id)
            )
            logger.info(f"Updated {cursor.rowcount} model records")
            
            # Update related display types
            cursor.execute(
                "UPDATE display_types SET category_name = ? WHERE category_id = ?",
                (new_name, id)
            )
            logger.info(f"Updated {cursor.rowcount} display type records")
            
            cursor.execute("COMMIT")
            return True
            
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        return False

def update_model(id, name, category_id):
    """Update model with proper category relationship"""
    try:
        with get_db_cursor() as cursor:
            # Get category name
            cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Category with ID {category_id} not found")
            
            category_name = result[0]
            
            # Update model
            cursor.execute(
                """UPDATE models 
                   SET name = ?, category_id = ?, category_name = ? 
                   WHERE id = ?""",
                (name, category_id, category_name, id)
            )
            
            if cursor.rowcount == 0:
                raise ValueError(f"Model with ID {id} not found")
                
            return True
            
    except Exception as e:
        logger.error(f"Error updating model: {str(e)}")
        return False

def update_display_type(id, name, category_id):
    """Update display type with proper category relationship"""
    try:
        with get_db_cursor() as cursor:
            # Get category name
            cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Category with ID {category_id} not found")
            
            category_name = result[0]
            
            # Update display type
            cursor.execute(
                """UPDATE display_types 
                   SET name = ?, category_id = ?, category_name = ? 
                   WHERE id = ?""",
                (name, category_id, category_name, id)
            )
            
            if cursor.rowcount == 0:
                raise ValueError(f"Display type with ID {id} not found")
                
            return True
            
    except Exception as e:
        logger.error(f"Error updating display type: {str(e)}")
        return False