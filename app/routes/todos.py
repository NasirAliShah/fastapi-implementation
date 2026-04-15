from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.security import get_current_user, TokenData
from app.models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse, TodoStatus
from app.database.connection import get_db
from app.database.models import Todo

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new todo for the authenticated user"""
    try:
        new_todo = Todo(
            user_id=int(current_user.user_id),
            title=todo_data.title,
            description=todo_data.description,
            status=todo_data.status,
            priority=todo_data.priority
        )
        
        db.add(new_todo)
        await db.commit()
        await db.refresh(new_todo)
        
        return new_todo
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating todo: {str(e)}")

@router.get("/", response_model=TodoListResponse)
async def list_todos(
    current_user: TokenData = Depends(get_current_user),
    status_filter: TodoStatus = Query(None, description="Filter by status"),
    priority: int = Query(None, ge=1, le=5, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    sort_by: str = Query("created_at", description="Sort by field"),
    db: AsyncSession = Depends(get_db)
):
    """Get todos for the authenticated user with filtering and pagination"""
    try:
        stmt = select(Todo).where(
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        
        if status_filter:
            stmt = stmt.where(Todo.status == status_filter)
        if priority:
            stmt = stmt.where(Todo.priority == priority)
        
        if sort_by == "created_at":
            stmt = stmt.order_by(desc(Todo.created_at))
        elif sort_by == "priority":
            stmt = stmt.order_by(Todo.priority)
        else:
            stmt = stmt.order_by(desc(Todo.created_at))
        
        count_stmt = select(func.count(Todo.id)).where(
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        if status_filter:
            count_stmt = count_stmt.where(Todo.status == status_filter)
        if priority:
            count_stmt = count_stmt.where(Todo.priority == priority)
        
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        result = await db.execute(stmt.offset(skip).limit(limit))
        todos = result.scalars().all()
        
        return TodoListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            items=todos
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todos: {str(e)}")

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific todo by ID (must belong to authenticated user)"""
    try:
        stmt = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        result = await db.execute(stmt)
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        return todo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todo: {str(e)}")

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Partially update a todo (only provided fields are updated)"""
    try:
        stmt = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        result = await db.execute(stmt)
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        update_data = todo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)
        
        await db.commit()
        await db.refresh(todo)
        
        return todo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a todo (marks as deleted instead of removing)"""
    try:
        stmt = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        result = await db.execute(stmt)
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        todo.is_deleted = True
        await db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting todo: {str(e)}")

@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(
    todo_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a todo as completed"""
    try:
        stmt = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        )
        result = await db.execute(stmt)
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        todo.status = TodoStatus.COMPLETED
        await db.commit()
        await db.refresh(todo)
        
        return todo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error completing todo: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_todo_stats(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about user's todos"""
    try:
        stmt = select(Todo.status, func.count(Todo.id)).where(
            Todo.user_id == int(current_user.user_id),
            Todo.is_deleted == False
        ).group_by(Todo.status)
        
        result = await db.execute(stmt)
        stats = result.all()
        
        summary = {
            "total": sum(count for _, count in stats),
            "pending": next((count for status, count in stats if status == TodoStatus.PENDING), 0),
            "in_progress": next((count for status, count in stats if status == TodoStatus.IN_PROGRESS), 0),
            "completed": next((count for status, count in stats if status == TodoStatus.COMPLETED), 0)
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
