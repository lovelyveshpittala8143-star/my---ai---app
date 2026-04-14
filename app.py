import streamlit as st
import os
from groq import Groq

# Set up Groq client (no key needed in code)
client = Groq()

st.title("My First AI App 😎")

# Text input
user_input = st.text_input("Ask me anything:")

if st.button("Get Answer"):
    if user_input:
        try:
            # Call Groq API
            response = client.chat.completions.create(
                model="llama3-8b-8192",  # Free model
                messages=[{"role": "user", "content": user_input}]
            )
            answer = response.choices[0].message.content
            st.write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Type something first!")
