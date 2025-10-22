import sqlite3
import os

def clean_duplicate_data():
    """Clean up duplicate and inconsistent data"""
    print("🧹 Cleaning up duplicate and inconsistent data...")
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Clean categories
        print("\n📋 Cleaning categories...")
        cursor.execute("""
            DELETE FROM categories 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM categories 
                GROUP BY name
            )
        """)
        print(f"✅ Removed {cursor.rowcount} duplicate categories")
        
        # Clean models
        print("\n📋 Cleaning models...")
        cursor.execute("""
            DELETE FROM models 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM models 
                GROUP BY name, category_id
            )
        """)
        print(f"✅ Removed {cursor.rowcount} duplicate models")
        
        # Clean display types
        print("\n📋 Cleaning display types...")
        cursor.execute("""
            DELETE FROM display_types 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM display_types 
                GROUP BY name, category_id
            )
        """)
        print(f"✅ Removed {cursor.rowcount} duplicate display types")
        
        # Update missing category IDs
        print("\n📋 Updating missing category relationships...")
        
        # For models
        cursor.execute("""
            UPDATE models 
            SET category_id = (
                SELECT id FROM categories 
                WHERE categories.name = models.category_name 
                LIMIT 1
            )
            WHERE category_id IS NULL
        """)
        print(f"✅ Updated {cursor.rowcount} model category relationships")
        
        # For display types
        cursor.execute("""
            UPDATE display_types 
            SET category_id = (
                SELECT id FROM categories 
                WHERE categories.name = display_types.category_name 
                LIMIT 1
            )
            WHERE category_id IS NULL
        """)
        print(f"✅ Updated {cursor.rowcount} display type category relationships")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database cleanup complete!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_duplicate_data()