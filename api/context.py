
from pydantic import BaseModel
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import ast

class QueryObject(BaseModel):
    query: str = ""
    name: str = ""
    year: str = ""
    major: str = ""
    domestic: bool

model = SentenceTransformer('all-MiniLM-L6-v2')

with open('mappings.json', 'r') as f:
    mappings = json.load(f)

for key in mappings:
    if isinstance(mappings[key], dict):
        for subkey in mappings[key]:
            mappings[key][subkey] = [t.lower() for t in mappings[key][subkey]]
    elif isinstance(mappings[key], list):
        mappings[key] = [t.lower() for t in mappings[key]]

resource_keys = ['category', 'name', 'location', 'contact_info','description', 'target_audience', 'source_url', 'embedding']

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def contextual_boost(result, mappings, major, year, is_international):
    score = 0
    text = (result['name'] + " " + result['description'] + " " + result['target_audience']).lower()

    if major in mappings['major']:
        if any(term.lower() in text for term in mappings['major'][major]):
            score += 3
            print("major: " + major)

    if year in mappings['year']:
        if any(term.lower() in text for term in mappings['year'][year]):
            score += 2.5

    if is_international:
        if any(term.lower() in text for term in mappings['international']):
            score += 1.5

    return score

def add_context(raw_results, query_object: QueryObject):
    results = []

    query_vec = None
    query_words = []
    if query_object.query and query_object.query.strip():
        query_vec = model.encode(query_object.query).astype(np.float32)
        query_words = query_object.query.lower().split()

    for result in raw_results:
        r = dict(zip(resource_keys, list(result)))

        embedding = np.array(ast.literal_eval(r['embedding']), dtype=np.float32)

        semantic = 0
        if query_vec is not None:
            semantic = cosine_similarity(query_vec, embedding)

        context = contextual_boost(
            r,
            mappings,
            query_object.major,
            query_object.year,
            not query_object.domestic
        )

        text = (r['name'] + " " + r['description'] + " " + r['target_audience']).lower()
        word_match_score = sum(1 for w in query_words if w in text)
        word_match_score *= 2.0

        score = semantic * 4 + context + word_match_score

        r_copy = r.copy()
        r_copy.pop('embedding', None)
        r_copy['score'] = float(score)

        results.append(r_copy)

    return sorted(results, key=lambda x: x['score'], reverse=True)