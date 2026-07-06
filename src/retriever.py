import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
DB_PATH = "data/rag.db"

def cosine_similarity(vec1, vec2):
    """İki vektör arasındaki benzerliği hesapla"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_top_chunks(query, top_k=3):
    """Sorguya en yakın chunk'ları getir"""
    query_embedding = EMBEDDING_MODEL.encode(query).tolist()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT kaynak, icerik, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for kaynak, icerik, embedding_json in rows:
        embedding = json.loads(embedding_json)
        score = cosine_similarity(query_embedding, embedding)
        results.append((score, kaynak, icerik))

    results.sort(reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    test_sorgu = "RAG nedir ne işe yarar?"
    print(f"Sorgu: {test_sorgu}\n")
    
    sonuclar = get_top_chunks(test_sorgu)
    for i, (score, kaynak, icerik) in enumerate(sonuclar):
        print(f"--- Sonuç {i+1} (benzerlik: {score:.3f}) ---")
        print(f"Kaynak: {kaynak}")
        print(f"İçerik: {icerik[:200]}...")
        print()