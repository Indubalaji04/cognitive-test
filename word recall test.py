import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(page_title="Word Recall Test", layout="centered")

# Session state variables
if "participant_info" not in st.session_state:
    st.session_state.participant_info = None
if "words" not in st.session_state:
    st.session_state.words = random.sample([
        "apple", "carpet", "elephant", "jungle", "river", "mountain", "guitar", "doctor", "planet", "mirror",
        "window", "pencil", "candle", "ocean", "rocket", "flower", "laptop", "camera", "banana", "pillow"
    ], 10)
if "current_word_index" not in st.session_state:
    st.session_state.current_word_index = 0
if "show_recall_input" not in st.session_state:
    st.session_state.show_recall_input = False
if "responses" not in st.session_state:
    st.session_state.responses = []

st.title("Word List Recall Test")

# Step 1: Participant Info
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
        st.experimental_rerun()

# Step 2: Show words one by one
elif st.session_state.current_word_index < len(st.session_state.words):
    word = st.session_state.words[st.session_state.current_word_index]
    st.subheader(f"Word {st.session_state.current_word_index + 1} of {len(st.session_state.words)}")
    st.markdown(f"<h1 style='text-align: center;'>{word}</h1>", unsafe_allow_html=True)
    time.sleep(1.5)  # Word display time
    st.session_state.current_word_index += 1
    st.experimental_rerun()

# Step 3: Ask participant to recall words
elif not st.session_state.show_recall_input:
    st.session_state.show_recall_input = True
    st.experimental_rerun()

# Step 4: Accept recall input
elif st.session_state.show_recall_input:
    st.subheader("Recall as many words as you can:")
    recalled_input = st.text_area("Enter the words you remember (separated by space or comma)")
    if st.button("Submit Responses"):
        recalled_words = [word.strip().lower() for word in recalled_input.replace(',', ' ').split()]
        correct_words = set(word.lower() for word in st.session_state.words)
        score = sum(1 for word in recalled_words if word in correct_words)

        result = {
            **st.session_state.participant_info,
            "WordsShown": ", ".join(st.session_state.words),
            "RecalledWords": ", ".join(recalled_words),
            "CorrectRecall": score,
            "TotalWords": len(st.session_state.words),
            "Accuracy": round(score / len(st.session_state.words) * 100, 2)
        }
        st.session_state.responses.append(result)

        df = pd.DataFrame(st.session_state.responses)
        st.success(f"You correctly recalled {score} out of {len(st.session_state.words)} words.")
        st.dataframe(df)
        filename = f"word_recall_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button("Download Results as CSV", df.to_csv(index=False), file_name=filename, mime="text/csv")
