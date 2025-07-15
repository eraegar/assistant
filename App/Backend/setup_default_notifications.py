#!/usr/bin/env python3
"""
Setup Default Notification Preferences
Creates default notification preferences for all existing managers
"""

import sys
import os

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models, database
from services.notification_service import get_notification_service

def setup_default_preferences():
    """Set up default notification preferences for all managers"""
    
    print("🔧 Setting up default notification preferences...")
    
    db = database.SessionLocal()
    try:
        notification_service = get_notification_service(db)
        
        # Get all managers
        managers = db.query(models.ManagerProfile).all()
        
        if not managers:
            print("❌ No managers found in database")
            return
        
        print(f"👥 Found {len(managers)} managers")
        
        # Default preferences to set up
        default_preferences = [
            {
                "notification_type": models.NotificationType.POTENTIAL_CLIENT_ENGAGED,
                "channel": models.NotificationChannel.IN_APP,
                "is_enabled": True
            },
            {
                "notification_type": models.NotificationType.PRICING_VIEWED_NO_REGISTRATION,
                "channel": models.NotificationChannel.IN_APP,
                "is_enabled": True
            },
            {
                "notification_type": models.NotificationType.MULTIPLE_SESSIONS_NO_REGISTRATION,
                "channel": models.NotificationChannel.IN_APP,
                "is_enabled": True
            },
            {
                "notification_type": models.NotificationType.HIGH_ENGAGEMENT_NO_CONVERSION,
                "channel": models.NotificationChannel.IN_APP,
                "is_enabled": True
            },
            # Email notifications for high priority alerts
            {
                "notification_type": models.NotificationType.HIGH_ENGAGEMENT_NO_CONVERSION,
                "channel": models.NotificationChannel.EMAIL,
                "is_enabled": True
            },
            # Daily summary
            {
                "notification_type": models.NotificationType.DAILY_SUMMARY,
                "channel": models.NotificationChannel.IN_APP,
                "is_enabled": True
            }
        ]
        
        total_created = 0
        
        for manager in managers:
            print(f"\n🔧 Setting up preferences for manager: {manager.user.name}")
            
            manager_created = 0
            for pref_config in default_preferences:
                # Check if preference already exists
                existing = db.query(models.ManagerNotificationPreference).filter(
                    models.ManagerNotificationPreference.manager_id == manager.id,
                    models.ManagerNotificationPreference.notification_type == pref_config["notification_type"],
                    models.ManagerNotificationPreference.channel == pref_config["channel"]
                ).first()
                
                if not existing:
                    # Create new preference
                    notification_service.update_manager_notification_preference(
                        manager_id=manager.id,
                        notification_type=pref_config["notification_type"],
                        channel=pref_config["channel"],
                        is_enabled=pref_config["is_enabled"]
                    )
                    manager_created += 1
                    total_created += 1
                    
                    print(f"   ✅ {pref_config['notification_type'].value} -> {pref_config['channel'].value}")
                else:
                    print(f"   ⏭️ {pref_config['notification_type'].value} -> {pref_config['channel'].value} (already exists)")
            
            print(f"   📊 Created {manager_created} new preferences for {manager.user.name}")
        
        print(f"\n✅ Setup completed! Created {total_created} notification preferences")
        print("\n💡 Managers now have default notifications enabled for:")
        print("   • Potential client engagement (in-app)")
        print("   • Pricing views without registration (in-app)")
        print("   • Multiple sessions without registration (in-app)")
        print("   • High engagement without conversion (in-app + email)")
        print("   • Daily summary (in-app)")
        
    except Exception as e:
        print(f"❌ Error setting up preferences: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    setup_default_preferences() 