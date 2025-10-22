import sqlite3
from contextlib import contextmanager
import logging
from datetime import datetime

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

def update_category_relationships(cursor, category_id, new_name):
    """Update category relationships in all tables"""
    # Update models
    cursor.execute("""
        UPDATE models 
        SET category_name = ? 
        WHERE category_id = ?
    """, (new_name, category_id))
    logger.info(f"Updated {cursor.rowcount} models for category {category_id}")

    # Update display types
    cursor.execute("""
        UPDATE display_types 
        SET category_name = ? 
        WHERE category_id = ?
    """, (new_name, category_id))
    logger.info(f"Updated {cursor.rowcount} display types for category {category_id}")

def update_category(category_id, new_name):
    """Update category with proper cascading updates"""
    try:
        with get_db_cursor() as cursor:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Update category
            cursor.execute("""
                UPDATE categories 
                SET name = ?,
                    category_name = ?  -- Update both columns for compatibility
                WHERE id = ?
            """, (new_name, new_name, category_id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Category with ID {category_id} not found")
            
            # Update relationships
            update_category_relationships(cursor, category_id, new_name)
            
            cursor.execute("COMMIT")
            logger.info(f"Successfully updated category {category_id} to {new_name}")
            return True
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        return False

def update_model(model_id, name, category_id):
    """Update model with proper category relationship"""
    try:
        with get_db_cursor() as cursor:
            # Get category name
            cursor.execute("SELECT name, category_name FROM categories WHERE id = ?", (category_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Category with ID {category_id} not found")
            
            category_name = result[0] or result[1]  # Use new or old column
            
            # Update model
            cursor.execute("""
                UPDATE models 
                SET name = ?,
                    model_name = ?,  -- Update both columns for compatibility
                    category_id = ?,
                    category_name = ?
                WHERE id = ?
            """, (name, name, category_id, category_name, model_id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Model with ID {model_id} not found")
            
            logger.info(f"Successfully updated model {model_id} to {name}")
            return True
    except Exception as e:
        logger.error(f"Error updating model: {str(e)}")
        return False

def update_display_type(display_type_id, name, category_id):
    """Update display type with proper category relationship"""
    try:
        with get_db_cursor() as cursor:
            # Get category name
            cursor.execute("SELECT name, category_name FROM categories WHERE id = ?", (category_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Category with ID {category_id} not found")
            
            category_name = result[0] or result[1]  # Use new or old column
            
            # Update display type
            cursor.execute("""
                UPDATE display_types 
                SET name = ?,
                    display_type_name = ?,  -- Update both columns for compatibility
                    category_id = ?,
                    category_name = ?
                WHERE id = ?
            """, (name, name, category_id, category_name, display_type_id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Display type with ID {display_type_id} not found")
            
            logger.info(f"Successfully updated display type {display_type_id} to {name}")
            return True
    except Exception as e:
        logger.error(f"Error updating display type: {str(e)}")
        return False

def fix_missing_relationships():
    """Fix any missing category relationships"""
    try:
        with get_db_cursor() as cursor:
            # Fix models relationships
            cursor.execute("""
                UPDATE models 
                SET category_id = (
                    SELECT id FROM categories 
                    WHERE categories.name = models.category_name 
                       OR categories.category_name = models.category_name 
                    LIMIT 1
                )
                WHERE category_id IS NULL
            """)
            logger.info(f"Fixed {cursor.rowcount} model relationships")
            
            # Fix display types relationships
            cursor.execute("""
                UPDATE display_types 
                SET category_id = (
                    SELECT id FROM categories 
                    WHERE categories.name = display_types.category_name 
                       OR categories.category_name = display_types.category_name 
                    LIMIT 1
                )
                WHERE category_id IS NULL
            """)
            logger.info(f"Fixed {cursor.rowcount} display type relationships")
            
            return True
    except Exception as e:
        logger.error(f"Error fixing relationships: {str(e)}")
        return False