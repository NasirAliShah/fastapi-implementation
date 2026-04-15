from app.database.connection import database

users_collection = database.get_collection("users")
todos_collection = database.get_collection("todos")
