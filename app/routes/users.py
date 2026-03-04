from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from app.models.user import UserResponse
from app.core.security import get_current_user, TokenData
from app.database.collections import users_collection

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def get_users(current_user: TokenData = Depends(get_current_user)):
    """Get all users from the database (requires authentication)"""
    try:
        users = await users_collection.find().to_list(100)
        for user in users:
            user["id"] = str(user["_id"])
            del user["_id"]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get a specific user by ID (requires authentication)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    """Delete a user by ID (requires authentication)"""
    try:
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
