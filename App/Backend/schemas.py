from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================

class UserRole(str, Enum):
    client = "client"
    assistant = "assistant"
    manager = "manager"

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    approved = "approved"
    revision_requested = "revision_requested"
    cancelled = "cancelled"
    rejected = "rejected"

class TaskType(str, Enum):
    personal = "personal"
    business = "business"

class SubscriptionPlan(str, Enum):
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

class SubscriptionStatus(str, Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class AssistantSpecialization(str, Enum):
    personal_only = "personal_only"
    business_only = "business_only"
    full_access = "full_access"

class AssistantStatus(str, Enum):
    online = "online"
    offline = "offline"

# =============================================================================
# BASE USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    name: str
    phone: str
    telegram_username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserLogin(BaseModel):
    phone: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    role: UserRole
    telegram_username: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# CLIENT SCHEMAS
# =============================================================================

class ClientRegister(BaseModel):
    name: str
    phone: str
    password: str
    telegram_username: Optional[str] = None

class ClientProfile(BaseModel):
    id: int
    email: Optional[str]
    
    class Config:
        from_attributes = True

class ClientOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    phone: str
    telegram_username: Optional[str]
    subscription: Optional["SubscriptionOut"]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Client task type permissions
class TaskTypePermissions(BaseModel):
    allowed_types: List[TaskType]
    plan_type: str  # "personal", "business", "full", "none"
    subscription_plan: str
    can_choose_type: bool
    message: str

# =============================================================================
# ASSISTANT SCHEMAS
# =============================================================================

class AssistantLogin(BaseModel):
    email: str
    password: str

class AssistantProfile(BaseModel):
    specialization: AssistantSpecialization
    status: AssistantStatus
    
class AssistantOut(BaseModel):
    id: int
    name: str
    email: str
    telegram_username: Optional[str]
    password: Optional[str] = None  # Password visible only to managers
    specialization: AssistantSpecialization
    status: AssistantStatus
    current_active_tasks: int
    total_tasks_completed: int
    average_rating: float
    
    class Config:
        from_attributes = True

class AssistantSummary(BaseModel):
    id: int
    name: str
    telegram_username: Optional[str]
    specialization: AssistantSpecialization
    
    class Config:
        from_attributes = True

# =============================================================================
# MANAGER SCHEMAS
# =============================================================================

class ManagerLogin(BaseModel):
    email: str
    password: str

class ManagerOut(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str]
    
    class Config:
        from_attributes = True

# =============================================================================
# SUBSCRIPTION SCHEMAS
# =============================================================================

class SubscriptionOut(BaseModel):
    id: int
    plan: SubscriptionPlan
    status: SubscriptionStatus
    started_at: datetime
    expires_at: Optional[datetime]
    auto_renew: bool
    
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan
    payment_token: str

class SubscriptionPlanInfo(BaseModel):
    name: str
    plan: SubscriptionPlan
    price: int  # kopecks per month
    features: List[str]
    task_types: List[TaskType]

# =============================================================================
# TASK SCHEMAS (Simplified - no priority/speed)
# =============================================================================

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: TaskType

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: TaskType
    status: TaskStatus
    created_at: datetime
    deadline: Optional[datetime]
    claimed_at: Optional[datetime]
    completed_at: Optional[datetime]
    approved_at: Optional[datetime]
    result: Optional[str]
    completion_notes: Optional[str]
    revision_notes: Optional[str]
    client_rating: Optional[int]
    client_feedback: Optional[str]
    client_id: int
    assistant_id: Optional[int]
    
    class Config:
        from_attributes = True

class TaskWithClient(TaskOut):
    client: ClientProfile
    
class TaskWithAssistant(TaskOut):
    assistant: Optional[AssistantSummary]

class TaskWithDetails(TaskOut):
    client: ClientProfile
    assistant: Optional[AssistantSummary]

# Task marketplace view for assistants
class TaskMarketplace(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: TaskType
    client_name: str  # First name only
    created_at: datetime
    deadline: Optional[datetime]
    time_remaining: str
    
    class Config:
        from_attributes = True

# Task completion by assistant
class TaskComplete(BaseModel):
    completion_summary: str
    detailed_result: str
    recommendation: Optional[str] = None
    next_steps_for_client: Optional[str] = None

# Task approval/rejection by client
class TaskApproval(BaseModel):
    rating: int  # 1-5 stars
    feedback: str

class TaskRevision(BaseModel):
    feedback: str
    additional_requirements: Optional[str] = None

# Task rejection by assistant
class TaskReject(BaseModel):
    reason: str

# =============================================================================
# MESSAGE SCHEMAS
# =============================================================================

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    content: str
    sender_id: int
    sender_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# ANALYTICS SCHEMAS
# =============================================================================

class TaskStats(BaseModel):
    pending: int
    in_progress: int
    completed: int
    approved: int
    total: int

class AssistantStats(BaseModel):
    total_active: int
    online_now: int
    with_active_tasks: int
    avg_tasks_per_assistant: float

class ClientStats(BaseModel):
    total_active: int
    new_registrations: int
    active_subscribers: int
    subscription_distribution: dict

class RevenueStats(BaseModel):
    new_subscriptions_today: int
    subscription_revenue_today: int
    monthly_recurring_revenue: int
    churn_rate: float

class OverviewAnalytics(BaseModel):
    tasks: TaskStats
    assistants: AssistantStats
    clients: ClientStats
    revenue: RevenueStats

# =============================================================================
# RESPONSE WRAPPERS
# =============================================================================

class StandardResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime = datetime.utcnow()

class DataResponse(StandardResponse):
    data: dict

class ErrorResponse(StandardResponse):
    error: str
    details: Optional[dict] = None

class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool
    next_offset: Optional[int] = None

class PaginatedResponse(DataResponse):
    pagination: PaginationInfo

