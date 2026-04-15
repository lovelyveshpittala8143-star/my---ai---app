import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from groq import Groq
import json
import os
from datetime import datetime
import time
import uuid

st.set_page_config(
    page_title="LovelyVesh AI",
    page_icon="✨",
    layout="wide"
)

# --- LOAD CONFIG ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- LOGIN ---
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
elif authentication_status:
    # --- LOGGED IN ---
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f'Welcome *{name}*')
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Built by lovelyvesh 👑")

    # --- SHARE CHAT FEATURE ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔗 Share Chat")
    if st.sidebar.button("Generate Share Link"):
        # Create unique ID for this chat
        share_id = str(uuid.uuid4())[:8]
        share_file = f"shared_chats/{share_id}.json"
        os.makedirs("shared_chats", exist_ok=True)
        with open(share_file, 'w') as f:
            json.dump(st.session_state.messages, f, indent=2)
        st.sidebar.success(f"Share ID: `{share_id}`")
        st.sidebar.code(f"?share={share_id}", language="text")
        st.sidebar.caption("Send this ID to friends. They add?share=ID to URL")

    # Check if someone opened a shared link
    query_params = st.query_params
    if "share" in query_params:
        share_id = query_params["share"]
        share_file = f"shared_chats/{share_id}.json"
        if os.path.exists(share_file):
            st.info(f"Viewing shared chat: {share_id}")
            with open(share_file, 'r') as f:
                shared_messages = json.load(f)
            for msg in shared_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if "timestamp" in msg:
                        st.caption(msg["timestamp"])
            st.stop() # Don't load normal chat

    # --- CLEAR CHAT BUTTON ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear Chat History"):
        history_file = f"chat_history/{username}_history.json"
        if os.path.exists(history_file):
            os.remove(history_file)
        st.session_state.messages = []
        st.rerun()

    # --- ADMIN PANEL LINK ---
    if username == "lovelyvesh": # Only you see this
        st.sidebar.markdown("---")
        st.sidebar.page_link("pages/2_🔐_Admin.py", label="Admin Panel", icon="🔐")

    st.title("✨ LovelyVesh AI")

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # --- CHAT HISTORY WITH TIMESTAMPS ---
    history_file = f"chat_history/{username}_history.json"
    os.makedirs("chat_history", exist_ok=True)

    if "messages" not in st.session_state:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                st.session_state.messages = json.load(f)
        else:
            st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # --- TIMESTAMP FEATURE ---
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")

    if prompt := st.chat_input("Ask anything..."):
        # --- ADD TIMESTAMP TO USER MSG ---
        timestamp = datetime.now().strftime("%I:%M %p | %b %d")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")

        with st.chat_message("assistant"):
            # --- TYPING ANIMATION ---
            with st.status("Your AI is thinking...", expanded=False) as status:
                time.sleep(0.5) # Fake thinking for effect
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                status.update(label="Done!", state="complete", expanded=False)

            msg_response = response.choices[0].message.content
            # --- ADD TIMESTAMP TO AI MSG ---
            ai_timestamp = datetime.now().strftime("%I:%M %p | %b %d")
            st.markdown(msg_response)
            st.caption(f"*{ai_timestamp}*")

            st.session_state.messages.append({
                "role": "assistant",
                "content": msg_response,
                "timestamp": ai_timestamp
            })

        # Save history
        with open(history_file, 'w') as f:
            json.dump(st.session_state.messages, f, indent=2)
