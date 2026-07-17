import sys
import os
import subprocess
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from retriever import get_top_chunks
from openai import OpenAI

CHAT_MODEL = "phi-3.5-mini-instruct-trtrtx-gpu:2"


def get_foundry_url():
    """Foundry Local'in o anki portunu otomatik bul."""
    try:
        result = subprocess.run(
            ["foundry", "service", "status"],
            capture_output=True, text=True, timeout=10
        )
        match = re.search(r"http://127\.0\.0\.1:(\d+)", result.stdout)
        if match:
            port = match.group(1)
            print(f"✅ Foundry portu bulundu: {port}")
            return f"http://127.0.0.1:{port}/v1"
    except Exception as e:
        print(f"⚠️  Port tespit hatası: {e}")
    print("⚠️  Varsayılan port kullanılıyor: 5273")
    return "http://127.0.0.1:5273/v1"


# Sunucu başlarken portu bir kez tespit et
FOUNDRY_URL = get_foundry_url()
client = OpenAI(base_url=FOUNDRY_URL, api_key="foundry")

app = Flask(__name__)

with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
    HTML = f.read()


@app.route("/")
def index():
    return HTML


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    soru = data.get("message", "")
    sonuclar = get_top_chunks(soru, top_k=3)
    if not sonuclar:
        return jsonify({"answer": "Belgelerde ilgili bilgi bulunamadı.", "sources": []})
    kaynaklar = list(set([k for _, k, _ in sonuclar]))
    bagiam = "\n\n".join([f"[{k}]: {i}" for _, k, i in sonuclar])
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sen yardımcı bir asistansın. Soruları SADECE verilen belge "
                    "içeriklerine dayanarak yanıtla. Belgede cevap yoksa "
                    "'Bu bilgi belgelerimde mevcut değil.' de. Türkçe yanıt ver."
                ),
            },
            {"role": "user", "content": f"Belgeler:\n{bagiam}\n\nSoru: {soru}"},
        ],
        temperature=0.3,
    )
    return jsonify({"answer": response.choices[0].message.content, "sources": kaynaklar})


if __name__ == "__main__":
    print(f"\n🚀 RAG Asistanı başlatılıyor...")
    print(f"🔗 Foundry URL: {FOUNDRY_URL}")
    print(f"🌐 Tarayıcıda aç: http://localhost:5000\n")
    app.run(debug=False, port=5000)
