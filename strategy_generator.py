import random
import os
import logging
import time

class StrategyGenerator:
    """
    다양한 변수 조합으로 새로운 전략을 생성하고 파일에 저장하는 클래스입니다.
    """
    def __init__(self, num_strategies=5000, output_file="generated_strategies.txt"):
        self.num_strategies = num_strategies
        self.output_file = output_file
        self.setup_logging()

    def setup_logging(self):
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

    def generate_strategies(self):
        """
        가상의 트레이딩 전략을 생성하고 파일에 저장합니다.
        """
        logging.info(f"--- {self.num_strategies}개의 새로운 전략 생성 시작 ---")
        
        # 전략 매개변수 조합
        profit_targets = [5, 10, 15, 20, 25, 30]
        stop_losses = [2, 3, 5, 7, 10]
        dollar_cost_averages = ["없음", "5%", "10%", "15%", "20%"]
        stock_types = ["high_volatility", "low_volatility", "stable"]

        with open(self.output_file, 'w', encoding='utf-8') as f:
            for i in range(self.num_strategies):
                profit_target = random.choice(profit_targets)
                stop_loss = random.choice(stop_losses)
                dollar_cost_average = random.choice(dollar_cost_averages)
                stock_type = random.choice(stock_types)
                
                strategy_name = f"종목특성_{stock_type}_수익_{profit_target}%_손절_{stop_loss}%_물타기_{dollar_cost_average}"
                f.write(f"{strategy_name}\n")
                
                # 진행 상황을 터미널에 실시간으로 표시
                if (i + 1) % 50 == 0:
                    percent_completed = (i + 1) / self.num_strategies * 100
                    print(f"✅ {i + 1}/{self.num_strategies} 전략 생성 완료 ({percent_completed:.1f}%)", flush=True)

        logging.info(f"--- {self.num_strategies}개의 전략 생성이 완료되었습니다. '{self.output_file}'에 저장됨 ---")
        
        complete_message = f"🎉 모든 전략({self.num_strategies}개) 생성이 완료되었습니다!\n새로운 전략들이 '{self.output_file}' 파일에 저장되었습니다."
        print(f"\n{complete_message}")
