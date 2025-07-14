import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Digit Span Test", layout="centered")

# Parameters
MIN_SPAN = 3
MAX_SPAN = 9
DISPLAY_BASE_TIME = 2
DISPLAY_PER_DIGIT = 0.5

# Session state init
for key in ["step", "direction", "span", "sequence", "start_time", "results", "user_input"]:
    if key not in st.session_state:
        st.session_state[key] = None

if "participant" not in st.session_state:
    with st.form("participant_info"):
        st.title("Digit Span Test")
        name = st.text_input("Full Name")
        sleep_hours = st.text_input("How many hours did you sleep last night?")
        submitted = st.form_submit_button("Start Test")
        if submitted and name and sleep_hours:
            st.session_state.participant = {
                "Name": name.strip(),
                "SleepHours": sleep_hours.strip()
            }
            st.session_state.direction = "forward"
            st.session_state.span = MIN_SPAN
            st.session_state.results = []
            st.session_state.step = "show"
            st.rerun()

elif st.session_state.direction in ["forward", "backward"]:
    # Show digit sequence
    if st.session_state.step == "show":
        st.subheader(f"{st.session_state.direction.title()} Digit Span Test")
        st.markdown(f"### Span: {st.session_state.span} digits")

        seq = [str(random.randint(0, 9)) for _ in range(st.session_state.span)]
        st.session_state.sequence = seq
        st.session_state.start_time = time.time()
        st.markdown(f"<h1 style='text-align:center;'>{' '.join(seq)}</h1>", unsafe_allow_html=True)

        # Schedule next step
        display_duration = DISPLAY_BASE_TIME + st.session_state.span * DISPLAY_PER_DIGIT
        if time.time() - st.session_state.start_time > display_duration:
            st.session_state.step = "input"
            st.rerun()

    # Input response
    elif st.session_state.step == "input":
        st.subheader("Enter the sequence:")
        with st.form("digit_input_form"):
            user_input = st.text_input("Type the digits without spaces")
            submitted = st.form_submit_button("Submit")
            if submitted:
                correct_seq = st.session_state.sequence if st.session_state.direction == "forward" else st.session_state.sequence[::-1]
                user_resp = user_input.strip().replace(" ", "")
                correct = user_resp == ''.join(correct_seq)

                st.session_state.results.append([
                    st.session_state.span,
                    ''.join(st.session_state.sequence),
                    st.session_state.direction,
                    user_resp,
                    correct
                ])

                if not correct:
                    st.warning("❌ Incorrect. This part ends here.")
                    if st.session_state.direction == "forward":
                        st.session_state.direction = "backward"
                        st.session_state.span = MIN_SPAN
                    else:
                        st.session_state.direction = "done"
                    st.session_state.step = "show"
                else:
                    st.success("✅ Correct!")
                    st.session_state.span += 1
                    if st.session_state.span > MAX_SPAN:
                        if st.session_state.direction == "forward":
                            st.session_state.direction = "backward"
                            st.session_state.span = MIN_SPAN
                        else:
                            st.session_state.direction = "done"
                    st.session_state.step = "show"
                st.rerun()

elif st.session_state.direction == "done":
    st.success("🎉 Digit Span Test Complete!")

    df = pd.DataFrame(st.session_state.results, columns=[
        "Span", "Sequence", "Direction", "Response", "Correct"
    ])

    st.dataframe(df)

    meta = pd.DataFrame({
        "Participant Name": [st.session_state.participant["Name"]],
        "Sleep Hours": [st.session_state.participant["SleepHours"]]
    })
    csv_data = pd.concat([meta.T, pd.DataFrame([[]]), df])
    csv = csv_data.to_csv(index=False, header=False)
    filename = f"digit_span_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    st.download_button("📥 Download Results", csv, file_name=filename, mime="text/csv")
