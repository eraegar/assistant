#!/usr/bin/env python3

import sys
import os

# Add the parent directory to the Python path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL, engine
import models

def migrate_add_telegram_interactions():
    """Add telegram_interactions table to the database"""
    print("🔄 Starting migration: Add telegram_interactions table")
    
    # Use the existing engine from database module
    
    try:
        # Create the telegram_interactions table
        models.TelegramInteraction.__table__.create(engine, checkfirst=True)
        print("✅ telegram_interactions table created successfully")
        
        # Verify the table was created
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='telegram_interactions'"))
            if result.fetchone():
                print("✅ Verified: telegram_interactions table exists")
            else:
                print("❌ Error: telegram_interactions table was not created")
                return False
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_add_telegram_interactions()
    if not success:
        sys.exit(1) 