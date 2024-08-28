from dotenv import load_dotenv
import pandas as pd
from langchain_openai import ChatOpenAI
from typing import Union

# Load environment variables (API KEY)
load_dotenv()

class QueryHandler:
    def __init__(self):
        self.llm: ChatOpenAI = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
        )

    def ask_question(self, content: Union[pd.DataFrame, str], question: str) -> str:
        """
        Ask a question using LangChain, limited to the content provided.

        Args:
            content (Union[pd.DataFrame, str]): The content to base the answer on.
                Can be either a DataFrame or a string (comparison summary).
            question (str): The question to be answered.

        Returns:
            str: The generated answer to the question.
        """
        prompt = self._create_prompt(content, question)
        return self._generate_response(prompt)

    def _create_prompt(self, content: Union[pd.DataFrame, str], question: str) -> str:
        """
        Create a prompt based on the content type and question.

        Args:
            content (Union[pd.DataFrame, str]): The content to base the answer on.
            question (str): The question to be answered.

        Returns:
            str: The generated prompt.
        """
        if isinstance(content, pd.DataFrame):
            content_str = content.head(10).to_string(index=False)
            return f"DataFrame content:\n{content_str}\n\nQuestion: {question}\nAnswer:"
        else:
            return f"Comparison Summary:\n{content}\n\nQuestion: {question}\nAnswer:"

    def _generate_response(self, prompt: str) -> str:
        """
        Generate a response using the LLM based on the given prompt.

        Args:
            prompt (str): The prompt to generate a response for.

        Returns:
            str: The generated response.
        """
        response = self.llm.stream([prompt])
        
        answer = ""
        for chunk in response:
            answer += chunk.content
        return answer.strip()