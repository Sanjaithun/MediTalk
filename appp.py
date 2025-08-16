import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import pyautogui
import webbrowser
import pywhatkit
import requests
import datetime
import time
import os
import smtplib
import winshell
from plyer import notification
import base64
import io

# --- Main Application Class ---
class MediTalkProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("MediTalk Pro Assistant")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # --- AI & Voice Engine Setup ---
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.configure_ai_model()

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Frame for Features
        self.left_frame = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.features_label = ctk.CTkLabel(self.left_frame, text="Features", font=ctk.CTkFont(size=20, weight="bold"))
        self.features_label.pack(pady=20)

        # Scrollable Frame for Feature Buttons
        self.scrollable_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="Commands")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.add_feature_buttons()

        # Right Frame for Interaction
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Response Text Area
        self.response_textbox = ctk.CTkTextbox(self.right_frame, font=("Helvetica", 14), wrap="word")
        self.response_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.response_textbox.insert("0.0", "Welcome to MediTalk Pro! Click the microphone to start.")

        # Bottom Frame for Controls
        self.bottom_frame = ctk.CTkFrame(self, height=100, corner_radius=10)
        self.bottom_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        
        # --- Simplified Microphone Button (No Image) ---
        self.mic_button = ctk.CTkButton(self.bottom_frame, text="🎤 Speak", font=("Helvetica", 24),
                                        command=self.start_listening_thread)
        self.mic_button.pack(pady=20, padx=20, fill="both", expand=True)

        self.status_label = ctk.CTkLabel(self, text="Status: Idle", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    def add_feature_buttons(self):
        """Adds buttons for all features to the scrollable frame."""
        features = {
            "Health Q&A": "Ask any health question",
            "Open Notepad": "Opens Notepad",
            "Open WhatsApp": "Opens WhatsApp Desktop",
            "Open Browser": "Opens your web browser",
            "Play on YouTube": "e.g., 'Play a song'",
            "Search Google": "e.g., 'Search for Python'",
            "Get Weather": "e.g., 'Weather in London'",
            "Get News": "e.g., 'Latest news'",
            "Tell Time": "What time is it?",
            "Wikipedia Search": "e.g., 'Wikipedia Albert Einstein'",
            "Set Reminder": "e.g., 'Remind me in 5 minutes'",
            "Send Email": "e.g., 'Send an email'",
            "System Shutdown": "Shutdown the computer",
            "Empty Recycle Bin": "Clears the recycle bin"
        }
        for feature, description in features.items():
            btn = ctk.CTkButton(self.scrollable_frame, text=feature, anchor="w")
            btn.pack(fill="x", padx=5, pady=5)

    def configure_ai_model(self):
        """Sets up the connection to the Gemini LLM."""
        try:
            # IMPORTANT: Paste your Gemini API key here
            YOUR_API_KEY = "AIzaSyAgTgnYzr9LbzSF5GSHYdgk5nTyhXEa1I0"
            genai.configure(api_key=YOUR_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            self.update_status(f"AI Config Error: {e}")

    def update_status(self, text):
        """Updates the status bar and prints to console."""
        self.status_label.configure(text=f"Status: {text}")
        print(text)

    def display_response(self, text):
        """Displays text in the main textbox."""
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("1.0", text)

    def speak(self, text):
        """Speaks the given text out loud."""
        self.update_status("Speaking...")
        self.display_response(text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def start_listening_thread(self):
        """Starts the main AI logic in a separate thread to prevent UI freezing."""
        self.mic_button.configure(state="disabled", text="Listening...")
        self.update_status("Listening...")
        threading.Thread(target=self.run_ai_logic, daemon=True).start()

    def run_ai_logic(self):
        """The core logic: listen, process, and respond."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)

            self.update_status("Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            self.display_response(f"You said: {command}")
            self.process_command(command)

        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Please try again.")
        except Exception as e:
            self.update_status(f"Error: {e}")
            self.speak("Sorry, I had trouble understanding. Please try again.")
        finally:
            self.mic_button.configure(state="normal", text="🎤 Speak")
            self.update_status("Idle")

    def process_command(self, command):
        """Determines the user's intent and executes the corresponding action."""
        # --- System & App Control ---
        if "open notepad" in command:
            self.speak("Opening Notepad.")
            os.system("notepad.exe")
        elif "open whatsapp" in command:
            self.speak("Opening WhatsApp.")
            # Update path if your WhatsApp is installed elsewhere
            # Example for default Windows user path. You might need to find the exact path.
            whatsapp_path = os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe")
            if os.path.exists(whatsapp_path):
                os.startfile(whatsapp_path)
            else:
                self.speak("WhatsApp application not found at the default path. Please open it manually.")
        elif "open browser" in command or "open chrome" in command:
            self.speak("Opening your browser.")
            webbrowser.open("http://google.com")
        elif "shutdown system" in command:
            self.speak("Shutting down the system in 5 seconds. Please save your work.")
            os.system("shutdown /s /t 5")
        elif "restart system" in command:
            self.speak("Restarting the system in 5 seconds.")
            os.system("shutdown /r /t 5")
        elif "empty recycle bin" in command:
            try:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
                self.speak("Recycle Bin has been emptied.")
            except Exception as e:
                self.speak("Could not empty the Recycle Bin.")

        # --- Information & Utilities ---
        elif "weather" in command:
            api_key = "PASTE_YOUR_OPENWEATHERMAP_API_KEY_HERE"
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            try:
                city_name = command.split(" in ")[-1]
                complete_url = base_url + "appid=" + api_key + "&q=" + city_name
                response = requests.get(complete_url)
                x = response.json()
                if x["cod"] != "404":
                    y = x["main"]
                    current_temperature = y["temp"] - 273.15 # Convert to Celsius
                    weather_description = x["weather"][0]["description"]
                    self.speak(f"The temperature in {city_name} is {current_temperature:.2f} degrees Celsius with {weather_description}.")
                else:
                    self.speak("City Not Found.")
            except Exception as e:
                self.speak("I couldn't fetch the weather. Please make sure you have entered your API key.")

        elif "news" in command:
            api_key = "PASTE_YOUR_NEWSAPI_KEY_HERE"
            main_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
            try:
                news = requests.get(main_url).json()
                articles = news["articles"]
                self.speak("Here are the top news headlines.")
                for i, article in enumerate(articles[:3]):
                    self.speak(f"Headline {i+1}: {article['title']}")
            except Exception as e:
                 self.speak("I couldn't fetch the news. Please make sure you have entered your API key.")
        
        elif "time" in command:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {strTime}")

        elif "wikipedia" in command:
            self.speak("Searching Wikipedia...")
            query = command.replace("wikipedia", "").strip()
            try:
                results = pywhatkit.info(query, lines=2)
                self.speak("According to Wikipedia...")
                self.speak(results)
            except:
                self.speak("I couldn't find any information on that topic on Wikipedia.")

        # --- Productivity & Communication ---
        elif "remind me" in command:
            reminder_text = command.replace("remind me", "").strip()
            self.speak(f"Reminder set: {reminder_text}")
            notification.notify(
                title='MediTalk Pro Reminder',
                message=reminder_text,
                timeout=10
            )

        elif "send email" in command:
            self.speak("I can't send emails just yet. This feature is coming soon!")

        # --- Entertainment ---
        elif "play" in command:
            query = command.replace("play", "").strip()
            self.speak(f"Playing {query} on YouTube.")
            pywhatkit.playonyt(query)

        # --- Default to LLM ---
        else:
            self.update_status("Getting response from AI model...")
            try:
                health_prompt = f"Act as a helpful medical assistant and answer this question clearly and simply, including a disclaimer to consult a doctor: {command}"
                response = self.model.generate_content(health_prompt)
                self.speak(response.text)
            except Exception as e:
                self.update_status(f"LLM Error: {e}")
                self.speak("I'm having trouble connecting to my knowledge base right now. Please check your Gemini API key.")

# --- Run the Application ---
if __name__ == "__main__":
    app = MediTalkProApp()
    app.mainloop()
