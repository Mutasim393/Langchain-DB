import pandas as pd
from docx import Document as DocxDocument

class DataComparer:
    def __init__(self, dataframes):
        """Initialize the DataComparer with a list of DataFrames."""
        self.dataframes = dataframes

    def process_dataframes(self):
        """Process the DataFrames and return a summary of their differences."""
        if len(self.dataframes) == 1:
            # Handle the single DataFrame scenario
            return self.process_single_dataframe(self.dataframes[0])
        elif len(self.dataframes) < 2:
            raise ValueError("At least two DataFrames are required for comparison.")
        
        # Handle multiple DataFrames comparison
        return self.compare_multiple_dataframes()

    def compare_multiple_dataframes(self):
        """Compare multiple DataFrames and return a summary of their differences."""
        comparison_results = []

        num_dfs = len(self.dataframes)
        for i in range(num_dfs):
            for j in range(i + 1, num_dfs):
                df1 = self.dataframes[i]
                df2 = self.dataframes[j]
                comparison_results.append(f"Comparing DataFrame {i + 1} with DataFrame {j + 1}:")
                comparison_results.append(self._compare_two_dataframes(df1, df2))
                comparison_results.append("\n")  # Add a newline between comparisons

        return "\n".join(comparison_results)

    def process_single_dataframe(self, df):
        """Generate a summary for a single DataFrame."""
        if 'Content' in df.columns:
            # Handle text content in a single DataFrame
            return f"Single file content:\n{df['Content'].iloc[0]}"
        else:
            # Handle tabular data in a single DataFrame
            summary = []
            summary.append(f"Single DataFrame shape: {df.shape}")
            summary.append(f"Column names: {list(df.columns)}")
            summary.append(f"Data preview:\n{df.head().to_string(index=False)}")
            return "\n".join(summary)

    def _compare_two_dataframes(self, df1, df2):
        """Compare two DataFrames and return a summary of their differences."""
        comparison_results = []

        if 'Content' in df1.columns and 'Content' in df2.columns:
            # Both DataFrames contain text content
            text1 = df1['Content'].iloc[0]
            text2 = df2['Content'].iloc[0]

            if text1 == text2:
                comparison_results.append("No differences in text content.")
            else:
                comparison_results.append("Differences found in text content.")
                comparison_results.append(f"File 1 Content:\n{text1}")
                comparison_results.append(f"File 2 Content:\n{text2}")
        else:
            # Convert tabular DataFrames to text before comparison
            df1_text = self.convert_dataframe_to_text(df1)
            df2_text = self.convert_dataframe_to_text(df2)

            if df1_text == df2_text:
                comparison_results.append("No differences in tabular content.")
            else:
                comparison_results.append("Differences found in tabular content.")
                comparison_results.append(f"File 1 Tabular Content:\n{df1_text}")
                comparison_results.append(f"File 2 Tabular Content:\n{df2_text}")

        return "\n".join(comparison_results)

    def convert_dataframe_to_text(self, df):
        """Convert a DataFrame to a text representation."""
        if df.empty:
            return ""
        # Convert the DataFrame to CSV format as a string
        return df.to_csv(index=False)
