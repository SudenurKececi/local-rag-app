import os
import sqlite3
import json
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
DB_PATH = "data/rag.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kaynak TEXT,
            icerik TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Veritabanı hazır.")

def chunk_text(text, chunk_size=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def get_embedding(text):
    embedding = EMBEDDING_MODEL.encode(text)
    return embedding.tolist()

def ingest_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_text(text)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)} işleniyor...")
        embedding = get_embedding(chunk)
        cursor.execute(
            "INSERT INTO documents (kaynak, icerik, embedding) VALUES (?, ?, ?)",
            (os.path.basename(filepath), chunk, json.dumps(embedding))
        )
    conn.commit()
    conn.close()
    print(f"✓ {os.path.basename(filepath)} yüklendi — {len(chunks)} chunk kaydedildi.")

if __name__ == "__main__":
    init_db()
    for filename in os.listdir("data"):
        if filename.endswith(".txt"):
            print(f"\n{filename} işleniyor...")
            ingest_file(os.path.join("data", filename))
    print("\nTüm belgeler yüklendi!")