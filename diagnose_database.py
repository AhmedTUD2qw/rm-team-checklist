#!/usr/bin/env python3
"""
Diagnose current database state to identify issues
"""

from database_config import get_database_connection

def diagnose_database():
    """Check current database state"""
    print("🔍 Diagnosing database state...")
    
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_type} database")
        
        # Check categories
        print("\n📊 Categories:")
        try:
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
        except:
            # Try old column names
            cursor.execute("PRAGMA table_info(categories)")
            columns = cursor.fetchall()
            print(f"  Categories table columns: {[col[1] for col in columns]}")
            
            # Try with old column name
            cursor.execute("SELECT * FROM categories ORDER BY category_name")
            categories = cursor.fetchall()
            print(f"  Found {len(categories)} categories with old schema")
            categories = [(cat[0], cat[1]) for cat in categories]  # id, category_name
        
        for cat in categories:
            print(f"  - {cat[0]}: {cat[1]}")
        
        # Check models
        print(f"\n📊 Models (Total: {len(categories)} categories):")
        for cat_id, cat_name in categories:
            try:
                cursor.execute("SELECT id, name FROM models WHERE category_id = %s" if db_type == 'postgresql' else "SELECT id, name FROM models WHERE category_id = ?", (cat_id,))
                models = cursor.fetchall()
            except:
                # Try old schema
                cursor.execute("SELECT id, model_name FROM models WHERE category_name = %s" if db_type == 'postgresql' else "SELECT id, model_name FROM models WHERE category_name = ?", (cat_name,))
                models = cursor.fetchall()
            
            print(f"  {cat_name} ({len(models)} models):")
            for model in models[:3]:  # Show first 3
                print(f"    - {model[0]}: {model[1]}")
            if len(models) > 3:
                print(f"    ... and {len(models) - 3} more")
        
        # Check display types
        print(f"\n📊 Display Types:")
        cursor.execute("SELECT COUNT(*) FROM display_types")
        display_count = cursor.fetchone()[0]
        print(f"  Total: {display_count}")
        
        # Check POP materials
        print(f"\n📊 POP Materials:")
        try:
            cursor.execute("SELECT COUNT(*) FROM pop_materials")
            pop_count = cursor.fetchone()[0]
            print(f"  Total: {pop_count}")
            
            if pop_count > 0:
                cursor.execute("SELECT pm.name, m.name as model_name FROM pop_materials pm JOIN models m ON pm.model_id = m.id LIMIT 5")
                materials = cursor.fetchall()
                print("  Sample materials:")
                for material in materials:
                    print(f"    - {material[0]} (Model: {material[1]})")
        except:
            # Try old schema
            try:
                cursor.execute("SELECT COUNT(*) FROM pop_materials_db")
                pop_count = cursor.fetchone()[0]
                print(f"  Total (old schema): {pop_count}")
                
                if pop_count > 0:
                    cursor.execute("SELECT material_name, model_name FROM pop_materials_db LIMIT 5")
                    materials = cursor.fetchall()
                    print("  Sample materials:")
                    for material in materials:
                        print(f"    - {material[0]} (Model: {material[1]})")
            except Exception as e:
                print(f"  Error checking POP materials: {e}")
        
        # Check users
        print(f"\n👥 Users:")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"  Total: {user_count}")
        
        # Check user_branches
        print(f"\n🏢 User Branches:")
        cursor.execute("SELECT COUNT(*) FROM user_branches")
        branch_count = cursor.fetchone()[0]
        print(f"  Total: {branch_count}")
        
        # Check data entries
        print(f"\n📝 Data Entries:")
        cursor.execute("SELECT COUNT(*) FROM data_entries")
        entry_count = cursor.fetchone()[0]
        print(f"  Total: {entry_count}")
        
        conn.close()
        
        print("\n✅ Database diagnosis completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_database()