import pandas as pd
import docx
import pdfplumber
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langchain_openai import ChatOpenAI

class FileHandler:
    def __init__(self, file_path=None, connection_string=None):
        self.file_path = file_path
        self.connection_string = connection_string
        self.engine = self.create_sqlite_engine() if not connection_string and file_path and file_path.endswith('.sql') else create_engine(connection_string) if connection_string else None
        self.df = self.load_file() if file_path else None
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3) if self.engine else None

    def create_sqlite_engine(self):
        """Create an SQLite in-memory engine for testing SQL files."""
        return create_engine('sqlite:///:memory:')

    def load_file(self):
        """Load file based on its extension and return a DataFrame."""
        if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
            return self.load_excel()
        elif self.file_path.endswith('.csv'):
            return self.load_csv()
        elif self.file_path.endswith('.pdf'):
            return self.load_pdf()
        elif self.file_path.endswith('.docx'):
            return self.load_docx()
        elif self.file_path.endswith('.sql'):
            return self.load_sql_file()
        elif self.file_path.startswith('sql://'):
            connection_string, query = self.extract_sql_params(self.file_path)
            return self.load_sql(connection_string, query)
        else:
            raise ValueError(f"Unsupported file type: {self.file_path}")

    def load_excel(self):
        """Read Excel file and return a DataFrame."""
        try:
            return pd.read_excel(self.file_path)
        except Exception as e:
            print(f"Error reading Excel file {self.file_path}: {e}")
            return pd.DataFrame()

    def load_csv(self):
        """Read CSV file and return a DataFrame."""
        try:
            return pd.read_csv(self.file_path)
        except Exception as e:
            print(f"Error reading CSV file {self.file_path}: {e}")
            return pd.DataFrame()

    def load_pdf(self):
        """Read PDF file and return a DataFrame."""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text_data = [page.extract_text() for page in pdf.pages]
            return pd.DataFrame({'Content': ["\n".join(text_data)]})
        except Exception as e:
            print(f"Error reading PDF file {self.file_path}: {e}")
            return pd.DataFrame()

    def load_docx(self):
        """Read DOCX file and return a DataFrame."""
        try:
            doc = docx.Document(self.file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            return pd.DataFrame({'Content': ["\n".join(paragraphs)]})
        except Exception as e:
            print(f"Error reading DOCX file {self.file_path}: {e}")
            return pd.DataFrame()

    def load_sql_file(self):
        """Read SQL file, execute the queries, and return a DataFrame."""
        if not self.engine:
            raise ValueError("No engine available for executing SQL file.")
        try:
            with open(self.file_path, 'r') as file:
                sql_commands = file.read().split(';')  # Split the SQL file into individual statements
            with self.engine.connect() as conn:
                for command in sql_commands:
                    command = command.strip()
                    if command:  # Only execute non-empty commands
                        conn.execute(text(command))
                
                # After executing the SQL, fetch the data from the created table(s)
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
                if tables:
                    table_name = tables[0][0]  # Assuming there's at least one table
                    return pd.read_sql(f"SELECT * FROM {table_name}", conn)
                else:
                    print(f"No tables found after executing SQL file {self.file_path}.")
                    return pd.DataFrame()
        except (SQLAlchemyError, IOError) as e:
            print(f"Error reading SQL file {self.file_path}: {e}")
            return pd.DataFrame()

    def extract_sql_params(self, file_path):
        """Extract SQL connection string and query from the file path."""
        # Customize this to extract actual connection string and query if embedded in the path
        connection_string = 'sqlite:///example.db'
        query = 'SELECT * FROM table_name'
        return connection_string, query

    def generate_sql(self, prompt):
        """Generate SQL code using LangChain based on a natural language prompt."""
        if not self.llm:
            raise ValueError("No LLM available for SQL generation.")
        response = self.llm(f"Generate SQL for the following request: {prompt}")
        return response.content.strip()

    def manage_database(self, management_prompt):
        """Generate and execute SQL for database management tasks (e.g., creating tables, modifying schemas)."""
        if not self.engine:
            raise ValueError("No database connection available for management.")
        
        sql_code = self.generate_sql(management_prompt)
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql_code))
            return f"Executed SQL: {sql_code}"
        except Exception as e:
            return f"Error executing SQL: {e}"

    def execute_sql_query(self, query):
        """Execute a raw SQL query and return the result as a DataFrame."""
        if not self.engine:
            raise ValueError("No database connection available.")
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            return pd.DataFrame()
