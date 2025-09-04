import os
import pandas as pd
from datetime import datetime

# --- 설정값 ---
DRIVE_LETTER = "D"
BASE_PATH = os.path.join(f"{DRIVE_LETTER}:/", "AI_Stock_Data")
DATA_PATH = os.path.join(BASE_PATH, "daily_price_fdr")
LOG_FILE_PATH = "fibonacci_screener_log.txt"

# 스캔할 기간 (거래일 기준)
LOOKBACK_PERIOD = 120 
# 주요 피보나치 레벨
FIB_LEVELS = [0.382, 0.618]
# 현재 주가가 레벨에 얼마나 근접해야 하는지 (오차 범위, %)
TOLERANCE = 1.0
# ----------------

# --- 로그 함수 ---
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
# --------------------

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    log(" Fibonacci Screener를 시작합니다...")
    
    # 데이터 폴더에 있는 모든 종목 파일을 가져옵니다.
    try:
        all_stock_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.csv')]
        log(f"✅ 총 {len(all_stock_files)}개 종목의 데이터를 확인했습니다.")
    except FileNotFoundError:
        log(f"❌ 데이터 폴더를 찾을 수 없습니다: {DATA_PATH}")
        exit()

    found_stocks = []
    total_files = len(all_stock_files)

    for i, file_name in enumerate(all_stock_files):
        stock_code = file_name.split('.')[0]
        if (i+1) % 100 == 0:
            log(f"    ... {i+1}/{total_files} 종목 스캔 중 ...")
            
        try:
            df = pd.read_csv(os.path.join(DATA_PATH, file_name))
            if len(df) < LOOKBACK_PERIOD:
                continue # 데이터가 너무 적으면 건너뜀

            # 최근 N일간의 데이터로 고점과 저점을 찾습니다.
            recent_df = df.tail(LOOKBACK_PERIOD)
            high_price = recent_df['high'].max()
            low_price = recent_df['low'].min()
            current_price = df['close'].iloc[-1]
            
            price_range = high_price - low_price
            if price_range == 0: continue

            # 각 피보나치 레벨을 확인합니다.
            for level in FIB_LEVELS:
                fib_price = high_price - price_range * level
                
                # 현재 주가가 피보나치 레벨 근처에 있는지 확인
                if abs(current_price - fib_price) / fib_price * 100 <= TOLERANCE:
                    log(f"🎯 종목 발견! [{stock_code}] 현재가({current_price:,.0f}원)가 {level*100:.1f}% 되돌림 레벨({fib_price:,.0f}원) 근처입니다.")
                    found_stocks.append({
                        'code': stock_code,
                        'level': f"{level*100:.1f}%",
                        'current_price': f"{current_price:,.0f}원",
                        'fib_price': f"{fib_price:,.0f}원"
                    })
                    break # 한 종목은 한 번만 추가

        except Exception as e:
            log(f"❌ {stock_code} 처리 중 오류 발생: {e}")

    log("\n--- [Fibonacci Screener 최종 결과] ---")
    if found_stocks:
        result_df = pd.DataFrame(found_stocks)
        log("피보나치 주요 레벨에 근접한 종목 리스트:")
        print(result_df.to_string())
    else:
        log("조건에 맞는 종목을 찾지 못했습니다.")