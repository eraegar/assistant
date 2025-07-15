from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# User role enums
class UserRole(enum.Enum):
    client = "client"
    assistant = "assistant"
    manager = "manager"

# Task enums (simplified - no priority/speed)
class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    approved = "approved"
    revision_requested = "revision_requested"
    cancelled = "cancelled"
    rejected = "rejected"

class TaskType(enum.Enum):
    personal = "personal"
    business = "business"

# Subscription enums
class SubscriptionPlan(enum.Enum):
    none = "none"
    personal_2h = "personal_2h"
    personal_5h = "personal_5h"
    personal_8h = "personal_8h"
    business_2h = "business_2h"
    business_5h = "business_5h"
    business_8h = "business_8h"
    full_2h = "full_2h"
    full_5h = "full_5h"
    full_8h = "full_8h"

class SubscriptionStatus(enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

# Assistant specialization
class AssistantSpecialization(enum.Enum):
    personal_only = "personal_only"
    business_only = "business_only"
    full_access = "full_access"

# Client-Assistant assignment status
class AssignmentStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

# Base User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    telegram_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Polymorphic relationships
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    assistant_profile = relationship("AssistantProfile", back_populates="user", uselist=False)
    manager_profile = relationship("ManagerProfile", back_populates="user", uselist=False)

# Client-specific profile
class ClientProfile(Base):
    __tablename__ = "client_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="client_profile")
    tasks = relationship("Task", back_populates="client")
    subscription = relationship("Subscription", back_populates="client", uselist=False)
    assigned_assistants = relationship("ClientAssistantAssignment", back_populates="client")

# Assistant-specific profile
class AssistantProfile(Base):
    __tablename__ = "assistant_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email = Column(String, nullable=False)
    specialization = Column(Enum(AssistantSpecialization), default=AssistantSpecialization.personal_only)
    status = Column(String, default="offline")  # online/offline
    current_active_tasks = Column(Integer, default=0)
    
    # Performance metrics
    total_tasks_completed = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Last known password (for management purposes only)
    last_known_password = Column(String, nullable=True)  # Stores password after creation/reset
    last_password_reset_at = Column(DateTime, nullable=True)  # When password was last reset
    
    # Relationships
    user = relationship("User", back_populates="assistant_profile")
    assigned_tasks = relationship("Task", back_populates="assistant")
    assigned_clients = relationship("ClientAssistantAssignment", back_populates="assistant")

# Manager-specific profile  
class ManagerProfile(Base):
    __tablename__ = "manager_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email = Column(String, nullable=False)
    department = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="manager_profile")

# Subscription model
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client_profiles.id"))
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.active)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    
    # Relationships
    client = relationship("ClientProfile", back_populates="subscription")

# Task model (simplified)
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    
    # Relationships
    client_id = Column(Integer, ForeignKey("client_profiles.id"))
    assistant_id = Column(Integer, ForeignKey("assistant_profiles.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)  # 24h from creation
    claimed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)  # When task was rejected by assistant
    
    # Task content
    result = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    revision_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)  # Reason for rejection by assistant
    
    # Client feedback
    client_rating = Column(Integer, nullable=True)  # 1-5 stars
    client_feedback = Column(Text, nullable=True)
    
    # Relationships
    client = relationship("ClientProfile", back_populates="tasks")
    assistant = relationship("AssistantProfile", back_populates="assigned_tasks")
    messages = relationship("Message", back_populates="task")

# Message model for task communication
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="messages")
    sender = relationship("User")

# File attachment model
class FileAttachment(Base):
    __tablename__ = "file_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task")
    uploader = relationship("User")

# Client-Assistant permanent assignment model
class ClientAssistantAssignment(Base):
    __tablename__ = "client_assistant_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client_profiles.id"), nullable=False)
    assistant_id = Column(Integer, ForeignKey("assistant_profiles.id"), nullable=False)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.active)
    is_primary = Column(Boolean, default=False)  # Indicates if this is the main assistant for client communication
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("manager_profiles.id"), nullable=True)  # Manager who created the assignment
    
    # Task type restrictions based on assistant specialization and client subscription
    allowed_task_types = Column(String, nullable=True)  # JSON string like '["personal"]' or '["personal", "business"]'
    
    # Relationships
    client = relationship("ClientProfile", back_populates="assigned_assistants")
    assistant = relationship("AssistantProfile", back_populates="assigned_clients")
    created_by_manager = relationship("ManagerProfile")

# Telegram Bot Analytics model
class TelegramAnalytics(Base):
    __tablename__ = "telegram_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(String, nullable=False, index=True)  # Telegram user ID
    username = Column(String, nullable=True)  # Telegram username
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Interaction tracking
    action = Column(String, nullable=False)  # 'start', 'view_pricing', 'view_examples', 'contact_support', etc.
    action_data = Column(Text, nullable=True)  # JSON data with additional context
    session_id = Column(String, nullable=True)  # Session identifier for grouping interactions
    
    # User state tracking  
    is_registered_user = Column(Boolean, default=False)  # Whether user is registered in our system
    user_role = Column(String, nullable=True)  # 'client', 'assistant', 'manager' if registered
    subscription_plan = Column(String, nullable=True)  # Current subscription plan if client
    
    # Conversion funnel tracking
    conversion_stage = Column(String, nullable=True)  # 'viewed_pricing', 'clicked_register', 'completed_registration', etc.
    referrer = Column(String, nullable=True)  # How user found the bot
    utm_source = Column(String, nullable=True)  # UTM tracking parameters
    utm_campaign = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # IP and device info (optional)
    user_agent = Column(String, nullable=True)
    language_code = Column(String, nullable=True)  # User's language preference

# Manager Notification System models
class NotificationType(enum.Enum):
    POTENTIAL_CLIENT_ENGAGED = "potential_client_engaged"
    PRICING_VIEWED_NO_REGISTRATION = "pricing_viewed_no_registration"
    MULTIPLE_SESSIONS_NO_REGISTRATION = "multiple_sessions_no_registration"
    HIGH_ENGAGEMENT_NO_CONVERSION = "high_engagement_no_conversion"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    IN_APP = "in_app"
    SMS = "sms"

class ManagerNotificationPreference(Base):
    __tablename__ = "manager_notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("manager_profiles.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Threshold settings for triggering notifications
    threshold_settings = Column(Text, nullable=True)  # JSON with specific thresholds
    
    # Schedule settings for periodic notifications
    schedule_hour = Column(Integer, nullable=True)  # Hour of day for daily/weekly summaries (0-23)
    schedule_day_of_week = Column(Integer, nullable=True)  # Day of week for weekly (0=Monday, 6=Sunday)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("ManagerProfile")
    
    # Unique constraint: one preference per manager/type/channel combination
    __table_args__ = (
        UniqueConstraint('manager_id', 'notification_type', 'channel', name='unique_manager_notification_preference'),
    )

class NotificationHistory(Base):
    __tablename__ = "notification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("manager_profiles.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    # Notification content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Related data
    related_telegram_user_id = Column(String, nullable=True)  # If related to specific user
    related_data = Column(Text, nullable=True)  # JSON with additional context
    
    # Delivery tracking
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    status = Column(String, default="sent")  # sent, delivered, read, failed
    
    # Delivery details
    delivery_details = Column(Text, nullable=True)  # JSON with delivery info (email address, telegram chat_id, etc.)
    
    # Relationships
    manager = relationship("ManagerProfile")

class PotentialClientAlert(Base):
    __tablename__ = "potential_client_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Engagement metrics
    total_interactions = Column(Integer, default=0)
    first_interaction_at = Column(DateTime, nullable=False)
    last_interaction_at = Column(DateTime, nullable=False)
    total_sessions = Column(Integer, default=1)
    
    # Key actions performed
    viewed_pricing = Column(Boolean, default=False)
    viewed_examples = Column(Boolean, default=False)
    contacted_support = Column(Boolean, default=False)
    clicked_register = Column(Boolean, default=False)
    
    # Engagement score (calculated based on actions and frequency)
    engagement_score = Column(Float, default=0.0)
    
    # Alert status
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime, nullable=True)
    managers_notified = Column(Text, nullable=True)  # JSON list of manager IDs notified
    
    # Follow-up tracking
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text, nullable=True)
    assigned_manager_id = Column(Integer, ForeignKey("manager_profiles.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_manager = relationship("ManagerProfile")