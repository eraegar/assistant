#!/usr/bin/env python3
"""
Script to update existing assignments to set primary status
"""

import sqlite3
import sys
import os

# Get the database path
backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, "test.db")

def update_assignments():
    """Update existing assignments to set primary status"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current assignments...")
        
        # Check if any assignments exist and if they have primary status
        cursor.execute('SELECT id, client_id, assistant_id, is_primary FROM client_assistant_assignments WHERE status = "active" LIMIT 5')
        assignments = cursor.fetchall()
        print('Current assignments:')
        for row in assignments:
            print(f'  ID: {row[0]}, Client: {row[1]}, Assistant: {row[2]}, Primary: {row[3]}')
            
        # Count total active assignments
        cursor.execute('SELECT COUNT(*) FROM client_assistant_assignments WHERE status = "active"')
        total = cursor.fetchone()[0]
        print(f'Total active assignments: {total}')

        if total == 0:
            print("✅ No assignments to update")
            return

        # Update existing assignments to be primary if they are the only assignment for a client
        print("🔄 Updating single assignments to primary status...")
        
        cursor.execute('''
            UPDATE client_assistant_assignments 
            SET is_primary = 1 
            WHERE id IN (
                SELECT c1.id
                FROM client_assistant_assignments c1
                WHERE c1.status = 'active'
                AND (SELECT COUNT(*) 
                     FROM client_assistant_assignments c2 
                     WHERE c2.client_id = c1.client_id 
                     AND c2.status = 'active') = 1
                AND c1.is_primary = 0
            )
        ''')

        affected = cursor.rowcount
        print(f'✅ Updated {affected} assignments to primary status')
        
        conn.commit()
        conn.close()
        
        print("🎉 Assignment update completed successfully!")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        raise

if __name__ == "__main__":
    update_assignments() 