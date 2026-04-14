import streamlit as st
from openai import OpenAI

st.title("My First AI App 🤖")

key = st.text_input("OpenAI API Key", type="password")
question = st.text_input("Ask me anything")

if st.button("Get Answer"):
    if key and question:
        try:
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}]
            )
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Enter both key and question")
