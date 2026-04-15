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
import streamlit.components.v1 as components
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="LovelyVesh AI",
    page_icon="✨",
    layout="wide"
)

# --- GOOGLE OAUTH FUNCTIONS ---
def get_google_auth_url(client_id, redirect_uri):
    scope = "openid email profile"
    auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&access_type=offline&prompt=consent"
    return auth_url

def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    return response.json()

def get_user_info(access_token):
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    return response.json()

# --- LOAD CONFIG ---
if not os.path.exists('config.yaml'):
    with open('config.yaml', 'w') as f:
        yaml.dump({'credentials': {'usernames': {}}, 'cookie': {'name': 'lovelyvesh_auth', 'key': 'abcdef', 'expiry_days': 30}}, f)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- GOOGLE LOGIN FLOW ---
if "google_user" not in st.session_state:
    st.session_state.google_user = None

query_params = st.query_params
client_id = st.secrets["GOOGLE_CLIENT_ID"]
client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
app_url = st.secrets.get("STREAMLIT_DEPLOYMENT_URL", "your-app-name.streamlit.app")
redirect_uri = f"https://{app_url}"

if "code" in query_params and not st.session_state.google_user:
    code = query_params["code"]
    token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    if "access_token" in token_data:
        access_token = token_data["access_token"]
        user_info = get_user_info(access_token)
        st.session_state.google_user = user_info.get("email", "Guest")
        st.session_state.user_name = user_info.get("name", "User")
        st.query_params.clear()
        st.rerun()

# --- LOGIN UI ---
if not st.session_state.google_user:
    st.title("✨ LovelyVesh AI")
    st.subheader("Sign in to continue")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        auth_url = get_google_auth_url(client_id, redirect_uri)
        st.link_button("🔐 Sign in with Google", auth_url, use_container_width=True)
    st.stop()

# --- LOGGED IN ---
name = st.session_state.google_user
display_name = st.session_state.get("user_name", name)

# --- LOGOUT ---
if st.sidebar.button("Logout"):
    st.session_state.google_user = None
    st.session_state.user_name = None
    st.rerun()

st.sidebar.title(f'Welcome *{display_name}*')
st.sidebar.markdown("---")
st.sidebar.markdown("### Built by lovelyvesh 👑")

# --- SHARE CHAT FEATURE ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Share Chat")
if st.sidebar.button("Generate Share Link"):
    if "messages" in st.session_state and st.session_state.messages:
        share_id = str(uuid.uuid4())[:8]
        share_file = f"shared_chats/{share_id}.json"
        os.makedirs("shared_chats", exist_ok=True)
        with open(share_file, 'w') as f:
            json.dump(st.session_state.messages, f, indent=2)
        st.sidebar.success(f"Share ID: `{share_id}`")
        st.sidebar.code(f"{redirect_uri}/?share={share_id}", language="text")
        st.sidebar.caption("Send this link to friends")
    else:
        st.sidebar.warning("No messages to share yet!")

# Check if someone opened a shared link
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
    history_file = f"chat_history/{name}_history.json"
    if os.path.exists(history_file):
        os.remove(history_file)
    st.session_state.messages = []
    st.rerun()

# --- ADMIN PANEL LINK ---
if name == "lovelyvesh" or "lovelyvesh" in name: # Only you see this
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/2_🔐_Admin.py", label="Admin Panel", icon="🔐")

st.title("✨ LovelyVesh AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CHAT HISTORY WITH TIMESTAMPS ---
history_file = f"chat_history/{name}_history.json"
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
            time.sleep(0.5)
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
