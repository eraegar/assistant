#!/usr/bin/env python3
"""
Standalone Notification Service Starter
Runs the notification scheduler as a background service
"""

import asyncio
import logging
import signal
import sys
from services.notification_scheduler import start_notification_scheduler, stop_notification_scheduler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_flag
    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True
    stop_notification_scheduler()

async def main():
    """Main function to run the notification service"""
    global shutdown_flag
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 Starting Manager Notification Service...")
    logger.info("📧 Will check for potential clients every 30 minutes")
    logger.info("🔄 Press Ctrl+C to stop")
    
    try:
        # Start the notification scheduler (runs every 30 minutes)
        await start_notification_scheduler(check_interval_minutes=30)
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
    finally:
        logger.info("✅ Notification service stopped")

if __name__ == "__main__":
    asyncio.run(main()) 