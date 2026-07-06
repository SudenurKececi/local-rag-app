import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retriever import get_top_chunks
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:60367/v1",
    api_key="foundry"
)
CHAT_MODEL = "phi-3.5-mini-instruct-trtrtx-gpu:2"

def answer_query(soru):
    sonuclar = get_top_chunks(soru, top_k=3)
    if not sonuclar:
        return "Belgelerde ilgili bilgi bulunamadı."

    bagiam = "\n\n".join([f"[{kaynak}]: {icerik}" for _, kaynak, icerik in sonuclar])

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Sen bir yardımcı asistansın. Soruları SADECE verilen belge içeriklerine dayanarak yanıtla. Belgede cevap yoksa 'Bu bilgi belgelerimde mevcut değil.' de."},
            {"role": "user", "content": f"Belgeler:\n{bagiam}\n\nSoru: {soru}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Yerel RAG Asistanı ===")
    print("Çıkmak için 'q' yaz.\n")
    while True:
        soru = input("Sorunuz: ").strip()
        if soru.lower() == "q":
            break
        if not soru:
            continue
        print("\nCevap:", answer_query(soru))
        print()