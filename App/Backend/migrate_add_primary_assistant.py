#!/usr/bin/env python3
"""
Migration script to add is_primary field to client_assistant_assignments table
"""

import sys
import os
from sqlalchemy import text

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database

def migrate_add_primary_field():
    """Add is_primary field to client_assistant_assignments table"""
    
    print("🔄 Adding is_primary field to client_assistant_assignments table...")
    
    # Create database engine
    engine = database.engine
    
    try:
        with engine.connect() as connection:
            # Check if column exists
            result = connection.execute(text("""
                PRAGMA table_info(client_assistant_assignments);
            """))
            
            columns = [row[1] for row in result.fetchall()]
            
            if 'is_primary' not in columns:
                # Add the new column
                connection.execute(text("""
                    ALTER TABLE client_assistant_assignments 
                    ADD COLUMN is_primary BOOLEAN DEFAULT 0;
                """))
                
                # Update existing assignments to set the first one as primary for each client
                connection.execute(text("""
                    UPDATE client_assistant_assignments 
                    SET is_primary = 1 
                    WHERE id IN (
                        SELECT MIN(id) 
                        FROM client_assistant_assignments 
                        WHERE status = 'active' 
                        GROUP BY client_id
                    );
                """))
                
                connection.commit()
                print("✅ Successfully added is_primary field and updated existing assignments")
            else:
                print("ℹ️  is_primary field already exists")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_add_primary_field()
    print("🎉 Migration completed!") 