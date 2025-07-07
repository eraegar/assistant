from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import models, schemas, database, auth

router = APIRouter(prefix="/api/v1/management", tags=["management"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_manager(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Ensure the current user is a manager, loaded in the current DB session"""
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user or user.role != models.UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manager role required."
        )
    if not user.manager_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager profile not found"
        )
    return user

# =============================================================================
# AUTHENTICATION & PROFILE
# =============================================================================

@router.post("/auth/register", response_model=schemas.ManagerOut)
def register_manager(manager_data: dict, db: Session = Depends(get_db)):
    """Register a new manager"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.phone == manager_data["phone"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    hashed_password = auth.get_password_hash(manager_data["password"])
    db_user = models.User(
        phone=manager_data["phone"],
        name=manager_data["name"],
        password_hash=hashed_password,
        role=models.UserRole.manager,
        telegram_username=manager_data.get("telegram_username")
    )
    db.add(db_user)
    db.flush()
    
    # Create manager profile
    manager_profile = models.ManagerProfile(
        user_id=db_user.id,
        email=manager_data["email"],
        department=manager_data.get("department", "Operations")
    )
    db.add(manager_profile)
    
    db.commit()
    db.refresh(db_user)
    
    return schemas.ManagerOut(
        id=db_user.id,
        name=db_user.name,
        email=manager_profile.email,
        department=manager_profile.department
    )

@router.post("/auth/login")
def login_manager(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Manager login"""
    print(f"🔐 Manager login attempt for phone: {credentials.phone}")
    user = db.query(models.User).filter(
        models.User.phone == credentials.phone,
        models.User.role == models.UserRole.manager
    ).first()

    if not user:
        print(f"❌ Manager not found for phone: {credentials.phone}")
        raise HTTPException(status_code=400, detail="Incorrect phone or password")

    if not auth.verify_password(credentials.password, user.password_hash):
        print(f"❌ Password verification failed for user: {user.id}")
        raise HTTPException(status_code=400, detail="Incorrect phone or password")

    token = auth.create_access_token({"user_id": user.id, "role": "manager"})
    print(f"✅ Manager login successful for user: {user.id}")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.ManagerOut)
def get_manager_profile(current_manager: models.User = Depends(get_current_manager)):
    """Get manager profile"""
    profile = current_manager.manager_profile
    
    return schemas.ManagerOut(
        id=current_manager.id,
        name=current_manager.name,
        email=profile.email,
        department=profile.department
    )

# =============================================================================
# OVERVIEW ANALYTICS
# =============================================================================

@router.get("/dashboard/overview")
def get_overview_analytics(
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get comprehensive overview analytics for management dashboard"""
    
    # Task statistics
    total_tasks = db.query(models.Task).count()
    pending_tasks = db.query(models.Task).filter(models.Task.status == models.TaskStatus.pending).count()
    in_progress_tasks = db.query(models.Task).filter(models.Task.status == models.TaskStatus.in_progress).count()
    completed_tasks = db.query(models.Task).filter(models.Task.status.in_([models.TaskStatus.completed, models.TaskStatus.approved])).count()
    
    # Assistant statistics
    total_assistants = db.query(models.AssistantProfile).count()
    online_assistants = db.query(models.AssistantProfile).filter(models.AssistantProfile.status == "online").count()
    assistants_with_tasks = db.query(models.AssistantProfile).filter(models.AssistantProfile.current_active_tasks > 0).count()
    avg_tasks_per_assistant = db.query(func.avg(models.AssistantProfile.current_active_tasks)).scalar() or 0.0
    
    # Client statistics
    total_clients = db.query(models.ClientProfile).count()
    active_subscribers = db.query(models.Subscription).filter(models.Subscription.status == models.SubscriptionStatus.active).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_tasks_week = db.query(models.Task).filter(models.Task.created_at >= week_ago).count()
    new_clients_week = db.query(models.User).filter(
        models.User.role == models.UserRole.client,
        models.User.created_at >= week_ago
    ).count()
    
    # Subscription distribution
    subscription_stats = db.query(
        models.Subscription.plan,
        func.count(models.Subscription.id)
    ).filter(
        models.Subscription.status == models.SubscriptionStatus.active
    ).group_by(models.Subscription.plan).all()
    
    subscription_distribution = {plan.value: count for plan, count in subscription_stats}
    
    # Revenue calculation
    total_revenue = 0
    for plan, count in subscription_stats:
        if plan == models.SubscriptionPlan.personal_2h:
            total_revenue += count * 15000  # 15,000 рублей
        elif plan == models.SubscriptionPlan.personal_5h:
            total_revenue += count * 30000  # 30,000 рублей
        elif plan == models.SubscriptionPlan.personal_8h:
            total_revenue += count * 50000  # 50,000 рублей
        elif plan == models.SubscriptionPlan.business_2h:
            total_revenue += count * 30000  # 30,000 рублей
        elif plan == models.SubscriptionPlan.business_5h:
            total_revenue += count * 60000  # 60,000 рублей
        elif plan == models.SubscriptionPlan.business_8h:
            total_revenue += count * 80000  # 80,000 рублей
        elif plan == models.SubscriptionPlan.full_2h:
            total_revenue += count * 40000  # 40,000 рублей
        elif plan == models.SubscriptionPlan.full_5h:
            total_revenue += count * 80000  # 80,000 рублей
        elif plan == models.SubscriptionPlan.full_8h:
            total_revenue += count * 100000  # 100,000 рублей
    
    return {
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks,
            "new_this_week": new_tasks_week
        },
        "assistants": {
            "total_active": total_assistants,
            "online_now": online_assistants,
            "with_active_tasks": assistants_with_tasks,
            "avg_tasks_per_assistant": round(avg_tasks_per_assistant, 1)
        },
        "clients": {
            "total_active": total_clients,
            "active_subscribers": active_subscribers,
            "new_this_week": new_clients_week,
            "subscription_distribution": subscription_distribution
        },
        "performance": {
            "task_completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            "assistant_utilization": round((assistants_with_tasks / total_assistants * 100) if total_assistants > 0 else 0, 1),
            "monthly_revenue": total_revenue
        }
    }

# =============================================================================
# TASK MANAGEMENT
# =============================================================================

@router.get("/tasks")
def get_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    assistant_id: Optional[int] = None,
    client_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get all tasks with filtering options"""
    
    query = db.query(models.Task)
    
    # Apply filters
    if status:
        query = query.filter(models.Task.status == status)
    
    if task_type:
        query = query.filter(models.Task.type == task_type)
    
    if assistant_id:
        query = query.filter(models.Task.assistant_id == assistant_id)
    
    if client_id:
        query = query.filter(models.Task.client_id == client_id)
    
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(models.Task.created_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(models.Task.created_at <= to_date)
        except ValueError:
            pass
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination and ordering
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    
    # Format response
    task_list = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.type.value,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "claimed_at": task.claimed_at.isoformat() if task.claimed_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "completion_notes": task.completion_notes,
            "client_rating": task.client_rating,
            "client_feedback": task.client_feedback,
            "client": {
                "id": task.client.id,
                "name": task.client.user.name,
                "phone": task.client.user.phone
            }
        }
        
        if task.assistant:
            task_data["assistant"] = {
                "id": task.assistant.id,
                "name": task.assistant.user.name,
                "specialization": task.assistant.specialization.value
            }
        else:
            task_data["assistant"] = None
            
        task_list.append(task_data)
    
    return {
        "tasks": task_list,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": skip,
            "has_more": skip + limit < total_count
        }
    }

@router.put("/tasks/{task_id}/reassign")
def reassign_task(
    task_id: int,
    reassign_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Reassign task to different assistant or unassign"""
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_assistant_id = reassign_data.get("assistant_id")
    
    # Remove from current assistant if any
    if task.assistant:
        task.assistant.current_active_tasks = max(0, task.assistant.current_active_tasks - 1)
    
    if new_assistant_id:
        # Assign to new assistant
        new_assistant = db.query(models.AssistantProfile).filter(
            models.AssistantProfile.id == new_assistant_id
        ).first()
        
        if not new_assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")
        
        # Check if assistant can handle this task type
        if (new_assistant.specialization == models.AssistantSpecialization.personal_only and 
            task.type == models.TaskType.business):
            raise HTTPException(
                status_code=400, 
                detail="Personal assistants cannot handle business tasks"
            )
        
        task.assistant_id = new_assistant_id
        task.status = models.TaskStatus.in_progress
        task.claimed_at = datetime.utcnow()
        new_assistant.current_active_tasks += 1
        
    else:
        # Unassign task
        task.assistant_id = None
        task.status = models.TaskStatus.pending
        task.claimed_at = None
    
    db.commit()
    
    return {"success": True, "message": "Task reassigned successfully"}

@router.delete("/tasks/{task_id}")
def cancel_task(
    task_id: int,
    cancellation_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Cancel a task (manager only)"""
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status in [models.TaskStatus.completed, models.TaskStatus.approved]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed tasks")
    
    # Remove from assistant if assigned
    if task.assistant:
        task.assistant.current_active_tasks = max(0, task.assistant.current_active_tasks - 1)
    
    task.status = models.TaskStatus.cancelled
    task.completion_notes = f"Cancelled by manager: {cancellation_data.get('reason', 'No reason provided')}"
    
    db.commit()
    
    return {"success": True, "message": "Task cancelled successfully"}

# =============================================================================
# ASSISTANT MANAGEMENT
# =============================================================================

@router.get("/assistants/available")
def get_available_assistants(
    task_type: Optional[str] = None,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get available assistants for task assignment"""
    
    query = db.query(models.AssistantProfile).filter(
        models.AssistantProfile.current_active_tasks < 5  # Not at capacity
    )
    
    # Filter by specialization based on task type
    if task_type:
        if task_type == "personal":
            query = query.filter(
                models.AssistantProfile.specialization.in_([
                    models.AssistantSpecialization.personal_only,
                    models.AssistantSpecialization.full_access
                ])
            )
        elif task_type == "business":
            query = query.filter(
                models.AssistantProfile.specialization.in_([
                    models.AssistantSpecialization.business_only,
                    models.AssistantSpecialization.full_access
                ])
            )
    
    assistants = query.all()
    
    available_assistants = []
    for assistant in assistants:
        # Check if assistant is available (not overloaded)
        is_available = assistant.current_active_tasks < 5
        
        assistant_data = {
            "id": assistant.id,
            "name": assistant.user.name,
            "email": assistant.email,
            "last_known_password": assistant.last_known_password,  # Real password from database
            "specialization": assistant.specialization.value,
            "status": assistant.status,
            "current_active_tasks": assistant.current_active_tasks,
            "total_tasks_completed": assistant.total_tasks_completed,
            "average_rating": assistant.average_rating,
            "is_available": is_available
        }
        available_assistants.append(assistant_data)
    
    return available_assistants

@router.post("/assistants/create", response_model=schemas.AssistantOut)
def create_assistant(
    assistant_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Create a new assistant account (manager only)"""
    
    # Validate required fields
    required_fields = ["name", "phone", "password", "email", "specialization"]
    for field in required_fields:
        if field not in assistant_data or not assistant_data[field]:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Format phone number to ensure it starts with +7
    phone = assistant_data["phone"]
    if not phone.startswith('+'):
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        elif phone.startswith('7'):
            phone = '+' + phone
        else:
            phone = '+7' + phone
    
    print(f"📞 Creating assistant with phone: {phone} (original: {assistant_data['phone']})")
    
    # Check if phone already exists
    existing_user = db.query(models.User).filter(models.User.phone == phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Validate specialization
    valid_specializations = ['personal_only', 'business_only', 'full_access']
    if assistant_data["specialization"] not in valid_specializations:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid specialization. Use one of: {', '.join(valid_specializations)}"
        )
    
    try:
        specialization = getattr(models.AssistantSpecialization, assistant_data["specialization"])
    except AttributeError:
        raise HTTPException(status_code=400, detail="Invalid specialization")
    
    # Create user
    hashed_password = auth.get_password_hash(assistant_data["password"])
    db_user = models.User(
        phone=phone,  # Use formatted phone number
        name=assistant_data["name"],
        password_hash=hashed_password,
        role=models.UserRole.assistant,
        telegram_username=assistant_data.get("telegram_username")
    )
    db.add(db_user)
    db.flush()
    
    # Create assistant profile
    assistant_profile = models.AssistantProfile(
        user_id=db_user.id,
        email=assistant_data["email"],
        specialization=specialization,
        status="offline",
        last_known_password=assistant_data["password"],  # Store original password
        last_password_reset_at=datetime.utcnow()
    )
    db.add(assistant_profile)
    
    db.commit()
    db.refresh(db_user)
    
    return schemas.AssistantOut(
        id=assistant_profile.id,
        name=db_user.name,
        email=assistant_profile.email,
        telegram_username=db_user.telegram_username,
        password=assistant_data["password"],  # Return the password for manager reference
        specialization=assistant_profile.specialization.value,
        status=assistant_profile.status,
        current_active_tasks=0,
        total_tasks_completed=0,
        average_rating=0.0
    )

@router.put("/assistants/{assistant_id}/status")
def update_assistant_status(
    assistant_id: int,
    status_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Force update assistant status (manager only)"""
    
    assistant = db.query(models.AssistantProfile).filter(
        models.AssistantProfile.id == assistant_id
    ).first()
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    new_status = status_data.get("status")
    if new_status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="Status must be 'online' or 'offline'")
    
    assistant.status = new_status
    assistant.user.last_active = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "message": f"Assistant status updated to {new_status}"}

@router.get("/assistants/{assistant_id}/performance")
def get_assistant_performance(
    assistant_id: int,
    days: int = Query(30, ge=1, le=365),
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for specific assistant"""
    
    assistant = db.query(models.AssistantProfile).filter(
        models.AssistantProfile.id == assistant_id
    ).first()
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    # Date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Task statistics
    tasks_in_period = db.query(models.Task).filter(
        models.Task.assistant_id == assistant_id,
        models.Task.claimed_at >= start_date,
        models.Task.claimed_at <= end_date
    ).all()
    
    total_tasks = len(tasks_in_period)
    completed_tasks = len([t for t in tasks_in_period if t.status in [models.TaskStatus.completed, models.TaskStatus.approved]])
    avg_completion_time = 0
    ratings = [t.client_rating for t in tasks_in_period if t.client_rating]
    
    if completed_tasks > 0:
        completion_times = []
        for task in tasks_in_period:
            if task.completed_at and task.claimed_at:
                time_diff = task.completed_at - task.claimed_at
                completion_times.append(time_diff.total_seconds() / 3600)  # hours
        
        if completion_times:
            avg_completion_time = sum(completion_times) / len(completion_times)
    
    # Task type distribution
    task_types = {}
    for task in tasks_in_period:
        task_type = task.type.value
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    return {
        "assistant": {
            "id": assistant.id,
            "name": assistant.user.name,
            "email": assistant.email,
            "specialization": assistant.specialization.value
        },
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "statistics": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            "average_completion_time_hours": round(avg_completion_time, 1),
            "average_rating": round(sum(ratings) / len(ratings), 1) if ratings else 0,
            "total_ratings": len(ratings),
            "task_type_distribution": task_types
        }
    }

@router.post("/assistants/{assistant_id}/reset-password")
async def reset_assistant_password(
    assistant_id: int,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Reset assistant password and return new password"""
    try:
        print(f"🔄 Password reset request for assistant: {assistant_id}")
        
        # Find assistant
        assistant_user = db.query(models.User).filter(
            models.User.id == assistant_id,
            models.User.role == models.UserRole.assistant
        ).first()
        
        if not assistant_user:
            raise HTTPException(status_code=404, detail="Assistant not found")
        
        # Generate new password
        import secrets
        import string
        
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # Update password
        hashed_password = auth.get_password_hash(new_password)
        assistant_user.password_hash = hashed_password
        
        # Store the new password in assistant profile for management reference
        assistant_profile = assistant_user.assistant_profile
        assistant_profile.last_known_password = new_password
        assistant_profile.last_password_reset_at = datetime.utcnow()
        
        db.commit()
        print(f"✅ Password reset successful for assistant: {assistant_id}")
        
        return {
            "success": True,
            "message": "Password reset successfully",
            "new_password": new_password,
            "assistant_name": assistant_user.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Password reset error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/clients/{client_id}/assign-assistant")
def assign_client_to_assistant(
    client_id: int,
    assignment_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Create permanent assignment between client and assistant (manager only)"""
    import json
    
    # Find client
    client = db.query(models.ClientProfile).filter(models.ClientProfile.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    assistant_id = assignment_data.get("assistant_id")
    if not assistant_id:
        raise HTTPException(status_code=400, detail="Assistant ID is required")
    
    # Find assistant
    assistant = db.query(models.AssistantProfile).filter(models.AssistantProfile.id == assistant_id).first()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    # Check if assistant is available (not overloaded)
    if assistant.current_active_tasks >= 5:
        raise HTTPException(status_code=400, detail="Assistant is at maximum capacity (5 active tasks)")
    
    # Check if client already has any active assignment (one assistant per client rule)
    existing_assignment = db.query(models.ClientAssistantAssignment).filter(
        models.ClientAssistantAssignment.client_id == client_id,
        models.ClientAssistantAssignment.status == models.AssignmentStatus.active
    ).first()
    
    if existing_assignment:
        existing_assistant = db.query(models.AssistantProfile).filter(
            models.AssistantProfile.id == existing_assignment.assistant_id
        ).first()
        raise HTTPException(
            status_code=400, 
            detail=f"Client is already assigned to assistant '{existing_assistant.user.name}'. Each client can have only one assistant."
        )
    
    # Determine allowed task types based on assistant specialization and client subscription
    allowed_task_types = []
    if assistant.specialization == models.AssistantSpecialization.personal_only:
        allowed_task_types = ["personal"]
    elif assistant.specialization == models.AssistantSpecialization.business_only:
        allowed_task_types = ["business"]
    else:  # full_access
        allowed_task_types = ["personal", "business"]
    
    # Further restrict based on client subscription if needed
    if client.subscription:
        if client.subscription.plan.value.startswith("personal_"):
            # Personal plans can only use personal tasks
            if "business" in allowed_task_types:
                allowed_task_types = ["personal"]
        elif client.subscription.plan.value.startswith("business_"):
            # Business plans can use business tasks, but check assistant capability
            pass  # Keep original allowed_task_types
        # Full plans can use any task type the assistant supports
    
    # Create permanent assignment
    assignment = models.ClientAssistantAssignment(
        client_id=client_id,
        assistant_id=assistant_id,
        status=models.AssignmentStatus.active,
        created_by=current_manager.manager_profile.id,
        allowed_task_types=json.dumps(allowed_task_types)
    )
    
    db.add(assignment)
    
    # Now assign any pending compatible tasks to this assistant
    pending_tasks = db.query(models.Task).filter(
        models.Task.client_id == client_id,
        models.Task.status == models.TaskStatus.pending,
        models.Task.assistant_id.is_(None)
    ).all()
    
    assigned_tasks = 0
    for task in pending_tasks:
        # Check if task type is allowed for this assignment
        if task.type.value in allowed_task_types:
            # Check if assistant still has capacity
            if assistant.current_active_tasks >= 5:
                break
                
            # Assign task
            task.assistant_id = assistant.id
            task.status = models.TaskStatus.in_progress
            task.claimed_at = datetime.utcnow()
            assigned_tasks += 1
            
            # Update assistant stats
            assistant.current_active_tasks += 1
    
    db.commit()
    
    return {
        "success": True, 
        "message": f"Client permanently assigned to assistant {assistant.user.name}",
        "assignment_id": assignment.id,
        "assigned_tasks": assigned_tasks,
        "allowed_task_types": allowed_task_types,
        "assistant": {
            "id": assistant.id,
            "name": assistant.user.name,
            "specialization": assistant.specialization.value,
            "current_active_tasks": assistant.current_active_tasks
        }
    }

@router.get("/assistants")
def get_all_assistants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get all assistants with their statistics"""
    
    query = db.query(models.AssistantProfile)
    
    if status:
        query = query.filter(models.AssistantProfile.status == status)
    
    if specialization:
        query = query.filter(models.AssistantProfile.specialization == specialization)
    
    total_count = query.count()
    assistants = query.offset(skip).limit(limit).all()
    
    assistant_list = []
    for assistant in assistants:
        # Get recent task statistics
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = db.query(models.Task).filter(
            models.Task.assistant_id == assistant.id,
            models.Task.claimed_at >= week_ago
        ).count()
        
        # Check if assistant is available (not overloaded)
        is_available = assistant.current_active_tasks < 5
        
        assistant_data = {
            "id": assistant.id,
            "name": assistant.user.name,
            "email": assistant.email,
            "phone": assistant.user.phone,
            "telegram_username": assistant.user.telegram_username,
            "specialization": assistant.specialization.value,
            "status": assistant.status,
            "current_active_tasks": assistant.current_active_tasks,
            "total_tasks_completed": assistant.total_tasks_completed,
            "average_rating": assistant.average_rating,
            "is_available": is_available,
            "recent_tasks_week": recent_tasks,
            "last_active": assistant.user.last_active.isoformat() if assistant.user.last_active else None,
            "created_at": assistant.user.created_at.isoformat(),
            "last_known_password": assistant.last_known_password,  # Include last known password
            "last_password_reset_at": assistant.last_password_reset_at.isoformat() if assistant.last_password_reset_at else None
        }
        assistant_list.append(assistant_data)
    
    return {
        "assistants": assistant_list,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": skip,
            "has_more": skip + limit < total_count
        }
    }

# =============================================================================
# CLIENT MANAGEMENT
# =============================================================================

@router.get("/clients")
def get_all_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    subscription_status: Optional[str] = None,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get all clients with active subscriptions and their assigned assistants"""
    import json
    
    # По умолчанию показываем только клиентов с активными подписками
    query = db.query(models.ClientProfile).join(models.Subscription).filter(
        models.Subscription.status == models.SubscriptionStatus.active
    )
    
    # Дополнительная фильтрация по статусу подписки (если требуется)
    if subscription_status:
        if subscription_status == "expired":
            # Показать клиентов с истекшими подписками
            query = db.query(models.ClientProfile).join(models.Subscription).filter(
                models.Subscription.status == models.SubscriptionStatus.expired
            )
        elif subscription_status == "all":
            # Показать всех клиентов (включая без подписки)
            query = db.query(models.ClientProfile)
    
    total_count = query.count()
    clients = query.offset(skip).limit(limit).all()
    
    client_list = []
    for client in clients:
        # Get task statistics
        total_tasks = db.query(models.Task).filter(models.Task.client_id == client.id).count()
        active_tasks = db.query(models.Task).filter(
            models.Task.client_id == client.id,
            models.Task.status.in_([models.TaskStatus.pending, models.TaskStatus.in_progress])
        ).count()
        
        # Get assigned assistants
        assigned_assistants = []
        assignments = db.query(models.ClientAssistantAssignment).filter(
            models.ClientAssistantAssignment.client_id == client.id,
            models.ClientAssistantAssignment.status == models.AssignmentStatus.active
        ).all()
        
        for assignment in assignments:
            allowed_types = []
            if assignment.allowed_task_types:
                try:
                    allowed_types = json.loads(assignment.allowed_task_types)
                except:
                    allowed_types = []
            
            assigned_assistants.append({
                "id": assignment.assistant.id,
                "name": assignment.assistant.user.name,
                "specialization": assignment.assistant.specialization.value,
                "status": assignment.assistant.status,
                "current_active_tasks": assignment.assistant.current_active_tasks,
                "allowed_task_types": allowed_types,
                "assignment_id": assignment.id,
                "assigned_at": assignment.created_at.isoformat()
            })
        
        client_data = {
            "id": client.id,
            "name": client.user.name,
            "email": client.email,
            "phone": client.user.phone,
            "telegram_username": client.user.telegram_username,
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "created_at": client.user.created_at.isoformat(),
            "assigned_assistants": assigned_assistants
        }
        
        # Add subscription info
        if client.subscription:
            client_data["subscription"] = {
                "id": client.subscription.id,
                "plan": client.subscription.plan.value,
                "status": client.subscription.status.value,
                "started_at": client.subscription.started_at.isoformat(),
                "expires_at": client.subscription.expires_at.isoformat() if client.subscription.expires_at else None,
                "auto_renew": client.subscription.auto_renew
            }
        else:
            client_data["subscription"] = None
            
        client_list.append(client_data)
    
    return {
        "clients": client_list,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": skip,
            "has_more": skip + limit < total_count
        }
    }

@router.put("/clients/{client_id}/subscription")
def manage_client_subscription(
    client_id: int,
    subscription_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Manage client subscription (manager override)"""
    
    client = db.query(models.ClientProfile).filter(models.ClientProfile.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    action = subscription_data.get("action")  # "activate", "cancel", "extend"
    
    if action == "cancel":
        if client.subscription:
            client.subscription.status = models.SubscriptionStatus.cancelled
            db.commit()
            return {"success": True, "message": "Subscription cancelled"}
        else:
            raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    elif action == "extend":
        if client.subscription and client.subscription.status == models.SubscriptionStatus.active:
            days_to_extend = subscription_data.get("days", 30)
            if client.subscription.expires_at:
                client.subscription.expires_at += timedelta(days=days_to_extend)
            else:
                client.subscription.expires_at = datetime.utcnow() + timedelta(days=days_to_extend)
            
            db.commit()
            return {"success": True, "message": f"Subscription extended by {days_to_extend} days"}
        else:
            raise HTTPException(status_code=400, detail="No active subscription to extend")
    
    elif action == "activate":
        plan = subscription_data.get("plan")
        if not plan:
            raise HTTPException(status_code=400, detail="Plan is required for activation")
        
        # Cancel existing subscription if any
        if client.subscription:
            client.subscription.status = models.SubscriptionStatus.cancelled
        
        # Create new subscription
        try:
            plan_enum = getattr(models.SubscriptionPlan, plan)
        except AttributeError:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        new_subscription = models.Subscription(
            client_id=client.id,
            plan=plan_enum,
            status=models.SubscriptionStatus.active,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            auto_renew=True
        )
        
        client.subscription = new_subscription
        db.commit()
        
        return {"success": True, "message": f"Subscription activated: {plan}"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate', 'cancel', or 'extend'")

# =============================================================================
# SYSTEM ANALYTICS
# =============================================================================

@router.get("/analytics/revenue")
def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get revenue analytics and subscription metrics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # New subscriptions in period
    new_subscriptions = db.query(models.Subscription).filter(
        models.Subscription.started_at >= start_date,
        models.Subscription.started_at <= end_date
    ).all()
    
    # Active subscriptions
    active_subscriptions = db.query(models.Subscription).filter(
        models.Subscription.status == models.SubscriptionStatus.active
    ).all()
    
    # Calculate revenue (simplified - using fixed prices)
    plan_prices = {
        "personal_2h": 2999,
        "personal_5h": 5999,
        "personal_8h": 8999,
        "business_2h": 4999,
        "business_5h": 7999,
        "business_8h": 11999,
        "full_2h": 6999,
        "full_5h": 9999,
        "full_8h": 14999
    }
    
    new_revenue = sum(plan_prices.get(sub.plan.value, 0) for sub in new_subscriptions)
    monthly_recurring_revenue = sum(plan_prices.get(sub.plan.value, 0) for sub in active_subscriptions)
    
    # Subscription distribution
    plan_distribution = {}
    for subscription in active_subscriptions:
        plan = subscription.plan.value
        plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
    
    # Churn rate (cancelled in period vs total at start of period)
    cancelled_in_period = db.query(models.Subscription).filter(
        models.Subscription.status == models.SubscriptionStatus.cancelled,
        models.Subscription.started_at < start_date
    ).count()
    
    total_at_start = len(active_subscriptions) + cancelled_in_period
    churn_rate = (cancelled_in_period / total_at_start * 100) if total_at_start > 0 else 0
    
    return {
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "revenue": {
            "new_subscriptions_count": len(new_subscriptions),
            "new_revenue_rubles": new_revenue / 100,  # Convert from kopecks
            "monthly_recurring_revenue_rubles": monthly_recurring_revenue / 100,
            "average_revenue_per_user": (monthly_recurring_revenue / len(active_subscriptions)) / 100 if active_subscriptions else 0
        },
        "subscriptions": {
            "total_active": len(active_subscriptions),
            "plan_distribution": plan_distribution,
            "churn_rate_percent": round(churn_rate, 2)
        }
    }

@router.get("/analytics/performance")
def get_performance_analytics(
    days: int = Query(30, ge=1, le=365),
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get system performance analytics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Task performance
    tasks_in_period = db.query(models.Task).filter(
        models.Task.created_at >= start_date,
        models.Task.created_at <= end_date
    ).all()
    
    total_tasks = len(tasks_in_period)
    completed_tasks = len([t for t in tasks_in_period if t.status in [models.TaskStatus.completed, models.TaskStatus.approved]])
    
    # Average task completion time
    completion_times = []
    for task in tasks_in_period:
        if task.completed_at and task.claimed_at:
            time_diff = task.completed_at - task.claimed_at
            completion_times.append(time_diff.total_seconds() / 3600)  # hours
    
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Assistant performance
    assistant_ratings = db.query(models.Task.client_rating).filter(
        models.Task.client_rating.isnot(None),
        models.Task.completed_at >= start_date,
        models.Task.completed_at <= end_date
    ).all()
    
    avg_rating = sum(rating[0] for rating in assistant_ratings) / len(assistant_ratings) if assistant_ratings else 0
    
    # Task assignment rate (how quickly tasks get claimed)
    pending_tasks = db.query(models.Task).filter(
        models.Task.status == models.TaskStatus.pending,
        models.Task.created_at >= start_date
    ).all()
    
    assignment_times = []
    claimed_tasks = db.query(models.Task).filter(
        models.Task.claimed_at >= start_date,
        models.Task.claimed_at <= end_date,
        models.Task.claimed_at.isnot(None)
    ).all()
    
    for task in claimed_tasks:
        if task.claimed_at:
            time_diff = task.claimed_at - task.created_at
            assignment_times.append(time_diff.total_seconds() / 3600)  # hours
    
    avg_assignment_time = sum(assignment_times) / len(assignment_times) if assignment_times else 0
    
    return {
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "task_performance": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate_percent": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            "average_completion_time_hours": round(avg_completion_time, 1),
            "average_assignment_time_hours": round(avg_assignment_time, 1),
            "pending_tasks": len(pending_tasks)
        },
        "quality_metrics": {
            "average_client_rating": round(avg_rating, 1),
            "total_ratings": len(assistant_ratings),
            "tasks_with_ratings_percent": round((len(assistant_ratings) / completed_tasks * 100) if completed_tasks > 0 else 0, 1)
        }
    } 

# =============================================================================
# CLIENT-ASSISTANT PERMANENT ASSIGNMENTS
# =============================================================================

@router.get("/assignments")
def get_all_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    client_id: Optional[int] = None,
    assistant_id: Optional[int] = None,
    status: Optional[str] = None,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Get all permanent client-assistant assignments"""
    import json
    
    query = db.query(models.ClientAssistantAssignment)
    
    if client_id:
        query = query.filter(models.ClientAssistantAssignment.client_id == client_id)
    if assistant_id:
        query = query.filter(models.ClientAssistantAssignment.assistant_id == assistant_id)
    if status:
        query = query.filter(models.ClientAssistantAssignment.status == status)
    
    total_count = query.count()
    assignments = query.offset(skip).limit(limit).all()
    
    assignment_list = []
    for assignment in assignments:
        allowed_types = []
        if assignment.allowed_task_types:
            try:
                allowed_types = json.loads(assignment.allowed_task_types)
            except:
                allowed_types = []
        
        assignment_data = {
            "id": assignment.id,
            "client": {
                "id": assignment.client.id,
                "name": assignment.client.user.name,
                "phone": assignment.client.user.phone
            },
            "assistant": {
                "id": assignment.assistant.id,
                "name": assignment.assistant.user.name,
                "specialization": assignment.assistant.specialization.value,
                "current_active_tasks": assignment.assistant.current_active_tasks
            },
            "status": assignment.status.value,
            "allowed_task_types": allowed_types,
            "created_at": assignment.created_at.isoformat(),
            "updated_at": assignment.updated_at.isoformat(),
            "created_by_manager": assignment.created_by_manager.user.name if assignment.created_by_manager else None
        }
        assignment_list.append(assignment_data)
    
    return {
        "assignments": assignment_list,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": skip,
            "has_more": skip + limit < total_count
        }
    }

@router.post("/assignments/create")
def create_assignment(
    assignment_data: dict,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Create a new permanent client-assistant assignment"""
    import json
    
    client_id = assignment_data.get("client_id")
    assistant_id = assignment_data.get("assistant_id")
    allowed_task_types = assignment_data.get("allowed_task_types", [])
    
    if not client_id or not assistant_id:
        raise HTTPException(status_code=400, detail="Client ID and Assistant ID are required")
    
    # Find client and assistant
    client = db.query(models.ClientProfile).filter(models.ClientProfile.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    assistant = db.query(models.AssistantProfile).filter(models.AssistantProfile.id == assistant_id).first()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    # Check if assignment already exists
    existing = db.query(models.ClientAssistantAssignment).filter(
        models.ClientAssistantAssignment.client_id == client_id,
        models.ClientAssistantAssignment.assistant_id == assistant_id,
        models.ClientAssistantAssignment.status == models.AssignmentStatus.active
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Active assignment already exists between this client and assistant")
    
    # Create assignment
    assignment = models.ClientAssistantAssignment(
        client_id=client_id,
        assistant_id=assistant_id,
        status=models.AssignmentStatus.active,
        created_by=current_manager.manager_profile.id,
        allowed_task_types=json.dumps(allowed_task_types) if allowed_task_types else None
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return {
        "success": True,
        "message": f"Assignment created between {client.user.name} and {assistant.user.name}",
        "assignment_id": assignment.id,
        "allowed_task_types": allowed_task_types
    }

@router.put("/assignments/{assignment_id}/deactivate")
def deactivate_assignment(
    assignment_id: int,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Deactivate a permanent client-assistant assignment"""
    
    assignment = db.query(models.ClientAssistantAssignment).filter(
        models.ClientAssistantAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != models.AssignmentStatus.active:
        raise HTTPException(status_code=400, detail="Assignment is not active")
    
    assignment.status = models.AssignmentStatus.inactive
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Assignment between {assignment.client.user.name} and {assignment.assistant.user.name} has been deactivated"
    }

@router.put("/assignments/{assignment_id}/reactivate")
def reactivate_assignment(
    assignment_id: int,
    current_manager: models.User = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Reactivate a permanent client-assistant assignment"""
    
    assignment = db.query(models.ClientAssistantAssignment).filter(
        models.ClientAssistantAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != models.AssignmentStatus.inactive:
        raise HTTPException(status_code=400, detail="Assignment is not inactive")
    
    # Check if assistant is not overloaded
    if assignment.assistant.current_active_tasks >= 5:
        raise HTTPException(status_code=400, detail="Assistant is at maximum capacity")
    
    assignment.status = models.AssignmentStatus.active
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Assignment between {assignment.client.user.name} and {assignment.assistant.user.name} has been reactivated"
    } 