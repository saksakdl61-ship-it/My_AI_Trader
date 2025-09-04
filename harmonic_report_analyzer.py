# harmonic_report_analyzer.py
# 이 스크립트는 harmonic_scanner.py가 생성한 리포트 파일을 읽고,
# 하모닉 패턴의 통계 데이터를 분석하여 결과를 보기 쉽게 정리해 출력합니다.

import os
import re

def analyze_report(file_path):
    """
    하모닉 패턴 리포트 파일을 읽어 분석하고 결과를 출력합니다.

    Args:
        file_path (str): 분석할 리포트 파일의 경로.
    """
    if not os.path.exists(file_path):
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. harmonic_scanner.py를 먼저 실행하여 리포트를 생성하세요.")
        return

    print("--- 하모닉 패턴 리포트 분석 ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"오류: '{file_path}' 파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    pattern_data = {}
    
    # 정규 표현식으로 전체 분석 횟수와 성공률을 추출합니다.
    total_analyzed_match = re.search(r"총 분석된 패턴 횟수:\s*(\d+)", content)
    total_analyzed = int(total_analyzed_match.group(1)) if total_analyzed_match else 0
    overall_rate_match = re.search(r"전체 패턴 성공률:\s*(.*)", content)
    overall_rate = overall_rate_match.group(1) if overall_rate_match else "N/A"
    
    print(f"전체 패턴 성공률: {overall_rate}")

    # 모든 패턴 데이터를 정규 표현식으로 한 번에 추출합니다.
    pattern_matches = re.findall(
        r'-\s*(.*?):\n\s*- 성공률:\s*(.*?)\n\s*- 성공 횟수:\s*(\d+)\n\s*- 총 횟수:\s*(\d+)',
        content,
        re.MULTILINE
    )

    if not pattern_matches:
        print("경고: 리포트 파일에서 유효한 패턴 데이터를 찾을 수 없습니다.")
        return
    
    for match in pattern_matches:
        pattern_name = match[0]
        success_rate = match[1]
        success_count = int(match[2])
        total_count = int(match[3])
        
        pattern_data[pattern_name] = {
            '성공률': success_rate,
            '성공 횟수': success_count,
            '총 횟수': total_count
        }
        
    print("-" * 35)
    print("패턴별 분석 결과 (성공률 높은 순):")
    
    # 성공률을 기준으로 패턴 데이터를 내림차순 정렬합니다.
    sorted_patterns = sorted(
        pattern_data.items(),
        key=lambda item: float(item[1]['성공률'].replace('%', '')),
        reverse=True
    )
    
    # 정렬된 데이터를 표 형태로 출력합니다.
    print(f"{'패턴':<15}{'성공률':<10}{'성공 횟수':<10}{'총 횟수':<10}")
    print("-" * 45)
    for pattern, stats in sorted_patterns:
        print(
            f"{pattern:<15}{stats['성공률']:<10}{stats['성공 횟수']:<10}{stats['총 횟수']:<10}"
        )
    print("-" * 45)
    print(f"총 분석된 패턴 횟수: {total_analyzed}")
    print("분석이 완료되었습니다.")


if __name__ == "__main__":
    report_file = "harmonic_scanner_report.txt"
    sample_report_content = """
--- 하모닉 패턴 통계적 확률 계산 결과 ---
총 분석된 패턴 횟수: 15
-----------------------------------
전체 패턴 성공률: 66.67%
-----------------------------------
패턴별 성공률:
  - Gartley:
    - 성공률: 75.00%
    - 성공 횟수: 3
    - 총 횟수: 4
  - Butterfly:
    - 성공률: 50.00%
    - 성공 횟수: 2
    - 총 횟수: 4
  - Crab:
    - 성공률: 75.00%
    - 성공 횟수: 3
    - 총 횟수: 4
  - Bat:
    - 성공률: 33.33%
    - 성공 횟수: 1
    - 총 횟수: 3
-----------------------------------
분석이 완료되었습니다.
"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(sample_report_content)
        
    analyze_report(report_file)
