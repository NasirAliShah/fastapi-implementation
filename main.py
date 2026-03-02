from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from bson import ObjectId
from database import user_collection
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    TokenData,
    TokenResponse
)

app = FastAPI(title="User Management API", description="A simple FastAPI + MongoDB application")

# Pydantic models for request/response validation
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

@app.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user and return JWT token"""
    try:
        # Check if user already exists
        existing_user = await user_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user document
        hashed_password = hash_password(user_data.password)
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "age": user_data.age
        }
        
        result = await user_collection.insert_one(user_dict)
        user_id = str(result.inserted_id)
        
        # Generate JWT token
        access_token = create_access_token(user_id=user_id, email=user_data.email)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user_data.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

@app.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    try:
        # Find user by email
        user = await user_collection.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Generate JWT token
        user_id = str(user["_id"])
        access_token = create_access_token(user_id=user_id, email=credentials.email)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": credentials.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")


@app.post("/users/", response_model=UserResponse)
async def create_user(user: User, current_user: TokenData = Depends(get_current_user)):
    """Create a new user in the database (requires authentication)"""
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
async def delete_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    """Delete a user by ID (requires authentication)"""
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
async def get_users(current_user: TokenData = Depends(get_current_user)):
    """Get all users from the database (requires authentication)"""
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
async def get_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get a specific user by ID (requires authentication)"""
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
