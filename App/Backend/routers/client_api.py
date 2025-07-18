from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

import models, schemas, database, auth

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_client(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Ensure the current user is a client, loaded in the current DB session"""
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user or user.role != models.UserRole.client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Client role required."
        )
    if not user.client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    return user

def check_subscription_for_task_type(client: models.User, task_type: schemas.TaskType):
    """Check if client's subscription allows the task type"""
    if not client.client_profile.subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required to create tasks"
        )
    
    subscription = client.client_profile.subscription
    if subscription.status != models.SubscriptionStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required to create tasks"
        )
    
    # Check task type permissions based on subscription plan
    plan = subscription.plan
    
    # Personal plans (personal_2h, personal_5h, personal_8h) - only personal tasks
    if plan in [models.SubscriptionPlan.personal_2h, models.SubscriptionPlan.personal_5h, models.SubscriptionPlan.personal_8h]:
        if task_type == schemas.TaskType.business:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Personal subscription plans only allow personal tasks. Upgrade to Business or Full plan for business tasks.",
                headers={"required_plans": "business,full", "current_plan": plan.value}
            )
    
    # Business plans (business_2h, business_5h, business_8h) - only business tasks
    elif plan in [models.SubscriptionPlan.business_2h, models.SubscriptionPlan.business_5h, models.SubscriptionPlan.business_8h]:
        if task_type == schemas.TaskType.personal:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Business subscription plans only allow business tasks. Upgrade to Full plan for personal tasks.",
                headers={"required_plans": "full", "current_plan": plan.value}
            )
    
    # Full plans (full_2h, full_5h, full_8h) - both personal and business tasks allowed
    # No restrictions for full plans

# =============================================================================
# AUTHENTICATION & PROFILE
# =============================================================================

@router.post("/auth/register", response_model=schemas.ClientOut)
def register_client(client_data: schemas.ClientRegister, db: Session = Depends(get_db)):
    """Register a new client"""
    # Check if phone already exists
    existing_user = db.query(models.User).filter(models.User.phone == client_data.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    hashed_password = auth.get_password_hash(client_data.password)
    db_user = models.User(
        phone=client_data.phone,
        name=client_data.name,
        password_hash=hashed_password,
        role=models.UserRole.client,
        telegram_username=client_data.telegram_username
    )
    db.add(db_user)
    db.flush()
    
    # Create client profile
    client_profile = models.ClientProfile(user_id=db_user.id)
    db.add(client_profile)
    
    db.commit()
    db.refresh(db_user)
    
    return schemas.ClientOut(
        id=db_user.id,
        name=db_user.name,
        email=None,
        phone=db_user.phone,
        telegram_username=db_user.telegram_username,
        subscription=None,
        created_at=db_user.created_at
    )

@router.post("/auth/login")
def login_client(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Client login"""
    user = db.query(models.User).filter(
        models.User.phone == credentials.phone,
        models.User.role == models.UserRole.client
    ).first()
    
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    
    token = auth.create_access_token({"user_id": user.id, "role": "client"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.ClientOut)
def get_client_profile(current_client: models.User = Depends(get_current_client)):
    """Get client profile with subscription info"""
    subscription = None
    if current_client.client_profile.subscription:
        subscription = schemas.SubscriptionOut.from_orm(current_client.client_profile.subscription)
    
    return schemas.ClientOut(
        id=current_client.id,
        name=current_client.name,
        email=current_client.client_profile.email,
        phone=current_client.phone,
        telegram_username=current_client.telegram_username,
        subscription=subscription,
        created_at=current_client.created_at
    )

@router.put("/profile")
def update_client_profile(
    profile_update: dict,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Update client profile"""
    if "name" in profile_update:
        current_client.name = profile_update["name"]
    if "telegram_username" in profile_update:
        current_client.telegram_username = profile_update["telegram_username"]
    if "email" in profile_update:
        current_client.client_profile.email = profile_update["email"]
    
    db.commit()
    return {"success": True, "message": "Profile updated successfully"}

# =============================================================================
# SUBSCRIPTION MANAGEMENT
# =============================================================================

@router.get("/subscription", response_model=schemas.SubscriptionOut)
def get_subscription(current_client: models.User = Depends(get_current_client)):
    """Get current subscription"""
    if not current_client.client_profile.subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return schemas.SubscriptionOut.from_orm(current_client.client_profile.subscription)

@router.get("/subscription/task-types")
def get_allowed_task_types(current_client: models.User = Depends(get_current_client)):
    """Get allowed task types based on current subscription"""
    if not current_client.client_profile.subscription:
        return {"allowed_types": [], "plan_type": "none", "subscription_plan": "none", "can_choose_type": False, "message": "No active subscription"}
    
    subscription = current_client.client_profile.subscription
    if subscription.status != models.SubscriptionStatus.active:
        return {"allowed_types": [], "plan_type": "none", "subscription_plan": subscription.plan.value, "can_choose_type": False, "message": "Subscription not active"}
    
    plan = subscription.plan
    
    # Determine allowed task types based on subscription plan
    if plan in [models.SubscriptionPlan.personal_2h, models.SubscriptionPlan.personal_5h, models.SubscriptionPlan.personal_8h]:
        allowed_types = ["personal"]
        plan_type = "personal"
    elif plan in [models.SubscriptionPlan.business_2h, models.SubscriptionPlan.business_5h, models.SubscriptionPlan.business_8h]:
        allowed_types = ["business"] 
        plan_type = "business"
    elif plan in [models.SubscriptionPlan.full_2h, models.SubscriptionPlan.full_5h, models.SubscriptionPlan.full_8h]:
        allowed_types = ["personal", "business"]
        plan_type = "full"
    else:
        allowed_types = []
        plan_type = "none"
    
    return {
        "allowed_types": allowed_types,
        "plan_type": plan_type,
        "subscription_plan": plan.value,
        "can_choose_type": len(allowed_types) > 1,
        "message": "success"
    }

@router.get("/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    print("📋 Subscription plans request")
    
    plans = [
        {
            "id": "personal_2h",
            "name": "Личный ассистент",
            "description": "2 часа работы в день",
            "subtitle": "Идеально для личных задач и повседневной помощи",
            "price": 15000,  # 15,000 рублей
            "price_formatted": "15 000 ₽/месяц",
            "hours_per_day": 2,
            "features": [
                "До 2 часов работы в день",
                "Неограниченные личные задачи",
                "Гарантия выполнения за 24 часа",
                "Прямое общение с ассистентами",
                "Поддержка по email",
                "История задач и отслеживание"
            ],
            "task_types": ["personal"],
            "popular": False
        },
        {
            "id": "personal_5h", 
            "name": "Личный ассистент",
            "description": "5 часов работы в день",
            "subtitle": "Идеально для личных задач и повседневной помощи",
            "price": 30000,  # 30,000 рублей
            "price_formatted": "30 000 ₽/месяц",
            "hours_per_day": 5,
            "features": [
                "До 5 часов работы в день",
                "Неограниченные личные задачи", 
                "Гарантия выполнения за 24 часа",
                "Прямое общение с ассистентами",
                "Поддержка по email",
                "История задач и отслеживание"
            ],
            "task_types": ["personal"],
            "popular": True
        },
        {
            "id": "personal_8h",
            "name": "Личный ассистент", 
            "description": "8 часов работы в день",
            "subtitle": "Идеально для личных задач и повседневной помощи",
            "price": 50000,  # 50,000 рублей
            "price_formatted": "50 000 ₽/месяц",
            "hours_per_day": 8,
            "features": [
                "До 8 часов работы в день",
                "Неограниченные личные задачи",
                "Гарантия выполнения за 24 часа",
                "Прямое общение с ассистентами",
                "Поддержка по email",
                "История задач и отслеживание"
            ],
            "task_types": ["personal"],
            "popular": False
        },
        {
            "id": "business_2h",
            "name": "Бизнес ассистент",
            "description": "2 часов работы в день", 
            "subtitle": "Идеально для бизнес-профессионалов и предпринимателей",
            "price": 30000,  # 30,000 рублей
            "price_formatted": "30 000 ₽/месяц",
            "hours_per_day": 2,
            "features": [
                "До 2 часов работы в день",
                "Неограниченные бизнес-задачи",
                "Гарантия выполнения за 24 часа", 
                "Приоритетный подбор ассистентов",
                "Бизнес-специализированные ассистенты",
                "Расширенная отчетность",
                "Приоритетная поддержка"
            ],
            "task_types": ["business"],
            "popular": True
        },
        {
            "id": "business_5h",
            "name": "Бизнес ассистент",
            "description": "5 часов работы в день",
            "subtitle": "Идеально для бизнес-профессионалов и предпринимателей", 
            "price": 60000,  # 60,000 рублей
            "price_formatted": "60 000 ₽/месяц",
            "hours_per_day": 5,
            "features": [
                "До 5 часов работы в день",
                "Неограниченные бизнес-задачи",
                "Гарантия выполнения за 24 часа",
                "Приоритетный подбор ассистентов", 
                "Бизнес-специализированные ассистенты",
                "Расширенная отчетность",
                "Приоритетная поддержка"
            ],
            "task_types": ["business"],
            "popular": False
        },
        {
            "id": "business_8h",
            "name": "Бизнес ассистент",
            "description": "8 часов работы в день",
            "subtitle": "Идеально для бизнес-профессионалов и предпринимателей",
            "price": 80000,  # 80,000 рублей  
            "price_formatted": "80 000 ₽/месяц",
            "hours_per_day": 8,
            "features": [
                "До 8 часов работы в день",
                "Неограниченные бизнес-задачи",
                "Гарантия выполнения за 24 часа",
                "Приоритетный подбор ассистентов",
                "Бизнес-специализированные ассистенты", 
                "Расширенная отчетность",
                "Приоритетная поддержка"
            ],
            "task_types": ["business"],
            "popular": False
        },
        {
            "id": "full_2h",
            "name": "Личный + Бизнес ассистент",
            "description": "2 часов работы в день",
            "subtitle": "Полный доступ ко всем типам задач и премиум-функциям",
            "price": 40000,  # 40,000 рублей
            "price_formatted": "40 000 ₽/месяц", 
            "hours_per_day": 2,
            "features": [
                "До 2 часов работы в день",
                "Неограниченные личные и бизнес-задачи",
                "Гарантия выполнения за 24 часа",
                "Приоритетный подбор ассистентов",
                "Все специализации ассистентов",
                "Расширенная аналитика",
                "Доступ к API"
            ],
            "task_types": ["personal", "business"],
            "popular": False
        },
        {
            "id": "full_5h",
            "name": "Личный + Бизнес ассистент",
            "description": "5 часов работы в день", 
            "subtitle": "Полный доступ ко всем типам задач и премиум-функциям",
            "price": 80000,  # 80,000 рублей
            "price_formatted": "80 000 ₽/месяц",
            "hours_per_day": 5,
            "features": [
                "До 5 часов работы в день",
                "Неограниченные личные и бизнес-задачи",
                "Гарантия выполнения за 24 часа",
                "Приоритетный подбор ассистентов",
                "Все специализации ассистентов",
                "Расширенная аналитика", 
                "Доступ к API"
            ],
            "task_types": ["personal", "business"],
            "popular": False
        },
        {
            "id": "full_8h",
            "name": "Личный + Бизнес ассистент",
            "description": "8 часов работы в день",
            "subtitle": "Полный доступ ко всем типам задач и премиум-функциям",
            "price": 100000,  # 100,000 рублей
            "price_formatted": "100 000 ₽/месяц",
            "hours_per_day": 8,
            "features": [
                "До 8 часов работы в день",
                "Неограниченные личные и бизнес-задачи",
                "Гарантия выполнения за 24 часа",
                "Приоритетный подбор ассистентов",
                "Все специализации ассистентов",
                "Расширенная аналитика",
                "Доступ к API"
            ],
            "task_types": ["personal", "business"],
            "popular": False
        }
    ]
    
    return {"plans": plans}

@router.post("/subscription/upgrade")
def upgrade_subscription(
    subscription_data: schemas.SubscriptionCreate,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Upgrade client subscription"""
    # Cancel existing subscription if any
    client_profile = current_client.client_profile
    if client_profile.subscription:
        client_profile.subscription.status = models.SubscriptionStatus.cancelled
    
    # Create new subscription
    new_subscription = models.Subscription(
        client_id=current_client.client_profile.id,
        plan=subscription_data.plan,
        status=models.SubscriptionStatus.active,
        started_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        auto_renew=True
    )
    
    # Assign the new subscription to the client's profile
    client_profile.subscription = new_subscription
    
    db.commit()
    # Refresh the client_profile to load the new subscription relationship
    db.refresh(client_profile)
    db.refresh(new_subscription)
    
    return {"success": True, "message": f"Subscription upgraded to {subscription_data.plan.value}"}

# =============================================================================
# TASK MANAGEMENT
# =============================================================================

@router.post("/tasks", response_model=schemas.TaskOut)
def create_task(
    task_data: schemas.TaskCreate,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    from services.task_assignment import TaskAssignmentService
    
    # Check subscription permissions
    check_subscription_for_task_type(current_client, task_data.type)
    
    # Create task with 24h deadline
    deadline = datetime.utcnow() + timedelta(hours=24)
    
    db_task = models.Task(
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        client_id=current_client.client_profile.id,
        deadline=deadline
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Try automatic assignment
    assignment_service = TaskAssignmentService(db)
    success = assignment_service.auto_assign_task(db_task)
    
    if not success:
        # Send to marketplace if no assistant available
        assignment_service.send_to_marketplace(db_task)
    
    # Refresh task to get updated status
    db.refresh(db_task)
    
    return schemas.TaskOut.from_orm(db_task)

@router.get("/tasks", response_model=List[schemas.TaskOut])
def get_client_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[schemas.TaskStatus] = None,
    type: Optional[schemas.TaskType] = None,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get client's tasks with filtering"""
    query = db.query(models.Task).filter(models.Task.client_id == current_client.client_profile.id)
    
    if status:
        query = query.filter(models.Task.status == status)
    if type:
        query = query.filter(models.Task.type == type)
    
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    return [schemas.TaskOut.from_orm(task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=schemas.TaskWithAssistant)
def get_task(
    task_id: int,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get specific task details"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Include assistant info if assigned
    task_data = schemas.TaskOut.from_orm(task)
    assistant_data = None
    if task.assistant:
        assistant_data = schemas.AssistantSummary(
            id=task.assistant.id,
            name=task.assistant.user.name,
            telegram_username=task.assistant.user.telegram_username,
            specialization=task.assistant.specialization
        )
    
    return schemas.TaskWithAssistant(
        **task_data.dict(),
        assistant=assistant_data
    )

@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Update task (only if not claimed)"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.pending:
        raise HTTPException(status_code=400, detail="Can only update pending tasks")
    
    # Update allowed fields
    if task_update.title:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    
    db.commit()
    return {"success": True, "message": "Task updated successfully"}

@router.delete("/tasks/{task_id}")
def cancel_task(
    task_id: int,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Cancel task (only if not claimed)"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.pending:
        raise HTTPException(status_code=400, detail="Can only cancel pending tasks")
    
    task.status = models.TaskStatus.cancelled
    db.commit()
    
    return {"success": True, "message": "Task cancelled successfully"}

# =============================================================================
# TASK INTERACTION
# =============================================================================

@router.post("/tasks/{task_id}/approve")
def approve_task(
    task_id: int,
    approval: schemas.TaskApproval,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Approve completed task"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.completed:
        raise HTTPException(status_code=400, detail="Task must be completed to approve")
    
    # Update task with approval
    task.status = models.TaskStatus.approved
    task.approved_at = datetime.utcnow()
    task.client_rating = approval.rating
    task.client_feedback = approval.feedback
    
    # Update assistant stats
    if task.assistant:
        task.assistant.total_tasks_completed += 1
        # Recalculate average rating (simplified)
        # In real implementation, you'd want a more sophisticated rating calculation
    
    db.commit()
    
    return {"success": True, "message": "Task approved successfully"}

@router.post("/tasks/{task_id}/request-revision")
def request_revision(
    task_id: int,
    revision: schemas.TaskRevision,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Request task revision"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.completed:
        raise HTTPException(status_code=400, detail="Task must be completed to request revision")
    
    # Update task status and add revision notes
    task.status = models.TaskStatus.revision_requested
    task.revision_notes = revision.feedback
    if revision.additional_requirements:
        task.description += f"\n\nAdditional requirements: {revision.additional_requirements}"
    
    db.commit()
    
    return {"success": True, "message": "Revision request sent to assistant"}

@router.get("/tasks/{task_id}/messages", response_model=List[schemas.MessageOut])
def get_task_messages(
    task_id: int,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get task messages"""
    # Verify task ownership
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    messages = db.query(models.Message).filter(models.Message.task_id == task_id).order_by(models.Message.created_at).all()
    
    return [
        schemas.MessageOut(
            id=msg.id,
            content=msg.content,
            sender_id=msg.sender_id,
            sender_name=msg.sender.name,
            created_at=msg.created_at
        ) for msg in messages
    ]

@router.post("/tasks/{task_id}/message")
def send_task_message(
    task_id: int,
    message: schemas.MessageCreate,
    current_client: models.User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Send message to assistant"""
    # Verify task ownership
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.client_id == current_client.client_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status == models.TaskStatus.pending:
        raise HTTPException(status_code=400, detail="Cannot send messages to unclaimed tasks")
    
    # Create message
    db_message = models.Message(
        task_id=task_id,
        sender_id=current_client.id,
        content=message.content
    )
    
    db.add(db_message)
    db.commit()
    
    return {"success": True, "message": "Message sent to assistant"} 