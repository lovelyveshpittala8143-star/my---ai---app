import streamlit as st
import os
import json
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Admin Panel", page_icon="🔐")

# Check login first
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status != True or username != "lovelyvesh":
    st.error("Admin access only. GTFO 😂")
    st.stop()

st.title("🔐 Admin Panel")
st.write(f"Welcome back, king {name}")

# --- SEE ALL USERS ---
st.subheader("All Users")
for user in config['credentials']['usernames']:
    st.write(f"- {user}")

st.markdown("---")

# --- SEE ALL CHAT HISTORIES ---
st.subheader("User Chat Histories")
if os.path.exists("chat_history"):
    for file in os.listdir("chat_history"):
        if file.endswith("_history.json"):
            user = file.replace("_history.json", "")
            with st.expander(f"💬 {user}'s chat"):
                with open(f"chat_history/{file}", 'r') as f:
                    data = json.load(f)
                    st.json(data, expanded=False)
                    st.write(f"Total messages: {len(data)}")
else:
    st.info("No chats yet")

st.markdown("---")

# --- SEE SHARED CHATS ---
st.subheader("Shared Chats")
if os.path.exists("shared_chats"):
    for file in os.listdir("shared_chats"):
        share_id = file.replace(".json", "")
        st.write(f"Share ID: `{share_id}` | Link: `?share={share_id}`")
else:
    st.info("No shared chats yet")
