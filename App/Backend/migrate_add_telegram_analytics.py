#!/usr/bin/env python3
"""
Migration script to add TelegramAnalytics table
"""

import sys
import os

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models, database

def migrate_add_telegram_analytics():
    """Add TelegramAnalytics table to database"""
    
    print("🔄 Adding TelegramAnalytics table...")
    
    try:
        # Create all tables (will only create missing ones)
        models.Base.metadata.create_all(bind=database.engine)
        
        print("✅ TelegramAnalytics table added successfully!")
        print("📊 Ready to track bot interactions and conversions")
        
        # Test the table by checking if it exists
        db = database.SessionLocal()
        try:
            # Try to query the table (will fail if not exists)
            count = db.query(models.TelegramAnalytics).count()
            print(f"📈 TelegramAnalytics table has {count} records")
        except Exception as e:
            print(f"❌ Error accessing TelegramAnalytics table: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_add_telegram_analytics() 