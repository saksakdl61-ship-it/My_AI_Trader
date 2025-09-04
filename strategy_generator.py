import random
import os
import logging
import time

def setup_logging():
    """
    전략 생성 과정을 로깅하도록 설정합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("strategy_generation_log.txt", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def generate_strategies(num_strategies, output_file):
    """
    다양한 변수 조합으로 새로운 전략을 생성하고 파일에 저장합니다.
    """
    logging.info(f"--- {num_strategies}개의 새로운 전략 생성 시작 ---")
    
    # 전략 매개변수 조합
    profit_targets = [5, 10, 15, 20, 25, 30]
    stop_losses = [2, 3, 5, 7, 10]
    dollar_cost_averages = ["없음", "5%", "10%", "15%", "20%"]
    stock_types = ["high_volatility", "low_volatility", "stable"]

    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(num_strategies):
            profit_target = random.choice(profit_targets)
            stop_loss = random.choice(stop_losses)
            dollar_cost_average = random.choice(dollar_cost_averages)
            stock_type = random.choice(stock_types)
            
            strategy_name = f"종목특성_{stock_type}_수익_{profit_target}%_손절_{stop_loss}%_물타기_{dollar_cost_average}"
            f.write(f"{strategy_name}\n")
            
            if (i + 1) % 50 == 0:
                logging.info(f"{i + 1}개의 전략이 생성되었습니다.")
    
    logging.info(f"--- {num_strategies}개의 전략 생성이 완료되었습니다. '{output_file}'에 저장됨 ---")

if __name__ == "__main__":
    setup_logging()
    output_file_name = "generated_strategies.txt"
    num_to_generate = 5000 # 한 번에 생성할 전략 수
    
    generate_strategies(num_to_generate, output_file_name)
    
    complete_message = f"🎉 모든 전략({num_to_generate}개) 생성이 완료되었습니다!\n새로운 전략들이 '{output_file_name}' 파일에 저장되었습니다."
    print(f"\n{complete_message}")
