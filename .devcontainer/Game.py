import streamlit as st
import random

st.set_page_config(page_title="Your AI Games", page_icon="🎮")

if st.session_state.get("authentication_status")!= True:
    st.error("Please login from main page first")
    st.stop()

st.title("RCB IPL Trophy Year 🎮")
st.sidebar.markdown("**Built by lovelyvesh** 👑")

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.q_num = 1
    st.session_state.correct_year = random.randint(2008, 2025)

st.write(f"**Question {st.session_state.q_num}** | Score: {st.session_state.score}")
st.write("RCB finally wins IPL in which year? 😭")

guess = st.number_input("Your guess:", min_value=2008, max_value=2050, step=1)

if st.button("Guess"):
    if guess == st.session_state.correct_year:
        st.success("CORRECT! RCB won IPL! Universe collapsed! +10 pts")
        st.session_state.score += 10
        st.balloons()
    else:
        hint = "too early, they still bottling" if guess < st.session_state.correct_year else "too late, even RCB can't choke that long"
        st.error(f"WRONG! {hint} -1 pt")
        st.session_state.score -= 1

    st.session_state.q_num += 1
    st.session_state.correct_year = random.randint(2008, 2025)
    st.rerun()
