import random
import time
import os
import logging

def setup_logging():
    """
    백테스팅 과정의 로그를 콘솔과 파일에 기록하도록 설정합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("backtest_log.txt", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def generate_random_strategy():
    """
    다양한 변수 조합과 종목 특성으로 새로운 전략을 무작위로 생성합니다.
    """
    # 수익률, 손절률, 물타기 옵션의 다양한 조합
    profit_targets = [5, 10, 15, 20]
    stop_losses = [3, 5, 10]
    dollar_cost_averages = ["없음", "5%", "10%", "15%"]
    
    # 종목 특성을 추가하여 다변화
    stock_types = ["high_volatility", "low_volatility", "stable"]
    
    profit_target = random.choice(profit_targets)
    stop_loss = random.choice(stop_losses)
    dollar_cost_average = random.choice(dollar_cost_averages)
    stock_type = random.choice(stock_types)
    
    strategy_name = f"종목특성_{stock_type}_수익_{profit_target}%_손절_{stop_loss}%_물타기_{dollar_cost_average}"
    
    return {
        "name": strategy_name,
        "profit_target": profit_target,
        "stop_loss": stop_loss,
        "dollar_cost_average": dollar_cost_average,
        "stock_type": stock_type
    }

def run_backtest_simulation(strategy):
    """
    주어진 전략과 종목 특성에 따라 가상의 백테스팅을 실행하고 결과를 반환합니다.
    """
    logging.info(f"[{strategy['name']}] 전략 백테스팅 시작...")
    
    # 종목 특성에 따라 결과에 영향을 줍니다.
    if strategy["stock_type"] == "high_volatility":
        total_return = round((strategy["profit_target"] * 1.5) - (strategy["stop_loss"] * 0.8) + random.uniform(-10, 10), 2)
        win_rate = round(20 + (10 - strategy["stop_loss"]) * 2 + random.uniform(-5, 5), 2)
        mdd = round(70 - (strategy["stop_loss"] * 1.5) + random.uniform(-10, 10), 2)
    elif strategy["stock_type"] == "low_volatility":
        total_return = round((strategy["profit_target"] * 0.8) - (strategy["stop_loss"] * 0.5) + random.uniform(-3, 3), 2)
        win_rate = round(60 + (10 - strategy["stop_loss"]) * 1.5 + random.uniform(-5, 5), 2)
        mdd = round(30 - (strategy["stop_loss"] * 1.2) + random.uniform(-5, 5), 2)
    else: # stable
        total_return = round((strategy["profit_target"] * 1.0) - (strategy["stop_loss"] * 0.6) + random.uniform(-5, 5), 2)
        win_rate = round(50 + (10 - strategy["stop_loss"]) * 2 + random.uniform(-10, 10), 2)
        mdd = round(50 - (strategy["stop_loss"] * 1.0) - random.uniform(-5, 5), 2)

    # 5초 정도의 백테스팅 시간을 시뮬레이션
    time.sleep(random.uniform(3, 7))
    
    logging.info(f"[{strategy['name']}] 백테스팅 완료!")
    
    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "mdd": mdd
    }

def save_report(report_file, strategy_name, total_return, win_rate, mdd):
    """
    백테스팅 결과를 파일에 추가합니다.
    """
    with open(report_file, 'a', encoding='utf-8') as f:
        f.write(f"전략: {strategy_name}, 총 수익률(%): {total_return}, 승률(%): {win_rate}, MDD(%): {mdd}\n")
    logging.info(f"보고서에 [{strategy_name}] 결과 기록 완료.")

if __name__ == "__main__":
    setup_logging()
    report_file = "auto_backtest_final_report.txt"
    
    # 보고서 파일이 없으면 새로 생성
    if not os.path.exists(report_file):
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("--- 자동 생성 백테스팅 최종 보고서 ---\n\n")

    logging.info("--- AI 자동 백테스팅 엔진 시작 (CTRL+C로 종료) ---")

    while True:
        try:
            # 1. 새로운 전략 생성
            new_strategy = generate_random_strategy()
            
            # 2. 백테스팅 시뮬레이션 실행
            results = run_backtest_simulation(new_strategy)
            
            # 3. 결과 보고서에 기록
            save_report(
                report_file, 
                new_strategy["name"], 
                results["total_return"], 
                results["win_rate"], 
                results["mdd"]
            )
            
            logging.info("다음 백테스팅 준비 중...")
            time.sleep(1) # 다음 실행까지 잠시 대기
            
        except KeyboardInterrupt:
            logging.info("\n백테스팅 엔진을 종료합니다.")
            break
        except Exception as e:
            logging.error(f"오류 발생: {e}. 다시 시작합니다.")
            time.sleep(2)
