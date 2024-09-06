import speech_recognition as sr
import pyttsx3
from langchain_openai import ChatOpenAI
import threading
from typing import Optional

class VoiceAssistant:
    def __init__(self, language: str = "en-US"):
        self.language: str = language
        self.llm: ChatOpenAI = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.tts_engine: pyttsx3.Engine = pyttsx3.init()
        self.stop_event: threading.Event = threading.Event()

        self.microphone: Optional[sr.Microphone] = None
        self.recognizer: Optional[sr.Recognizer] = None
        self._initialize_microphone()

    def _initialize_microphone(self) -> None:
        """Initialize microphone if available."""
        try:
            self.microphone = sr.Microphone()
            self.recognizer = sr.Recognizer()
            print("Microphone successfully initialized.")
        except OSError:
            print("No default input device available. Microphone will not be used.")

    def stop(self):
        """Stop any ongoing text-to-speech."""
        self.stop_event.set()
        if self.tts_thread and self.tts_thread.is_alive():
            self.tts_engine.stop()

    def listen(self) -> Optional[str]:
        """Capture voice input from the user and convert it to text."""
        if not self.microphone or not self.recognizer:
            print("Microphone is not available.")
            return None

        with self.microphone as source:
            print("How can I help you?")
            self.speak("How can I help you?")
            audio = self.recognizer.listen(source)
        
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            self.speak("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            self.speak(f"Sorry, there was an error with the speech recognition service: {str(e)}")
        
        return None

    def standardize_language(self, text: Optional[str]) -> Optional[str]:
        """Standardize the language of the given text using an LLM."""
        if not text:
            return None

        prompt = f"Please rephrase the following text in a more standard and formal language: '{text}'"
        response = self.llm(prompt)
        return response.content.strip()

    def speak(self, text: Optional[str]) -> None:
        """Convert the text to speech and play it back to the user."""
        if not text:
            return

        def tts() -> None:
            """Thread function for text-to-speech."""
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

        self.stop_event.clear()
        self.tts_thread = threading.Thread(target=tts)
        self.tts_thread.start()

    def get_query(self) -> Optional[str]:
        """Capture user's voice input, standardize it, and return the standardized text."""
        user_text = self.listen()
        return self.standardize_language(user_text) if user_text else None

    def respond(self, response_text: str) -> None:
        """Respond to the user by speaking the text out loud."""
        if response_text:
            self.speak(response_text)
