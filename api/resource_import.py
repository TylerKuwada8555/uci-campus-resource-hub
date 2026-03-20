import sqlite3 as s3
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

conn = s3.connect("resources.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY,
    category TEXT,
    name TEXT,
    location TEXT,
    contact_info TEXT,
    description TEXT,
    target_audience TEXT,
    source_url TEXT,
    embedding TEXT
)
""")

conn.commit()
conn.close()

with open("uci_resources.json", "r", encoding="utf-8") as f:
    resources = json.load(f)
with open("new_resources.json", "r", encoding="utf-8") as f:
    new_resources = json.load(f)

conn = s3.connect("resources.db")
cursor = conn.cursor()

for r in resources + new_resources:
    text = r["name"] + " " + r["description"] + " " + r["target_audience"]

    embedding = model.encode(text).tolist()

    cursor.execute(
        """
        INSERT INTO resources (category, name, location, contact_info, description, target_audience, source_url, embedding) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            r["category"],
            r["name"],
            r["location"],
            r["contact_info"],
            r["description"],
            r["target_audience"],
            r["source_url"],
            json.dumps(embedding)
        )
    )

conn.commit()
conn.close()