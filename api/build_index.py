import sqlite3 as s3
import numpy as np
import faiss
import ast

conn = s3.connect("resources.db")
cursor = conn.cursor()

cursor.execute("SELECT id, embedding FROM resources")
rows = cursor.fetchall()

ids = []
embeddings = []

for rid, emb_str in rows:
    emb = np.array(ast.literal_eval(emb_str), dtype=np.float32)
    ids.append(rid)
    embeddings.append(emb)

embeddings = np.vstack(embeddings)

faiss.normalize_L2(embeddings)

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

faiss.write_index(index, "resources.index")
np.save("ids.npy", np.array(ids))