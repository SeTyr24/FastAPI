from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
from contextlib import contextmanager

app = FastAPI(title="ToDo Service", version="1.0.0")

# Database configuration
DB_DIR = "/app/data"
DB_PATH = os.path.join(DB_DIR, "todos.db")

# Ensure data directory exists
os.makedirs(DB_DIR, exist_ok=True)


class TodoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database and create table if not exists"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {"message": "ToDo Service API", "docs": "/docs"}


@app.post("/items", response_model=TodoItem, status_code=201)
async def create_item(item: TodoItemCreate):
    """Create a new todo item"""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, item.completed)
        )
        conn.commit()
        item_id = cursor.lastrowid
        
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (item_id,)).fetchone()
        return TodoItem(**dict(row))


@app.get("/items", response_model=List[TodoItem])
async def get_items():
    """Get all todo items"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
        return [TodoItem(**dict(row)) for row in rows]


@app.get("/items/{item_id}", response_model=TodoItem)
async def get_item(item_id: int):
    """Get a specific todo item by ID"""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return TodoItem(**dict(row))


@app.put("/items/{item_id}", response_model=TodoItem)
async def update_item(item_id: int, item: TodoItemUpdate):
    """Update a todo item by ID"""
    with get_db() as conn:
        # Check if item exists
        existing = conn.execute("SELECT * FROM todos WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if item.title is not None:
            update_fields.append("title = ?")
            params.append(item.title)
        if item.description is not None:
            update_fields.append("description = ?")
            params.append(item.description)
        if item.completed is not None:
            update_fields.append("completed = ?")
            params.append(item.completed)
        
        if update_fields:
            params.append(item_id)
            conn.execute(
                f"UPDATE todos SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            conn.commit()
        
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (item_id,)).fetchone()
        return TodoItem(**dict(row))


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Delete a todo item by ID"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (item_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return None
