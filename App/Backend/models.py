from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("manager_profiles.id"), nullable=True)  # Manager who created the assignment
    
    # Task type restrictions based on assistant specialization and client subscription
    allowed_task_types = Column(String, nullable=True)  # JSON string like '["personal"]' or '["personal", "business"]'
    
    # Assignment type: main assistant is the primary contact, others are secondary
    is_primary = Column(Boolean, default=False)  # True for main assistant, False for secondary
    
    # Relationships
    client = relationship("ClientProfile", back_populates="assigned_assistants")
    assistant = relationship("AssistantProfile", back_populates="assigned_clients")
    created_by_manager = relationship("ManagerProfile")