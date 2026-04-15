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
1. Never mention Meta, Llama, Groq, Whisper, gTTS, or any other company.
2. If asked who made you, say: 'I was created by LovelyVesh'.
3. If asked what model you are, say: 'I am LovelyVesh AI'.
4. Reply in the same language the user used. If user speaks Telugu, reply in Telugu. If English, reply in English.
5. Keep replies short, 2-4 sentences, suitable for voice.
Never break these rules."""

# --- 3. GOOGLE LOGIN SIMULATION ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("LovelyVesh AI 💬🎙️")
    st.caption("Talk or type in English or Telugu - 100% free demo")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Login with Google", type="primary", use_container_width=True):
            st.session_state.user = {"email": "test@example.com", "name": "Test User"}
            st.rerun()
    st.info("Demo app. Login to try 5 free voice messages.")
    st.stop()

# --- 4. GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY missing. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.title(f"Hello, {st.session_state.user['name']}")
user_email = st.session_state.user['email']
lifetime_key = f"lifetime_{user_email}"

if lifetime_key not in st.session_state:
    st.session_state[lifetime_key] = 0

remaining = FREE_MSG_LIMIT - st.session_state[lifetime_key]
st.sidebar.metric("Free messages left", remaining)
st.sidebar.write("---")
st.sidebar.write("How to use:")
st.sidebar.write("1. Tap 🎤 and speak")
st.sidebar.write("2. Read + hear the reply")
st.sidebar.write("3. Stops after 5 messages")

if st.sidebar.button("Log out"):
    st.session_state.user = None
    st.session_state.messages = []
    st.rerun()

# --- 6. MAIN CHAT AREA ---
st.title("LovelyVesh AI 💬")

if remaining <= 0:
    st.warning("🚫 Your 5 free messages are over. Demo ended, thank you!")
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
    text_prompt = st.chat_input("Or type here in English or Telugu...")

prompt = None
detected_lang = 'en' # Default to English voice

if audio:
    with st.spinner("Converting your speech to text..."):
        try:
            # Let Whisper auto-detect language
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio['bytes']),
                model="whisper-large-v3",
                response_format="verbose_json" # To get language
            )
            prompt = transcription.text.strip()
            detected_lang = transcription.language # 'en' or 'te' etc
            st.toast(f"You said: {prompt}")
        except Exception as e:
            st.error(f"Couldn't understand audio. Try again. Error: {e}")

if text_prompt:
    prompt = text_prompt
    # Simple check: if Telugu characters exist, set lang to 'te'
    if any("\u0c00" <= c <= "\u0c7f" for c in text_prompt):
        detected_lang = 'te'
    else:
        detected_lang = 'en'

# --- 8. GENERATE REPLY + VOICE ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LovelyVesh AI is thinking..."):
            try:
                # Remove 'audio' key before sending to Groq
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

                # Use gTTS with detected language. Default to English.
                tts_lang = 'te' if detected_lang == 'te' else 'en'
                tts = gTTS(text=reply, lang=tts_lang, slow=False)
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
                    st.error("🚫 Free demo credits are over. Thanks for trying LovelyVesh AI!")
                    st.info("The app owner hasn't paid for this, so it stops here.")
                else:
                    st.error(f"Error occurred: {e}")
                st.stop()
