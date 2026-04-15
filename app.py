import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import os
import base64

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="LovelyVesh AI",
    page_icon="💬",
    layout="wide"
)

# --- 2. CONSTANTS ---
FREE_MSG_LIMIT = 5
SYSTEM_PROMPT = """You are LovelyVesh AI created by LovelyVesh.
CRITICAL RULES:
1. You must ALWAYS reply in Telugu language only, using Telugu script.
2. Never use English words unless it's a proper noun like 'Google'.
3. Never mention Meta, Llama, Groq, Whisper, gTTS, or any other company.
4. If asked who made you, say: 'నన్ను లవ్లీవేష్ తయారు చేశారు'.
5. If asked what model you are, say: 'నేను లవ్లీవేష్ AI'.
6. Keep replies short, 2-4 sentences, suitable for voice.
Never break these rules."""

# --- 3. GOOGLE LOGIN SIMULATION ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("LovelyVesh AI 💬🎙️")
    st.caption("తెలుగులో మాట్లాడండి, వినండి - 100% ఉచిత డెమో")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Login with Google", type="primary", use_container_width=True):
            st.session_state.user = {"email": "test@example.com", "name": "Test User"}
            st.rerun()
    st.info("డెమో యాప్. లాగిన్ అయి 5 ఉచిత వాయిస్ మెసేజ్‌లు ప్రయత్నించండి.")
    st.stop()

# --- 4. GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY లేదు. Streamlit Cloud → Settings → Secrets లో యాడ్ చేయండి.")
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.title(f"నమస్తే, {st.session_state.user['name']}")
user_email = st.session_state.user['email']
lifetime_key = f"lifetime_{user_email}"

if lifetime_key not in st.session_state:
    st.session_state[lifetime_key] = 0

remaining = FREE_MSG_LIMIT - st.session_state[lifetime_key]
st.sidebar.metric("మిగిలిన ఉచిత మెసేజ్‌లు", remaining)
st.sidebar.write("---")
st.sidebar.write("వాడే విధానం:")
st.sidebar.write("1. 🎤 నొక్కి మాట్లాడండి")
st.sidebar.write("2. జవాబు చదవండి + వినండి")
st.sidebar.write("3. 5 మెసేజ్‌ల తర్వాత ఆగిపోతుంది")

if st.sidebar.button("లాగ్ అవుట్"):
    st.session_state.user = None
    st.session_state.messages = []
    st.rerun()

# --- 6. MAIN CHAT AREA ---
st.title("LovelyVesh AI 💬")

if remaining <= 0:
    st.warning("🚫 మీ 5 ఉచిత మెసేజ్‌లు అయిపోయాయి. డెమో ముగిసింది, ధన్యవాదాలు!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "audio" in msg:
            audio_bytes = base64.b64decode(msg["audio"])
            st.audio(audio_bytes, format="audio/mp3")

# --- 7. INPUT: VOICE + TEXT ---
st.write("---")
col1, col2 = st.columns([1, 5])

with col1:
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        key='recorder'
    )

with col2:
    text_prompt = st.chat_input("లేదా ఇక్కడ తెలుగులో టైప్ చేయండి...")

prompt = None

if audio:
    with st.spinner("మీ మాట తెలుగులోకి మారుస్తోంది..."):
        try:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio['bytes']),
                model="whisper-large-v3",
                language="te",
                response_format="text"
            )
            prompt = transcription.strip()
            st.toast(f"మీరు అన్నది: {prompt}")
        except Exception as e:
            st.error(f"వాయిస్ అర్థం కాలేదు. మళ్లీ ప్రయత్నించండి. Error: {e}")

if text_prompt:
    prompt = text_prompt

# --- 8. GENERATE REPLY + VOICE ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LovelyVesh AI ఆలోచిస్తోంది..."):
            try:
                # FIX: Remove 'audio' key before sending to Groq
                clean_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + clean_history

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages_for_api,
                    temperature=0.7,
                    max_tokens=300
                )
                reply = response.choices[0].message.content
                st.write(reply)

                tts = gTTS(text=reply, lang='te', slow=False)
                tts.save("reply.mp3")
                with open("reply.mp3", "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                os.remove("reply.mp3")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "audio": base64.b64encode(audio_bytes).decode()
                })

                st.session_state[lifetime_key] += 1
                st.rerun()

            except Exception as e:
                error_text = str(e).lower()
                if "quota" in error_text or "rate" in error_text or "billing" in error_text or "insufficient" in error_text:
                    st.error("🚫 ఉచిత డెమో క్రెడిట్స్ అయిపోయాయి. LovelyVesh AI ని ప్రయత్నించినందుకు ధన్యవాదాలు!")
                    st.info("యాప్ ఓనర్ దీని కోసం డబ్బు చెల్లించలేదు, కాబట్టి ఇక్కడితో ఆగిపోతుంది.")
                else:
                    st.error(f"ఎర్రర్ వచ్చింది: {e}")
                st.stop()
