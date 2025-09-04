import os
import pandas as pd
import pandas_ta as ta
import random
import numpy as np
from datetime import datetime

# --- 설정값 ---
DRIVE_LETTER = "D"
BASE_PATH = os.path.join(f"{DRIVE_LETTER}:/", "AI_Stock_Data")
DATA_PATH = os.path.join(BASE_PATH, "daily_price_fdr")
REPORT_FILE_PATH = "evolution_report.txt" 
LOG_FILE_PATH = "evolution_log.txt"
INITIAL_CAPITAL = 10000000
FEE_RATE = 0.00015
# ----------------

# --- 로그 함수 ---
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
# --------------------

# --- 유전자 풀 및 전략 생성 함수 ---
buy_conditions = [
    "rsi < 35",
    "macd > macd_signal",
    "close > open", # 양봉
]
sell_conditions = [
    "rsi > 65",
    "macd < macd_signal",
]
def create_random_strategy():
    strategy = {'buy': [], 'sell': []}
    strategy['buy'] = random.sample(buy_conditions, random.randint(1, 2))
    strategy['sell'] = random.sample(sell_conditions, 1)
    return strategy
# ---------------------------------

# --- (<<<< 여기가 완전히 새로 재설계되었습니다!) ---
# '하루씩' 판단하는 새로운 백테스팅 엔진
def run_backtest_for_strategy(df, strategy):
    capital = INITIAL_CAPITAL
    position = None
    
    # 1. 모든 컬럼 이름을 소문자로 통일
    df.columns = [col.lower() for col in df.columns]
    
    # 2. 보조지표 계산
    df.ta.rsi(append=True)
    df.ta.macd(append=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # 3. 보조지표 이름도 소문자로 통일
    df.columns = [col.lower() for col in df.columns]

    for i in range(1, len(df)):
        # 현재 날짜의 데이터만 가져옴
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # 유전자(조건)를 하나씩 평가
        buy_signal = True
        for condition in strategy['buy']:
            if 'rsi' in condition and not (row['rsi_14'] < 35): buy_signal = False
            if 'macd' in condition and not (row['macd_12_26_9'] > row['macds_12_26_9']): buy_signal = False
            if 'close > open' in condition and not (row['close'] > row['open']): buy_signal = False
        
        sell_signal = True
        for condition in strategy['sell']:
            if 'rsi' in condition and not (row['rsi_14'] > 65): sell_signal = False
            if 'macd' in condition and not (row['macd_12_26_9'] < row['macds_12_26_9']): sell_signal = False

        if position is None and buy_signal:
            buy_price = row['close']
            quantity = capital // buy_price
            if quantity > 0:
                capital -= buy_price * quantity * (1 + FEE_RATE)
                position = {'price': buy_price, 'quantity': quantity}
        
        elif position is not None and sell_signal:
            sell_price = row['close']
            capital += sell_price * position['quantity'] * (1 - FEE_RATE)
            position = None

    if position is not None:
        capital += df['close'].iloc[-1] * position['quantity']
        
    return (capital / INITIAL_CAPITAL - 1) * 100
# --------------------------------------------

# --- 메인 실행 부분 (이전과 동일) ---
if __name__ == "__main__":
    log("🧬 '전략 진화' 프로그램을 시작합니다.")
    population_size = 20
    population = [create_random_strategy() for _ in range(population_size)]
    log(f"\n--- [1세대 초기 전략 {population_size}개 생성 완료] ---")
    try:
        stock_df = pd.read_csv(os.path.join(DATA_PATH, "005930.csv"))
        log("\n--- [삼성전자 데이터로 백테스팅 시작] ---")
    except FileNotFoundError:
        log("\n❌ '005930.csv' 파일을 찾을 수 없습니다. D드라이브 경로를 확인해주세요.")
        exit()
    strategy_scores = []
    with open(REPORT_FILE_PATH, "w", encoding="utf-8") as report:
        report.write(f"=== AI 자동 생성 전략 백테스팅 리포트 ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
        report.write("테스트 종목: 005930 (삼성전자)\n\n")
        for i, strategy in enumerate(population):
            strategy_desc = f"매수: {' & '.join(strategy['buy'])} | 매도: {' & '.join(strategy['sell'])}"
            log(f"\n[전략 {i+1}/{population_size} 테스트 중] {strategy_desc}")
            try:
                score = run_backtest_for_strategy(stock_df.copy(), strategy)
                strategy_scores.append({'strategy': strategy_desc, 'score': score})
                log(f"  -> 결과 점수(수익률): {score:.2f}%")
                report.write(f"전략 {i+1}: {strategy_desc}\n")
                report.write(f"  -> 수익률: {score:.2f}%\n\n")
            except Exception as e:
                log(f"  -> ❌ 테스트 중 오류 발생: {e}")
                report.write(f"전략 {i+1}: {strategy_desc}\n")
                report.write(f"  -> 오류 발생: {e}\n\n")
            report.flush()
    valid_scores = [s for s in strategy_scores if 'score' in s]
    if valid_scores:
        winner = sorted(valid_scores, key=lambda x: x['score'], reverse=True)[0]
        final_report_summary = "\n--- [1세대 적자생존 경쟁 결과] ---\n"
        final_report_summary += "🏆 최고의 전략이 탄생했습니다!\n"
        final_report_summary += f"  - 전략 내용: {winner['strategy']}\n"
        final_report_summary += f"  - 최종 점수(수익률): {winner['score']:.2f}%\n"
        log(final_report_summary)
        with open(REPORT_FILE_PATH, "a", encoding="utf-8") as report:
            report.write(final_report_summary)