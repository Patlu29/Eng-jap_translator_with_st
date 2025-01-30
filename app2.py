import streamlit as st
import sqlite3
import torch
from transformers import MarianMTModel, MarianTokenizer
import pykakasi
from gtts import gTTS
import os

# Load the translation model and tokenizer
MODEL_NAME = "Patlu29/eng-jap_trans"
model = MarianMTModel.from_pretrained(MODEL_NAME)
tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)

# Initialize pykakasi for Romanji conversion
kakasi = pykakasi.kakasi()
kakasi.setMode("H", "a")
kakasi.setMode("K", "a")
kakasi.setMode("J", "a")
kakasi.setMode("s", True)
converter = kakasi.getConverter()

# Database setup
conn = sqlite3.connect("translations.db", check_same_thread=False)
c = conn.cursor()

# Ensure the table includes the correct schema
c.execute('''CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english_text TEXT UNIQUE NOT NULL,
                japanese_text TEXT NOT NULL,
                romanji_text TEXT NOT NULL,
                audio_file TEXT NOT NULL)''')
conn.commit()

# Ensure audio directory exists
os.makedirs("audio_files", exist_ok=True)

# Streamlit UI
st.title("English to Japanese Translator")
english_text = st.text_area("Enter English text:", "")
if st.button("Translate"):
    if english_text.strip():
        c.execute("SELECT japanese_text, romanji_text, audio_file FROM translations WHERE english_text = ?", (english_text.lower(),))
        result = c.fetchone()
        
        if result:
            japanese_text, romanji_text, audio_filename = result
        else:
            japanese_text = tokenizer.decode(model.generate(**tokenizer(english_text, return_tensors="pt"))[0], skip_special_tokens=True)
            romanji_text = converter.do(japanese_text)
            audio_filename = f"{english_text.lower().replace(' ', '_')}.mp3"
            audio_path = os.path.join("audio_files", audio_filename)
            gTTS(text=romanji_text, lang="ja").save(audio_path)
            c.execute("INSERT INTO translations (english_text, japanese_text, romanji_text, audio_file) VALUES (?, ?, ?, ?)",
                      (english_text.lower(), japanese_text, romanji_text, audio_filename))
            conn.commit()
        
        st.subheader("Japanese Translation:")
        st.write(japanese_text)

        st.subheader("Romanji:")
        st.write(romanji_text)

        st.subheader("Audio Pronunciation:")
        st.audio(f"audio_files/{audio_filename}", format="audio/mp3")
    else:
        st.error("Please enter text to translate.")

if st.button("View Saved Translations"):
    c.execute("SELECT english_text, japanese_text, romanji_text, audio_file FROM translations")
    translations = c.fetchall()
    for item in translations:
        st.subheader(f"English: {item[0]}")
        st.write(f"Japanese: {item[1]}")
        st.write(f"Romanji: {item[2]}")
        st.audio(f"audio_files/{item[3]}", format="audio/mp3")






# Apply custom CSS styles
st.markdown("""
    <style>
        .stApp {
            background-color: #f2f1f7;
            font-family: 'Arial', sans-serif;
            color: #2d046e;
        }
        .stTitle title{
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #2d046e;
        }
        .stSubHeader subheader {
            border: 2px solid #2d046e;
            color: #2d046e;
        }
        .stTextArea textarea {
            background-color: #f2f1f7;
            border: 2px solid #2d046e;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            color: #2d046e;
        }
        .stButton>button {
            background-color: #2d046e;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px 20px;
        }
        .stButton>button:hover {
            background-color: #f2f1f7;
            color: #2d046e;
            border: 2px solid #2d046e;
        }
        .stSlidebar {
            background-color: #2d046e;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 18px;
        }
    </style>
    """, unsafe_allow_html=True)
