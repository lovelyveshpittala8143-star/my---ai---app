import streamlit as st
from groq import Groq

st.title("My First AI App 😎")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

user_input = st.text_input("Ask me anything:")

if st.button("Get Answer"):
    if user_input:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": user_input}]
            )
            answer = response.choices[0].message.content
            st.write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Type something first!")
