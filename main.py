from file_handler import FileHandler
from comparison import DataComparer
from query_handler import QueryHandler

def main(file_path1, file_path2, question):
    # Initialize FileHandlers
    handler1 = FileHandler(file_path1)
    handler2 = FileHandler(file_path2)

    # Get DataFrames
    df1 = handler1.df
    df2 = handler2.df

    # Initialize DataComparer
    comparer = DataComparer(df1, df2)
    comparison_summary = comparer.process_dataframes()

    # Initialize QueryHandler
    query_handler = QueryHandler()
    response = query_handler.ask_question(comparison_summary, question)

    print(response)

if __name__ == "__main__":
    file_path1 = "C:\\Users\\Sam\\Desktop\\db 1.xlsx"
    file_path2 = "C:\\Users\\Sam\\Desktop\\db 2.xlsx"
    question = "what are the ratios you can calculate for Japan?"

    main(file_path1, file_path2, question)