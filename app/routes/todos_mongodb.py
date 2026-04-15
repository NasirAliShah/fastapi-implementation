from fastapi import APIRouter, HTTPException, Depends, Query, status
from bson import ObjectId
from datetime import datetime
from app.database.mongodb_connection import todos_collection
from app.core.security import get_current_user, TokenData
from app.models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse, TodoStatus

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new todo for the authenticated user (MongoDB)"""
    try:
        todo_dict = {
            "user_id": current_user.user_id,
            "title": todo_data.title,
            "description": todo_data.description,
            "status": todo_data.status,
            "priority": todo_data.priority,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_deleted": False
        }
        
        result = await todos_collection.insert_one(todo_dict)
        created_todo = await todos_collection.find_one({"_id": result.inserted_id})
        
        return _format_todo(created_todo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating todo: {str(e)}")

@router.get("/", response_model=TodoListResponse)
async def list_todos(
    current_user: TokenData = Depends(get_current_user),
    status_filter: TodoStatus = Query(None, description="Filter by status"),
    priority: int = Query(None, ge=1, le=5, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    sort_by: str = Query("created_at", description="Sort by field")
):
    """Get todos for the authenticated user with filtering and pagination (MongoDB)"""
    try:
        query = {
            "user_id": current_user.user_id,
            "is_deleted": False
        }
        
        if status_filter:
            query["status"] = status_filter
        if priority:
            query["priority"] = priority
        
        sort_order = -1 if sort_by == "created_at" else 1
        sort_field = sort_by if sort_by in ["created_at", "priority", "status"] else "created_at"
        
        total = await todos_collection.count_documents(query)
        
        todos = await todos_collection.find(query)\
            .sort(sort_field, sort_order)\
            .skip(skip)\
            .limit(limit)\
            .to_list(limit)
        
        formatted_todos = [_format_todo(todo) for todo in todos]
        
        return TodoListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            items=formatted_todos
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todos: {str(e)}")

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific todo by ID (MongoDB)"""
    try:
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")
        
        todo = await todos_collection.find_one({
            "_id": ObjectId(todo_id),
            "user_id": current_user.user_id,
            "is_deleted": False
        })
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        return _format_todo(todo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todo: {str(e)}")

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Partially update a todo (MongoDB)"""
    try:
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")
        
        todo = await todos_collection.find_one({
            "_id": ObjectId(todo_id),
            "user_id": current_user.user_id,
            "is_deleted": False
        })
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        update_data = todo_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await todos_collection.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_data}
        )
        
        updated_todo = await todos_collection.find_one({"_id": ObjectId(todo_id)})
        return _format_todo(updated_todo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Soft delete a todo (MongoDB)"""
    try:
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")
        
        result = await todos_collection.update_one(
            {
                "_id": ObjectId(todo_id),
                "user_id": current_user.user_id,
                "is_deleted": False
            },
            {
                "$set": {
                    "is_deleted": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting todo: {str(e)}")

@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(
    todo_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Mark a todo as completed (MongoDB)"""
    try:
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")
        
        todo = await todos_collection.find_one({
            "_id": ObjectId(todo_id),
            "user_id": current_user.user_id,
            "is_deleted": False
        })
        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        await todos_collection.update_one(
            {"_id": ObjectId(todo_id)},
            {
                "$set": {
                    "status": TodoStatus.COMPLETED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        updated_todo = await todos_collection.find_one({"_id": ObjectId(todo_id)})
        return _format_todo(updated_todo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing todo: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_todo_stats(
    current_user: TokenData = Depends(get_current_user)
):
    """Get statistics about user's todos (MongoDB)"""
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": current_user.user_id,
                    "is_deleted": False
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats = await todos_collection.aggregate(pipeline).to_list(None)
        
        summary = {
            "total": sum(s["count"] for s in stats),
            "pending": next((s["count"] for s in stats if s["_id"] == "pending"), 0),
            "in_progress": next((s["count"] for s in stats if s["_id"] == "in_progress"), 0),
            "completed": next((s["count"] for s in stats if s["_id"] == "completed"), 0)
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

def _format_todo(todo: dict) -> TodoResponse:
    """Helper function to format MongoDB document to TodoResponse"""
    return TodoResponse(
        id=str(todo["_id"]),
        user_id=todo["user_id"],
        title=todo["title"],
        description=todo.get("description"),
        status=todo["status"],
        priority=todo["priority"],
        created_at=todo["created_at"],
        updated_at=todo["updated_at"],
        is_deleted=todo.get("is_deleted", False)
    )
