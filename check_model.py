import requests

base = "http://127.0.0.1:60367"
data = {
    "model": "phi-3.5-mini-instruct-trtrtx-gpu:2",
    "messages": [{"role": "user", "content": "hi"}]
}

paths = [
    "/openai/chat/completions",
    "/openai/v1/chat/completions",
    "/v1/chat/completions",
    "/chat/completions",
]

for path in paths:
    try:
        r = requests.post(base + path, json=data, timeout=5)
        print(f"{path} → {r.status_code}")
    except Exception as e:
        print(f"{path} → HATA: {e}")