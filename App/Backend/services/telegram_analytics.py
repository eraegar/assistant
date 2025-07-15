#!/usr/bin/env python3
"""
Telegram Bot Analytics Service
Handles tracking and analysis of bot interactions for conversion analysis
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

import models, database

class TelegramAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def track_interaction(
        self,
        telegram_user_id: str,
        action: str,
        action_data: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None,
        conversion_stage: Optional[str] = None
    ) -> models.TelegramAnalytics:
        """Track a user interaction with the bot"""
        
        # Create session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Check if user is registered in our system
        registered_user = self._check_user_registration(telegram_user_id)
        
        # Create analytics record
        analytics_record = models.TelegramAnalytics(
            telegram_user_id=telegram_user_id,
            username=user_info.get('username') if user_info else None,
            first_name=user_info.get('first_name') if user_info else None,
            last_name=user_info.get('last_name') if user_info else None,
            action=action,
            action_data=json.dumps(action_data) if action_data else None,
            session_id=session_id,
            is_registered_user=registered_user is not None,
            user_role=registered_user.get('role') if registered_user else None,
            subscription_plan=registered_user.get('subscription_plan') if registered_user else None,
            conversion_stage=conversion_stage,
            language_code=user_info.get('language_code') if user_info else None
        )
        
        self.db.add(analytics_record)
        self.db.commit()
        self.db.refresh(analytics_record)
        
        return analytics_record
    
    def _check_user_registration(self, telegram_user_id: str) -> Optional[Dict[str, str]]:
        """Check if user is registered in our system and return their info"""
        
        # Check in User table by telegram_username (simplified approach)
        # In real implementation, you'd need a proper telegram_user_id field
        user = self.db.query(models.User).filter(
            models.User.telegram_username.like(f"%{telegram_user_id}%")
        ).first()
        
        if user:
            user_info = {
                'role': user.role.value,
                'subscription_plan': None
            }
            
            # Get subscription plan if user is a client
            if user.role == models.UserRole.client and user.client_profile and user.client_profile.subscription:
                user_info['subscription_plan'] = user.client_profile.subscription.plan.value
            
            return user_info
        
        return None
    
    def get_conversion_funnel_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel statistics for the last N days"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Key conversion stages
        stages = [
            'started_bot',
            'viewed_pricing', 
            'viewed_examples',
            'clicked_register',
            'completed_registration',
            'created_first_task'
        ]
        
        funnel_stats = {}
        
        for stage in stages:
            count = self.db.query(models.TelegramAnalytics).filter(
                models.TelegramAnalytics.conversion_stage == stage,
                models.TelegramAnalytics.created_at >= start_date
            ).count()
            
            unique_users = self.db.query(models.TelegramAnalytics.telegram_user_id).filter(
                models.TelegramAnalytics.conversion_stage == stage,
                models.TelegramAnalytics.created_at >= start_date
            ).distinct().count()
            
            funnel_stats[stage] = {
                'total_events': count,
                'unique_users': unique_users
            }
        
        return funnel_stats
    
    def get_interaction_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of bot interactions for the last N days"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total interactions
        total_interactions = self.db.query(models.TelegramAnalytics).filter(
            models.TelegramAnalytics.created_at >= start_date
        ).count()
        
        # Unique users
        unique_users = self.db.query(models.TelegramAnalytics.telegram_user_id).filter(
            models.TelegramAnalytics.created_at >= start_date
        ).distinct().count()
        
        # New users (first interaction)
        new_users = self.db.query(func.count(func.distinct(models.TelegramAnalytics.telegram_user_id))).filter(
            models.TelegramAnalytics.created_at >= start_date,
            models.TelegramAnalytics.action == 'start'
        ).scalar()
        
        # Registered users who interacted
        registered_users = self.db.query(models.TelegramAnalytics.telegram_user_id).filter(
            models.TelegramAnalytics.created_at >= start_date,
            models.TelegramAnalytics.is_registered_user == True
        ).distinct().count()
        
        # Most popular actions
        popular_actions = self.db.query(
            models.TelegramAnalytics.action,
            func.count(models.TelegramAnalytics.id).label('count')
        ).filter(
            models.TelegramAnalytics.created_at >= start_date
        ).group_by(models.TelegramAnalytics.action).order_by(
            func.count(models.TelegramAnalytics.id).desc()
        ).limit(10).all()
        
        return {
            'period_days': days,
            'total_interactions': total_interactions,
            'unique_users': unique_users,
            'new_users': new_users,
            'registered_users': registered_users,
            'conversion_rate': round((registered_users / unique_users * 100) if unique_users > 0 else 0, 2),
            'popular_actions': [{'action': action, 'count': count} for action, count in popular_actions]
        }
    
    def get_user_journey(self, telegram_user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get interaction journey for a specific user"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        interactions = self.db.query(models.TelegramAnalytics).filter(
            models.TelegramAnalytics.telegram_user_id == telegram_user_id,
            models.TelegramAnalytics.created_at >= start_date
        ).order_by(models.TelegramAnalytics.created_at).all()
        
        journey = []
        for interaction in interactions:
            journey.append({
                'action': interaction.action,
                'action_data': json.loads(interaction.action_data) if interaction.action_data else None,
                'conversion_stage': interaction.conversion_stage,
                'timestamp': interaction.created_at.isoformat(),
                'session_id': interaction.session_id
            })
        
        return journey
    
    def get_engagement_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get insights about user engagement patterns"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Users who engaged but didn't register
        unregistered_engaged_users = self.db.query(models.TelegramAnalytics.telegram_user_id).filter(
            models.TelegramAnalytics.created_at >= start_date,
            models.TelegramAnalytics.is_registered_user == False,
            models.TelegramAnalytics.action.in_(['view_pricing', 'view_examples', 'contact_support'])
        ).distinct().count()
        
        # Users who viewed pricing but didn't register
        pricing_viewers = self.db.query(models.TelegramAnalytics.telegram_user_id).filter(
            models.TelegramAnalytics.created_at >= start_date,
            models.TelegramAnalytics.action == 'view_pricing',
            models.TelegramAnalytics.is_registered_user == False
        ).distinct().count()
        
        # Average interactions per user
        avg_interactions = self.db.query(func.avg(
            func.count(models.TelegramAnalytics.id)
        )).group_by(models.TelegramAnalytics.telegram_user_id).filter(
            models.TelegramAnalytics.created_at >= start_date
        ).scalar() or 0
        
        # Time distribution of interactions
        hourly_distribution = self.db.query(
            func.extract('hour', models.TelegramAnalytics.created_at).label('hour'),
            func.count(models.TelegramAnalytics.id).label('count')
        ).filter(
            models.TelegramAnalytics.created_at >= start_date
        ).group_by(func.extract('hour', models.TelegramAnalytics.created_at)).all()
        
        return {
            'unregistered_engaged_users': unregistered_engaged_users,
            'pricing_viewers_not_registered': pricing_viewers,
            'avg_interactions_per_user': round(avg_interactions, 2),
            'hourly_distribution': [{'hour': int(hour), 'count': count} for hour, count in hourly_distribution]
        }

def get_analytics_service(db: Session = None) -> TelegramAnalyticsService:
    """Factory function to get analytics service instance"""
    if db is None:
        db = database.SessionLocal()
    return TelegramAnalyticsService(db) 