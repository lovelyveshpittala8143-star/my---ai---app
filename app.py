import streamlit as st
from groq import Groq

st.title("RCB Roast Bot 🔥")
st.caption("Built by you. Powered by Groq.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state: # Line 1: Create memory
    st.session_state.messages = [{"role": "system", "content": "You are RCB Roast Bot. You are sarcastic, funny, and roast everything. Keep replies under 3 lines."}] # Line 2: Give it personality

for msg in st.session_state.messages[1:]: # Line 3: Show old chats
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me to roast something..."): # Line 4: Better input box
    st.session_state.messages.append({"role": "user", "content": prompt}) # Line 5: Save user msg
    st.chat_message("user").write(prompt)
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=st.session_state.messages
    )
    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
