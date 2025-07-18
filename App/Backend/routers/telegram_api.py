from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

import models, database

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class InteractionCreate(BaseModel):
    user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interaction_type: str
    additional_data: Optional[str] = None

@router.post("/interactions")
async def log_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
):
    """Log a Telegram bot interaction"""
    try:
        db_interaction = models.TelegramInteraction(
            user_id=interaction.user_id,
            username=interaction.username,
            first_name=interaction.first_name,
            last_name=interaction.last_name,
            interaction_type=interaction.interaction_type,
            additional_data=interaction.additional_data
        )
        
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        
        return {"success": True, "id": db_interaction.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log interaction: {str(e)}")

@router.get("/analytics")
async def get_telegram_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get Telegram bot usage analytics with enhanced conversion tracking"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total interactions
        total_interactions = db.query(models.TelegramInteraction).filter(
            models.TelegramInteraction.created_at >= start_date
        ).count()
        
        # Unique users
        unique_users = db.query(models.TelegramInteraction.user_id).filter(
            models.TelegramInteraction.created_at >= start_date
        ).distinct().count()
        
        # Interactions by type
        interaction_types = db.query(
            models.TelegramInteraction.interaction_type,
            func.count(models.TelegramInteraction.id)
        ).filter(
            models.TelegramInteraction.created_at >= start_date
        ).group_by(models.TelegramInteraction.interaction_type).all()
        
        interaction_distribution = {interaction_type: count for interaction_type, count in interaction_types}
        
        # Daily interactions
        daily_stats = db.query(
            func.date(models.TelegramInteraction.created_at).label('date'),
            func.count(models.TelegramInteraction.id).label('count')
        ).filter(
            models.TelegramInteraction.created_at >= start_date
        ).group_by(func.date(models.TelegramInteraction.created_at)).all()
        
        daily_interactions = {str(date): count for date, count in daily_stats}
        
        # Enhanced conversion tracking
        # Users who pressed the app button
        app_button_users = db.query(models.TelegramInteraction.user_id).filter(
            models.TelegramInteraction.created_at >= start_date,
            models.TelegramInteraction.interaction_type == "app_button_pressed"
        ).distinct().count()
        
        # Users who registered after bot interaction (based on telegram_username correlation)
        registered_users = db.query(models.User).filter(
            models.User.created_at >= start_date,
            models.User.role == models.UserRole.client
        ).count()
        
        # Users with active subscriptions (assuming they came from telegram)
        users_with_subscriptions = db.query(models.User).join(models.ClientProfile).join(models.Subscription).filter(
            models.User.created_at >= start_date,
            models.User.role == models.UserRole.client,
            models.Subscription.status == models.SubscriptionStatus.active
        ).count()
        
        # Conversion rates
        app_button_rate = (app_button_users / unique_users * 100) if unique_users > 0 else 0
        registration_rate = (registered_users / unique_users * 100) if unique_users > 0 else 0
        subscription_rate = (users_with_subscriptions / unique_users * 100) if unique_users > 0 else 0
        
        # Funnel conversion rates
        app_to_registration_rate = (registered_users / app_button_users * 100) if app_button_users > 0 else 0
        registration_to_subscription_rate = (users_with_subscriptions / registered_users * 100) if registered_users > 0 else 0
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "conversion_rate": round(registration_rate, 2),
                "registered_users": registered_users,
                "users_with_subscriptions": users_with_subscriptions
            },
            "user_journey": {
                "unique_telegram_users": unique_users,
                "app_button_pressed": app_button_users,
                "registered_users": registered_users,
                "paying_customers": users_with_subscriptions
            },
            "conversion_funnel": {
                "telegram_to_app_rate": round(app_button_rate, 2),
                "telegram_to_registration_rate": round(registration_rate, 2),
                "telegram_to_subscription_rate": round(subscription_rate, 2),
                "app_to_registration_rate": round(app_to_registration_rate, 2),
                "registration_to_subscription_rate": round(registration_to_subscription_rate, 2)
            },
            "interaction_distribution": interaction_distribution,
            "daily_interactions": daily_interactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/analytics/user-journey")
async def get_user_journey_analytics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed journey analytics for a specific Telegram user"""
    try:
        # Get all interactions for this user
        interactions = db.query(models.TelegramInteraction).filter(
            models.TelegramInteraction.user_id == user_id
        ).order_by(models.TelegramInteraction.created_at).all()
        
        if not interactions:
            raise HTTPException(status_code=404, detail="No interactions found for this user")
        
        # Try to find if this user registered (by matching telegram username or other data)
        user_record = None
        first_interaction = interactions[0]
        
        if first_interaction.username is not None:
            # Try to find user by telegram username
            user_record = db.query(models.User).filter(
                models.User.telegram_username.ilike(f"%{first_interaction.username.replace('@', '')}%")
            ).first()
        
        # Count interaction types
        interaction_counts = {}
        for interaction in interactions:
            interaction_counts[interaction.interaction_type] = interaction_counts.get(interaction.interaction_type, 0) + 1
        
        # Check subscription status if user found
        subscription_info = None
        if user_record is not None and user_record.role == models.UserRole.client:
            client_profile = user_record.client_profile
            if client_profile is not None and client_profile.subscription is not None:
                subscription_info = {
                    "plan": client_profile.subscription.plan.value,
                    "status": client_profile.subscription.status.value,
                    "started_at": client_profile.subscription.started_at.isoformat(),
                    "expires_at": client_profile.subscription.expires_at.isoformat() if client_profile.subscription.expires_at else None
                }
        
        return {
            "user_id": user_id,
            "telegram_user_info": {
                "username": first_interaction.username,
                "first_name": first_interaction.first_name,
                "last_name": first_interaction.last_name
            },
            "interaction_summary": {
                "total_interactions": len(interactions),
                "first_interaction": interactions[0].created_at.isoformat(),
                "last_interaction": interactions[-1].created_at.isoformat(),
                "interaction_counts": interaction_counts
            },
            "conversion_status": {
                "is_registered": user_record is not None,
                "is_client": user_record is not None and user_record.role == models.UserRole.client,
                "has_subscription": subscription_info is not None,
                "subscription_info": subscription_info
            },
            "detailed_interactions": [
                {
                    "type": interaction.interaction_type,
                    "timestamp": interaction.created_at.isoformat(),
                    "additional_data": interaction.additional_data
                }
                for interaction in interactions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user journey: {str(e)}") 