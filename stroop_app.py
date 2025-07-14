
import streamlit as st
import random
import time
import pandas as pd

# ---------------------------
# Initialize session state
# ---------------------------
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "start_time" not in st.session_state:
    st.session_state.start_time = 0

# ---------------------------
# Participant Info
# ---------------------------
st.title("ðŸ§  Stroop Test")
if not st.session_state.test_started:
    with st.form("participant_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Age", min_value=1, max_value=100, step=1)
        profession = st.text_input("Profession")
        sleep_hours = st.number_input("Hours of sleep last night", min_value=0.0, max_value=24.0, step=0.5)
        start_btn = st.form_submit_button("Start Test")
        if start_btn and name and profession:
            st.session_state.name = name
            st.session_state.age = age
            st.session_state.profession = profession
            st.session_state.sleep_hours = sleep_hours
            st.session_state.test_started = True
            st.session_state.trial_index = 0
            st.rerun()

# ---------------------------
# Test Parameters
# ---------------------------
colors = ["RED", "GREEN", "BLUE", "YELLOW"]
color_map = {
    "RED": "red",
    "GREEN": "green",
    "BLUE": "blue",
    "YELLOW": "yellow"
}
num_trials = 5

# ---------------------------
# Run Test
# ---------------------------
if st.session_state.test_started and st.session_state.trial_index < num_trials:
    trial = st.session_state.trial_index
    word = random.choice(colors)
    font_color = random.choice(colors)

    # Save current trial word/color
    st.session_state.current_word = word
    st.session_state.current_color = font_color

    st.markdown(f"### Trial {trial + 1}")
    st.markdown(f"<h1 style='color:{color_map[font_color]};'>{word}</h1>", unsafe_allow_html=True)

    if st.session_state.start_time == 0:
        st.session_state.start_time = time.time()

    col1, col2 = st.columns(2)
    chosen = None
    with col1:
        if st.button("RED"):
            chosen = "RED"
        if st.button("GREEN"):
            chosen = "GREEN"
    with col2:
        if st.button("BLUE"):
            chosen = "BLUE"
        if st.button("YELLOW"):
            chosen = "YELLOW"

    if chosen:
        rt = time.time() - st.session_state.start_time
        correct = (chosen == font_color)  # âœ… FIXED: check against font_color, not word
        st.session_state.responses.append({
            "Trial": trial + 1,
            "Word": word,
            "Font Color": font_color,
            "Response": chosen,
            "Correct": correct,
            "Reaction Time (s)": round(rt, 3)
        })
        st.session_state.trial_index += 1
        st.session_state.start_time = 0
        st.rerun()

# ---------------------------
# Show Results
# ---------------------------
elif st.session_state.test_started and st.session_state.trial_index >= num_trials:
    st.success("âœ… Test Completed!")

    df = pd.DataFrame(st.session_state.responses)
    st.dataframe(df)

    # Save to CSV
    filename = f"{st.session_state.name.replace(' ', '_')}_stroop_results.csv"
    df["Name"] = st.session_state.name
    df["Age"] = st.session_state.age
    df["Profession"] = st.session_state.profession
    df["Sleep Hours"] = st.session_state.sleep_hours

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("ðŸ“¥ Download Results as CSV", data=csv, file_name=filename, mime="text/csv")
