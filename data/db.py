import sqlite3 as s3
from fastapi import FastAPI
from pydantic import BaseModel

conn = s3.connect("resources.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    location TEXT,
    description TEXT,
    target audience TEXT,
    source_url TEXT UNIQUE,
    tags TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS inverted_index(
    word TEXT,
    resource_id INTEGER,
    frequency INTEGER,
    FOREIGN KEY(resource_id) REFERENCES resources(id)
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_word ON inverted_index(word)")
conn.close()
app = FastAPI()

def get_db():
    conn = s3.connect("resources.db")
    return conn

@app.get("/api/query")
def query(query_term: str):
    db = get_db()
    cursor = db.cur()
    
    return {"message": "Hello from Python backend"}


