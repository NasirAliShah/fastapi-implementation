from fastapi import FastAPI
from app.routes import auth, users, todos

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    This is the app factory pattern - centralizes app creation and configuration.
    Benefits:
    - Testability: Create multiple app instances for testing
    - Configuration: Different configs for dev/prod
    - Modularity: Separate app creation from routes
    - Reusability: Use same app in different contexts
    """
    
    app = FastAPI(
        title="User Management API",
        description="Complete user and todo management system with JWT authentication",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Register routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(todos.router)
    
    # Health check endpoint
    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {"message": "MongoDB + FastAPI connected!"}
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        print("✓ Application started successfully")
        print("✓ Database connected")
        print("✓ Routes registered")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        print("✓ Application shutting down")
    
    return app

app = create_app()
