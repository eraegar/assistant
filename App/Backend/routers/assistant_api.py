from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

import models, schemas, database, auth

router = APIRouter(prefix="/api/v1/assistants", tags=["assistants"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_assistant(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Ensure the current user is an assistant, loaded in the current DB session"""
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user or user.role != models.UserRole.assistant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Assistant role required."
        )
    if not user.assistant_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant profile not found"
        )
    return user

def format_time_remaining(deadline: datetime) -> str:
    """Format time remaining until deadline"""
    if not deadline:
        return "No deadline"
    
    time_diff = deadline - datetime.utcnow()
    if time_diff.total_seconds() <= 0:
        return "Overdue"
    
    hours = int(time_diff.total_seconds() // 3600)
    minutes = int((time_diff.total_seconds() % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def can_claim_task(assistant: models.AssistantProfile, task: models.Task) -> bool:
    """Check if assistant can claim a specific task"""
    # Check specialization
    if (task.type == models.TaskType.business and 
        assistant.specialization == models.AssistantSpecialization.personal_only):
        return False
    
    # Check if assistant is online
    if assistant.status != "online":
        return False
    
    return True

# =============================================================================
# AUTHENTICATION & PROFILE
# =============================================================================

@router.post("/auth/register", response_model=schemas.AssistantOut)
def register_assistant(assistant_data: dict, db: Session = Depends(get_db)):
    """Register a new assistant"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.phone == assistant_data["phone"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    hashed_password = auth.get_password_hash(assistant_data["password"])
    db_user = models.User(
        phone=assistant_data["phone"],
        name=assistant_data["name"],
        password_hash=hashed_password,
        role=models.UserRole.assistant,
        telegram_username=assistant_data.get("telegram_username")
    )
    db.add(db_user)
    db.flush()
    
    # Create assistant profile
    specialization = assistant_data.get("specialization", "personal_only")
    if specialization not in [spec.value for spec in models.AssistantSpecialization]:
        specialization = "personal_only"
    
    assistant_profile = models.AssistantProfile(
        user_id=db_user.id,
        email=assistant_data["email"],
        specialization=getattr(models.AssistantSpecialization, specialization),
        status="offline"
    )
    db.add(assistant_profile)
    
    db.commit()
    db.refresh(db_user)
    
    return schemas.AssistantOut(
        id=db_user.id,
        name=db_user.name,
        email=assistant_profile.email,
        telegram_username=db_user.telegram_username,
        specialization=assistant_profile.specialization,
        status=assistant_profile.status,
        current_active_tasks=0,
        total_tasks_completed=0,
        average_rating=0.0
    )

@router.post("/auth/login")
def login_assistant(credentials: dict, db: Session = Depends(get_db)):
    """Assistant login"""
    user = db.query(models.User).filter(
        models.User.phone == credentials["phone"],
        models.User.role == models.UserRole.assistant
    ).first()
    
    if not user or not auth.verify_password(credentials["password"], user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    
    token = auth.create_access_token({"user_id": user.id, "role": "assistant"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.AssistantOut)
def get_assistant_profile(current_assistant: models.User = Depends(get_current_assistant)):
    """Get assistant profile"""
    profile = current_assistant.assistant_profile
    
    return schemas.AssistantOut(
        id=current_assistant.id,
        name=current_assistant.name,
        email=profile.email,
        telegram_username=current_assistant.telegram_username,
        specialization=profile.specialization,
        status=profile.status,
        current_active_tasks=profile.current_active_tasks,
        total_tasks_completed=profile.total_tasks_completed,
        average_rating=profile.average_rating
    )

@router.put("/profile/status")
def update_assistant_status(
    status_data: dict,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Update assistant online/offline status"""
    new_status = status_data.get("status", "offline")
    if new_status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="Status must be 'online' or 'offline'")
    
    current_assistant.assistant_profile.status = new_status
    current_assistant.last_active = datetime.utcnow()
    
    db.commit()
    return {"success": True, "message": f"Status updated to {new_status}"}

# =============================================================================
# TASK MARKETPLACE
# =============================================================================

@router.get("/tasks/marketplace", response_model=List[schemas.TaskMarketplace])
def get_marketplace_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    task_type: Optional[schemas.TaskType] = None,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Get available tasks in marketplace"""
    query = db.query(models.Task).filter(
        models.Task.status == models.TaskStatus.pending,
        models.Task.assistant_id.is_(None)  # Unclaimed tasks
    )
    
    # Filter by task type based on assistant specialization
    assistant_spec = current_assistant.assistant_profile.specialization
    if assistant_spec == models.AssistantSpecialization.personal_only:
        query = query.filter(models.Task.type == models.TaskType.personal)
    # Business specialists can handle both personal and business tasks
    
    if task_type:
        query = query.filter(models.Task.type == task_type)
    
    tasks = query.order_by(models.Task.created_at.asc()).offset(skip).limit(limit).all()
    
    marketplace_tasks = []
    for task in tasks:
        # Calculate time remaining
        if task.deadline:
            time_remaining = task.deadline - datetime.utcnow()
            if time_remaining.total_seconds() > 0:
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                time_remaining_str = f"{hours}ч {minutes}м"
            else:
                time_remaining_str = "Просрочено"
        else:
            time_remaining_str = "Без дедлайна"
        
        marketplace_tasks.append(schemas.TaskMarketplace(
            id=task.id,
            title=task.title,
            description=task.description,
            type=task.type,
            client_name=task.client.user.name.split()[0],  # First name only
            created_at=task.created_at,
            deadline=task.deadline,
            time_remaining=time_remaining_str
        ))
    
    return marketplace_tasks

@router.post("/tasks/{task_id}/claim")
def claim_task(
    task_id: int,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Claim a task from marketplace"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.status == models.TaskStatus.pending,
        models.Task.assistant_id.is_(None)
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or already claimed")
    
    # Check if assistant can handle this task type
    assistant_spec = current_assistant.assistant_profile.specialization
    if (assistant_spec == models.AssistantSpecialization.personal_only and 
        task.type == models.TaskType.business):
        raise HTTPException(
            status_code=403, 
            detail="Personal assistants cannot claim business tasks"
        )
    
    # Claim the task
    task.assistant_id = current_assistant.assistant_profile.id
    task.status = models.TaskStatus.in_progress
    task.claimed_at = datetime.utcnow()
    
    # Update assistant stats
    current_assistant.assistant_profile.current_active_tasks += 1
    
    db.commit()
    
    return {"success": True, "message": "Task claimed successfully"}

# =============================================================================
# ASSIGNED TASKS MANAGEMENT
# =============================================================================

@router.get("/tasks/assigned", response_model=List[schemas.TaskOut])
def get_assigned_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[schemas.TaskStatus] = None,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current assistant"""
    query = db.query(models.Task).filter(
        models.Task.assistant_id == current_assistant.assistant_profile.id
    )
    
    if status:
        query = query.filter(models.Task.status == status)
    
    tasks = query.order_by(models.Task.claimed_at.desc()).offset(skip).limit(limit).all()
    return [schemas.TaskOut.from_orm(task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=schemas.TaskWithClient)
def get_task_details(
    task_id: int,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Get detailed task information"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Include client info
    task_data = schemas.TaskOut.from_orm(task)
    client_data = schemas.ClientProfile(
        id=task.client.id,
        email=task.client.email
    )
    
    return schemas.TaskWithClient(
        **task_data.dict(),
        client=client_data
    )

@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    completion_data: schemas.TaskComplete,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Mark task as completed with results"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id,
        models.Task.status.in_([models.TaskStatus.in_progress, models.TaskStatus.revision_requested])
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not available for completion")
    
    # Update task with completion data
    task.status = models.TaskStatus.completed
    task.completed_at = datetime.utcnow()
    task.result = completion_data.detailed_result
    task.completion_notes = completion_data.completion_summary
    
    # Update assistant stats
    current_assistant.assistant_profile.current_active_tasks -= 1
    current_assistant.assistant_profile.total_tasks_completed += 1
    
    db.commit()
    
    return {"success": True, "message": "Task completed successfully"}

@router.put("/tasks/{task_id}/update")
def update_task_progress(
    task_id: int,
    update_data: dict,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Update task progress notes"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if "completion_notes" in update_data:
        task.completion_notes = update_data["completion_notes"]
    
    db.commit()
    return {"success": True, "message": "Task updated successfully"}

# =============================================================================
# TASK COMMUNICATION
# =============================================================================

@router.get("/tasks/{task_id}/messages", response_model=List[schemas.MessageOut])
def get_task_messages(
    task_id: int,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Get messages for a specific task"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    messages = db.query(models.Message).filter(
        models.Message.task_id == task_id
    ).order_by(models.Message.created_at.asc()).all()
    
    return [schemas.MessageOut(
        id=msg.id,
        content=msg.content,
        sender_id=msg.sender_id,
        sender_name=msg.sender.name,
        created_at=msg.created_at
    ) for msg in messages]

@router.post("/tasks/{task_id}/message")
def send_task_message(
    task_id: int,
    message: schemas.MessageCreate,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Send a message in task communication"""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create message
    db_message = models.Message(
        task_id=task_id,
        sender_id=current_assistant.id,
        content=message.content
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return {"success": True, "message": "Message sent successfully"}

@router.post("/tasks/{task_id}/reject")
def reject_task(
    task_id: int,
    rejection_data: dict,
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Reject a task and return it to marketplace"""
    # Get task
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.assistant_id == current_assistant.assistant_profile.id,
        models.Task.status.in_([models.TaskStatus.in_progress, models.TaskStatus.revision_requested])
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not assigned to you or not available for rejection"
        )
    
    rejection_reason = rejection_data.get("reason", "").strip()
    if not rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required"
        )
    
    # Return task to marketplace with pending status
    task.status = models.TaskStatus.pending
    task.rejected_at = datetime.utcnow()
    task.rejection_reason = rejection_reason
    
    # Remove assistant assignment to return task to marketplace
    task.assistant_id = None
    task.claimed_at = None
    
    # Update assistant's active task count
    current_assistant.assistant_profile.current_active_tasks = max(0, current_assistant.assistant_profile.current_active_tasks - 1)
    
    # Add rejection message to task
    rejection_message = models.Message(
        task_id=task.id,
        sender_id=current_assistant.id,
        content=f"Задача отклонена ассистентом. Причина: {rejection_reason}"
    )
    db.add(rejection_message)
    
    db.commit()
    
    return {
        "success": True, 
        "message": "Task rejected and returned to marketplace",
        "task_id": task_id,
        "rejection_reason": rejection_reason
    }

# =============================================================================
# ANALYTICS & DASHBOARD
# =============================================================================

@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_assistant: models.User = Depends(get_current_assistant),
    db: Session = Depends(get_db)
):
    """Get assistant dashboard statistics"""
    assistant_id = current_assistant.assistant_profile.id
    
    # Task statistics
    total_tasks = db.query(models.Task).filter(
        models.Task.assistant_id == assistant_id
    ).count()
    
    active_tasks = db.query(models.Task).filter(
        models.Task.assistant_id == assistant_id,
        models.Task.status.in_([models.TaskStatus.in_progress, models.TaskStatus.revision_requested])
    ).count()
    
    completed_tasks = db.query(models.Task).filter(
        models.Task.assistant_id == assistant_id,
        models.Task.status.in_([models.TaskStatus.completed, models.TaskStatus.approved])
    ).count()
    
    # Average rating
    avg_rating = db.query(models.Task.client_rating).filter(
        models.Task.assistant_id == assistant_id,
        models.Task.client_rating.isnot(None)
    ).all()
    
    average_rating = sum([rating[0] for rating in avg_rating]) / len(avg_rating) if avg_rating else 0.0
    
    # Available tasks in marketplace
    available_tasks = db.query(models.Task).filter(
        models.Task.status == models.TaskStatus.pending,
        models.Task.assistant_id.is_(None)
    ).count()
    
    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "average_rating": round(average_rating, 1),
        "available_marketplace_tasks": available_tasks,
        "status": current_assistant.assistant_profile.status,
        "specialization": current_assistant.assistant_profile.specialization.value
    } 