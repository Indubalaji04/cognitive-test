import streamlit as st
import random
import time
import pandas as pd

# Set page config
st.set_page_config(page_title="Stroop Test", layout="centered")

# Initialize session state
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.results = []
    st.session_state.start_time = 0
    st.session_state.completed = False

# Constants
color_map = {"RED": "red", "BLUE": "blue", "GREEN": "green", "YELLOW": "yellow"}
color_names = list(color_map.keys())
NUM_TRIALS = 20

# Collect participant info
if "name" not in st.session_state:
    with st.form("participant_info"):
        name = st.text_input("Enter your name:")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")

        if submitted and name and sleep_hours:
            st.session_state.name = name.strip()
            st.session_state.sleep_hours = sleep_hours.strip()
            st.experimental_rerun()

# Run test
if "name" in st.session_state and not st.session_state.completed:
    trial = st.session_state.trial_index
    if trial < NUM_TRIALS:
        # Generate stimuli
        if "current_trial" not in st.session_state:
            word = random.choice(color_names)
            ink_color = random.choice(color_names)
            st.session_state.current_trial = (word, ink_color)
            st.session_state.start_time = time.time()

        word, ink_color = st.session_state.current_trial

        st.markdown("### Identify the INK COLOR of the word shown below:")
        st.markdown(
            f"<h1 style='text-align: center; color:{color_map[ink_color]};'>{word}</h1>",
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        buttons = [col1.button("RED"), col2.button("GREEN"), col3.button("BLUE"), col4.button("YELLOW")]
        response = None
        for i, btn in enumerate(buttons):
            if btn:
                response = ["RED", "GREEN", "BLUE", "YELLOW"][i]
                break

        if response:
            rt = round(time.time() - st.session_state.start_time, 2)
            correct = response == ink_color
            st.session_state.results.append([
                trial + 1, word, ink_color, color_map[ink_color], response, correct, rt
            ])
            st.session_state.trial_index += 1
            del st.session_state.current_trial
            st.experimental_rerun()
    else:
        st.session_state.completed = True

# Show results
if st.session_state.get("completed"):
    st.success("✅ Test Completed!")

    df = pd.DataFrame(
        st.session_state.results,
        columns=["Trial", "Word", "Ink Color", "Ink Code", "Response", "Correct", "Reaction Time (s)"]
    )

    # Color formatting in table
    def highlight_ink(val):
        return f'color: {val}'

    styled_df = df.style.applymap(highlight_ink, subset=["Ink Code"])
    st.dataframe(styled_df)

    # CSV download
    filename = f"{st.session_state.name.lower().replace(' ', '_')}_stroop_results.csv"
    meta = pd.DataFrame({
        "Participant Name": [st.session_state.name],
        "Sleep Hours": [st.session_state.sleep_hours]
    })
    csv_data = pd.concat([meta.T, pd.DataFrame([[]]), df.drop(columns=["Ink Code"])])
    csv = csv_data.to_csv(index=False, header=False)
    st.download_button("📥 Download Results as CSV", csv, file_name=filename, mime="text/csv")

    # Visual recap
    st.markdown("### Visual Recap of Each Trial:")
    for row in st.session_state.results:
        trial, word, ink_color, ink_code, response, correct, rt = row
        st.markdown(
            f"<span style='font-size:18px;'>"
            f"Trial {trial}: <strong style='color:{ink_code}'>{word}</strong> "
            f"(Ink: {ink_color}, Response: {response}, "
            f"{'✅' if correct else '❌'}, RT: {rt}s)"
            f"</span>",
            unsafe_allow_html=True
        )
