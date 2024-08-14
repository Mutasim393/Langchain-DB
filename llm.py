from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize the ChatOpenAI model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
)

def read_excel_file(file_path):
    """Read Excel file and return a DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def process_dataframes(df1, df2):
    """Compare two DataFrames and return a summary of their differences."""
    if df1 is None or df2 is None:
        return "No data available from one or both files."

    comparison_results = []

    # Compare the shapes of the DataFrames
    if df1.shape != df2.shape:
        comparison_results.append(f"The files have different shapes: {df1.shape} vs {df2.shape}")

    # Compare column names
    if list(df1.columns) != list(df2.columns):
        comparison_results.append("The files have different column names.")
        comparison_results.append(f"File 1 columns: {list(df1.columns)}")
        comparison_results.append(f"File 2 columns: {list(df2.columns)}")

    # Identify any differences in data
    differences = df1.compare(df2, align_axis=0, keep_shape=True, keep_equal=False)
    if differences.empty:
        comparison_results.append("No differences in data content.")
    else:
        comparison_results.append("Differences found in data:")
        comparison_results.append(differences.to_string(index=False))

    return "\n".join(comparison_results)

def ask_question_about_comparison(file_path1, file_path2, question):
    """Read the Excel files, compare them, and ask a question using LangChain."""
    df1 = read_excel_file(file_path1)
    df2 = read_excel_file(file_path2)
    comparison_summary = process_dataframes(df1, df2)
    
    # Combine the comparison summary and the question
    prompt = f"Comparison Summary:\n{comparison_summary}\n\nQuestion: {question}\nAnswer:"
    
    # Stream the response
    response = llm.stream([prompt])
    
    # Print the response
    for chunk in response:
        print(chunk.content, end="", flush=True)

file_path1 = "C:\\Users\\Sam\\Desktop\\db 1.xlsx"
file_path2 = "C:\\Users\\Sam\\Desktop\\db 2.xlsx"
question = "What is the country with the lowest population?"

ask_question_about_comparison(file_path1, file_path2, question)