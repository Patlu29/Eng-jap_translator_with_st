import pytest
from translator import translate_to_japanese, convert_to_romanji, generate_audio

def test_translate_to_japanese():
    english_text = "Hello"
    japanese_text = translate_to_japanese(english_text)
    assert isinstance(japanese_text, str)
    assert len(japanese_text) > 0  # Ensure output is not empty

def test_convert_to_romanji():
    japanese_text = "こんにちは"
    romanji_text = convert_to_romanji(japanese_text)
    assert isinstance(romanji_text, str)
    assert romanji_text.lower() == "konnichiwa"

def test_generate_audio():
    romanji_text = "konnichiwa"
    audio_data = generate_audio(romanji_text)
    assert isinstance(audio_data, bytes)
    assert len(audio_data) > 0  # Ensure audio data is generated
