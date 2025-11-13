# FastAPI + MongoDB User Management API

A simple REST API built with FastAPI and MongoDB for user management.

## Features

- Create users with name, email, and age
- Get all users
- Get user by ID
- MongoDB integration with Motor (async driver)
- Interactive API documentation with Swagger UI

## Setup

### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fastapi-implementation
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your MongoDB connection details
   nano .env  # or use your preferred editor
   ```
   
   Update `.env` with your **actual** MongoDB credentials:
   ```env
   MONGODB_URL=mongodb://your_username:your_password@localhost:27017/your_database?authSource=admin
   DATABASE_NAME=your_database_name
   ```
   
   ⚠️ **Security Note**: Never commit your `.env` file to Git. It contains sensitive credentials and is already excluded in `.gitignore`.

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- **GET /** - Health check
- **POST /users/** - Create a new user
- **GET /users/** - Get all users
- **GET /users/{user_id}** - Get user by ID

## API Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Example Usage

### Create a user
```bash
curl -X POST "http://127.0.0.1:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "age": 25}'
```

### Get all users
```bash
curl http://127.0.0.1:8000/users/
```