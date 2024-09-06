from dotenv import load_dotenv
import pandas as pd
from langchain_openai import ChatOpenAI
from typing import Union, List

# Load environment variables (API KEY)
load_dotenv()

class QueryHandler:
    def __init__(self):
        self.llm: ChatOpenAI = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5,
        )
        self.history: List[str] = []  # List to store the history of questions and answers

    def ask_question(self, content: Union[pd.DataFrame, str], question: str) -> str:
        """
        Ask a question using LangChain, with context from previous questions and answers.

        Args:
            content (Union[pd.DataFrame, str]): The content to base the answer on.
                Can be either a DataFrame or a string (comparison summary).
            question (str): The question to be answered.

        Returns:
            str: The generated answer to the question.
        """
        prompt = self._create_prompt(content, question)
        answer = self._generate_response(prompt)
        self._update_history(question, answer)
        return self.display_full_conversation()

    def _create_prompt(self, content: Union[pd.DataFrame, str], question: str) -> str:
        """
        Create a prompt based on the content type, question, and conversation history.

        Args:
            content (Union[pd.DataFrame, str]): The content to base the answer on.
            question (str): The question to be answered.

        Returns:
            str: The generated prompt.
        """
        if isinstance(content, pd.DataFrame):
            content_str = content.head(250).to_string(index=False)
            content_str = f"DataFrame content:\n{content_str}\n\n"
        else:
            content_str = f"Comparison Summary:\n{content}\n\n"
        
        # Combine history into prompt, only including the latest context
        history_str = "\n\n".join(self.history)
        return f"{history_str}\n{content_str}Question: {question}\nAnswer:"

    def _generate_response(self, prompt: str) -> str:
        """
        Generate a response using the LLM based on the given prompt.

        Args:
            prompt (str): The prompt to generate a response for.

        Returns:
            str: The generated response.
        """
        response = self.llm.stream([prompt])
        answer = "".join(chunk.content for chunk in response)
        return answer.strip()

    def _update_history(self, question: str, answer: str) -> None:
        """
        Update the conversation history with the latest question and answer.

        Args:
            question (str): The question asked.
            answer (str): The answer received.
        """
        self.history.append(f"Question: {question}\n\nAnswer: {answer}\n")
        # Optional: Limit history length to prevent excessive data accumulation
        if len(self.history) > 10:  # Adjust as needed
            self.history.pop(0)  # Remove the oldest entry

    def display_full_conversation(self) -> str:
        """
        Retrieve the latest part of the conversation history formatted for display.

        Returns:
            str: The latest part of the conversation history formatted for display.
        """
        if not self.history:
            return ""
        
        # Find the last occurrence of a question to start from
        latest_question_index = len(self.history) - 1
        while latest_question_index >= 0 and not self.history[latest_question_index].startswith("Question:"):
            latest_question_index -= 1
        
        # Display from the latest question forward
        if latest_question_index >= 0:
            return "\n\n".join(self.history[latest_question_index:])
        return ""
