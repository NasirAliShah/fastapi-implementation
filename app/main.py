from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()

if DB_TYPE == "mongodb":
    from app.routes import auth_mongodb as auth
    from app.routes import users_mongodb as users
    from app.routes import todos_mongodb as todos
else:
    from app.routes import auth, users, todos

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Supports both MongoDB and PostgreSQL based on DB_TYPE environment variable.
    """
    
    app = FastAPI(
        title="User Management API",
        description="Complete user and todo management system with JWT authentication",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Register routers based on database type
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(todos.router)
    
    # Health check endpoint
    @app.get("/")
    async def root():
        """Health check endpoint"""
        db_info = "PostgreSQL" if DB_TYPE == "postgresql" else "MongoDB"
        return {
            "message": f"FastAPI + {db_info} connected!",
            "database": db_info
        }
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        db_info = "PostgreSQL" if DB_TYPE == "postgresql" else "MongoDB"
        print(f"✓ Application started successfully")
        print(f"✓ Database: {db_info}")
        print(f"✓ Routes registered")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        print("✓ Application shutting down")
    
    return app

app = create_app()
