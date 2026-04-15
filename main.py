"""
Entry point for the FastAPI application.

This file runs the application using uvicorn.
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
