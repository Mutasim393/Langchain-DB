import pandas as pd
from docx import Document as DocxDocument

class DataComparer:
    def __init__(self, df1, df2):
        self.df1 = df1
        self.df2 = df2

    def process_dataframes(self):
        """Compare two DataFrames and return a summary of their differences."""
        if self.df1 is None or self.df2 is None:
            return "No data available from one or both files."

        comparison_results = []

        # Compare the shapes of the DataFrames
        if self.df1.shape != self.df2.shape:
            comparison_results.append(f"The files have different shapes: {self.df1.shape} vs {self.df2.shape}")

        # Compare column names
        if list(self.df1.columns) != list(self.df2.columns):
            comparison_results.append("The files have different column names.")
            comparison_results.append(f"File 1 columns: {list(self.df1.columns)}")
            comparison_results.append(f"File 2 columns: {list(self.df2.columns)}")

        # Identify any differences in data
        differences = self.df1.compare(self.df2, align_axis=0, keep_shape=True, keep_equal=False)
        if differences.empty:
            comparison_results.append("No differences in data content.")
        else:
            comparison_results.append("Differences found in data:")
            comparison_results.append(differences.to_string(index=False))

        return "\n".join(comparison_results)