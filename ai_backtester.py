import os
os.environ["PYTHONUNBUFFERED"] = "1"
import pandas as pd
import pandas_ta as ta
import FinanceDataReader as fdr
from datetime import datetime
import numpy as np
import requests
import time
import configparser

# === 설정 파일 읽기 ===
config = configparser.ConfigParser()
config.read('config_home.ini')

try:
    BOT_TOKEN = config['API_KEYS']['TELEGRAM_BOT_TOKEN']
    CHAT_ID = config['API_KEYS']['TELEGRAM_CHAT_ID']
    BASE_PATH = config['PATHS']['BASE_PATH']
except KeyError:
    print("❌ config_home.ini 파일에서 설정값을 찾을 수 없습니다. 경로와 키 이름을 확인해주세요.")
    exit()

# === 경로 설정 ===
DATA_PATH = os.path.join(BASE_PATH, "daily_price_fdr")
LOG_FILE_PATH = "auto_backtester_log.txt"
REPORT_FILE_PATH = "auto_backtest_final_report.txt"

# === 전략 파라미터 조합 ===
STRATEGY_PARAMS = []
profit_targets = [0.10, 0.15, 0.20, 0.25]
stop_losses = [0.05, 0.10, 0.15]
dca_options = [None, 0.10, 0.15] # None: 물타기 없음

for pt in profit_targets:
    for sl in stop_losses:
        for dca in dca_options:
            name = f"전략: 수익률 {int(pt*100)}%, 손절율 {int(sl*100)}%, 물타기 {bool(dca)}"
            STRATEGY_PARAMS.append({'profit_target': pt, 'stop_loss': sl, 'buy_the_dip': dca, 'strategy_name': name})

# === 공통 설정 ===
INITIAL_CAPITAL = 10000000
FEE_RATE = 0.00015

# === 함수들 ===
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message, flush=True)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def send_telegram_message(text):
    max_length = 4000
    for i in range(0, len(text), max_length):
        chunk = text[i:i+max_length]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': chunk}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            log(f"❌ 텔레그램 메시지 발송 중 오류: {e}")
    log(f"✉️ 텔레그램 메시지 발송 완료: {text[:30]}...")

def calculate_fibonacci_levels(df_slice):
    high_price = df_slice['high'].max()
    low_price = df_slice['low'].min()
    price_range = high_price - low_price
    if price_range == 0: return {}
    return {
        'level_38.2%': high_price - price_range * 0.382,
        'level_61.8%': high_price - price_range * 0.618
    }

def run_backtest_strategy(df, params):
    capital = INITIAL_CAPITAL
    position = None
    trade_log = []
    capital_history = [INITIAL_CAPITAL]
    
    df.ta.rsi(append=True)
    df.ta.macd(append=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    for i in range(60, len(df)):
        current_price = df['close'].iloc[i]
        
        # 매수 조건
        if position is None:
            # 1. 피보나치 지지선 확인
            sub_df_for_fib = df.iloc[i-60:i]
            fib_levels = calculate_fibonacci_levels(sub_df_for_fib)
            is_fib_support = False
            for level_price in fib_levels.values():
                if level_price * 0.99 <= current_price <= level_price * 1.01:
                    is_fib_support = True
                    break
            
            # 2. 반등 신호 확인 (RSI 또는 MACD)
            rsi = df['RSI_14'].iloc[i]
            macd = df['MACD_12_26_9'].iloc[i]
            signal = df['MACDs_12_26_9'].iloc[i]
            prev_macd = df['MACD_12_26_9'].iloc[i-1]
            prev_signal = df['MACDs_12_26_9'].iloc[i-1]
            is_rebound = (rsi <= 35) or (prev_macd < prev_signal and macd > signal)

            if is_fib_support and is_rebound:
                quantity = (capital * (0.5 if params['buy_the_dip'] else 1.0)) // current_price
                if quantity > 0:
                    cost = current_price * quantity * (1 + FEE_RATE)
                    capital -= cost
                    position = {'price': current_price, 'quantity': quantity, 'dca_done': False}
        
        # 매도 및 물타기 로직
        elif position is not None:
            current_price = df['close'].iloc[i]
            profit_rate = (current_price - position['price']) / position['price']
            
            if profit_rate >= params['profit_target'] or profit_rate <= -params['stop_loss']:
                sell_value = current_price * position['quantity'] * (1 - FEE_RATE)
                capital += sell_value
                trade_log.append({'result': 'Win' if profit_rate >= 0 else 'Loss'})
                position = None
            elif params['buy_the_dip'] and not position['dca_done'] and profit_rate <= -params['buy_the_dip']:
                dca_quantity = capital // current_price
                if dca_quantity > 0:
                    dca_cost = dca_quantity * current_price * (1 + FEE_RATE)
                    capital -= dca_cost
                    total_quantity = position['quantity'] + dca_quantity
                    total_cost = (position['price'] * position['quantity']) + (current_price * dca_quantity)
                    position['price'] = total_cost / total_quantity
                    position['quantity'] = total_quantity
                    position['dca_done'] = True
        
        current_value = capital + (current_price * position['quantity'] if position else 0)
        capital_history.append(current_value)

    if position is not None: capital += df['close'].iloc[-1] * position['quantity']
    
    peak = np.maximum.accumulate(capital_history)
    drawdown = (peak - capital_history) / peak
    mdd = np.max(drawdown) * 100 if not np.all(peak == 0) else 0
    total_return = (capital / INITIAL_CAPITAL - 1) * 100
    win_count = sum(1 for t in trade_log if t.get('result') == 'Win')
    win_rate = (win_count / len(trade_log) * 100) if trade_log else 0
    
    return total_return, win_rate, mdd, len(trade_log)

def get_completed_tasks(file_path):
    completed = set()
    if not os.path.exists(file_path): return completed
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "전략:" in line and "->" in line:
                completed.add(line.split('->')[0].strip())
    return completed

if __name__ == "__main__":
    log("🚀 AI 비서 전략 자동 탐색기 (피보나치 강화 v1)를 시작합니다...")
    completed_tasks = get_completed_tasks(REPORT_FILE_PATH)
    log(f"✅ 총 {len(completed_tasks)}개의 기존 전략 결과를 확인했습니다.")
    
    try:
        stock_list_df = fdr.StockListing('KRX')
        if 'Code' in stock_list_df.columns:
            stock_list_df.rename(columns={'Code': 'Symbol'}, inplace=True)
        stock_codes = stock_list_df[stock_list_df['Symbol'].str.match(r'^\d{6}$')]['Symbol'].tolist()
        log(f"✅ 총 {len(stock_codes)}개 종목 리스트를 불러왔습니다.")
    except Exception as e:
        log(f"❌ 종목 리스트 로딩 실패: {e}")
        exit()

    with open(REPORT_FILE_PATH, "a", encoding="utf-8") as report:
        for strategy in STRATEGY_PARAMS:
            if strategy['strategy_name'] in completed_tasks:
                log(f"이미 완료된 전략: '{strategy['strategy_name']}' ... 건너뜁니다.")
                continue

            log(f"\n--- {strategy['strategy_name']} 백테스팅을 시작합니다. ---")
            results = []
            for i, code in enumerate(stock_codes):
                if (i+1) % 100 == 0: log(f"    ... {i+1}/{len(stock_codes)} 종목 처리 중 ...")
                file_path = os.path.join(DATA_PATH, f"{code}.csv")
                if not os.path.exists(file_path): continue

                try:
                    df = pd.read_csv(file_path)
                    df['date'] = pd.to_datetime(df['date'].astype(str), errors='coerce')
                    df.dropna(subset=['date'], inplace=True)
                    df.set_index('date', inplace=True)
                    if len(df) < 100: continue
                    
                    total_return, win_rate, mdd, num_trades = run_backtest_strategy(df.copy(), strategy)
                    
                    if num_trades > 0:
                        results.append({'return': total_return, 'win_rate': win_rate, 'mdd': mdd})
                except Exception as e:
                    log(f"❌ {code} 백테스팅 중 오류: {e}")

            if results:
                result_df = pd.DataFrame(results)
                avg_return = result_df['return'].mean()
                avg_win_rate = result_df['win_rate'].mean()
                avg_mdd = result_df['mdd'].mean()
                
                result_line = (f"{strategy['strategy_name']} -> "
                               f"총 수익률: {avg_return:.2f}%, "
                               f"승률: {avg_win_rate:.2f}%, "
                               f"MDD: {avg_mdd:.2f}%\n")
                report.write(result_line)
                report.flush()
                
    final_report_text = f"🎉 모든 백테스팅 완료! 최종 결과는 '{REPORT_FILE_PATH}' 파일에 저장되었습니다."
    log(final_report_text)
    send_telegram_message(final_report_text)
