import pandas as pd
from typing import List, Union

class DataComparer:
    def __init__(self, dataframes: List[pd.DataFrame]):
        """Initialize the DataComparer with a list of DataFrames."""
        self.dataframes: List[pd.DataFrame] = dataframes

    def process_dataframes(self) -> Union[pd.DataFrame, str]:
        """Process the DataFrames and return a summary of their differences."""
        if len(self.dataframes) == 1:
            return self.dataframes[0]
        elif len(self.dataframes) < 2:
            raise ValueError("At least two DataFrames are required for comparison.")
        
        return self._compare_multiple_dataframes()

    def _compare_multiple_dataframes(self) -> str:
        """Compare multiple DataFrames and return a summary of their differences."""
        comparison_results: List[str] = []

        num_dfs = len(self.dataframes)
        for i in range(num_dfs):
            for j in range(i + 1, num_dfs):
                df1 = self.dataframes[i]
                df2 = self.dataframes[j]
                comparison_results.append(f"Comparing DataFrame {i + 1} with DataFrame {j + 1}:")
                comparison_results.append(self._compare_two_dataframes(df1, df2))
                comparison_results.append("\n")  # Add a newline between comparisons

        return "\n".join(comparison_results)

    def process_single_dataframe(self, df: pd.DataFrame) -> str:
        """Generate a summary for a single DataFrame."""
        if 'Content' in df.columns:
            return f"Single file content:\n{df['Content'].iloc[0]}"
        else:
            summary = [
                f"Single DataFrame shape: {df.shape}",
                f"Column names: {list(df.columns)}",
                f"Data preview:\n{df.head().to_string(index=False)}"
            ]
            return "\n".join(summary)

    def _compare_two_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame) -> str:
        """Compare two DataFrames and return a summary of their differences."""
        comparison_results: List[str] = []

        if 'Content' in df1.columns and 'Content' in df2.columns:
            comparison_results.extend(self._compare_text_content(df1, df2))
        else:
            comparison_results.extend(self._compare_tabular_content(df1, df2))

        return "\n".join(comparison_results)

    def _compare_text_content(self, df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
        """Compare text content of two DataFrames."""
        text1 = df1['Content'].iloc[0]
        text2 = df2['Content'].iloc[0]

        if text1 == text2:
            return ["No differences in text content."]
        else:
            return [
                "Differences found in text content.",
                f"File 1 Content:\n{text1}",
                f"File 2 Content:\n{text2}"
            ]

    def _compare_tabular_content(self, df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
        """Compare tabular content of two DataFrames."""
        df1_text = self._convert_dataframe_to_text(df1)
        df2_text = self._convert_dataframe_to_text(df2)

        if df1_text == df2_text:
            return ["No differences in tabular content."]
        else:
            return [
                "Differences found in tabular content.",
                f"File 1 Tabular Content:\n{df1_text}",
                f"File 2 Tabular Content:\n{df2_text}"
            ]

    @staticmethod
    def _convert_dataframe_to_text(df: pd.DataFrame) -> str:
        """Convert a DataFrame to a text representation."""
        return df.to_csv(index=False) if not df.empty else ""