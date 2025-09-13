import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os

# --- Initialization ---
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# --- Configure the LLM ---
# IMPORTANT: Replace with your actual API key
# For better security, consider using environment variables in a real project
YOUR_API_KEY = "AIzaSyAgTgnYzr9LbzSF5GSHYdgk5nTyhXEa1I0" 
genai.configure(api_key=YOUR_API_KEY)

# Create the model
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# This pre-prompt sets the rules and personality for our AI
system_instruction = """
You are "MediTalk AI", a compassionate and helpful voice-based healthcare assistant.
Your purpose is to provide clear, simple, and safe health information.
Your audience includes the elderly and people with visual impairments, so your answers must be easy to understand and concise.

IMPORTANT RULES:
1.  **NEVER provide a diagnosis.** You are not a doctor. Never say "you might have..." or "it sounds like...".
2.  **ALWAYS include a disclaimer.** After every response related to symptoms, conditions, or medical advice, you MUST say: "Please remember, I am an AI assistant and not a medical professional. Consult with a doctor for any health concerns."
3.  **Keep answers brief and to the point.** Use simple language.
4.  If asked about a topic outside of health, wellness, or medicine, politely decline by saying, "I can only provide information about health-related topics."
5.  If a user describes a serious emergency (e.g., "chest pain," "can't breathe"), your ONLY response should be: "This sounds like an emergency. Please contact your local emergency services immediately."
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# --- Core Functions ---
def speak(text):
    """Converts text to speech."""
    print(f"MediTalk AI: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listens for user voice input from the microphone."""
    with sr.Microphone() as source:
        print("\nI'm listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            speak("Sorry, I can't connect to the speech service right now.")
            return None

def get_llm_response(command):
    """Sends the command to the LLM and gets a response."""
    if not command:
        return None
        
    # Check for exit command first to avoid sending it to the LLM
    if "goodbye" in command or "exit" in command:
        return "Goodbye! Stay healthy."

    try:
        print("Getting response from the AI model...")
        response = model.generate_content(command)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return "I'm having a little trouble thinking right now. Please try again in a moment."

# --- Main Application Loop ---
if __name__ == "__main__":
    speak("MediTalk AI is now active and ready to help.")
    
    while True:
        user_command = listen()
        if user_command:
            if "goodbye" in user_command or "exit" in user_command:
                speak("Goodbye! Stay healthy.")
                break
            
            ai_response = get_llm_response(user_command)
            speak(ai_response)

# # import speech_recognition as sr
# # import pyttsx3
# # import spacy

# # # --- Initialization ---
# # # Initialize the recognizer for listening
# # recognizer = sr.Recognizer()

# # # Initialize the text-to-speech engine for speaking (works offline)
# # tts_engine = pyttsx3.init()

# # # Initialize spaCy for NLP
# # nlp = spacy.load("en_core_web_sm")

# # # --- Core Functions ---
# # def speak(text):
# #     """Converts text to speech."""
# #     print(f"MediTalk AI: {text}")
# #     tts_engine.say(text)
# #     tts_engine.runAndWait()

# # def listen():
# #     """Listens for user voice input from the microphone."""
# #     with sr.Microphone() as source:
# #         print("Listening...")
# #         recognizer.adjust_for_ambient_noise(source) # Adjust for background noise
# #         audio = recognizer.listen(source)
        
# #         try:
# #             print("Recognizing...")
# #             # Use Google's online recognizer for now (we can swap for offline later)
# #             command = recognizer.recognize_google(audio).lower()
# #             print(f"You said: {command}")
# #             return command
# #         except sr.UnknownValueError:
# #             print("Sorry, I did not understand that.")
# #             return None
# #         except sr.RequestError:
# #             speak("Sorry, my speech service is down. Please check your internet connection.")
# #             return None

# # def process_command(command):
# #     """Processes the recognized command to determine user intent."""
# #     if command:
# #         if "hello" in command:
# #             speak("Hello! I am MediTalk AI. How can I assist you with your health today?")
# #         elif "goodbye" in command or "exit" in command:
# #             speak("Goodbye! Stay healthy.")
# #             return "exit" # Signal to exit the loop
# #         else:
# #             speak("I'm still learning. I can't help with that yet.")
# #     return None

# # # --- Main Application Loop ---
# # if __name__ == "__main__":
# #     speak("MediTalk AI is now active.")
    
# #     while True:
# #         user_command = listen()
# #         if user_command:
# #             result = process_command(user_command)
# #             if result == "exit":
# #                 break
# import speech_recognition as sr
# import pyttsx3
# import spacy

# # --- Initialization ---
# recognizer = sr.Recognizer()
# tts_engine = pyttsx3.init()
# nlp = spacy.load("en_core_web_sm")

# # --- Knowledge Base ---
# # A simple dictionary to store health information.
# # In a real app, this would be a large, reliable database.
# knowledge_base = {
#     "symptoms": {
#         "headache": "For a common headache, you can try resting in a quiet, dark room, drinking water, and taking an over-the-counter pain reliever. However, if the pain is severe or persistent, please consult a doctor.",
#         "fever": "A fever is often a sign that your body is fighting an infection. Make sure to get plenty of rest and drink fluids. If your fever is very high or lasts for more than a few days, it is important to see a healthcare professional.",
#         "cough": "For a simple cough, you can try drinking warm tea with honey or using cough drops. If your cough is severe, accompanied by other symptoms like a high fever, or lasts for weeks, please see a doctor."
#     },
#     "exercises": {
#         "breathing": "Let's do a simple deep breathing exercise. Inhale slowly through your nose for four seconds. Hold your breath for seven seconds. Then, exhale slowly through your mouth for eight seconds. Repeat this a few times to feel more relaxed.",
#         "stretching": "For a simple neck stretch, slowly tilt your head towards your right shoulder and hold for 15 seconds. Then, repeat on the left side. This can help relieve tension."
#     }
# }

# # --- Core Functions ---
# def speak(text):
#     """Converts text to speech."""
#     print(f"MediTalk AI: {text}")
#     tts_engine.say(text)
#     tts_engine.runAndWait()

# def listen():
#     """Listens for user voice input from the microphone."""
#     with sr.Microphone() as source:
#         print("\nListening for your command...")
#         recognizer.adjust_for_ambient_noise(source, duration=0.5)
#         try:
#             audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
#             print("Recognizing...")
#             command = recognizer.recognize_google(audio).lower()
#             print(f"You said: {command}")
#             return command
#         except sr.WaitTimeoutError:
#             print("Listening timed out. Please try speaking again.")
#             return None
#         except sr.UnknownValueError:
#             return None # Don't say anything if speech is unintelligible
#         except sr.RequestError:
#             speak("Sorry, my speech service is down. Please check your internet connection.")
#             return None

# def process_command(command):
#     """Processes the command using NLP to provide a helpful response."""
#     if not command:
#         return None

#     # Use spaCy to analyze the text
#     doc = nlp(command)
    
#     # --- Intent 1: Greeting ---
#     if any(token.lemma_ in ["hello", "hi", "hey"] for token in doc):
#         speak("Hello! I am MediTalk AI. How can I assist you with your health today?")
#         return None

#     # --- Intent 2: Asking about Symptoms ---
#     if "symptom" in command or "feel" in command or "have" in command:
#         # A more robust check for symptoms
#         found_symptom = False
#         for token in doc:
#             # Check for nouns that are in our symptom knowledge base
#             if token.pos_ == "NOUN" and token.lemma_ in knowledge_base["symptoms"]:
#                 speak(knowledge_base["symptoms"][token.lemma_])
#                 speak("Please remember, this is for informational purposes only and not a substitute for professional medical advice.")
#                 found_symptom = True
#                 break
#         if found_symptom:
#             return None

#     # --- Intent 3: Asking for Exercises ---
#     if "exercise" in command or "stretches" in command:
#         found_exercise = False
#         for token in doc:
#             if token.lemma_ in knowledge_base["exercises"]:
#                 speak(knowledge_base["exercises"][token.lemma_])
#                 found_exercise = True
#                 break
#         if found_exercise:
#             return None
            
#     # --- Intent 4: Exit ---
#     if any(token.lemma_ in ["goodbye", "exit", "quit"] for token in doc):
#         speak("Goodbye! Stay healthy.")
#         return "exit"

#     # --- Default Fallback Response ---
#     speak("I'm sorry, I don't have information on that topic right now. You can ask me about symptoms like headaches, or for an exercise like breathing.")
#     return None

# # --- Main Application Loop ---
# if __name__ == "__main__":
#     speak("MediTalk AI is now active. How can I help you?")
    
#     while True:
#         user_command = listen()
#         if user_command:
#             result = process_command(user_command)
#             if result == "exit":
#                 break

# const GEMINI_API_KEY = "AIzaSyADhFxYOJG-PpymgfPlzxhlCBQ5XvpZm7I";
# const GOOGLE_SEARCH_API_KEY = "AIzaSyCVMVTJwLvSC7XJjTMuh1XpOiCJht8QbTg";
# const GOOGLE_SEARCH_CX = "149fc2eb221274d84";
