# intelligent_trader.py
# 이 스크립트는 custom_analysis_report.txt 파일을 읽어
# 종목 특성별 최적의 전략을 학습한 후, 실제 거래 시뮬레이션을 실행합니다.

import os
import random
import re
import logging

def setup_logging():
    """
    스크립트 실행 과정을 로깅하도록 설정합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def get_optimal_strategies(report_file):
    """
    분석 보고서 파일에서 각 종목 특성별 최적 전략을 파싱하여 반환합니다.
    """
    strategies = {}
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_stock_type = None
        for line in lines:
            # 특성 그룹 헤더 찾기 (예: ✅ [HIGH VOLATILITY])
            stock_type_match = re.search(r'✅ \[(.*?)\].*', line)
            if stock_type_match:
                current_stock_type = stock_type_match.group(1).strip().replace(' ', '_').lower()
                # 이미 최적 전략을 찾았다면 건너뜀
                if current_stock_type in strategies:
                    current_stock_type = None
                    continue
                
                strategies[current_stock_type] = {}
                continue

            # 현재 특성 그룹에서 첫 번째 전략을 찾기
            if current_stock_type:
                strategy_match = re.search(r'전략: (.*)', line)
                if strategy_match:
                    strategy_string = strategy_match.group(1).strip()
                    param_match = re.search(r'종목특성_.*?_수익_(\d+)%_손절_(\d+)%_물타기_(.*)', strategy_string)
                    if param_match:
                        profit = int(param_match.group(1))
                        loss = int(param_match.group(2))
                        dca = param_match.group(3)
                        
                        # 첫 번째로 발견된 최적 전략만 저장
                        strategies[current_stock_type] = {
                            'profit': profit,
                            'loss': loss,
                            'dca': dca
                        }
                        current_stock_type = None # 다음 그룹으로 넘어가기 위해 초기화

    except FileNotFoundError:
        logging.error(f"오류: '{report_file}' 파일을 찾을 수 없습니다. 'custom_analyzer.py'를 먼저 실행하여 보고서를 생성해주세요.")
        return None
    except Exception as e:
        logging.error(f"오류: 보고서 파일을 파싱하는 중 문제가 발생했습니다. 에러: {e}")
        return None
        
    return strategies

def find_harmonic_patterns():
    """
    하모닉 패턴을 스캔하고 가장 신뢰할 수 있는 패턴을 반환합니다.
    """
    logging.info("➡️ 하모닉 패턴 스캔 중...")
    reliable_patterns = ["Gartley", "Crab"]
    
    # 데모를 위해 항상 패턴을 감지하도록 수정
    if True:
        pattern = random.choice(reliable_patterns)
        logging.info(f"✅ 신뢰할 수 있는 하모닉 패턴 감지: {pattern}")
        return pattern
    else:
        logging.info("❌ 신뢰할 수 있는 하모닉 패턴을 찾지 못했습니다. 다음 기회를 기다립니다.")
        return None

def execute_intelligent_trade(strategies):
    """
    학습된 지식과 하모닉 패턴을 기반으로 지능적인 거래를 시뮬레이션합니다.
    """
    stock_types = list(strategies.keys())
    if not stock_types:
        logging.error("분석된 전략 데이터가 없습니다. 실행을 종료합니다.")
        return False
        
    # 가상으로 한 종목의 특성을 무작위로 선택합니다.
    identified_type = random.choice(stock_types)
    optimal_strategy = strategies[identified_type]
    
    logging.info(f"--- 지능형 트레이더의 의사결정 시뮬레이션 ---")
    logging.info(f"✅ 시장 분석 완료: 현재 종목의 특성은 '{identified_type.upper().replace('_', ' ')}'입니다.")
    logging.info(f"📚 학습된 최적 전략 선택: {optimal_strategy}")

    # 1. 하모닉 패턴 스캔
    detected_pattern = find_harmonic_patterns()
    
    # 2. 패턴이 감지되지 않으면 거래를 실행하지 않고 종료
    if not detected_pattern:
        logging.info("\n지능형 트레이더 실행이 완료되었습니다.")
        return False
        
    # 3. 패턴이 감지되면 거래 실행
    print("\n🚀 전략 실행 중...")
    print(f"- 익절 목표: {optimal_strategy['profit']}%")
    print(f"- 손절 목표: {optimal_strategy['loss']}%")
    print(f"- 물타기: {optimal_strategy['dca']}")
    
    # 랜덤 성공/실패 시뮬레이션 (70% 확률로 성공)
    if random.random() < 0.7:
        print("\n🎉 거래 성공! 예상 수익률을 달성했습니다.")
        return True
    else:
        print("\n⚠️ 손절 조건에 도달했습니다. 거래를 종료합니다.")
        return False

if __name__ == "__main__":
    setup_logging()
    
    # 1. 보고서에서 최적 전략을 학습
    report_file_name = 'custom_analysis_report.txt'
    optimal_strategies = get_optimal_strategies(report_file_name)
    
    if optimal_strategies:
        # 2. 학습된 지식을 기반으로 거래 실행
        execute_intelligent_trade(optimal_strategies)
    
    logging.info("\n지능형 트레이더 실행이 완료되었습니다.")
