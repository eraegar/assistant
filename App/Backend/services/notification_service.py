#!/usr/bin/env python3
"""
Manager Notification Service
Handles detection of potential clients and notification delivery to managers
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

import models, database
from services.telegram_analytics import TelegramAnalyticsService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = TelegramAnalyticsService(db)
    
    def calculate_engagement_score(self, user_analytics: List[models.TelegramAnalytics]) -> float:
        """Calculate engagement score based on user interactions"""
        
        if not user_analytics:
            return 0.0
        
        score = 0.0
        
        # Base points for each interaction type
        action_scores = {
            'start': 1.0,
            'view_pricing': 3.0,
            'view_examples': 2.0,
            'contact_support': 5.0,
            'click_register': 4.0,
            'view_services': 1.5,
            'ask_question': 3.0,
            'request_callback': 6.0,
            'view_testimonials': 2.0,
        }
        
        # Count interactions and calculate base score
        for analytics in user_analytics:
            action_score = action_scores.get(analytics.action, 0.5)
            score += action_score
        
        # Bonus for multiple sessions
        sessions = set(a.session_id for a in user_analytics if a.session_id)
        if len(sessions) > 1:
            score += len(sessions) * 1.0
        
        # Bonus for time spent (multiple interactions in short time)
        if len(user_analytics) > 5:
            score += 2.0
        elif len(user_analytics) > 3:
            score += 1.0
        
        # Bonus for conversion stage progression
        conversion_stages = [a.conversion_stage for a in user_analytics if a.conversion_stage]
        unique_stages = set(conversion_stages)
        if 'viewed_pricing' in unique_stages:
            score += 2.0
        if 'clicked_register' in unique_stages:
            score += 3.0
        
        return min(score, 100.0)  # Cap at 100
    
    def detect_potential_clients(self, hours_back: int = 24) -> List[models.PotentialClientAlert]:
        """Detect potential clients who engaged but didn't register"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get unregistered users with recent activity
        unregistered_analytics = self.db.query(models.TelegramAnalytics).filter(
            models.TelegramAnalytics.created_at >= cutoff_time,
            models.TelegramAnalytics.is_registered_user == False
        ).all()
        
        # Group by telegram_user_id
        user_analytics = {}
        for analytics in unregistered_analytics:
            user_id = analytics.telegram_user_id
            if user_id not in user_analytics:
                user_analytics[user_id] = []
            user_analytics[user_id].append(analytics)
        
        potential_clients = []
        
        for telegram_user_id, analytics_list in user_analytics.items():
            # Check if we already have an alert for this user (avoid duplicates)
            existing_alert = self.db.query(models.PotentialClientAlert).filter(
                models.PotentialClientAlert.telegram_user_id == telegram_user_id
            ).first()
            
            if existing_alert:
                # Update existing alert
                alert = self._update_potential_client_alert(existing_alert, analytics_list)
            else:
                # Create new alert
                alert = self._create_potential_client_alert(telegram_user_id, analytics_list)
            
            if alert and alert.engagement_score >= 5.0:  # Minimum threshold
                potential_clients.append(alert)
        
        return potential_clients
    
    def _create_potential_client_alert(self, telegram_user_id: str, analytics_list: List[models.TelegramAnalytics]) -> Optional[models.PotentialClientAlert]:
        """Create a new potential client alert"""
        
        if not analytics_list:
            return None
        
        # Get user info from most recent interaction
        latest_analytics = max(analytics_list, key=lambda x: x.created_at)
        
        # Calculate engagement metrics
        engagement_score = self.calculate_engagement_score(analytics_list)
        sessions = set(a.session_id for a in analytics_list if a.session_id)
        
        # Check key actions
        actions = [a.action for a in analytics_list]
        viewed_pricing = 'view_pricing' in actions
        viewed_examples = 'view_examples' in actions
        contacted_support = 'contact_support' in actions or 'ask_question' in actions
        clicked_register = 'click_register' in actions
        
        alert = models.PotentialClientAlert(
            telegram_user_id=telegram_user_id,
            username=latest_analytics.username,
            first_name=latest_analytics.first_name,
            last_name=latest_analytics.last_name,
            total_interactions=len(analytics_list),
            first_interaction_at=min(a.created_at for a in analytics_list),
            last_interaction_at=max(a.created_at for a in analytics_list),
            total_sessions=len(sessions),
            viewed_pricing=viewed_pricing,
            viewed_examples=viewed_examples,
            contacted_support=contacted_support,
            clicked_register=clicked_register,
            engagement_score=engagement_score
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def _update_potential_client_alert(self, alert: models.PotentialClientAlert, analytics_list: List[models.TelegramAnalytics]) -> models.PotentialClientAlert:
        """Update existing potential client alert with new data"""
        
        # Recalculate engagement score with all analytics
        all_analytics = self.db.query(models.TelegramAnalytics).filter(
            models.TelegramAnalytics.telegram_user_id == alert.telegram_user_id,
            models.TelegramAnalytics.is_registered_user == False
        ).all()
        
        engagement_score = self.calculate_engagement_score(all_analytics)
        sessions = set(a.session_id for a in all_analytics if a.session_id)
        
        # Update metrics
        alert.total_interactions = len(all_analytics)
        alert.last_interaction_at = max(a.created_at for a in all_analytics)
        alert.total_sessions = len(sessions)
        alert.engagement_score = engagement_score
        
        # Update key actions
        actions = [a.action for a in all_analytics]
        alert.viewed_pricing = alert.viewed_pricing or 'view_pricing' in actions
        alert.viewed_examples = alert.viewed_examples or 'view_examples' in actions
        alert.contacted_support = alert.contacted_support or ('contact_support' in actions or 'ask_question' in actions)
        alert.clicked_register = alert.clicked_register or 'click_register' in actions
        
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        return alert
    
    def should_send_notification(self, alert: models.PotentialClientAlert, notification_type: models.NotificationType) -> bool:
        """Determine if notification should be sent based on alert and type"""
        
        # Don't send if already sent recently
        if alert.alert_sent and alert.alert_sent_at:
            time_since_last = datetime.utcnow() - alert.alert_sent_at
            if time_since_last < timedelta(hours=4):  # Minimum 4 hours between notifications
                return False
        
        # Type-specific criteria
        if notification_type == models.NotificationType.POTENTIAL_CLIENT_ENGAGED:
            return alert.engagement_score >= 5.0 and not alert.alert_sent
        
        elif notification_type == models.NotificationType.PRICING_VIEWED_NO_REGISTRATION:
            return alert.viewed_pricing and alert.engagement_score >= 3.0
        
        elif notification_type == models.NotificationType.MULTIPLE_SESSIONS_NO_REGISTRATION:
            return alert.total_sessions >= 2 and alert.engagement_score >= 4.0
        
        elif notification_type == models.NotificationType.HIGH_ENGAGEMENT_NO_CONVERSION:
            return alert.engagement_score >= 10.0 and alert.clicked_register
        
        return False
    
    def send_notifications_for_alert(self, alert: models.PotentialClientAlert) -> List[models.NotificationHistory]:
        """Send notifications to managers for a potential client alert"""
        
        notifications_sent = []
        
        # Get active managers with notification preferences
        managers = self.db.query(models.ManagerProfile).all()
        
        for manager in managers:
            # Check each notification type
            for notification_type in [
                models.NotificationType.POTENTIAL_CLIENT_ENGAGED,
                models.NotificationType.PRICING_VIEWED_NO_REGISTRATION,
                models.NotificationType.MULTIPLE_SESSIONS_NO_REGISTRATION,
                models.NotificationType.HIGH_ENGAGEMENT_NO_CONVERSION
            ]:
                
                if self.should_send_notification(alert, notification_type):
                    # Get manager preferences for this notification type
                    preferences = self.db.query(models.ManagerNotificationPreference).filter(
                        models.ManagerNotificationPreference.manager_id == manager.id,
                        models.ManagerNotificationPreference.notification_type == notification_type,
                        models.ManagerNotificationPreference.is_enabled == True
                    ).all()
                    
                    for preference in preferences:
                        notification = self._create_notification_for_alert(
                            alert, manager, notification_type, preference.channel
                        )
                        
                        if notification:
                            notifications_sent.append(notification)
        
        # Mark alert as sent
        if notifications_sent:
            alert.alert_sent = True
            alert.alert_sent_at = datetime.utcnow()
            alert.managers_notified = json.dumps([n.manager_id for n in notifications_sent])
            self.db.commit()
        
        return notifications_sent
    
    def _create_notification_for_alert(
        self, 
        alert: models.PotentialClientAlert, 
        manager: models.ManagerProfile, 
        notification_type: models.NotificationType,
        channel: models.NotificationChannel
    ) -> Optional[models.NotificationHistory]:
        """Create and send notification for an alert"""
        
        # Generate notification content
        title, message = self._generate_notification_content(alert, notification_type)
        
        # Create notification record
        notification = models.NotificationHistory(
            manager_id=manager.id,
            notification_type=notification_type,
            channel=channel,
            title=title,
            message=message,
            related_telegram_user_id=alert.telegram_user_id,
            related_data=json.dumps({
                'engagement_score': alert.engagement_score,
                'total_interactions': alert.total_interactions,
                'total_sessions': alert.total_sessions,
                'viewed_pricing': alert.viewed_pricing,
                'contacted_support': alert.contacted_support
            })
        )
        
        # Send via appropriate channel
        delivery_success = self._send_notification(notification, manager)
        
        if delivery_success:
            notification.status = "delivered"
            notification.delivered_at = datetime.utcnow()
        else:
            notification.status = "failed"
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def _generate_notification_content(self, alert: models.PotentialClientAlert, notification_type: models.NotificationType) -> Tuple[str, str]:
        """Generate notification title and message"""
        
        user_name = alert.first_name or alert.username or f"User {alert.telegram_user_id}"
        
        if notification_type == models.NotificationType.POTENTIAL_CLIENT_ENGAGED:
            title = "🔥 Потенциальный клиент проявил интерес"
            message = f"""
Пользователь {user_name} активно взаимодействует с ботом!

📊 Статистика:
• Оценка заинтересованности: {alert.engagement_score:.1f}/100
• Количество взаимодействий: {alert.total_interactions}
• Сессий: {alert.total_sessions}
• Смотрел цены: {'✅' if alert.viewed_pricing else '❌'}
• Обращался в поддержку: {'✅' if alert.contacted_support else '❌'}

⏰ Первое взаимодействие: {alert.first_interaction_at.strftime('%d.%m.%Y %H:%M')}
⏰ Последнее взаимодействие: {alert.last_interaction_at.strftime('%d.%m.%Y %H:%M')}

💡 Рекомендуется связаться с пользователем для персонального предложения!
""".strip()
        
        elif notification_type == models.NotificationType.PRICING_VIEWED_NO_REGISTRATION:
            title = "💰 Пользователь изучал цены, но не регистрируется"
            message = f"""
Пользователь {user_name} смотрел цены, но пока не зарегистрировался.

📊 Детали:
• Оценка заинтересованности: {alert.engagement_score:.1f}/100
• Взаимодействий: {alert.total_interactions}
• Смотрел примеры: {'✅' if alert.viewed_examples else '❌'}

⏰ Последнее взаимодействие: {alert.last_interaction_at.strftime('%d.%m.%Y %H:%M')}

💡 Возможно, стоит предложить скидку или персональную консультацию!
""".strip()
        
        elif notification_type == models.NotificationType.MULTIPLE_SESSIONS_NO_REGISTRATION:
            title = "🔄 Пользователь возвращается, но не регистрируется"
            message = f"""
Пользователь {user_name} уже {alert.total_sessions} раз возвращался к боту!

📊 Активность:
• Сессий: {alert.total_sessions}
• Взаимодействий: {alert.total_interactions}
• Оценка заинтересованности: {alert.engagement_score:.1f}/100

⏰ Период активности: {alert.first_interaction_at.strftime('%d.%m.%Y')} - {alert.last_interaction_at.strftime('%d.%m.%Y')}

💡 Высокий интерес! Рекомендуется персональный контакт.
""".strip()
        
        elif notification_type == models.NotificationType.HIGH_ENGAGEMENT_NO_CONVERSION:
            title = "🎯 Очень заинтересованный пользователь!"
            message = f"""
Пользователь {user_name} показывает высокую заинтересованность!

🔥 Высокие показатели:
• Оценка заинтересованности: {alert.engagement_score:.1f}/100
• Взаимодействий: {alert.total_interactions}
• Сессий: {alert.total_sessions}
• Нажимал "Регистрация": {'✅' if alert.clicked_register else '❌'}

⏰ Последняя активность: {alert.last_interaction_at.strftime('%d.%m.%Y %H:%M')}

🚨 ПРИОРИТЕТНЫЙ ЛИД! Необходим срочный контакт!
""".strip()
        
        else:
            title = "📱 Уведомление о потенциальном клиенте"
            message = f"Пользователь {user_name} проявил интерес к услугам."
        
        return title, message
    
    def _send_notification(self, notification: models.NotificationHistory, manager: models.ManagerProfile) -> bool:
        """Send notification via appropriate channel"""
        
        try:
            if notification.channel == models.NotificationChannel.EMAIL:
                return self._send_email_notification(notification, manager)
            
            elif notification.channel == models.NotificationChannel.TELEGRAM:
                return self._send_telegram_notification(notification, manager)
            
            elif notification.channel == models.NotificationChannel.IN_APP:
                return self._send_in_app_notification(notification, manager)
            
            elif notification.channel == models.NotificationChannel.SMS:
                return self._send_sms_notification(notification, manager)
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def _send_email_notification(self, notification: models.NotificationHistory, manager: models.ManagerProfile) -> bool:
        """Send email notification (placeholder implementation)"""
        
        # TODO: Implement actual email sending
        logger.info(f"Email notification sent to {manager.email}: {notification.title}")
        
        notification.delivery_details = json.dumps({
            'email': manager.email,
            'method': 'email'
        })
        
        return True
    
    def _send_telegram_notification(self, notification: models.NotificationHistory, manager: models.ManagerProfile) -> bool:
        """Send Telegram notification (placeholder implementation)"""
        
        # TODO: Implement Telegram bot message sending to manager
        logger.info(f"Telegram notification sent to manager {manager.id}: {notification.title}")
        
        notification.delivery_details = json.dumps({
            'telegram_username': manager.user.telegram_username,
            'method': 'telegram_bot'
        })
        
        return True
    
    def _send_in_app_notification(self, notification: models.NotificationHistory, manager: models.ManagerProfile) -> bool:
        """Send in-app notification (stored in database)"""
        
        # In-app notifications are stored in the database and shown when manager logs in
        logger.info(f"In-app notification created for manager {manager.id}: {notification.title}")
        
        notification.delivery_details = json.dumps({
            'method': 'in_app'
        })
        
        return True
    
    def _send_sms_notification(self, notification: models.NotificationHistory, manager: models.ManagerProfile) -> bool:
        """Send SMS notification (placeholder implementation)"""
        
        # TODO: Implement SMS sending
        logger.info(f"SMS notification sent to manager {manager.id}: {notification.title}")
        
        notification.delivery_details = json.dumps({
            'phone': manager.user.phone,
            'method': 'sms'
        })
        
        return True
    
    def process_potential_clients(self, hours_back: int = 24) -> Dict[str, int]:
        """Main method to detect and notify about potential clients"""
        
        potential_clients = self.detect_potential_clients(hours_back)
        
        total_alerts = len(potential_clients)
        total_notifications = 0
        
        for alert in potential_clients:
            notifications = self.send_notifications_for_alert(alert)
            total_notifications += len(notifications)
        
        return {
            'potential_clients_detected': total_alerts,
            'notifications_sent': total_notifications,
            'hours_analyzed': hours_back
        }
    
    def get_manager_notification_preferences(self, manager_id: int) -> List[models.ManagerNotificationPreference]:
        """Get notification preferences for a manager"""
        
        return self.db.query(models.ManagerNotificationPreference).filter(
            models.ManagerNotificationPreference.manager_id == manager_id
        ).all()
    
    def update_manager_notification_preference(
        self, 
        manager_id: int, 
        notification_type: models.NotificationType,
        channel: models.NotificationChannel,
        is_enabled: bool,
        threshold_settings: Optional[Dict] = None
    ) -> models.ManagerNotificationPreference:
        """Update or create manager notification preference"""
        
        preference = self.db.query(models.ManagerNotificationPreference).filter(
            models.ManagerNotificationPreference.manager_id == manager_id,
            models.ManagerNotificationPreference.notification_type == notification_type,
            models.ManagerNotificationPreference.channel == channel
        ).first()
        
        if preference:
            preference.is_enabled = is_enabled
            preference.threshold_settings = json.dumps(threshold_settings) if threshold_settings else None
            preference.updated_at = datetime.utcnow()
        else:
            preference = models.ManagerNotificationPreference(
                manager_id=manager_id,
                notification_type=notification_type,
                channel=channel,
                is_enabled=is_enabled,
                threshold_settings=json.dumps(threshold_settings) if threshold_settings else None
            )
            self.db.add(preference)
        
        self.db.commit()
        self.db.refresh(preference)
        
        return preference

def get_notification_service(db: Session = None) -> NotificationService:
    """Factory function to get notification service instance"""
    if db is None:
        db = database.SessionLocal()
    return NotificationService(db) 