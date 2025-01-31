# English to Japanese Translator with Romanji and Audio

Site is now live on --> https://eng-jap-translator.streamlit.app/ 🚀

# Tech used

This is a English to Japanese Translator web application using:

- Streamlit - For create frontend & interact with backend and database

- SQLite Database – Stores translations and audio files

- MarianMT Model – Translates English to Japanese

- Pykakasi – Converts Japanese text to Romanji

- gTTS – Generates audio pronunciation

# Features

✅ Translate English text to Japanese using MarianMT Model
✅ Convert Japanese text to Romanji (Latin script)
✅ Generate and store audio pronunciation
✅ Fetch previous translations from SQLite database
✅ Frontend and backend managed in streamlit
✅ Deployed using Streamlit Cloud

# Installation & Setup

1️⃣ Application Setup (Streamlit)

Prerequisites:

- Install Python (3.8+)

- Install dependencies

    pip install -r requirements.txt

- Run the Web application Server

    streamlit run app.py

Streamlit will start on http://localhost:8501

# See past translations

- Navigate navbar --> click View saved translations
- It will show (Id, Japanese_text, Romanji_text, Audio)

# Tech Stack

- Backend & Frontend: Streamlit, SQLite

- Translation Model: MarianMT

- Text Processing: Pykakasi

- Audio Generation: gTTS

Deployment: Streamlit cloud

# Test

- Pytest conducted and successfully completed
  
# Future Improvements

🔹 Add user authentication (JWT)
🔹 Enhance UI/UX with Material UI or TailwindCSS
🔹 Implement caching for faster translations
🔹 Allow file uploads for bulk translations


# Contributors

👨‍💻 Prakash Rajan – Developer & Maintainer
