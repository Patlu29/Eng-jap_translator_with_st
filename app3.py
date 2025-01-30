import streamlit as st
import sqlite3
import torch
from transformers import MarianMTModel, MarianTokenizer
import pykakasi
from gtts import gTTS
import io

# Install dependencies
# !pip install streamlit torch transformers pykakasi gtts

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

def view_saved_translations():
    """Retrieve and display saved translations from the database."""
    c.execute("SELECT id, english_text, japanese_text, romanji_text, audio FROM translations")
    rows = c.fetchall()
    if rows:
        for row in rows:
            st.write(f"**ID:** {row[0]}")
            st.write(f"**English:** {row[1]}")
            st.write(f"**Japanese:** {row[2]}")
            st.write(f"**Romanji:** {row[3]}")
            st.audio(row[4], format="audio/mp3")
            st.write("---")
    else:
        st.write("No translations saved yet.")

# Streamlit UI
st.markdown(
    """
    <style>
    body {
      font-family: 'Arial', sans-serif;
      background-color: #f2f1f7;
      margin: 0;
      padding: 0;
      line-height: 1.6;
    }
    h1 {
      text-align: center;
      color: #2d046e;
      font-size: 2.5rem;
      margin-top: 20px;
    }
    h2, p, h5 {
      text-align: center;
      color: #2d046e;
      font-size: 1.5rem;
      margin-top: 20px;
    }
    textarea {
      width: 90%;
      max-width: 800px;
      padding: 15px;
      margin: 20px auto;
      display: block;
      font-size: 1rem;
      border: 2px solid #2d046e;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      background-color: #ffffff;
      color: #333;
    }
    button {
      display: block;
      margin: 0 auto;
      padding: 12px 20px;
      background-color: #2d046e;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      transition: background-color 0.3s ease, transform 0.2s ease;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    button:hover {
      background-color: #4b12a3;
      transform: translateY(-2px);
    }
    button:active {
      transform: translateY(0);
    }
    audio {
      display: block;
      margin: 20px auto;
      width: 90%;
      max-width: 800px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("English to Japanese Translator")

english_text = st.text_area("Enter English text:", "")
if st.button("Translate"):
    if english_text.strip():
        result = get_translation(english_text.lower())
        if result:
            japanese_text, romanji_text, audio_data = result
        else:
            japanese_text = translate_to_japanese(english_text)
            romanji_text = convert_to_romanji(japanese_text)
            audio_data = generate_audio(romanji_text)
            save_translation(english_text.lower(), japanese_text, romanji_text, audio_data)

        st.subheader("Japanese Translation:")
        st.write(japanese_text)

        st.subheader("Romanji:")
        st.write(romanji_text)

        st.subheader("Audio Pronunciation:")
        st.audio(audio_data, format="audio/mp3")
    else:
        st.error("Please enter text to translate.")

if st.button("View Saved Translations"):
    view_saved_translations()
