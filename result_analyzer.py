# result_analyzer.py
# 이 스크립트는 'auto_backtest_final_report.txt' 파일을 읽어 각 전략의 성과를 분석하고,
# 총수익률(Total Return)이 높은 순서대로 순위를 매겨 표로 출력합니다.

import os
import pandas as pd
import re

def analyze_backtest_results(file_path):
    """
    백테스팅 결과를 분석하고 순위를 매겨 출력하는 함수.
    
    Args:
        file_path (str): 백테스팅 결과 파일의 경로.
    """
    
    # 파일이 존재하는지 확인합니다.
    if not os.path.exists(file_path):
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 백테스팅이 진행 중인지 확인해주세요.")
        return

    # 결과를 저장할 리스트를 초기화합니다.
    results = []
    pattern = re.compile(
        r"^(.*?) -> 총 수익률: ([\-\d\.]+)%, 승률: ([\d\.]+)%, MDD: ([\d\.]+)%"
    )

    try:
        # 파일을 읽고 각 줄을 분석합니다.
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    strategy = match.group(1)
                    total_return = float(match.group(2))
                    win_rate = float(match.group(3))
                    mdd = float(match.group(4))
                    results.append({
                        "전략": strategy,
                        "총 수익률(%)": total_return,
                        "승률(%)": win_rate,
                        "MDD(%)": mdd
                    })
    except IOError as e:
        print(f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}")
        return

    # Pandas DataFrame으로 변환하여 데이터 처리를 용이하게 합니다.
    if not results:
        print("분석할 유효한 백테스팅 결과가 없습니다.")
        return
        
    df = pd.DataFrame(results)
    
    # 총수익률이 높은 순서대로 정렬합니다.
    df_sorted = df.sort_values(by="총 수익률(%)", ascending=False)
    
    # 보기 좋은 표 형태로 출력합니다.
    print("\n--- 백테스팅 전략 순위 (총 수익률 기준) ---")
    print(df_sorted.to_string(index=False))
    print("-------------------------------------------\n")


if __name__ == "__main__":
    backtest_report_file = 'auto_backtest_final_report.txt'
    analyze_backtest_results(backtest_report_file)
