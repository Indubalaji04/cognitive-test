import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="Flanker Test", layout="centered")

# Initialize session state variables
if "responses" not in st.session_state:
    st.session_state.responses = []
if "current_trial" not in st.session_state:
    st.session_state.current_trial = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "participant_info" not in st.session_state:
    st.session_state.participant_info = None

# Define trials (arrows and correct response)
flanker_trials = [
    {"stimulus": "→→→→→", "correct": "Right"},
    {"stimulus": "←←←←←", "correct": "Left"},
    {"stimulus": "→→←→→", "correct": "Left"},
    {"stimulus": "←←→←←", "correct": "Right"},
    {"stimulus": "→←→←→", "correct": "Left"},
    {"stimulus": "←→←→←", "correct": "Right"},
]
random.shuffle(flanker_trials)

st.title("Flanker Test")

# Step 1: Get participant info
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
            st.session_state.start_time = time.time()
            st.rerun()

# Step 2: Run trials
elif st.session_state.current_trial < len(flanker_trials):
    trial = flanker_trials[st.session_state.current_trial]
    st.subheader(f"Trial {st.session_state.current_trial + 1} of {len(flanker_trials)}")
    st.markdown(f"<h1 style='text-align: center; font-size: 64px'>{trial['stimulus']}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("Left"):
        rt = time.time() - st.session_state.start_time
        st.session_state.responses.append({
            **st.session_state.participant_info,
            "Stimulus": trial["stimulus"],
            "CorrectAnswer": trial["correct"],
            "UserResponse": "Left",
            "Correct": trial["correct"] == "Left",
            "ReactionTime": round(rt, 3),
        })
        st.session_state.current_trial += 1
        st.session_state.start_time = time.time()
        st.rerun()

    if col2.button("Right"):
        rt = time.time() - st.session_state.start_time
        st.session_state.responses.append({
            **st.session_state.participant_info,
            "Stimulus": trial["stimulus"],
            "CorrectAnswer": trial["correct"],
            "UserResponse": "Right",
            "Correct": trial["correct"] == "Right",
            "ReactionTime": round(rt, 3),
        })
        st.session_state.current_trial += 1
        st.session_state.start_time = time.time()
        st.rerun()

# Step 3: Show results
elif st.session_state.participant_info and st.session_state.current_trial >= len(flanker_trials):
    st.success("Test completed! Download your results below.")
    df = pd.DataFrame(st.session_state.responses)
    st.dataframe(df)
    filename = f"flanker_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("Download Results as CSV", df.to_csv(index=False), file_name=filename, mime="text/csv")



       
