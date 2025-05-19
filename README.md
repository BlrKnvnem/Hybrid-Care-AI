# HybridCare AI

HybridCare AI is a desktop application built using Python's Tkinter GUI toolkit that serves as an AI-powered virtual therapist and doctor. It supports voice input/output, mood-based interaction, multilingual responses (English and Hindi), and leverages Google Gemini API for generating intelligent, empathetic responses.

---

## 🧠 Features

- 🎙️ **Voice Interaction**: Speak to the assistant and receive voice responses using SpeechRecognition and gTTS.
- 💬 **Multilingual Support**: Detects and supports English and Hindi conversations.
- 🎭 **Mood-Based Responses**: Select your mood (Happy, Sad, Stressed) for personalized interactions and sound effects.
- 💡 **Dual Role**: Acts as both a **Therapist** (for mental health) and a **Doctor** (for basic physical health advice).
- 💾 **Session Logging**: Saves each session in a text file under the `convo/` directory.
- 🌗 **Dark/Light Mode Toggle**: Switch between themes for better visibility and comfort.
- 🎧 **Ambient Sound Feedback**: Plays mood-related audio cues for immersion.

---

## 🚀 Installation

1. **Clone this repository**

```bash
git clone https://github.com/yourusername/HybridCareAI.git
cd HybridCareAI
```

2. **Install dependencies**

Install the required libraries using pip:

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `tkinter`
- `gtts`
- `pygame`
- `Pillow`
- `speechrecognition`
- `langdetect`
- `google-generativeai`

3. **Set up your Google API Key**

Replace the `GOOGLE_API_KEY` in `main.py` with your own Gemini API key from Google.

---

## 📁 Directory Structure

```
HybridCareAI/
│
├── main.py                # Main application script
├── convo/                 # Stores session logs (auto-created)
├── speech_cache/          # Temporary folder for speech audio (auto-created)
├── assets/                # Optional: Store mood sound files and therapist image
└── README.md              # This file
```

> Note: Update the therapist image path in `main.py` as needed.

---

## ✅ How to Use

1. Run the application:

```bash
python main.py
```

2. Click **"Start Session"**
3. Choose your **mood**
4. Type or use **"Speak"** to interact
5. Toggle between **dark/light mode** as needed
6. Click **"End Session"** to finish

Session data will be saved automatically under `/convo`.

---

## 🛡️ Ethical Disclaimer

HybridCare AI is **not a substitute for professional medical or psychological advice**. It provides general suggestions based on patterns and should not be used in emergencies.

---


## 📜 License

This project is licensed under the MIT License.

---

