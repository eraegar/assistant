from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class TaskAssignmentService:
    """Service for handling task assignments and marketplace logic"""
    
    def __init__(self, db):
        self.db = db
    
    def find_assigned_assistants(self, task):
        """Find all permanently assigned assistants for this client and task type"""
        try:
            # Import models here to avoid circular imports
            from models import ClientAssistantAssignment, AssignmentStatus, AssistantProfile, TaskType
            
            # Get all assigned assistants for this client
            assignments = self.db.query(ClientAssistantAssignment).filter(
                ClientAssistantAssignment.client_id == task.client_id,
                ClientAssistantAssignment.status == AssignmentStatus.active
            ).all()
            
            assigned_assistants = []
            
            for assignment in assignments:
                assistant = assignment.assistant
                
                # Check task type compatibility
                allowed_types = []
                if assignment.allowed_task_types:
                    try:
                        allowed_types = json.loads(assignment.allowed_task_types)
                    except:
                        allowed_types = []
                
                # If no specific types set, use assistant specialization
                if not allowed_types:
                    if assistant.specialization.value == "personal_only":
                        allowed_types = ["personal"]
                    elif assistant.specialization.value == "business_only":
                        allowed_types = ["business"]
                    else:  # full_access
                        allowed_types = ["personal", "business"]
                
                # Check if task type is allowed
                if task.type.value in allowed_types:
                    assigned_assistants.append(assistant)
                    logger.info(f"Found assigned assistant {assistant.id} for client {task.client_id}, task type {task.type.value}")
            
            logger.info(f"Found {len(assigned_assistants)} assigned assistants for client {task.client_id}, task type {task.type.value}")
            return assigned_assistants
            
        except Exception as e:
            logger.error(f"Error finding assigned assistants: {str(e)}")
            return []
    
    def assign_to_multiple_assistants(self, task):
        """Assign task to all available assigned assistants (new multi-assistant system)"""
        # Get all assigned assistants for this client and task type
        assigned_assistants = self.find_assigned_assistants(task)
        
        if assigned_assistants:
            logger.info(f"Task {task.id} is available to {len(assigned_assistants)} assigned assistants")
            # Task stays in marketplace but is also visible to assigned assistants
            # They can compete to claim it first
            return True
        
        # If no assigned assistants, task goes to general marketplace
        logger.info(f"Task {task.id} has no assigned assistants, going to general marketplace")
        return False
    
    def _is_assistant_compatible(self, assignment, assistant, task):
        """Check if assistant is available and compatible with task type"""
        # Check if assistant is available (not overloaded)
        if assistant.current_active_tasks >= 5:
            return False
        
        # Check task type compatibility
        allowed_types = []
        if assignment.allowed_task_types:
            try:
                allowed_types = json.loads(assignment.allowed_task_types)
            except:
                allowed_types = []
        
        # If no specific types set, use assistant specialization
        if not allowed_types:
            if assistant.specialization.value == "personal_only":
                allowed_types = ["personal"]
            elif assistant.specialization.value == "business_only":
                allowed_types = ["business"]
            else:  # full_access
                allowed_types = ["personal", "business"]
        
        # Check if task type is allowed
        return task.type.value in allowed_types
    
    def find_best_assistant(self, task):
        """Find the best available assistant for a task"""
        # First check for permanently assigned assistant
        assigned_assistant = self.find_assigned_assistants(task)
        if assigned_assistant:
            return assigned_assistant
        
        if assigned_assistant:
            logger.info(f"Task {task.id} is available to {len(assigned_assistant)} assigned assistants")
            # Task stays in marketplace but is also visible to assigned assistants
            # They can compete to claim it first
            return True
        
        # If no assigned assistants, task goes to general marketplace
        logger.info(f"Task {task.id} has no assigned assistants, going to general marketplace")
        return False
    
    def auto_assign_task(self, task) -> bool:
        """Try to make task available to assigned assistants (new multi-assistant system)"""
        try:
            # Import models here to avoid circular imports
            from models import TaskStatus
            
            # Make task available to assigned assistants
            has_assigned_assistants = self.assign_to_multiple_assistants(task)
            
            # Task stays in pending status but is now available to assigned assistants
            # in addition to the general marketplace
            logger.info(f"Task {task.id} is now available in marketplace (assigned assistants: {has_assigned_assistants})")
            return True
            
        except Exception as e:
            logger.error(f"Error in auto_assign_task: {str(e)}")
            self.db.rollback()
            return False
    
    def send_to_marketplace(self, task) -> bool:
        """Send task to marketplace (already in pending status)"""
        try:
            # Task is already in marketplace when status=pending and assistant_id=None
            # Set deadline if not set
            if not task.deadline:
                task.deadline = datetime.utcnow() + timedelta(hours=24)
            
            self.db.commit()
            logger.info(f"Task {task.id} is now available in marketplace")
            return True
            
        except Exception as e:
            logger.error(f"Error sending task to marketplace: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_task_rejection(self, task, reason: str = "Task rejected by assistant") -> bool:
        """Handle when an assistant rejects a task"""
        try:
            # Import models here to avoid circular imports
            from models import TaskStatus
            
            # Reset task for marketplace
            task.status = TaskStatus.pending  # Back to pending for marketplace
            task.assistant_id = None
            task.claimed_at = None
            task.rejected_at = datetime.utcnow()
            task.rejection_reason = reason
            
            # Set or extend deadline
            if not task.deadline or task.deadline < datetime.utcnow():
                task.deadline = datetime.utcnow() + timedelta(hours=24)
            
            self.db.commit()
            logger.info(f"Task {task.id} rejected and returned to marketplace. Reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling task rejection: {str(e)}")
            self.db.rollback()
            return False
    
    def get_rejected_tasks_for_reassignment(self, limit: int = 10):
        """Get rejected tasks that need reassignment"""
        try:
            # Import models here to avoid circular imports
            from models import Task, TaskStatus
            
            # Get tasks that were rejected and are now pending
            rejected_tasks = self.db.query(Task).filter(
                Task.status == TaskStatus.pending,
                Task.assistant_id.is_(None),
                Task.rejected_at.isnot(None)
            ).order_by(Task.rejected_at.desc()).limit(limit).all()
            
            return rejected_tasks
            
        except Exception as e:
            logger.error(f"Error getting rejected tasks: {str(e)}")
            return []
    
    def handle_task_timeout(self, task) -> bool:
        """Handle task that hasn't been claimed within timeout period"""
        return True
    
    def handle_assistant_failure(self, task, reason: str = "Assistant unavailable") -> bool:
        """Handle when an assistant can't complete a task"""
        return True
    
    def process_pending_tasks(self) -> None:
        """Process all pending tasks for assignment and timeout handling"""
        try:
            # Import models here to avoid circular imports
            from models import Task, TaskStatus
            
            # Get all pending tasks
            pending_tasks = self.db.query(Task).filter(
                Task.status == TaskStatus.pending,
                Task.assistant_id.is_(None)
            ).limit(5).all()  # Process max 5 at a time
            
            for task in pending_tasks:
                try:
                    # Try auto-assignment
                    self.auto_assign_task(task)
                except Exception as e:
                    logger.error(f"Error processing pending task {task.id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error processing pending tasks: {str(e)}")
    
    def get_marketplace_stats(self) -> dict:
        """Get marketplace statistics"""
        try:
            # Import models here to avoid circular imports
            from models import Task, TaskStatus, AssistantProfile
            
            total_pending = self.db.query(Task).filter(
                Task.status == TaskStatus.pending,
                Task.assistant_id.is_(None)
            ).count()
            
            rejected_tasks = self.db.query(Task).filter(
                Task.status == TaskStatus.pending,
                Task.assistant_id.is_(None),
                Task.rejected_at.isnot(None)
            ).count()
            
            overdue_tasks = self.db.query(Task).filter(
                Task.status == TaskStatus.pending,
                Task.assistant_id.is_(None),
                Task.created_at < datetime.utcnow() - timedelta(hours=2)
            ).count()
            
            online_assistants = self.db.query(AssistantProfile).filter(
                AssistantProfile.status == "online"
            ).count()
            
            return {
                "total_pending_tasks": total_pending,
                "rejected_tasks": rejected_tasks,
                "overdue_tasks": overdue_tasks,
                "online_assistants": online_assistants,
                "avg_assignment_time_minutes": 0,
                "assignment_needed": total_pending > 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting marketplace stats: {str(e)}")
            return {
                "total_pending_tasks": 0,
                "rejected_tasks": 0,
                "overdue_tasks": 0,
                "online_assistants": 0,
                "avg_assignment_time_minutes": 0,
                "assignment_needed": False,
                "last_updated": datetime.utcnow().isoformat()
            }

def get_task_assignment_service(db=None):
    """Factory function to get TaskAssignmentService instance"""
    from database import SessionLocal
    if db is None:
        db = SessionLocal()
    return TaskAssignmentService(db) 