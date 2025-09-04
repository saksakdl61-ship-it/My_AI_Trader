# continuous_backtester.py
# 이 스크립트는 다양한 종목 특성을 고려하여 무한히 백테스팅을 실행하고
# 결과를 파일에 누적 기록합니다.

import os
import random
import time
import logging

def setup_logging():
    """
    스크립트 실행 과정을 로깅하도록 설정합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backtest_log.txt', mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def simulate_backtest(stock_type, strategy_name):
    """
    가상의 백테스팅을 시뮬레이션하고 결과를 반환합니다.
    종목 특성에 따라 결과가 달라지도록 조정합니다.
    """
    profit = 0.0
    win_rate = 0.0
    mdd = 0.0
    
    # 각 종목 특성에 따른 가상의 백테스팅 결과 시뮬레이션
    if stock_type == "high_volatility":
        profit = random.uniform(25, 40)
        win_rate = random.uniform(15, 30)
        mdd = random.uniform(30, 60)
    elif stock_type == "low_volatility":
        profit = random.uniform(10, 20)
        win_rate = random.uniform(30, 50)
        mdd = random.uniform(15, 30)
    elif stock_type == "stable":
        profit = random.uniform(15, 25)
        win_rate = random.uniform(20, 40)
        mdd = random.uniform(20, 40)
    elif stock_type == "growth":
        # 성장주는 높은 수익률과 변동성 시뮬레이션
        profit = random.uniform(30, 50)
        win_rate = random.uniform(10, 25)
        mdd = random.uniform(40, 70)
    elif stock_type == "dividend":
        # 배당주는 안정적인 수익률과 낮은 변동성 시뮬레이션
        profit = random.uniform(5, 15)
        win_rate = random.uniform(40, 60)
        mdd = random.uniform(5, 20)
    elif stock_type == "cyclical":
        # 경기민감주는 변동성이 크고 예측 불가능한 수익 시뮬레이션
        profit = random.uniform(-10, 30)
        win_rate = random.uniform(20, 50)
        mdd = random.uniform(30, 60)

    return profit, win_rate, mdd

def generate_and_log_backtest_result():
    """
    새로운 전략을 생성하고 백테스팅 후 결과를 파일에 기록합니다.
    """
    # 확장된 종목 특성 목록
    STOCK_TYPES = ["high_volatility", "low_volatility", "stable", "growth", "dividend", "cyclical"]
    
    # 전략 매개변수 생성
    profit_targets = [5, 10, 15, 20]
    stop_losses = [3, 5, 10]
    dollar_cost_averaging = ["없음", "5%", "10%", "15%"]

    stock_type = random.choice(STOCK_TYPES)
    profit = random.choice(profit_targets)
    loss = random.choice(stop_losses)
    dca = random.choice(dollar_cost_averaging)

    strategy_name = f"종목특성_{stock_type}_수익_{profit}%_손절_{loss}%_물타기_{dca}"
    
    logging.info(f"[{strategy_name}] 전략 백테스팅 시작...")
    
    # 가상 백테스팅 실행 (2~5초 소요)
    time.sleep(random.uniform(2, 5))
    
    # 결과 시뮬레이션
    total_profit, win_rate, mdd = simulate_backtest(stock_type, strategy_name)

    logging.info(f"[{strategy_name}] 백테스팅 완료!")
    
    report_entry = f" {strategy_name:<40} {total_profit:>10.2f} {win_rate:>10.2f} {mdd:>10.2f}\n"

    with open("auto_backtest_final_report.txt", "a", encoding="utf-8") as report_file:
        report_file.write(report_entry)
        
    logging.info(f"보고서에 [{strategy_name}] 결과 기록 완료.")
    
    return strategy_name

if __name__ == "__main__":
    setup_logging()
    
    try:
        logging.info("--- AI 자동 백테스팅 엔진 시작 (CTRL+C로 종료) ---")
        while True:
            generate_and_log_backtest_result()
            logging.info("다음 백테스팅 준비 중...")
            time.sleep(1) # 다음 실행까지 1초 대기
    except KeyboardInterrupt:
        logging.info("\n백테스팅 엔진을 종료합니다")
    except Exception as e:
        logging.error(f"오류 발생: {e}")
