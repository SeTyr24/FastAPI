from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
import sqlite3
import os
import string
import random
from contextlib import contextmanager

app = FastAPI(title="URL Shortener Service", version="1.0.0")

# Database configuration
DB_DIR = "/app/data"
DB_PATH = os.path.join(DB_DIR, "urls.db")

# Ensure data directory exists
os.makedirs(DB_DIR, exist_ok=True)


class URLCreate(BaseModel):
    url: str


class URLResponse(BaseModel):
    short_id: str
    short_url: str
    full_url: str


class URLStats(BaseModel):
    short_id: str
    full_url: str


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
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_id TEXT UNIQUE NOT NULL,
                full_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def generate_short_id(length=6):
    """Generate a random short ID"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {"message": "URL Shortener Service API", "docs": "/docs"}


@app.post("/shorten", response_model=URLResponse, status_code=201)
async def shorten_url(url_data: URLCreate):
    """Create a shortened URL"""
    with get_db() as conn:
        # Generate unique short_id
        max_attempts = 10
        for _ in range(max_attempts):
            short_id = generate_short_id()
            
            # Check if short_id already exists
            existing = conn.execute(
                "SELECT short_id FROM urls WHERE short_id = ?", 
                (short_id,)
            ).fetchone()
            
            if not existing:
                break
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate unique short ID"
            )
        
        # Insert new URL
        conn.execute(
            "INSERT INTO urls (short_id, full_url) VALUES (?, ?)",
            (short_id, url_data.url)
        )
        conn.commit()
        
        # Return response
        return URLResponse(
            short_id=short_id,
            short_url=f"/{short_id}",
            full_url=url_data.url
        )


@app.get("/{short_id}")
async def redirect_url(short_id: str):
    """Redirect to the full URL by short_id"""
    # Prevent accessing stats endpoint through this route
    if short_id == "stats" or short_id == "shorten":
        raise HTTPException(status_code=404, detail="URL not found")
    
    with get_db() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id = ?", 
            (short_id,)
        ).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="URL not found")
        
        return RedirectResponse(url=row["full_url"], status_code=307)


@app.get("/stats/{short_id}", response_model=URLStats)
async def get_url_stats(short_id: str):
    """Get statistics/information about a shortened URL"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT short_id, full_url FROM urls WHERE short_id = ?", 
            (short_id,)
        ).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="URL not found")
        
        return URLStats(
            short_id=row["short_id"],
            full_url=row["full_url"]
        )
