import streamlit as st
import sqlite3
import torch
from transformers import MarianMTModel, MarianTokenizer
import pykakasi
from gtts import gTTS
import io

# Page configuration
st.set_page_config(
    page_title="End-Jap Translator",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f2f1f7;
        color: #2d046e;
    }
    .title {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        color: #00004d;
    }
    textarea {
        border: 2px solid #2d046e !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        width: 100%;
        background-color: #f2f1f7 !important;
        color: #2d046e !important;
    }
    .stTextArea>label {
        color: #2d046e;
    }
    .stButton>button {
        background-color: #00004d;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        box-shadow: 0px 0px 8px #2d046e;
        color: #2d046e;
    }
    [data-testid="stSidebar"] {
        background-color: #f2f1f7;  /* Light purple */
        border: 2px solid #2d046e;
        width: 350px !important;
    }
    [data-testid="stSidebar"] button {
        background-color: #2d046e !important;
        color: white !important;
        border: 2px solid #2d046e;
        border-radius: 8px;
        font-size: 16px;
    }
    .custom-subheader {
        color: #2d046e !important;  /* Dark purple */
        padding: 5px 0;
        border-bottom: 3px solid #2d046e; /* Underline effect */
        margin-bottom: 10px;
        font-size: 30px;
        font-weight: bold;
    }
    
    @media screen and (max-width: 768px) {
        .title {
            font-size: 32px; /* Smaller tablets & large phones */
        }
        .custom-subheader {
            font-size: 23px;
        }
        [data-testid="stSidebar"] {
            width: 250px !important;
        }
    }

    @media screen and (max-width: 480px) {
        .title {
            font-size: 24px; /* Mobile devices */
        }
        .custom-subheader {
            font-size: 15px;
        }
        [data-testid="stSidebar"] {
            width: 100px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

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

# Translation functions
def translate_to_japanese(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def convert_to_romanji(japanese_text):
    return converter.do(japanese_text)

def generate_audio(romanji_text):
    audio_buffer = io.BytesIO()
    tts = gTTS(text=romanji_text, lang="ja")
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

def save_translation(english, japanese, romanji, audio):
    try:
        c.execute("INSERT INTO translations (english_text, japanese_text, romanji_text, audio) VALUES (?, ?, ?, ?)",
                  (english, japanese, romanji, audio))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

def get_translation(english):
    c.execute("SELECT japanese_text, romanji_text, audio FROM translations WHERE english_text = ?", (english,))
    return c.fetchone()

def view_saved_translations():
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

# Web app UI
st.markdown('<p class="title">English to Japanese Translator</p>', unsafe_allow_html=True)

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

        st.markdown('<div class="custom-subheader">Japanese Translation:</div>', unsafe_allow_html=True)
        st.write(japanese_text)

        st.markdown('<div class="custom-subheader">Romanji:</div>', unsafe_allow_html=True)
        st.write(romanji_text)

        st.markdown('<div class="custom-subheader">Audio Pronunciation:</div>', unsafe_allow_html=True)
        st.audio(audio_data, format="audio/mp3")
    else:
        st.error("Please enter text to translate.")

if st.sidebar.button("View Saved Translations"):
    view_saved_translations()
