import tkinter as tk
import threading
from typing import List, Optional
import pandas as pd
from file_handler import FileHandler
from comparison import DataComparer
from gui_handler import GUIHandler
from query_handler import QueryHandler
from voice_assistant import VoiceAssistant

class App:
    def __init__(self):
        self.dataframes: List[pd.DataFrame] = []
        self.file_paths: List[str] = []
        self.comparison_summary: str = ""
        self.voice_assistant: Optional[VoiceAssistant] = None
        self.microphone_available: bool = self._check_microphone_availability()
        self.stop_event: threading.Event = threading.Event()
        self.voice_thread: Optional[threading.Thread] = None

        # Initialize QueryHandler once
        self.query_handler = QueryHandler()

    def _check_microphone_availability(self) -> bool:
        """Check if a microphone is available and initialize VoiceAssistant."""
        try:
            self.voice_assistant = VoiceAssistant(language="en-US")
            return True
        except OSError:
            return False

    def load_files(self, file_paths: List[str]) -> str:
        """Load selected files and handle multiple file processing if necessary."""
        new_dataframes = []
        for file_path in file_paths:
            try:
                handler = FileHandler(file_path)
                new_dataframes.append(handler.df)
            except Exception as e:
                return f"Error processing file {file_path}: {str(e)}"

        self.dataframes.extend(new_dataframes)
        self.file_paths.extend(file_paths)
        self._update_comparison_summary()
        return "Files successfully loaded."

    def remove_files(self, file_paths: List[str]) -> str:
        """Remove specified files and update dataframes."""
        paths_to_remove = set(file_paths)
        self.dataframes = [df for df, path in zip(self.dataframes, self.file_paths) if path not in paths_to_remove]
        self.file_paths = [path for path in self.file_paths if path not in paths_to_remove]
        self._update_comparison_summary()
        return "Files successfully removed."

    def _update_comparison_summary(self) -> None:
        """Update comparison summary based on the current dataframes."""
        if len(self.dataframes) >= 2:
            comparer = DataComparer(self.dataframes)
            self.comparison_summary = comparer.process_dataframes()
        else:
            self.comparison_summary = ""

    def handle_query(self, question: str) -> str:
        """Process the query based on loaded files and return the response."""
        if self.voice_assistant:
            standardized_question = self.voice_assistant.standardize_language(question)
        else:
            standardized_question = question

        if standardized_question:
            # Use the single instance of QueryHandler
            if len(self.dataframes) == 1:  # Single file processing
                response = self.query_handler.ask_question(self.dataframes[0], standardized_question)
            else:  # Multiple file processing
                response = self.query_handler.ask_question(self.comparison_summary, standardized_question)

            return response
        else:
            return "Sorry, I couldn't understand your question."

    def respond(self, response: str, voice_response_enabled: bool) -> Optional[str]:
        """Play voice response if enabled."""
        if voice_response_enabled and self.voice_assistant:
            self.stop_event.clear()
            if self.voice_thread and self.voice_thread.is_alive():
                self.stop_event.set()
                self.voice_assistant.stop()
            self.voice_thread = threading.Thread(target=self._voice_response, args=(response,))
            self.voice_thread.start()
        return None

    def _voice_response(self, response: str) -> None:
        """Play voice response in a separate thread."""
        if not self.stop_event.is_set():
            try:
                self.voice_assistant.respond(response)
            except Exception as e:
                print(f"Error during voice response: {str(e)}")

    def stop_voice_assistant(self):
        """Stop the voice assistant if it's running."""
        if self.voice_thread and self.voice_thread.is_alive():
            self.stop_event.set()
            self.voice_assistant.stop()

    def main(self) -> None:
        """Initialize the GUI and start the main loop."""
        root = tk.Tk()
        GUIHandler(root, self)
        root.mainloop()

if __name__ == "__main__":
    app = App()
    app.main()
