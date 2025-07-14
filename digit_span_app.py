import streamlit as st
import random
import pandas as pd
from datetime import datetime

# App config
st.set_page_config(page_title="Digit Span Test", layout="centered")

# Parameters
MIN_SPAN = 3
MAX_SPAN = 9

# Initialize session state
defaults = {
    "step": None,
    "direction": None,
    "span": None,
    "sequence": None,
    "results": [],
    "participant": None,
    "correct_last": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Participant info collection
if not st.session_state.participant:
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
            st.session_state.step = "show"
            st.rerun()

# Show digit sequence
elif st.session_state.direction in ["forward", "backward"]:
    if st.session_state.step == "show":
        st.subheader(f"{st.session_state.direction.title()} Digit Span Test")
        st.markdown(f"### Span: {st.session_state.span} digits")

        if st.session_state.sequence is None:
            seq = [str(random.randint(0, 9)) for _ in range(st.session_state.span)]
            st.session_state.sequence = seq

        st.markdown(
            f"<h1 style='text-align:center;'>{' '.join(st.session_state.sequence)}</h1>",
            unsafe_allow_html=True
        )

        if st.button("Next"):
            st.session_state.step = "input"
            st.rerun()

    # Input phase
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

            st.session_state.correct_last = correct
            st.session_state.step = "feedback"
            st.rerun()

    # Feedback phase
    elif st.session_state.step == "feedback":
        if st.session_state.correct_last:
            st.success("✅ Correct!")
        else:
            st.warning("❌ Incorrect. This part ends here.")

        if st.button("Next Trial"):
            # Switch direction or finish
            if not st.session_state.correct_last:
                if st.session_state.direction == "forward":
                    st.session_state.direction = "backward"
                    st.session_state.span = MIN_SPAN
                else:
                    st.session_state.direction = "done"
            else:
                st.session_state.span += 1
                if st.session_state.span > MAX_SPAN:
                    if st.session_state.direction == "forward":
                        st.session_state.direction = "backward"
                        st.session_state.span = MIN_SPAN
                    else:
                        st.session_state.direction = "done"

            st.session_state.step = "show"
            st.session_state.sequence = None
            st.rerun()

# Test complete
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
