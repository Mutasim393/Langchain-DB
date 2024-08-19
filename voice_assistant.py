import speech_recognition as sr
import pyttsx3
from langchain_openai import ChatOpenAI

class VoiceAssistant:
    def __init__(self, language="en-US"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = language
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.tts_engine = pyttsx3.init()

    def listen(self):
        """Capture voice input from the user and convert it to text."""
        with self.microphone as source:
            print("Say something!")
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition; {e}")
            return None

    def standardize_language(self, text):
        """Standardize the language of the given text using an LLM."""
        if not text:
            return None

        # Generate a standardized version of the input text
        prompt = f"Please rephrase the following text in a more standard and formal language: '{text}'"
        response = self.llm(prompt)
        return response.content.strip()

    def speak(self, text):
        """Convert the text to speech and play it back to the user."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def get_query(self):
        """Capture user's voice input, standardize it, and return the standardized text."""
        # Capture the voice input
        user_text = self.listen()

        if user_text:
            # Standardize the captured text
            standardized_text = self.standardize_language(user_text)
            print(f"Standardized Query: {standardized_text}")
            return standardized_text
        else:
            return None

    def respond(self, response_text):
        """Respond to the user by speaking the text out loud."""
        print(f"Response: {response_text}")
        self.speak(response_text)

# Usage example
if __name__ == "__main__":
    # Example: Listening for input in Spanish ("es-ES")
    voice_assistant = VoiceAssistant(language="es-ES")
    standardized_query = voice_assistant.get_query()

    if standardized_query:
        # Respond to the user
        response_text = f"You asked: {standardized_query}. Let me help with that."
        voice_assistant.respond(response_text)
        # Proceed with the standardized query using the existing QueryHandler
        # question = standardized_query
        # ... continue with the existing logic to handle the query
