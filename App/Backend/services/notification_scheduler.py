#!/usr/bin/env python3
"""
Notification Scheduler Service
Runs periodic tasks to detect potential clients and send notifications
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict

import database
from services.notification_service import get_notification_service

logger = logging.getLogger(__name__)

class NotificationScheduler:
    def __init__(self, check_interval_minutes: int = 30):
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.running = False
        self.last_check = None
        
    async def start(self):
        """Start the notification scheduler"""
        self.running = True
        logger.info("🚀 Notification scheduler started")
        
        while self.running:
            try:
                await self.run_check_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the notification scheduler"""
        self.running = False
        logger.info("🛑 Notification scheduler stopped")
    
    async def run_check_cycle(self):
        """Run a complete check cycle for potential clients"""
        cycle_start = datetime.utcnow()
        logger.info(f"🔄 Starting notification check cycle at {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        db = database.SessionLocal()
        try:
            notification_service = get_notification_service(db)
            
            # Determine hours to check based on last check time
            hours_back = self._calculate_hours_to_check()
            
            # Process potential clients
            result = notification_service.process_potential_clients(hours_back)
            
            # Log results
            self.last_check = cycle_start
            logger.info(f"✅ Check cycle completed:")
            logger.info(f"   Potential clients detected: {result['potential_clients_detected']}")
            logger.info(f"   Notifications sent: {result['notifications_sent']}")
            logger.info(f"   Hours analyzed: {result['hours_analyzed']}")
            
            # Clean up old notification history (optional)
            self._cleanup_old_notifications(db)
            
        except Exception as e:
            logger.error(f"❌ Error during check cycle: {e}")
            raise
        finally:
            db.close()
    
    def _calculate_hours_to_check(self) -> int:
        """Calculate how many hours back to check based on last check time"""
        if self.last_check is None:
            # First run - check last 24 hours
            return 24
        
        # Calculate time since last check
        time_since_last = datetime.utcnow() - self.last_check
        hours_since_last = int(time_since_last.total_seconds() / 3600) + 1
        
        # Limit to reasonable range
        return min(max(hours_since_last, 1), 48)
    
    def _cleanup_old_notifications(self, db):
        """Clean up old notification records (keep last 30 days)"""
        try:
            from models import NotificationHistory, PotentialClientAlert
            
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old notification history
            old_notifications = db.query(NotificationHistory).filter(
                NotificationHistory.sent_at < cutoff_date
            ).count()
            
            if old_notifications > 0:
                db.query(NotificationHistory).filter(
                    NotificationHistory.sent_at < cutoff_date
                ).delete()
                
                logger.info(f"🧹 Cleaned up {old_notifications} old notification records")
            
            # Clean up old potential client alerts that were resolved
            old_alerts = db.query(PotentialClientAlert).filter(
                PotentialClientAlert.created_at < cutoff_date,
                PotentialClientAlert.follow_up_required == False
            ).count()
            
            if old_alerts > 0:
                db.query(PotentialClientAlert).filter(
                    PotentialClientAlert.created_at < cutoff_date,
                    PotentialClientAlert.follow_up_required == False
                ).delete()
                
                logger.info(f"🧹 Cleaned up {old_alerts} old potential client alerts")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            db.rollback()

# Global scheduler instance
_scheduler_instance = None

def get_scheduler(check_interval_minutes: int = 30) -> NotificationScheduler:
    """Get or create the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = NotificationScheduler(check_interval_minutes)
    return _scheduler_instance

async def start_notification_scheduler(check_interval_minutes: int = 30):
    """Start the notification scheduler as a background task"""
    scheduler = get_scheduler(check_interval_minutes)
    await scheduler.start()

def stop_notification_scheduler():
    """Stop the notification scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()

# For testing - synchronous version
def run_single_check():
    """Run a single notification check (for testing/manual execution)"""
    import asyncio
    
    async def single_check():
        scheduler = NotificationScheduler()
        await scheduler.run_check_cycle()
    
    asyncio.run(single_check())

if __name__ == "__main__":
    # Manual execution for testing
    print("🧪 Running single notification check...")
    run_single_check()
    print("✅ Single check completed") 