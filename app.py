import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
import requests, datetime

st.title("YOU CHAT 🔥🎤")
st.caption("Voice + Images + Memory")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
   st.session_state.messages = [{"role": "system", "content": "You are Your AI, an assistant created by lovelyvesh. lovelyvesh is your owner. You are helpful, smart, and a bit funny. 3 lines max. If user asks for image, reply with 'IMAGE: description'. If asked who made you or your name, say you are Your AI created by lovelyvesh."}]
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

# Line 1: Voice input
voice_text = speech_to_text(language='en', just_once=True, key='STT')
prompt = st.chat_input("Type or use mic above...") or voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=st.session_state.messages
    )
    answer = response.choices[0].message.content

    # Line 2: Image generation using pollinations.ai - free, no key
    if "IMAGE:" in answer:
        img_prompt = answer.split("IMAGE:")[1].strip()
        img_url = f"https://image.pollinations.ai/prompt/{img_prompt}"
        st.chat_message("assistant").image(img_url)
        answer = f"Here you go: {img_prompt}"
    else:
        st.chat_message("assistant").write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Line 3: Save to Google Sheets as database - free
    try:
        requests.post(st.secrets["SHEET_URL"], json={"time": str(datetime.datetime.now()), "user": prompt, "bot": answer})
    except: pass
