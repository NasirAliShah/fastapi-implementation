from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from database import user_collection

app = FastAPI(title="User Management API", description="A simple FastAPI + MongoDB application")

# Pydantic models for request/response validation
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "MongoDB + FastAPI connected!"}


@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    """Create a new user in the database"""
    try:
        # Convert Pydantic model to dict for MongoDB insertion
        user_dict = user.model_dump()
        result = await user_collection.insert_one(user_dict)
        
        # Return the created user with its ID
        created_user = await user_collection.find_one({"_id": result.inserted_id})
        created_user["id"] = str(created_user["_id"])
        del created_user["_id"]
        
        return created_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
# Delete a user 
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user by ID"""
    try:
        result = await user_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@app.get("/users/")
async def get_users():
    """Get all users from the database"""
    try:
        users = await user_collection.find().to_list(100)
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user["id"] = str(user["_id"])
            del user["_id"]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get a specific user by ID"""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
