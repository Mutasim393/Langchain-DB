from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables (API KEY)
load_dotenv()

class QueryHandler:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
        )

    def ask_question(self, comparison_summary, question):
        """Ask a question using LangChain."""
        # Combine the comparison summary and the question
        prompt = f"Comparison Summary:\n{comparison_summary}\n\nQuestion: {question}\nAnswer:"

        # Stream the response
        response = self.llm.stream([prompt])
        
        # Collect and return the response
        answer = ""
        for chunk in response:
            answer += chunk.content
        return answer