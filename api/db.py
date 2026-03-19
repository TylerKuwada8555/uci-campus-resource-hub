
import sqlite3 as s3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import faiss
import numpy as np

from context import add_context, QueryObject, model

def get_db():
    return s3.connect("resources.db", check_same_thread=False)

index = faiss.read_index("resources.index")
ids = np.load("ids.npy")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/query")
def query(query_object: QueryObject):
    db = get_db()
    cursor = db.cursor()
    query_object = QueryObject(
        query = query_object.query.lower(),
        name = query_object.name.lower(),
        major = query_object.major.lower(),
        year = query_object.year.lower(),
        domestic=query_object.domestic
    )

    if query_object.query and query_object.query.strip():
        query_vec = model.encode(query_object.query).astype(np.float32)
        query_vec = query_vec.reshape(1, -1)

        faiss.normalize_L2(query_vec)

        k = 20
        _, indices = index.search(query_vec, k)

        matched_ids = [int(ids[i]) for i in indices[0] if i != -1]

        if not matched_ids:
            db.close()
            return []

        placeholders = ",".join(["?"] * len(matched_ids))
        cursor.execute(f"""
            SELECT category, name, location, contact_info,description, target_audience, source_url, embedding
            FROM resources
            WHERE id IN ({placeholders})
        """, matched_ids)

        raw_results = cursor.fetchall()

    else:
        cursor.execute("""
            SELECT category, name, location, contact_info,description, target_audience, source_url, embedding
            FROM resources
            LIMIT 50
        """)
        raw_results = cursor.fetchall()

    ranked_results = add_context(raw_results, query_object)

    db.close()
    return ranked_results