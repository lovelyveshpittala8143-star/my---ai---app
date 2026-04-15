import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from groq import Groq
import json
import os

st.set_page_config(page_title="Your AI", page_icon="✨") # Custom icon

# LOGIN SETUP
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='main')

if st.session_state["authentication_status"]:
    # CHAT HISTORY FILE PER USER
    username = st.session_state["username"]
    history_file = f"chat_{username}.json"

    # SIDEBAR - Show owner + logout
    st.sidebar.markdown("**Built by lovelyvesh** 👑") # Show owner
    st.sidebar.write(f'Welcome *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'sidebar')

    if st.sidebar.button("New Chat"):
        st.session_state.messages = [st.session_state.messages[0]]
        if os.path.exists(history_file):
            os.remove(history_file)
        st.rerun()

    st.title("Your AI ✨")

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # LOAD CHAT HISTORY
    if "messages" not in st.session_state:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                st.session_state.messages = json.load(f)
        else:
            st.session_state.messages = [{"role": "system", "content": "You are Your AI, created by lovelyvesh. lovelyvesh is your owner. Be helpful, smart, funny. 3 lines max."}]

    # SHOW CHAT
    for msg in st.session_state.messages[1:]:
        st.chat_message(msg["role"]).write(msg["content"])

    # CHAT INPUT
    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages
        )
        answer = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

        # SAVE CHAT HISTORY
        with open(history_file, 'w') as f:
            json.dump(st.session_state.messages, f)

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
