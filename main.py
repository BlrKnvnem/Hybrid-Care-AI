import tkinter as tk
from tkinter import ttk
import time
import hashlib
import os
import pygame
from gtts import gTTS
import google.generativeai as genai
import speech_recognition as sr
import threading
from PIL import Image, ImageTk
from langdetect import detect

GOOGLE_API_KEY = 'AIzaSyDyRQjO5itfdvQjyXEtrlgediIXvgcE_cQ'

class AI:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.session_active = False
        self.SPEECH_CACHE = "speech_cache"
        self.WRITE_FOLDER = "convo"
        self.VOL = 0.8
        self.TIMEOUT_DURATION = 12
        self.response_cache = {}
        self.dark_mode = True
        self.mood = None
        self.language = "en"
        self.current_language = "en"

        os.makedirs(self.SPEECH_CACHE, exist_ok=True)
        os.makedirs(self.WRITE_FOLDER, exist_ok=True)

        pygame.mixer.init()

        self.sound_effects = {
            "Happy 😊": "happy_chime.mp3",
            "Sad 😢": "sad_tone.mp3",
            "Stressed 😫": "relaxing_nature.mp3"
        }

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True

        # Main window setup
        self.root = tk.Tk()
        self.root.title("HybridCare AI")
        self.root.geometry("900x700")
        self.root.config(bg='#1e1e1e')
        self.root.minsize(800, 600)

        # Custom font
        self.custom_font = ('Poppins', 12)
        self.title_font = ('Poppins', 20, 'bold')
        self.chat_font = ('Poppins', 11)

        # Main container
        self.main_container = tk.Frame(self.root, bg='#1e1e1e')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Header Frame
        self.header_frame = tk.Frame(self.main_container, bg='#045de9', height=80)
        self.header_frame.pack(fill='x', pady=(0, 10))


        # Title Label
        self.label = tk.Label(self.header_frame, text="HybridCare AI", 
                            font=self.title_font, foreground='white', background='#045de9')
        self.label.pack(pady=15)

        # Therapist Image
        try:
            self.load_image("C:\\Users\\krish\\Downloads\\download.jpg")  # Update with your image path
            self.image_label = tk.Label(self.main_container, image=self.Therapist, bg='#1e1e1e', bd=0)
            self.image_label.pack(pady=10)
        except:
            self.image_label = tk.Label(self.main_container, text="Therapist Image", bg='#1e1e1e', fg='white')
            self.image_label.pack(pady=10)

        # Welcome Message
        self.welcome_label = tk.Label(self.main_container, 
                                    text="Hello! I'm your AI Therapist. How can I help you today?",
                                    font=self.custom_font, fg='white', bg='#1e1e1e', wraplength=600)
        self.welcome_label.pack(pady=10)

        # Mood Selection Buttons
        self.mood_frame = tk.Frame(self.main_container, bg='#1e1e1e')
        self.mood_frame.pack(pady=10)
        
        self.moods = ["Happy 😊", "Sad 😢", "Stressed 😫"]
        for mood in self.moods:
            mood_button = ttk.Button(
                self.mood_frame, 
                text=mood, 
                style='TButton', 
                command=lambda m=mood: self.set_mood(m)
            )
            mood_button.pack(side='left', padx=5)

        # Chat Frame Container
        self.chat_container = tk.Frame(self.main_container, bg='#1e1e1e')
        self.chat_container.pack(fill='both', expand=True, pady=10)

        # Chat Frame
        self.chat_frame = tk.Frame(self.chat_container, bg='#333333', bd=2, relief='flat')
        self.chat_frame.pack(fill='both', expand=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.chat_frame)
        self.scrollbar.pack(side='right', fill='y')

        # Chat Text
        self.chat_text = tk.Text(self.chat_frame, bg='#333333', fg='white', 
                                font=self.chat_font, wrap=tk.WORD, 
                                yscrollcommand=self.scrollbar.set,
                                padx=10, pady=10)
        self.chat_text.pack(fill='both', expand=True)
        self.scrollbar.config(command=self.chat_text.yview)

        # Input Frame
        self.input_frame = tk.Frame(self.main_container, bg='#1e1e1e')
        self.input_frame.pack(fill='x', pady=(5, 10))

        # Input Textbox
        self.input_textbox = tk.Text(self.input_frame, height=4, font=self.custom_font, 
                                   bg='#444444', fg='white', bd=0, wrap=tk.WORD,
                                   insertbackground='white')
        self.input_textbox.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.add_placeholder(self.input_textbox, "Type or speak your message here...")

        # Button Frame
        self.button_frame = tk.Frame(self.input_frame, bg='#1e1e1e')
        self.button_frame.pack(side='right', fill='y')

        # Send Button
        self.send_button = ttk.Button(self.button_frame, text="Send", 
                                     style='TButton', command=self.send_text_message)
        self.send_button.pack(fill='x', pady=(0, 5))

        # Speak Button
        self.speak_button = ttk.Button(self.button_frame, text="Speak", 
                                      style='TButton', command=self.start_speech_input)
        self.speak_button.pack(fill='x')

        # Control Frame
        self.control_frame = tk.Frame(self.main_container, bg='#1e1e1e')
        self.control_frame.pack(fill='x', pady=10)

        # Chat Button
        self.chat_button = ttk.Button(self.control_frame, text="Start Session", 
                                     style='TButton', command=self.toggle_chat)
        self.chat_button.pack(side='left', padx=5)

        # Dark Mode Button
        self.dark_mode_button = ttk.Button(self.control_frame, text="Toggle Dark Mode", 
                                          style='TButton', command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side='left', padx=5)

        # Status Label
        self.status_label = tk.Label(self.main_container, text="", font=self.custom_font, 
                                   foreground='#045de9', background='#1e1e1e')
        self.status_label.pack(side='bottom', pady=5)

        # Style for ttk.Button
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TButton', font=self.custom_font, 
                           background='#045de9', foreground='white', 
                           borderwidth=0, focuscolor='none')
        self.style.map('TButton',
                      background=[('active', '#0348b5')],
                      foreground=[('active', 'white')])

        # Configure text tags for chat
        self.chat_text.tag_config('user', foreground='#4fc3f7')
        self.chat_text.tag_config('bot', foreground='#81c784')
        self.chat_text.tag_config('system', foreground='#ffb74d')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_image(self, path):
        """Load and resize the therapist image."""
        image = Image.open(path)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        self.Therapist = ImageTk.PhotoImage(image)

    def add_placeholder(self, textbox, placeholder):
        """Add placeholder text to the input textbox."""
        textbox.insert(tk.END, placeholder)
        textbox.config(fg='gray')
        textbox.bind("<FocusIn>", lambda event: self.clear_placeholder(textbox, placeholder))
        textbox.bind("<FocusOut>", lambda event: self.add_placeholder(textbox, placeholder))

    def clear_placeholder(self, textbox, placeholder):
        """Clear placeholder text when the textbox is focused."""
        if textbox.get("1.0", tk.END).strip() == placeholder:
            textbox.delete("1.0", tk.END)
            textbox.config(fg='white')

    def toggle_dark_mode(self):
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Dark mode colors
            bg_color = '#1e1e1e'
            text_color = 'white'
            chat_bg = '#333333'
            input_bg = '#444444'
            header_bg = '#045de9'
        else:
            # Light mode colors
            bg_color = '#ffffff'
            text_color = 'black'
            chat_bg = '#f0f0f0'
            input_bg = '#ffffff'
            header_bg = '#045de9'

        # Update all widgets
        self.root.config(bg=bg_color)
        self.main_container.config(bg=bg_color)
        self.header_frame.config(bg=header_bg)
        self.label.config(bg=header_bg, fg='white')  # Keep header text white
        self.image_label.config(bg=bg_color)
        self.welcome_label.config(bg=bg_color, fg=text_color)
        self.mood_frame.config(bg=bg_color)
        self.chat_container.config(bg=bg_color)
        self.chat_frame.config(bg=chat_bg)
        self.chat_text.config(bg=chat_bg, fg=text_color)
        self.input_frame.config(bg=bg_color)
        self.input_textbox.config(bg=input_bg, fg=text_color, insertbackground=text_color)
        self.button_frame.config(bg=bg_color)
        self.control_frame.config(bg=bg_color)
        self.status_label.config(bg=bg_color, fg=header_bg)

    def set_mood(self, mood):
        """Set the user's mood and provide mood-specific feedback."""
        self.mood = mood
        self.welcome_label.config(text=f"You're feeling {mood}. Let's talk about it!")
        self.add_to_chat(f"System: Mood set to {mood}\n", 'system')

        # Mood-specific response
        if mood == "Happy 😊":
            response = "It's great to hear you're feeling happy! Let's keep the positivity going!"
        elif mood == "Sad 😢":
            response = "I'm here for you. Let's talk about what's on your mind."
        elif mood == "Stressed 😫":
            response = "Feeling stressed? Let's work on some relaxation techniques together."
        
        self.text_to_speech(response)
        self.add_to_chat(f"Rossane: {response}\n", 'bot')

    def on_closing(self):
        """Handle window closing."""
        if self.session_active:
            self.session_active = False
            time.sleep(1)  # Give threads time to finish
        self.root.destroy()

    def toggle_chat(self):
        """Toggle the chat session."""
        if self.session_active:
            self.session_active = False
            self.chat_button.config(text="Start Session")
            self.add_to_chat("System: Session ended\n", 'system')
            self.text_to_speech("Goodbye! Session ended.")
        else:
            self.session_active = True
            self.chat_button.config(text="End Session")
            self.chat_text.delete(1.0, tk.END)
            self.add_to_chat("System: Session started\n", 'system')
            self.text_to_speech("Session started.")
            chat_thread = threading.Thread(target=self.chat)
            chat_thread.daemon = True
            chat_thread.start()

    def send_text_message(self):
        """Send text message from input box."""
        if not self.session_active:
            self.text_to_speech("Please start a session first.")
            return
            
        user_input = self.input_textbox.get("1.0", tk.END).strip()
        if not user_input or user_input == "Type or speak your message here...":
            return
            
        self.input_textbox.delete("1.0", tk.END)
        self.process_user_input(user_input)

    def start_speech_input(self):
        """Start speech input in a separate thread."""
        if not self.session_active:
            self.text_to_speech("Please start a session first.")
            return
            
        speech_thread = threading.Thread(target=self.speech_input_thread)
        speech_thread.daemon = True
        speech_thread.start()

    def speech_input_thread(self):
        """Thread for handling speech input."""
        self.status_label.config(text="Listening...")
        self.root.update()
        
        user_input = self.speech_to_text()
        
        self.status_label.config(text="")
        self.root.update()
        
        if user_input:
            self.input_textbox.delete("1.0", tk.END)
            self.input_textbox.insert(tk.END, user_input)
            self.process_user_input(user_input)

    def process_user_input(self, user_input):
        """Process user input and generate response."""
        self.add_to_chat(f"You: {user_input}\n", 'user')
        
        # Detect language
        try:
            detected_lang = detect(user_input)
            if detected_lang == "hi":
                self.current_language = "hi"
            else:
                self.current_language = "en"
        except:
            self.current_language = "en"

        if user_input.lower() in ["exit", "quit", "bye"]:
            if self.current_language == "hi":
                goodbye_msg = "अलविदा! मुझे आशा है कि आपका दिन अच्छा होगा।"
            else:
                goodbye_msg = "Goodbye! I hope you have a great day."
            
            self.add_to_chat(f"Rossane: {goodbye_msg}\n", 'bot')
            self.text_to_speech(goodbye_msg, self.current_language)
            self.toggle_chat()
            return

        # Get response in a separate thread
        response_thread = threading.Thread(target=self.get_response, args=(user_input,))
        response_thread.daemon = True
        response_thread.start()

    def get_response(self, user_input):
        """Get response from AI and update UI."""
        self.status_label.config(text="Thinking...")
        self.root.update()
        
        response = self.bot(user_input, self.current_language)
        
        self.status_label.config(text="")
        self.root.update()
        
        self.add_to_chat(f"Rossane: {response}\n", 'bot')
        self.text_to_speech(response, self.current_language)

    def add_to_chat(self, text, tag):
        """Add text to chat window with appropriate tag."""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, text, tag)
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def detect_language(self, text):
        """Detect the language of the input text."""
        try:
            return detect(text)
        except:
            return "en"

    def bot(self, prompt: str, lang: str = "en") -> str:
        """Generate a response using the AI model."""
        cache_key = f"{lang}_{prompt}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            mood_prompt = f"The user is feeling {self.mood}. " if self.mood else ""
            
            if lang == "hi":
                prompt_text = f"""
                आप एक AI हैं जो एक चिकित्सक और डॉक्टर दोनों की भूमिका निभाते हैं।
                एक चिकित्सक के रूप में, आप भावनात्मक समर्थन, संज्ञानात्मक व्यवहार थेरेपी तकनीक और मानसिक स्वास्थ्य मार्गदर्शन प्रदान करते हैं।
                एक डॉक्टर के रूप में, आप उपयोगकर्ता के लक्षणों के आधार पर सामान्य चिकित्सा सलाह, लक्षण विश्लेषण और प्राथमिक चिकित्सा सुझाव प्रदान करते हैं।

                यदि उपयोगकर्ता मानसिक स्वास्थ्य के बारे में पूछता है, तो एक चिकित्सक के रूप में जवाब दें।
                यदि उपयोगकर्ता शारीरिक स्वास्थ्य के बारे में पूछता है, तो एक डॉक्टर के रूप में जवाब दें।

                **महत्वपूर्ण**: अपने उत्तर संक्षिप्त, सीधे और 2-3 वाक्यों से अधिक न रखें।

                **बेसिक मेडिकल ज्ञान**:
                - सर्दी और गले में खराश के लिए: बुखार और दर्द के लिए पेरासिटामोल (500mg) लें, और गले की लोज़ेंजेस का उपयोग करें या गर्म नमक के पानी से गरारे करें।
                - बुखार के लिए: हर 6 घंटे में पेरासिटामोल (500mg) लें और हाइड्रेटेड रहें।
                - सिरदर्द के लिए: आइबुप्रोफेन (400mg) या पेरासिटामोल (500mg) लें और एक शांत, अंधेरे कमरे में आराम करें।
                - पेट दर्द के लिए: मसालेदार भोजन से बचें, एंटासिड लें और खूब पानी पिएं।
                - एलर्जी के लिए: सेटिरिज़िन (10mg) जैसे एंटीहिस्टामाइन लें और एलर्जेन से बचें।

                {mood_prompt}उपयोगकर्ता: {prompt}
                AI:
                """
            else:
                prompt_text = f"""
                You are an AI that acts both as a therapist and a doctor.
                As a therapist, you provide emotional support, cognitive behavioral therapy techniques, and mental health guidance.
                As a doctor, you provide general medical advice, symptom analysis, and first-aid suggestions based on user symptoms.

                If the user asks about mental health, respond as a therapist.
                If the user asks about physical health, respond as a doctor.

                **Important**: Keep your responses concise, to the point, and no longer than 2-3 sentences.

                **Basic Medicinal Knowledge**:
                - For cold and sore throat: Take paracetamol (500mg) for fever and pain, and use throat lozenges or gargle with warm salt water.
                - For fever: Take paracetamol (500mg) every 6 hours and stay hydrated.
                - For headache: Take ibuprofen (400mg) or paracetamol (500mg) and rest in a quiet, dark room.
                - For stomach ache: Avoid spicy food, take antacids, and drink plenty of water.
                - For allergies: Take antihistamines like cetirizine (10mg) and avoid allergens.

                {mood_prompt}User: {prompt}
                AI:
                """
            
            response = model.generate_content(prompt_text)
            response_text = response.text.strip()
            self.response_cache[cache_key] = response_text
            return response_text
        except Exception as e:
            return f"Error: {str(e)}"

    def text_to_speech(self, text: str, lang: str = None) -> None:
        """Convert text to speech."""
        if not text:
            return
            
        if not lang:
            lang = self.current_language
            
        filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
        filepath = os.path.join(self.SPEECH_CACHE, filename)

        if not os.path.exists(filepath):
            try:
                tts = gTTS(text, lang=lang)
                tts.save(filepath)
            except Exception as e:
                print(f"Error in TTS: {e}")
                return

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.VOL)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def speech_to_text(self) -> str:
        """Convert speech to text."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    text = self.recognizer.recognize_google(audio, language=self.current_language)
                except sr.UnknownValueError:
                    text = self.recognizer.recognize_google(audio, language="en")
                
                return text

        except sr.WaitTimeoutError:
            self.status_label.config(text="Listening timed out")
            self.root.update()
            return ""
        except sr.UnknownValueError:
            self.status_label.config(text="Could not understand audio")
            self.root.update()
            return ""
        except sr.RequestError as e:
            self.status_label.config(text=f"Speech service error: {e}")
            self.root.update()
            return ""
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.root.update()
            return ""

    def chat(self) -> None:
        """Handle the chat session."""
        self.text_to_speech("Welcome to the session. You can speak or type your messages.")
        self.text_to_speech("Hi, I am Rossane. Could you tell me your name?")
        
        self.status_label.config(text="Waiting for your name...")
        self.root.update()
        
        name = ""
        while not name and self.session_active:
            name = self.speech_to_text()
            if not name:
                self.text_to_speech("Please say your name clearly.")
                time.sleep(1)

        if not self.session_active:
            return

        name = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()
        self.add_to_chat(f"System: User identified as {name}\n", 'system')
        self.text_to_speech(f"Hi {name}, let's begin our session. What's on your mind today?")

        filename = os.path.join(self.WRITE_FOLDER, f"{name}.txt")

        with open(filename, "a", encoding='utf-8') as convo_file:
            convo_file.write(f"Session started at {time.ctime()}\n")
            
            while self.session_active:
                # The actual conversation is now handled through button clicks
                # or speech input, so we just need to wait here
                time.sleep(0.5)

            convo_file.write(f"Session ended at {time.ctime()}\n\n")

if __name__ == "__main__":
    app = AI()
    app.root.mainloop()