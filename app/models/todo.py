from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TodoStatus = TodoStatus.PENDING
    priority: int = Field(default=1, ge=1, le=5)

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: TodoStatus
    priority: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

class TodoListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TodoResponse]
