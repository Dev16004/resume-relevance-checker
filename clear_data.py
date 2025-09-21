#!/usr/bin/env python3
"""
Script to clear all data from the resume checker database
"""

import os
import sys
from database import DatabaseManager

def clear_all_data():
    """Clear all data from all tables"""
    try:
        # Initialize database manager
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("🗑️  Clearing all data from database...")
        
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Clear all tables in the correct order (to avoid foreign key issues)
        tables_to_clear = [
            'analysis_results',
            'resume_skills', 
            'skills',
            'resumes',
            'job_descriptions'
        ]
        
        for table in tables_to_clear:
            cursor.execute(f'DELETE FROM {table}')
            count = cursor.rowcount
            print(f"   ✅ Cleared {count} records from {table}")
        
        # Reset auto-increment counters
        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        # Re-enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n🎉 All data cleared successfully!")
        print("   - All resumes deleted")
        print("   - All job descriptions deleted") 
        print("   - All analysis results deleted")
        print("   - All skills data deleted")
        print("   - Auto-increment counters reset")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def clear_vector_store():
    """Clear vector store data"""
    try:
        # Remove ChromaDB directory if it exists
        chroma_path = "./chroma_db"
        if os.path.exists(chroma_path):
            import shutil
            shutil.rmtree(chroma_path)
            print("🗑️  Vector store (ChromaDB) cleared")
        else:
            print("ℹ️  No vector store found to clear")
    except Exception as e:
        print(f"⚠️  Warning: Could not clear vector store: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧹 RESUME CHECKER - DATA CLEANUP")
    print("=" * 50)
    
    # Confirm with user
    confirm = input("\n⚠️  This will DELETE ALL DATA. Are you sure? (type 'YES' to confirm): ")
    
    if confirm == "YES":
        print("\n🚀 Starting data cleanup...")
        
        # Clear database
        if clear_all_data():
            # Clear vector store
            clear_vector_store()
            print("\n✨ Database cleanup completed successfully!")
        else:
            print("\n❌ Database cleanup failed!")
            sys.exit(1)
    else:
        print("\n🛑 Operation cancelled. No data was deleted.")
        sys.exit(0)