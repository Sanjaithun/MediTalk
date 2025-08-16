import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import threading # Important for keeping the UI responsive
import pywhatkit # For playing YouTube videos
import webbrowser # For opening websites

# --- Main Application Class ---
class MediTalkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("MediTalk AI")
        self.geometry("400x300")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        # --- AI & Voice Setup ---
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.configure_ai_model()

        # --- UI Widgets ---
        self.status_label = ctk.CTkLabel(self, text="Click the button and speak", font=("Helvetica", 16))
        self.status_label.pack(pady=20)

        self.mic_button = ctk.CTkButton(self, text="🎤 Speak", font=("Helvetica", 24), command=self.start_listening_thread)
        self.mic_button.pack(pady=40, padx=40, fill="both", expand=True)

    def configure_ai_model(self):
        """Sets up the connection to the Gemini LLM."""
        try:
            # IMPORTANT: Paste your API key here
            YOUR_API_KEY = "AIzaSyAgTgnYzr9LbzSF5GSHYdgk5nTyhXEa1I0"
            genai.configure(api_key=YOUR_API_KEY)
            
            system_instruction = """
            You are "MediTalk AI", a helpful voice assistant.
            If the query is health-related, you MUST act as a compassionate healthcare assistant. Provide clear, safe health information and ALWAYS end with the disclaimer: "Please remember, I am an AI assistant. Consult a doctor for any health concerns." You must NEVER give a diagnosis.
            If the query is NOT health-related, act as a general helpful assistant.
            If a health query sounds like an emergency (e.g., "chest pain," "can't breathe"), your ONLY response must be: "This sounds like an emergency. Please contact your local emergency services immediately."
            """
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
        except Exception as e:
            self.status_label.configure(text="Error: Could not configure AI. Check API Key.")
            print(f"Configuration Error: {e}")

    def speak(self, text):
        """Speaks the given text out loud."""
        self.status_label.configure(text="Speaking...")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        self.status_label.configure(text="Click the button and speak")

    def start_listening_thread(self):
        """Starts the main AI logic in a separate thread to prevent UI freezing."""
        self.mic_button.configure(state="disabled", text="Listening...")
        self.status_label.configure(text="Listening...")
        threading.Thread(target=self.run_ai_logic, daemon=True).start()

    def run_ai_logic(self):
        """The core logic: listen, process, and respond."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5)
                
            self.status_label.configure(text="Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")

            # --- Command Processing ---
            if "play" in command:
                song_or_video = command.replace("play", "").strip()
                self.speak(f"Playing {song_or_video} on YouTube.")
                pywhatkit.playonyt(song_or_video)
            
            elif "search for" in command or "google" in command:
                query = command.replace("search for", "").replace("google", "").strip()
                self.speak(f"Searching for {query}.")
                webbrowser.open(f"https://www.google.com/search?q={query}")

            elif "goodbye" in command or "exit" in command:
                self.speak("Goodbye! Stay healthy.")
                self.after(1000, self.destroy) # Close the app after 1 second
            
            else: # If it's not a special command, ask the LLM
                self.status_label.configure(text="Thinking...")
                response = self.model.generate_content(command)
                self.speak(response.text)

        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.speak("Sorry, I had trouble understanding. Please try again.")
        
        finally:
            self.mic_button.configure(state="normal", text="🎤 Speak")
            self.status_label.configure(text="Click the button and speak")

# --- Run the Application ---
if __name__ == "__main__":
    app = MediTalkApp()
    app.mainloop()