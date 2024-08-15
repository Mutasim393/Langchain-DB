import pandas as pd
import tabula
import docx
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
        elif self.file_path.startswith('sql://'):  # Assuming SQL files start with a specific protocol
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
            df_list = tabula.read_pdf(self.file_path, pages='all', multiple_tables=True)
            return pd.concat(df_list, ignore_index=True)
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return None

    def load_docx(self):
        """Read DOCX file and return a DataFrame."""
        try:
            doc = docx.Document(self.file_path)
            data = []
            for table in doc.tables:
                keys = None
                for i, row in enumerate(table.rows):
                    text = [cell.text.strip() for cell in row.cells]
                    if i == 0:
                        keys = tuple(text)
                        continue
                    if keys:
                        row_data = dict(zip(keys, text))
                        data.append(row_data)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error reading DOCX file: {e}")
            return None

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
        # Example implementation: this function should be customized
        # according to how you store or pass SQL connection details.
        # For this example, we're just simulating with dummy values.
        # This part needs to be adapted based on your specific requirements.
        connection_string = 'sqlite:///example.db'  # Replace with your actual connection string
        query = 'SELECT * FROM table_name'  # Replace with your actual SQL query
        return connection_string, query