import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="WCST (Simplified)", layout="centered")

if "responses" not in st.session_state:
    st.session_state.responses = []
if "trial_num" not in st.session_state:
    st.session_state.trial_num = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_rule" not in st.session_state:
    st.session_state.current_rule = random.choice(["color", "shape"])
if "participant_info" not in st.session_state:
    st.session_state.participant_info = None

shapes = ["circle", "triangle", "square"]
colors = ["red", "green", "blue"]
cards = [{"shape": random.choice(shapes), "color": random.choice(colors)} for _ in range(5)]

st.title("Wisconsin Card Sorting Test (WCST) - Simplified")

if not st.session_state.participant_info:
    with st.form(key="participant_info_form"):
        st.subheader("Participant Information")
        name = st.text_input("Full Name")
        age = st.text_input("Age")
        profession = st.text_input("Profession")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")

    if submitted and name and age and profession and sleep_hours:
        st.session_state.participant_info = {
            "Name": name,
            "Age": age,
            "Profession": profession,
            "SleepHours": sleep_hours,
        }
        st.session_state.trial_num = 0
        st.session_state.responses = []
        st.session_state.current_rule = random.choice(["color", "shape"])
        st.experimental_rerun()

elif st.session_state.trial_num < 10:
    trial_card = {"shape": random.choice(shapes), "color": random.choice(colors)}
    rule = st.session_state.current_rule
    st.subheader(f"Trial {st.session_state.trial_num + 1} / 10")
    st.markdown(f"<h2>Sort this card: {trial_card['color']} {trial_card['shape']}</h2>", unsafe_allow_html=True)
    st.markdown("Choose the correct match:")

    col1, col2, col3 = st.columns(3)
    options = [random.choice(cards) for _ in range(3)]
    picked = None

    for i, col in enumerate([col1, col2, col3]):
        with col:
            if col.button(f"{options[i]['color']} {options[i]['shape']}", key=i):
                picked = options[i]

    if picked:
        rt = time.time() - st.session_state.start_time if st.session_state.start_time else 0
        correct = picked[rule] == trial_card[rule]
        st.session_state.responses.append({
            **st.session_state.participant_info,
            "TrialCard": f"{trial_card['color']} {trial_card['shape']}",
            "ChosenCard": f"{picked['color']} {picked['shape']}",
            "Rule": rule,
            "Correct": correct,
            "ReactionTime": round(rt, 2),
        })
        st.session_state.trial_num += 1
        if st.session_state.trial_num % 3 == 0:
            st.session_state.current_rule = random.choice(["color", "shape"])
        st.session_state.start_time = time.time()
        st.experimental_rerun()

else:
    df = pd.DataFrame(st.session_state.responses)
    st.success("Test completed! Download your results below.")
    st.dataframe(df)
    filename = f"wcst_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("Download Results as CSV", df.to_csv(index=False), file_name=filename, mime="text/csv")


    
