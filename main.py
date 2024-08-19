from file_handler import FileHandler
from comparison import DataComparer
from query_handler import QueryHandler
from voice_assistant import VoiceAssistant  # Import the VoiceAssistant class
import speech_recognition as sr

def main(file_path1, file_path2, question):
    # Initialize FileHandlers
    handler1 = FileHandler(file_path1)
    handler2 = FileHandler(file_path2)

    # Get DataFrames
    df1 = handler1.df
    df2 = handler2.df

    # Initialize DataComparer
    comparer = DataComparer(df1, df2)
    comparison_summary = comparer.process_dataframes()

    # Initialize QueryHandler
    query_handler = QueryHandler()

    # Check if microphone is available
    microphone_available = True
    try:
        sr.Microphone()
    except OSError:
        microphone_available = False

    if microphone_available:
        # If the microphone is available, use the VoiceAssistant to standardize the question
        voice_assistant = VoiceAssistant(language="en-US")
        standardized_question = voice_assistant.standardize_language(question)
    else:
        # If no microphone, use the original question as-is
        standardized_question = question

    print(f"Standardized Question: {standardized_question}")

    # Ask the question using the standardized query
    response = query_handler.ask_question(comparison_summary, standardized_question)

    # Print the response
    print(response)

if __name__ == "__main__":
    file_path1 = "C:\\Users\\Sam\\Desktop\\db 1.xlsx"
    file_path2 = "C:\\Users\\Sam\\Desktop\\db 2 sql.sql"
    question = "which country has the lowest population in both files?"

    main(file_path1, file_path2, question)