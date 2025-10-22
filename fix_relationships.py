from database_manager_fix import fix_missing_relationships

if __name__ == "__main__":
    if fix_missing_relationships():
        print("✅ Successfully fixed missing relationships")
    else:
        print("❌ Error fixing relationships")