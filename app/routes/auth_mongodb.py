from fastapi import APIRouter, HTTPException, status
from app.models.user import UserRegister, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    TokenResponse
)
from app.database.mongodb_connection import users_collection

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user and return JWT token (MongoDB)"""
    try:
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = hash_password(user_data.password)
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "age": user_data.age
        }
        
        result = await users_collection.insert_one(user_dict)
        user_id = str(result.inserted_id)
        
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

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return JWT token (MongoDB)"""
    try:
        user = await users_collection.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
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
