import tkinter as tk
from tkinter import filedialog
from file_handler import FileHandler
from comparison import DataComparer
from query_handler import QueryHandler
from voice_assistant import VoiceAssistant
import speech_recognition as sr

def get_question_from_microphone(voice_assistant):
    """Capture question from the microphone using the VoiceAssistant and print it for debugging."""
    question = voice_assistant.get_query()
    print(f"Heard Question: {question}")  # Print the question for diagnostic purposes
    return question

def get_question_from_user():
    """Get the question from user input."""
    question = input("Please type your question: ")
    return question

def select_files(prompt):
    """Open a file dialog and return a list of selected file paths."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(
        title=prompt,
        filetypes=[
            ("All files", "*.*")  # Allow all file types for testing or other use cases
        ]
    )
    return list(file_paths)

def main():
    # Prompt the user to select multiple files
    print("Please select the files to process (you can select multiple files):")
    file_paths = select_files("Select files to process")

    if len(file_paths) < 2:
        print("At least two files are required for comparison. Exiting program.")
        return

    # Initialize FileHandlers and read files
    dataframes = []
    for file_path in file_paths:
        try:
            handler = FileHandler(file_path)
            df = handler.df
            dataframes.append(df)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    if len(dataframes) < 2:
        print("At least two files are required for comparison. Exiting program.")
        return

    # Initialize DataComparer with the list of DataFrames
    comparer = DataComparer(dataframes)
    comparison_summary = comparer.process_dataframes()

    # Initialize QueryHandler
    query_handler = QueryHandler()

    # Initialize VoiceAssistant and check microphone availability
    try:
        voice_assistant = VoiceAssistant(language="en-US")
        microphone_available = True
    except OSError:
        print("No default microphone found. Switching to text input mode.")
        voice_assistant = None
        microphone_available = False

    while True:
        # Ask user for input method
        if microphone_available:
            input_method = input("Do you want to use the microphone or type your question? (type/microphone): ").strip().lower()
        else:
            input_method = 'type'  # Force text input if microphone is not available

        if input_method == 'microphone' and microphone_available:
            # Get the question from the user via microphone
            question = get_question_from_microphone(voice_assistant)
            if question is None:
                if voice_assistant:
                    voice_assistant.speak("No question detected, please try again.")
                print("No question detected, please try again.")
                continue
        elif input_method == 'type' or not microphone_available:
            # Get the question from user input
            question = get_question_from_user()
        else:
            if voice_assistant:
                voice_assistant.speak("Invalid option, please choose 'microphone' or 'type'.")
            print("Invalid option, please choose 'microphone' or 'type'.")
            continue

        if not question:
            if voice_assistant:
                voice_assistant.speak("I didn't get that. Please try again.")
            print("I didn't get that. Please try again.")
            continue

        # Standardize the question using VoiceAssistant
        if voice_assistant:
            standardized_question = voice_assistant.standardize_language(question)
        else:
            standardized_question = question

        if standardized_question:
            # Print standardized question for debugging purposes
            print(f"Standardized Question: {standardized_question}")

            # Ask the question using the standardized query
            response = query_handler.ask_question(comparison_summary, standardized_question)

            # Print and vocalize the response
            print(response)
            if voice_assistant:
                voice_assistant.respond(response)
        else:
            if voice_assistant:
                voice_assistant.speak("Sorry, I couldn't understand your question. Please try again.")
            print("Sorry, I couldn't understand your question. Please try again.")

        # Ask the user if they want to continue
        continue_prompt = input("Do you want to ask another question? (yes/no): ").strip().lower()
        if continue_prompt != 'yes':
            if voice_assistant:
                voice_assistant.speak("Exiting the program. Have a great day!")
            print("Exiting the program. Have a great day!")
            break

if __name__ == "__main__":
    main()
