import pandas as pd
from docx import Document as DocxDocument
import pdfplumber
from sqlalchemy import create_engine, text
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from langchain_openai import ChatOpenAI
from typing import Optional, Union
import os

class FileHandler:
    def __init__(self, file_path: Optional[str] = None, connection_string: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self.connection_string: Optional[str] = connection_string
        self.engine = self._create_engine()
        self.df: pd.DataFrame = pd.DataFrame()
        self.llm: Optional[ChatOpenAI] = self._initialize_llm()

        if file_path:
            self.df = self.load_file()

    def _create_engine(self) -> Optional[Union[sqlalchemy.engine.base.Engine, sqlalchemy.engine.base.Connection]]:
        """Create an appropriate database engine based on the input."""
        if not self.connection_string and self.file_path and self.file_path.endswith('.sql'):
            return create_engine('sqlite:///:memory:')
        elif self.connection_string:
            return create_engine(self.connection_string)
        return None

    def _initialize_llm(self) -> Optional[ChatOpenAI]:
        """Initialize the language model if an engine is available."""
        return ChatOpenAI(model="gpt-4o", temperature=0.1) if self.engine else None

    def load_file(self) -> pd.DataFrame:
        """Load file based on its extension and return a DataFrame."""
        if not self.file_path:
            raise ValueError("No file path provided.")

        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        loaders = {
            '.xlsx': self._load_excel,
            '.xls': self._load_excel,
            '.csv': self._load_csv,
            '.pdf': self._load_pdf,
            '.docx': self._load_docx,
            '.sql': self._load_sql_file
        }

        loader = loaders.get(file_extension)
        if loader:
            return loader()
        elif self.file_path.startswith('sql://'):
            return self._load_sql_query()
        else:
            raise ValueError(f"Unsupported file type: {self.file_path}")

    def _load_excel(self) -> pd.DataFrame:
        """Read Excel file and return a DataFrame."""
        try:
            return pd.read_excel(self.file_path)
        except Exception as e:
            print(f"Error reading Excel file {self.file_path}: {str(e)}")
            return pd.DataFrame()

    def _load_csv(self) -> pd.DataFrame:
        """Read CSV file and return a DataFrame."""
        try:
            return pd.read_csv(self.file_path)
        except Exception as e:
            print(f"Error reading CSV file {self.file_path}: {str(e)}")
            return pd.DataFrame()

    def _load_pdf(self) -> pd.DataFrame:
        """Read PDF file and return a DataFrame."""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text_data = [page.extract_text() for page in pdf.pages]
            return pd.DataFrame({'Content': ["\n".join(text_data)]})
        except Exception as e:
            print(f"Error reading PDF file {self.file_path}: {str(e)}")
            return pd.DataFrame()

    def _load_docx(self) -> pd.DataFrame:
        """Read DOCX file and return a DataFrame."""
        try:
            doc = DocxDocument(self.file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            return pd.DataFrame({'Content': ["\n".join(paragraphs)]})
        except Exception as e:
            print(f"Error reading DOCX file {self.file_path}: {str(e)}")
            return pd.DataFrame()

    def _load_sql_file(self) -> pd.DataFrame:
        """Read SQL file, execute the queries, and return a DataFrame."""
        if not self.engine:
            raise ValueError("No engine available for executing SQL file.")
        try:
            with open(self.file_path, 'r') as file:
                sql_commands = file.read().split(';')
            with self.engine.connect() as conn:
                for command in sql_commands:
                    command = command.strip()
                    if command:
                        conn.execute(text(command))
                
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
                if tables:
                    table_name = tables[0][0]
                    return pd.read_sql(f"SELECT * FROM {table_name}", conn)
                else:
                    print(f"No tables found after executing SQL file {self.file_path}.")
                    return pd.DataFrame()
        except (SQLAlchemyError, IOError) as e:
            print(f"Error reading SQL file {self.file_path}: {str(e)}")
            return pd.DataFrame()

    def _load_sql_query(self) -> pd.DataFrame:
        """Execute a SQL query and return the result as a DataFrame."""
        connection_string, query = self._extract_sql_params(self.file_path)
        try:
            engine = create_engine(connection_string)
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error executing SQL query: {str(e)}")
            return pd.DataFrame()

    def _extract_sql_params(self, file_path: str) -> tuple[str, str]:
        """Extract SQL connection string and query from the file path."""
        # This is a placeholder implementation. You should customize this based on your needs.
        return 'sqlite:///example.db', 'SELECT * FROM table_name'

    def generate_sql(self, prompt: str) -> str:
        """Generate SQL code using LangChain based on a natural language prompt."""
        if not self.llm:
            raise ValueError("No LLM available for SQL generation.")
        response = self.llm(f"Generate SQL for the following request: {prompt}")
        return response.content.strip()

    def manage_database(self, management_prompt: str) -> str:
        """Generate and execute SQL for database management tasks."""
        if not self.engine:
            raise ValueError("No database connection available for management.")
        
        sql_code = self.generate_sql(management_prompt)
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql_code))
            return f"Executed SQL: {sql_code}"
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        """Execute a raw SQL query and return the result as a DataFrame."""
        if not self.engine:
            raise ValueError("No database connection available.")
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error executing SQL query: {str(e)}")
            return pd.DataFrame()