#!/usr/bin/env python3
"""
Migration script to add is_primary field to client_assistant_assignments table
This field will help identify the main assistant for client communication
"""

import sys
import os
from sqlalchemy import text

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database

def migrate_add_primary_field():
    """Add is_primary field to client_assistant_assignments table"""
    
    engine = database.engine
    
    try:
        print("🔄 Adding is_primary field to client_assistant_assignments table...")
        
        with engine.connect() as connection:
            # Add the new column
            connection.execute(text("""
                ALTER TABLE client_assistant_assignments 
                ADD COLUMN is_primary BOOLEAN DEFAULT FALSE
            """))
            connection.commit()
            
            print("✅ Successfully added is_primary field")
            
            # Set existing single assignments as primary
            print("🔄 Setting existing single assignments as primary...")
            
            # Find clients with only one assignment and mark it as primary
            result = connection.execute(text("""
                UPDATE client_assistant_assignments 
                SET is_primary = TRUE 
                WHERE id IN (
                    SELECT MIN(id) 
                    FROM client_assistant_assignments 
                    WHERE status = 'active'
                    GROUP BY client_id 
                    HAVING COUNT(*) = 1
                )
            """))
            connection.commit()
            
            affected_rows = result.rowcount
            print(f"✅ Marked {affected_rows} existing assignments as primary")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_add_primary_field()
    print("🎉 Migration completed successfully!") 