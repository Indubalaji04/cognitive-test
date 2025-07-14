import streamlit as st
import random
import time
import pandas as pd

# Page setup
st.set_page_config(page_title="Digit Span Test", layout="centered")

# -----------------------------
# Configuration Parameters
# -----------------------------
NUM_TRIALS = 8
DIGIT_LENGTH_START = 3
MAX_DIGITS = 10
DISPLAY_BASE_TIME = 1      # Reduced from 2 to 1 second
DISPLAY_PER_DIGIT = 0.3    # Reduced from 0.5 to 0.3 seconds

# -----------------------------
# Initialize session state
# -----------------------------
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.results = []
    st.session_state.completed = False
    st.session_state.digit_sequence = None
    st.session_state.showing = True

# -----------------------------
# Collect participant info
# -----------------------------
if "name" not in st.session_state:
    with st.form("participant_info"):
        name = st.text_input("Enter your name:")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")
        if submitted and name and sleep_hours:
            st.session_state.name = name.strip()
            st.session_state.sleep_hours = sleep_hours.strip()
            st.rerun()

# -----------------------------
# Run test
# -----------------------------
if "name" in st.session_state and not st.session_state.completed:
    trial = st.session_state.trial_index
    digit_length = min(DIGIT_LENGTH_START + trial, MAX_DIGITS)

    if trial < NUM_TRIALS:
        if st.session_state.digit_sequence is None:
            digits = random.sample([str(i) for i in range(10)], digit_length)
            st.session_state.digit_sequence = digits
            st.session_state.show_time = time.time()
            st.session_state.showing = True

        if st.session_state.showing:
            st.markdown(f"### Trial {trial + 1}: Memorize this number sequence")
            seq = ' '.join(st.session_state.digit_sequence)
            st.markdown(
                f"<div style='text-align:center; font-size:48px; font-weight:bold;'>{seq}</div>",
                unsafe_allow_html=True
            )

            # ⏱ Adjusted display time here
            if time.time() - st.session_state.show_time > DISPLAY_BASE_TIME + digit_length * DISPLAY_PER_DIGIT:
                st.session_state.showing = False
                st.rerun()

        else:
            st.markdown(f"### Trial {trial + 1}: Enter the number sequence you saw")
            with st.form("response_form"):
                response = st.text_input("Enter digits in order (no spaces):")
                submitted = st.form_submit_button("Submit")
                if submitted:
                    correct_seq = ''.join(st.session_state.digit_sequence)
                    is_correct = response.strip() == correct_seq
                    rt = round(time.time() - st.session_state.show_time, 2)
                    st.session_state.results.append([
                        trial + 1,
                        correct_seq,
                        response.strip(),
                        is_correct,
                        rt
                    ])
                    st.session_state.trial_index += 1
                    st.session_state.digit_sequence = None
                    st.session_state.showing = True
                    st.rerun()
    else:
        st.session_state.completed = True

# -----------------------------
# Show results
# -----------------------------
if st.session_state.completed:
    st.success("✅ Digit Span Test Completed!")

    df = pd.DataFrame(
        st.session_state.results,
        columns=["Trial", "Correct Sequence", "Your Response", "Correct", "Reaction Time (s)"]
    )

    st.dataframe(df)

    # CSV download
    meta = pd.DataFrame({
        "Participant Name": [st.session_state.name],
        "Sleep Hours": [st.session_state.sleep_hours]
    })
    csv_data = pd.concat([meta.T, pd.DataFrame([[]]), df])
    csv = csv_data.to_csv(index=False, header=False)
    filename = f"{st.session_state.name.lower().replace(' ', '_')}_digit_span_results.csv"
    st.download_button("📥 Download Results as CSV", csv, file_name=filename, mime="text/csv")

    # Visual recap
    st.markdown("### Recap:")
    for trial, correct_seq, response, correct, rt in st.session_state.results:
        st.markdown(
            f"<span style='font-size:18px;'>"
            f"Trial {trial}: <strong>{correct_seq}</strong> | "
            f"Response: <strong>{response}</strong> | "
            f"{'✅ Correct' if correct else '❌ Incorrect'} | RT: {rt}s"
            f"</span>",
            unsafe_allow_html=True
        )
