import streamlit as st
import random
import time
import pandas as pd

# Config
st.set_page_config(page_title="Digit Span Test", layout="centered")

# Initialize session
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.results = []
    st.session_state.completed = False

NUM_TRIALS = 8
MAX_DIGITS = 10
DIGIT_LENGTH_START = 3

# Collect participant info
if "name" not in st.session_state:
    with st.form("participant_form"):
        name = st.text_input("Enter your name:")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")
        if submitted and name and sleep_hours:
            st.session_state.name = name.strip()
            st.session_state.sleep_hours = sleep_hours.strip()
            st.rerun()

# Run test
if "name" in st.session_state and not st.session_state.completed:
    trial = st.session_state.trial_index
    digit_length = min(DIGIT_LENGTH_START + trial, MAX_DIGITS)

    if trial < NUM_TRIALS:
        if "digit_sequence" not in st.session_state:
            digits = random.sample([str(i) for i in range(10)], digit_length)
            st.session_state.digit_sequence = digits
            st.session_state.show_time = time.time()
            st.session_state.showing = True

        if st.session_state.showing:
            st.markdown(f"### Trial {trial + 1}: Memorize this number sequence")
            st.markdown(f"<h1 style='text-align:center;'>{' '.join(st.session_state.digit_sequence)}</h1>", unsafe_allow_html=True)
            if time.time() - st.session_state.show_time > 2 + digit_length * 0.5:
                st.session_state.showing = False
                st.rerun()
        else:
            st.markdown(f"### Trial {trial + 1}: Type the number sequence you saw")
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
                    del st.session_state.digit_sequence
                    st.rerun()
    else:
        st.session_state.completed = True

# Show results
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

    st.download_button("📥 Download Results CSV", csv, file_name=filename, mime="text/csv")

    # Visual summary
    st.markdown("### Summary Recap:")
    for trial, correct_seq, response, correct, rt in st.session_state.results:
        st.markdown(
            f"<span style='font-size:18px;'>"
            f"Trial {trial}: Sequence: <strong>{correct_seq}</strong> | "
            f"Response: <strong>{response}</strong> | "
            f"{'✅ Correct' if correct else '❌ Incorrect'} | RT: {rt}s"
            f"</span>",
            unsafe_allow_html=True
        )
