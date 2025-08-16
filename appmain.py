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
        self.listening_animation_active = False

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
            "Send WhatsApp": "e.g., 'Send a WhatsApp message'",
            "Open VS Code": "Opens Visual Studio Code",
            "Open CMD": "Opens Command Prompt",
            "Open Notepad": "Opens Notepad",
            "Send Email": "Opens your default email client",
            "Play on YouTube": "e.g., 'Play a song'",
            "Search Google": "e.g., 'Search for Python'",
            "Get Weather": "e.g., 'Weather in London'",
            "Get News": "e.g., 'Latest news'",
            "Tell Time": "What time is it?",
            "Wikipedia Search": "e.g., 'Wikipedia Albert Einstein'",
            "Set Reminder": "e.g., 'Remind me in 5 minutes'",
            "System Shutdown": "Shutdown the computer",
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
            # FIXED: Updated to a current and valid model name
            self.model = genai.GenerativeModel('gemini-1.5-flash')
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
        
    def listen_for_response(self, prompt):
        """A dedicated listening function to get specific user input."""
        self.speak(prompt)
        with sr.Microphone() as source:
            self.update_status("Listening for your response...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                self.update_status("Recognizing...")
                response = self.recognizer.recognize_google(audio).lower()
                self.display_response(f"You said: {response}")
                return response
            except Exception as e:
                self.speak("Sorry, I didn't catch that. Please try again.")
                return None

    def start_listening_thread(self):
        """Starts the main AI logic in a separate thread to prevent UI freezing."""
        self.mic_button.configure(state="disabled")
        self.listening_animation_active = True
        threading.Thread(target=self.listening_animation, daemon=True).start()
        threading.Thread(target=self.run_ai_logic, daemon=True).start()

    def listening_animation(self):
        """Creates a pulsing color effect on the button while listening."""
        original_color = self.mic_button.cget("fg_color")
        pulse_color = "#34A853" # Green color
        
        while self.listening_animation_active:
            self.mic_button.configure(fg_color=pulse_color, text="Listening...")
            time.sleep(0.5)
            if not self.listening_animation_active: break
            self.mic_button.configure(fg_color=original_color, text="Listening...")
            time.sleep(0.5)
        
        # Restore original state
        self.mic_button.configure(fg_color=original_color, text="🎤 Speak")


    def run_ai_logic(self):
        """The core logic: listen, process, and respond."""
        try:
            with sr.Microphone() as source:
                self.update_status("Listening for a command...")
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
            self.listening_animation_active = False
            self.mic_button.configure(state="normal")
            self.update_status("Idle")
            
    def send_whatsapp_desktop(self):
        """Guides the user to send a WhatsApp message via the desktop app."""
        try:
            contact_name = self.listen_for_response("Who should I send the message to?")
            if not contact_name: return

            message = self.listen_for_response("What is the message?")
            if not message: return
            
            self.speak(f"Okay, sending your message to {contact_name}.")

            # Open WhatsApp Desktop App
            whatsapp_path = os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe")
            if not os.path.exists(whatsapp_path):
                self.speak("I couldn't find the WhatsApp desktop app at its default location.")
                return
            os.startfile(whatsapp_path)
            time.sleep(8) # Wait for app to load

            # Click on the search bar (adjust coordinates if necessary)
            pyautogui.click(x=250, y=115) 
            time.sleep(1)
            pyautogui.write(contact_name)
            time.sleep(2)

            # Click on the contact in the list
            pyautogui.click(x=250, y=250)
            time.sleep(1)

            # Type and send the message
            pyautogui.write(message)
            time.sleep(1)
            pyautogui.press('enter')
            
            self.speak("The message has been sent.")

        except Exception as e:
            self.speak("I ran into a problem trying to send the message. Please make sure the WhatsApp app is installed and ready.")
            self.update_status(f"WhatsApp Error: {e}")


    def process_command(self, command):
        """Determines the user's intent and executes the corresponding action."""
        try:
            # --- System & App Control ---
            if "open notepad" in command:
                self.speak("Opening Notepad.")
                os.startfile("notepad.exe")
            elif "open command prompt" in command:
                self.speak("Opening Command Prompt.")
                os.startfile("cmd.exe")
            elif "open vs code" in command or "open visual studio code" in command:
                self.speak("Opening VS Code.")
                vscode_path = os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
                if os.path.exists(vscode_path):
                    os.startfile(vscode_path)
                else:
                    self.speak("I couldn't find VS Code at the default path. Trying to launch from command.")
                    os.system("code") # Fallback for if 'code' is in PATH
            elif "send a whatsapp message" in command:
                self.send_whatsapp_desktop()
            elif "send email" in command:
                self.speak("Opening your email client.")
                os.startfile('mailto:')
            elif "open browser" in command or "open chrome" in command:
                self.speak("Opening your browser.")
                webbrowser.open("http://google.com")
            elif "shutdown system" in command:
                self.speak("Shutting down the system in 5 seconds. Please save your work.")
                os.system("shutdown /s /t 5")
            
            # --- Information & Utilities ---
            elif "weather" in command:
                api_key = "PASTE_YOUR_OPENWEATHERMAP_API_KEY_HERE"
                base_url = "http://api.openweathermap.org/data/2.5/weather?"
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

            elif "news" in command:
                api_key = "0cd463c33f6e402ca87195024161672a"
                main_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
                news = requests.get(main_url).json()
                articles = news["articles"]
                self.speak("Here are the top news headlines.")
                for i, article in enumerate(articles[:3]):
                    self.speak(f"Headline {i+1}: {article['title']}")
            
            elif "time" in command:
                strTime = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {strTime}")

            elif "wikipedia" in command:
                self.speak("Searching Wikipedia...")
                query = command.replace("wikipedia", "").strip()
                results = pywhatkit.info(query, lines=2)
                self.speak("According to Wikipedia...")
                self.speak(results)

            # --- Productivity & Communication ---
            elif "remind me" in command:
                reminder_text = command.replace("remind me", "").strip()
                self.speak(f"Reminder set: {reminder_text}")
                notification.notify(
                    title='MediTalk Pro Reminder',
                    message=reminder_text,
                    timeout=10
                )

            # --- Entertainment ---
            elif "play" in command:
                query = command.replace("play", "").strip()
                self.speak(f"Playing {query} on YouTube.")
                pywhatkit.playonyt(query)

            # --- Default to LLM ---
            else:
                self.update_status("Getting response from AI model...")
                health_prompt = f"Act as a helpful medical assistant and answer this question clearly and simply, including a disclaimer to consult a doctor: {command}"
                response = self.model.generate_content(health_prompt)
                self.speak(response.text)
        
        except Exception as e:
            self.speak("Sorry, I encountered an error while processing that command.")
            self.update_status(f"Processing Error: {e}")


# --- Run the Application ---
if __name__ == "__main__":
    app = MediTalkProApp()
    app.mainloop()
