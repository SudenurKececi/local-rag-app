import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from retriever import get_top_chunks
from openai import OpenAI
import time

st.set_page_config(
    page_title="Yerel RAG Asistanı",
    page_icon="🤖",
    layout="wide"
)

# Session state başlangıç
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Tema renkleri
if st.session_state.dark_mode:
    bg          = "#1E1E2E"
    sidebar_bg  = "#13131F"
    card_bg     = "#2A2A3E"
    card_border = "#3A3A5C"
    text_color  = "#E0E0E0"
    sub_color   = "#9E9E9E"
    input_bg    = "#2A2A3E"
    user_bubble = "#1565C0"
    asst_bubble = "#2A2A3E"
    asst_border = "#3A3A5C"
    expander_bg = "#1E1E2E"
else:
    bg          = "#EFF6FC"
    sidebar_bg  = "#0078D4"
    card_bg     = "#FFFFFF"
    card_border = "#D0E8F8"
    text_color  = "#1A1A1A"
    sub_color   = "#605E5C"
    input_bg    = "#FFFFFF"
    user_bubble = "#0078D4"
    asst_bubble = "#FFFFFF"
    asst_border = "#D0E8F8"
    expander_bg = "#EFF6FC"

st.markdown(f"""
<style>
    /* Genel arka plan */
    .stApp {{ background-color: {bg}; }}
    .stApp * {{ color: {text_color}; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sidebar_bg} 0%, {"#005a9e" if not st.session_state.dark_mode else "#0D0D1A"} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.25); }}

    /* Chat mesaj alanları */
    [data-testid="stChatMessage"] {{
        border-radius: 16px;
        padding: 10px 16px;
        margin: 6px 0;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: {user_bubble}22;
        border-left: 4px solid {user_bubble};
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        background-color: {asst_bubble};
        border-left: 4px solid #50E6FF;
        border: 1px solid {asst_border};
        box-shadow: 0 2px 8px rgba(0,120,212,0.07);
    }}

    /* Chat input */
    [data-testid="stChatInput"] textarea {{
        background-color: {input_bg} !important;
        border: 2px solid #0078D4 !important;
        border-radius: 12px !important;
        color: {text_color} !important;
    }}
    [data-testid="stChatInput"]:focus-within {{
        box-shadow: 0 0 0 3px rgba(0,120,212,0.18) !important;
    }}

    /* Sidebar butonları */
    div[data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255,255,255,0.12) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
        border-radius: 10px !important;
        width: 100%;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    div[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: rgba(255,255,255,0.28) !important;
        border-color: white !important;
        transform: translateY(-1px);
    }}

    /* Başlık */
    .ms-header {{
        background: linear-gradient(135deg, #0078D4, #00BCF2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    .ms-subheader {{
        color: {sub_color};
        font-size: 13px;
        margin-bottom: 20px;
        margin-top: 2px;
    }}

    /* Mesaj sayacı kutusu */
    .msg-count-box {{
        background-color: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 10px;
        padding: 10px 14px;
        text-align: center;
        font-size: 13px;
        margin: 6px 0;
    }}

    /* Typing animasyonu */
    .typing-dots {{
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 6px 0;
    }}
    .typing-dots span {{
        width: 8px;
        height: 8px;
        background-color: #0078D4;
        border-radius: 50%;
        animation: bounce 1.2s infinite ease-in-out;
    }}
    .typing-dots span:nth-child(1) {{ animation-delay: 0s; }}
    .typing-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
    .typing-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
    @keyframes bounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
        30% {{ transform: translateY(-8px); opacity: 1; }}
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {expander_bg} !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        color: #0078D4 !important;
        border: 1px solid {card_border} !important;
    }}

    /* Hoş geldiniz kartı */
    .welcome-card {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
        color: {sub_color};
        box-shadow: 0 2px 12px rgba(0,120,212,0.06);
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_client():
    return OpenAI(
        base_url="http://127.0.0.1:60367/v1",
        api_key="foundry"
    )

CHAT_MODEL = "phi-3.5-mini-instruct-trtrtx-gpu:2"

def answer_query(soru, client):
    sonuclar = get_top_chunks(soru, top_k=3)
    if not sonuclar:
        return "Belgelerde ilgili bilgi bulunamadı.", []
    kaynaklar = list(set([kaynak for _, kaynak, _ in sonuclar]))
    bagiam = "\n\n".join([f"[{kaynak}]: {icerik}" for _, kaynak, icerik in sonuclar])
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Sen yardımcı bir asistansın. Soruları SADECE verilen belge içeriklerine dayanarak yanıtla. Belgede cevap yoksa 'Bu bilgi belgelerimde mevcut değil.' de. Türkçe yanıt ver."},
            {"role": "user", "content": f"Belgeler:\n{bagiam}\n\nSoru: {soru}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content, kaynaklar

# ── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 RAG Asistanı")
    st.markdown("*Microsoft Foundry Local*")
    st.markdown("---")

    mode_label = "☀️ Açık Moda Geç" if st.session_state.dark_mode else "🌙 Karanlık Moda Geç"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown("**Nasıl çalışır?**")
    st.markdown("1️⃣ Sorunuzu yazın")
    st.markdown("2️⃣ Belgelerden ilgili parçalar bulunur")
    st.markdown("3️⃣ Yerel LLM cevap üretir")
    st.markdown("---")
    st.markdown("**⚙️ Yapılandırma**")
    st.markdown("🧠 `phi-3.5-mini`")
    st.markdown("🔤 `multilingual-MiniLM`")
    st.markdown("🗄️ `SQLite`")
    st.markdown("---")

    msg_count = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f"""
    <div class="msg-count-box">
        💬 <b>{msg_count}</b> mesaj &nbsp;|&nbsp; ❓ <b>{user_count}</b> soru
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Ana İçerik ────────────────────────────────────────
st.markdown('<div class="ms-header">Yerel RAG Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="ms-subheader">⚡ Çevrimdışı &nbsp;·&nbsp; 🔒 Gizli &nbsp;·&nbsp; 📄 Belgelerinizden cevaplar</div>', unsafe_allow_html=True)

# Hoş geldiniz ekranı
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3 style="-webkit-text-fill-color:unset; color:#0078D4;">Merhaba! 👋</h3>
        <p>Belgeleriniz hakkında soru sorabilirsiniz.<br>
        Yüklenen belgelerden otomatik olarak cevap üretilir.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

# Geçmiş mesajlar
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"📄 {len(msg['sources'])} kaynaktan yanıtlandı"):
                for s in msg["sources"]:
                    st.markdown(f"• `{s}`")

# Chat input
if soru := st.chat_input("Sorunuzu buraya yazın..."):
    client = get_client()

    st.session_state.messages.append({"role": "user", "content": soru})
    with st.chat_message("user", avatar="👤"):
        st.markdown(soru)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("""
        <div class="typing-dots">
            <span></span><span></span><span></span>
            &nbsp;<i style="font-size:13px; opacity:0.6;">Düşünüyor...</i>
        </div>
        """, unsafe_allow_html=True)

        cevap, kaynaklar = answer_query(soru, client)
        placeholder.markdown(cevap)

        if kaynaklar:
            with st.expander(f"📄 {len(kaynaklar)} kaynaktan yanıtlandı"):
                for s in kaynaklar:
                    st.markdown(f"• `{s}`")

    st.session_state.messages.append({
        "role": "assistant",
        "content": cevap,
        "sources": kaynaklar
    })