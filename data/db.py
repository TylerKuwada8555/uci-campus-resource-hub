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

class QueryObject(BaseModel):
    query: str
    name: str
    year: int
    major: str
    domestic: bool

def get_db():
    conn = s3.connect("resources.db")
    return conn

@app.post("/api/query")
def query(query_object: QueryObject):
    db = get_db()
    cursor = db.cursor()

    query_term = query_object['query'].lower()
    query_term = remove_punctuation(query_term)
    tokens = query_term.split()

    # cursor.execute("""
    # SELECT p.url, p.title
    # FROM pages p
    # JOIN inverted_index i ON p.id = i.page_id
    # WHERE i.word = 'machine'
    # ORDER BY i.frequency DESC;
    # """)

    return {"message": "Hello from Python backend"}


