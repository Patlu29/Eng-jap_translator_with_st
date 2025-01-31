import torch
from transformers import MarianMTModel, MarianTokenizer
import pykakasi
from gtts import gTTS
import io

# Load the translation model
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
