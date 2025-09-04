# result_analyzer.py (Class-based version)
# This script reads 'auto_backtest_final_report.txt', analyzes the performance
# of each strategy, and ranks them by Total Return.

import os
import pandas as pd
import re

class ResultAnalyzer:
    """
    Analyzes backtest results from a specified file.
    """
    def __init__(self, file_path):
        """
        Initializes the analyzer with the path to the report file.

        Args:
            file_path (str): The path to the backtest result file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Error: '{file_path}' not found. Please check if backtesting is complete.")
        self.file_path = file_path
        self.results = self._parse_results()

    def _parse_results(self):
        """
        Parses the report file to extract strategy performance data.
        This is a private method used internally.
        
        Returns:
            list: A list of dictionaries, each containing results for a strategy.
        """
        results_data = []
        pattern = re.compile(
            r"^(.*?) -> 총 수익률: ([\-\d\.]+)%, 승률: ([\d\.]+)%, MDD: ([\d\.]+)%"
        )
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = pattern.match(line.strip())
                    if match:
                        strategy, total_return, win_rate, mdd = match.groups()
                        results_data.append({
                            "전략": strategy,
                            "총 수익률(%)": float(total_return),
                            "승률(%)": float(win_rate),
                            "MDD(%)": float(mdd)
                        })
        except IOError as e:
            print(f"Error: An issue occurred while reading the file - {e}")
            return []
            
        return results_data

    def get_ranked_df(self):
        """
        Returns the backtest results as a pandas DataFrame, sorted by total return.

        Returns:
            pd.DataFrame: A sorted DataFrame of the backtest results.
        """
        if not self.results:
            return pd.DataFrame() # Return an empty DataFrame if no results
            
        df = pd.DataFrame(self.results)
        return df.sort_values(by="총 수익률(%)", ascending=False)

    def display_ranking(self):
        """
        Prints the ranked results in a formatted table.
        """
        if not self.results:
            print("No valid backtest results available to analyze.")
            return

        df_sorted = self.get_ranked_df()
        
        print("\n--- 백테스팅 전략 순위 (총 수익률 기준) ---")
        print(df_sorted.to_string(index=False))
        print("-------------------------------------------\n")


# This block allows the script to be run directly for testing.
if __name__ == "__main__":
    backtest_report_file = 'auto_backtest_final_report.txt'
    try:
        analyzer = ResultAnalyzer(backtest_report_file)
        analyzer.display_ranking()
    except FileNotFoundError as e:
        print(e)
