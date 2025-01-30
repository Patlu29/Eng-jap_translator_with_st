import streamlit as st
import sqlite3
import torch
from transformers import MarianMTModel, MarianTokenizer
import pykakasi
from gtts import gTTS
import io

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
conn = sqlite3.connect("translations.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english_text TEXT UNIQUE NOT NULL,
                japanese_text TEXT NOT NULL,
                romanji_text TEXT NOT NULL,
                audio BLOB NOT NULL)''')
conn.commit()

def translate_to_japanese(sentence):
    """Translate English sentence to Japanese."""
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def convert_to_romanji(japanese_text):
    """Convert Japanese text to Romanji."""
    return converter.do(japanese_text)

def generate_audio(romanji_text):
    """Generate audio from Romanji text and return as binary."""
    audio_buffer = io.BytesIO()
    tts = gTTS(text=romanji_text, lang="ja")
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

def save_translation(english, japanese, romanji, audio):
    """Save translation to the database."""
    try:
        c.execute("INSERT INTO translations (english_text, japanese_text, romanji_text, audio) VALUES (?, ?, ?, ?)",
                  (english, japanese, romanji, audio))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

def get_translation(english):
    """Retrieve translation from the database."""
    c.execute("SELECT japanese_text, romanji_text, audio FROM translations WHERE english_text = ?", (english,))
    return c.fetchone()

# Streamlit UI
st.title("English to Japanese Translator")

english_text = st.text_area("Enter English text:", "")
if st.button("Translate"):
    if english_text.strip():
        # Check database for existing translation
        result = get_translation(english_text.lower())
        if result:
            japanese_text, romanji_text, audio_data = result
        else:
            # Perform translation
            japanese_text = translate_to_japanese(english_text)
            romanji_text = convert_to_romanji(japanese_text)
            audio_data = generate_audio(romanji_text)
            save_translation(english_text.lower(), japanese_text, romanji_text, audio_data)

        # Display results
        st.subheader("Japanese Translation:")
        st.write(japanese_text)

        st.subheader("Romanji:")
        st.write(romanji_text)

        st.subheader("Audio Pronunciation:")
        st.audio(audio_data, format="audio/mp3")
    else:
        st.error("Please enter text to translate.")
