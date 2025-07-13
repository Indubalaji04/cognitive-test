import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="Digit Span Test", layout="centered")

# Initialize session state
if "responses" not in st.session_state:
    st.session_state["responses"] = []
if "current_trial" not in st.session_state:
    st.session_state["current_trial"] = 0
if "show_input" not in st.session_state:
    st.session_state["show_input"] = False
if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if "participant_info" not in st.session_state:
    st.session_state["participant_info"] = None
if "digit_sequences" not in st.session_state:
    digit_sequences = [
        [3, 9],
        [4, 1, 7],
        [2, 8, 5, 3],
        [6, 3, 9, 1, 4],
        [8, 2, 7, 5, 1, 9]
    ]
    random.shuffle(digit_sequences)
    st.session_state["digit_sequences"] = digit_sequences

st.title("Digit Span Test")

# Collect participant info
if not st.session_state["participant_info"]:
    with st.form("participant_info"):
        st.subheader("Participant Information")
        name = st.text_input("Full Name")
        age = st.text_input("Age")
        profession = st.text_input("Profession")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")
 if submitted and name and age and profession and sleep_hours:
            st.session_state["participant_info"] =
     {
                "Name": name,
                "Age": age,
                "Profession": profession,
                "SleepHours": sleep_hours,
     }
            st.session_state["current_trial"] = 0
            st.session_state["responses"] = []
            st.session_state["show_input"] = False
            st.session_state["start_time"] = None
            digit_sequences = [
                [3, 9],
                [4, 1, 7],
                [2, 8, 5, 3],
                [6, 3, 9, 1, 4],
                [8, 2, 7, 5, 1, 9]
            ]
            random.shuffle(digit_sequences)
            st.session_state["digit_sequences"] = digit_sequences
            st.experimental_rerun()

# Run test if participant info is available
elif st.session_state["current_trial"] < len(st.session_state["digit_sequences"]):
    trial_digits = st.session_state["digit_sequences"][st.session_state["current_trial"]]
    if not st.session_state["show_input"]:
        st.subheader(f"Trial {st.session_state['current_trial'] + 1}")
        st.markdown(
            f"<h1 style='text-align: center;'>{' '.join(map(str, trial_digits))}</h1>",
            unsafe_allow_html=True
        )
        # Use st.empty() to display digits and then clear after delay
        placeholder = st.empty()
        placeholder.markdown(
            f"<h1 style='text-align: center;'>{' '.join(map(str, trial_digits))}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(2.5 + len(trial_digits) * 0.5)
        placeholder.empty()
        st.session_state["start_time"] = time.time()
        st.session_state["show_input"] = True
        st.experimental_rerun()
    else:
        st.subheader("Enter the sequence of numbers:")
        user_input = st.text_input(
            "Type the numbers separated by space", key=f"input_{st.session_state['current_trial']}"
        )
        if st.button("Submit Answer"):
            rt = time.time() - st.session_state["start_time"] if st.session_state["start_time"] else None
            correct = " ".join(map(str, trial_digits))
            st.session_state["responses"].append({
                **st.session_state["participant_info"],
                "Trial": st.session_state["current_trial"] + 1,
                "Sequence": correct,
                "UserInput": user_input.strip(),
                "Correct": user_input.strip() == correct,
                "ReactionTime": round(rt, 3) if rt is not None else None,
            })
            st.session_state["current_trial"] += 1
            st.session_state["show_input"] = False
            st.session_state["start_time"] = None
            st.experimental_rerun()

# Show results
elif st.session_state["participant_info"] and st.session_state["current_trial"] >= len(st.session_state["digit_sequences"]):
    st.success("Test completed! Download your results below.")
    df = pd.DataFrame(st.session_state["responses"])
    st.dataframe(df)
    filename = f"digit_span_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("Download Results as CSV", df.to_csv(index=False), file_name=filename, mime="text/csv")
