#!/usr/bin/env python3
"""
Text validation utilities for character limits and content sanitization
"""

import re
from typing import Optional, Tuple
from fastapi import HTTPException

# Character limits configuration (imported from schemas)
TASK_TITLE_MIN_LENGTH = 5
TASK_TITLE_MAX_LENGTH = 200
TASK_DESCRIPTION_MAX_LENGTH = 2000
TASK_RESULT_MAX_LENGTH = 5000
COMPLETION_NOTES_MAX_LENGTH = 1000
REVISION_NOTES_MAX_LENGTH = 1000
CLIENT_FEEDBACK_MAX_LENGTH = 1000
MESSAGE_CONTENT_MAX_LENGTH = 2000

def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Sanitize text by removing excessive whitespace and normalizing line breaks
    """
    if not text:
        return None
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Return None for empty strings
    if not text:
        return None
    
    # Normalize line breaks and remove excessive whitespace
    text = re.sub(r'\r\n|\r', '\n', text)  # Normalize line endings
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive line breaks
    text = re.sub(r'[ \t]+', ' ', text)  # Collapse multiple spaces/tabs
    text = re.sub(r' *\n *', '\n', text)  # Remove spaces around line breaks
    
    return text

def validate_text_length(
    text: Optional[str], 
    field_name: str,
    min_length: int = 0,
    max_length: int = 10000,
    required: bool = True
) -> Optional[str]:
    """
    Validate text length and return sanitized text
    
    Args:
        text: Text to validate
        field_name: Name of the field for error messages
        min_length: Minimum required length
        max_length: Maximum allowed length
        required: Whether the field is required
    
    Returns:
        Sanitized text or None
        
    Raises:
        HTTPException: If validation fails
    """
    
    # Sanitize first
    text = sanitize_text(text)
    
    # Check if required
    if required and not text:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} is required and cannot be empty"
        )
    
    # If not required and empty, return None
    if not required and not text:
        return None
    
    # Check length constraints
    if text:
        length = len(text)
        
        if length < min_length:
            raise HTTPException(
                status_code=422,
                detail=f"{field_name} must be at least {min_length} characters long (current: {length})"
            )
        
        if length > max_length:
            raise HTTPException(
                status_code=422,
                detail=f"{field_name} must not exceed {max_length} characters (current: {length})"
            )
    
    return text

def validate_task_title(title: str) -> str:
    """Validate task title"""
    return validate_text_length(
        title, 
        "Task title",
        min_length=TASK_TITLE_MIN_LENGTH,
        max_length=TASK_TITLE_MAX_LENGTH,
        required=True
    )

def validate_task_description(description: Optional[str]) -> Optional[str]:
    """Validate task description"""
    return validate_text_length(
        description,
        "Task description",
        min_length=0,
        max_length=TASK_DESCRIPTION_MAX_LENGTH,
        required=False
    )

def validate_task_result(result: str) -> str:
    """Validate task completion result"""
    return validate_text_length(
        result,
        "Task result",
        min_length=20,
        max_length=TASK_RESULT_MAX_LENGTH,
        required=True
    )

def validate_completion_notes(notes: Optional[str]) -> Optional[str]:
    """Validate task completion notes"""
    return validate_text_length(
        notes,
        "Completion notes",
        min_length=0,
        max_length=COMPLETION_NOTES_MAX_LENGTH,
        required=False
    )

def validate_client_feedback(feedback: str) -> str:
    """Validate client feedback"""
    return validate_text_length(
        feedback,
        "Client feedback",
        min_length=5,
        max_length=CLIENT_FEEDBACK_MAX_LENGTH,
        required=True
    )

def validate_revision_notes(notes: str) -> str:
    """Validate revision request notes"""
    return validate_text_length(
        notes,
        "Revision notes",
        min_length=10,
        max_length=REVISION_NOTES_MAX_LENGTH,
        required=True
    )

def validate_message_content(content: str) -> str:
    """Validate message content"""
    return validate_text_length(
        content,
        "Message content",
        min_length=1,
        max_length=MESSAGE_CONTENT_MAX_LENGTH,
        required=True
    )

def get_text_stats(text: Optional[str]) -> dict:
    """
    Get statistics about text content
    
    Returns:
        Dict with character count, word count, line count
    """
    if not text:
        return {
            "character_count": 0,
            "word_count": 0,
            "line_count": 0,
            "is_empty": True
        }
    
    # Count characters (excluding leading/trailing whitespace)
    clean_text = text.strip()
    char_count = len(clean_text)
    
    # Count words
    word_count = len(clean_text.split()) if clean_text else 0
    
    # Count lines
    line_count = len(clean_text.split('\n')) if clean_text else 0
    
    return {
        "character_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "is_empty": char_count == 0
    }

class ValidationError(Exception):
    """Custom validation error for better error handling"""
    
    def __init__(self, field_name: str, message: str, current_length: int = None, max_length: int = None):
        self.field_name = field_name
        self.message = message
        self.current_length = current_length
        self.max_length = max_length
        super().__init__(message)

def validate_all_task_fields(
    title: str,
    description: Optional[str] = None,
    task_type: str = None
) -> Tuple[str, Optional[str]]:
    """
    Validate all task creation fields at once
    
    Returns:
        Tuple of (validated_title, validated_description)
        
    Raises:
        ValidationError: If any field fails validation
    """
    try:
        validated_title = validate_task_title(title)
        validated_description = validate_task_description(description)
        
        return validated_title, validated_description
        
    except HTTPException as e:
        raise ValidationError(
            field_name="task_fields",
            message=e.detail
        ) 