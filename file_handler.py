import pandas as pd
import tabula
import docx
import pdfplumber
from sqlalchemy import create_engine

class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self.load_file()

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
        elif self.file_path.startswith('sql://'):
            connection_string, query = self.extract_sql_params(self.file_path)
            return self.load_sql(connection_string, query)
        else:
            raise ValueError(f"Unsupported file type: {self.file_path}")

    def load_excel(self):
        """Read Excel file and return a DataFrame."""
        try:
            df = pd.read_excel(self.file_path)
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None

    def load_csv(self):
        """Read CSV file and return a DataFrame."""
        try:
            df = pd.read_csv(self.file_path)
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def load_pdf(self):
        """Read PDF file and return a DataFrame."""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text_data = []
                for page in pdf.pages:
                    text_data.append(page.extract_text())
            text_combined = "\n".join(text_data)
            return pd.DataFrame({'Content': [text_combined]})
        except Exception as e:
            print(f"Error reading PDF file {self.file_path}: {e}")
            return pd.DataFrame()

    def load_docx(self):
        """Read DOCX file and return a DataFrame."""
        try:
            doc = docx.Document(self.file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            text_combined = "\n".join(paragraphs)
            return pd.DataFrame({'Content': [text_combined]})
        except Exception as e:
            print(f"Error reading DOCX file: {e}")
            return pd.DataFrame()

    def load_sql(self, connection_string, query):
        """Read SQL database and return a DataFrame."""
        try:
            engine = create_engine(connection_string)
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error reading SQL data: {e}")
            return None

    def extract_sql_params(self, file_path):
        """Extract SQL connection string and query from the file path."""
        connection_string = 'sqlite:///example.db'
        query = 'SELECT * FROM table_name'
        return connection_string, query