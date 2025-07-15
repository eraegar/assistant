#!/usr/bin/env python3
"""
Migration script to add Manager Notification System tables
"""

import sys
import os

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models, database

def migrate_add_notification_system():
    """Add Manager Notification System tables to database"""
    
    print("🔄 Adding Manager Notification System tables...")
    
    try:
        # Create all tables (will only create missing ones)
        models.Base.metadata.create_all(bind=database.engine)
        
        print("✅ Manager Notification System tables added successfully!")
        print("📊 New tables:")
        print("   - manager_notification_preferences")
        print("   - notification_history") 
        print("   - potential_client_alerts")
        
        # Test the tables by checking if they exist
        db = database.SessionLocal()
        try:
            # Try to query the tables (will fail if not exists)
            prefs_count = db.query(models.ManagerNotificationPreference).count()
            history_count = db.query(models.NotificationHistory).count()
            alerts_count = db.query(models.PotentialClientAlert).count()
            
            print(f"📈 manager_notification_preferences: {prefs_count} records")
            print(f"📈 notification_history: {history_count} records")
            print(f"📈 potential_client_alerts: {alerts_count} records")
        except Exception as e:
            print(f"❌ Error accessing notification tables: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_add_notification_system() 