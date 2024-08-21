from file_handler import FileHandler
from comparison import DataComparer
from query_handler import QueryHandler
from voice_assistant import VoiceAssistant  # Import the VoiceAssistant class

def get_question_from_microphone(voice_assistant):
    """Capture question from the microphone using the VoiceAssistant."""
    return voice_assistant.get_query()

def get_question_from_user():
    """Get the question from user input."""
    question = input("Please type your question: ")
    return question

def main(file_path1, file_path2):
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

    # Initialize VoiceAssistant
    voice_assistant = VoiceAssistant(language="en-US")

    while True:
        # Ask user for input method
        input_method = input("Do you want to use the microphone or type your question? (type/microphone): ").strip().lower()

        if input_method == 'microphone':
            # Get the question from the user via microphone
            question = get_question_from_microphone(voice_assistant)
            if question is None:
                voice_assistant.speak("No question detected, please try again.")
                print("No question detected, please try again.")
                continue
        elif input_method == 'type':
            # Get the question from user input
            question = get_question_from_user()
        else:
            voice_assistant.speak("Invalid option, please choose 'microphone' or 'type'.")
            print("Invalid option, please choose 'microphone' or 'type'.")
            continue

        if not question:
            voice_assistant.speak("I didn't get that. Please try again.")
            print("I didn't get that. Please try again.")
            continue

        # Standardize the question using VoiceAssistant
        standardized_question = voice_assistant.standardize_language(question)
        if standardized_question:
            # Print standardized question for debugging purposes
            # print(f"Standardized Question: {standardized_question}")  # Comment this out for user-facing script

            # Ask the question using the standardized query
            response = query_handler.ask_question(comparison_summary, standardized_question)

            # Print and vocalize the response
            print(response)
            voice_assistant.respond(response)
        else:
            voice_assistant.speak("Sorry, I couldn't understand your question. Please try again.")
            print("Sorry, I couldn't understand your question. Please try again.")

        # Ask the user if they want to continue
        continue_prompt = input("Do you want to ask another question? (yes/no): ").strip().lower()
        if continue_prompt != 'yes':
            voice_assistant.speak("Exiting the program. Have a great day!")
            print("Exiting the program. Have a great day!")
            break

if __name__ == "__main__":
    file_path1 = "C:\\Users\\Mutasim El-Khidir\\OneDrive - Swansea University\\Desktop\\Langchain-DB-SQL-tested\\2254626 - Design 1.docx"
    file_path2 = "C:\\Users\\Mutasim El-Khidir\\OneDrive - Swansea University\\Desktop\\Langchain-DB-SQL-tested\\2254626 - Design 1.pdf"

    main(file_path1, file_path2)
