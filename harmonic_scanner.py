import os
import pandas as pd
from datetime import datetime

# --- 설정값 ---
DRIVE_LETTER = "D"
BASE_PATH = os.path.join(f"{DRIVE_LETTER}:/", "AI_Stock_Data")
DATA_PATH = os.path.join(BASE_PATH, "daily_price_fdr")
# (<<<< 여기가 추가되었습니다!)
# 로그 파일과 결과 보고서 파일을 별도로 관리합니다.
LOG_FILE_PATH = "harmonic_scanner_log.txt"
REPORT_FILE_PATH = "harmonic_scan_report.txt" 

SWING_WINDOW = 5
TOLERANCE = 0.05 
PROB_CHECK_DAYS = 20
PROB_TARGET_PROFIT = 5
# ----------------

# --- 로그 함수 ---
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
# --------------------

# --- (핵심 기능 함수들은 이전과 동일합니다) ---
def find_swing_points(df):
    swings = []
    for i in range(SWING_WINDOW, len(df) - SWING_WINDOW):
        window = df.iloc[i - SWING_WINDOW : i + SWING_WINDOW + 1]
        if df['high'].iloc[i] == window['high'].max():
            swings.append({'type': 'H', 'index': i, 'price': df['high'].iloc[i]})
        elif df['low'].iloc[i] == window['low'].min():
            swings.append({'type': 'L', 'index': i, 'price': df['low'].iloc[i]})
    return swings

def check_pattern_success(df, pattern_end_index):
    entry_price = df['close'].iloc[pattern_end_index]
    target_price = entry_price * (1 + PROB_TARGET_PROFIT / 100)
    if pattern_end_index + PROB_CHECK_DAYS < len(df):
        future_prices = df['high'].iloc[pattern_end_index + 1 : pattern_end_index + PROB_CHECK_DAYS + 1]
        if future_prices.max() >= target_price:
            return True
    return False

def scan_harmonic_patterns(swings, df):
    found_patterns = []
    for i in range(len(swings) - 4):
        x, a, b, c, d = swings[i], swings[i+1], swings[i+2], swings[i+3], swings[i+4]
        if x['type'] == 'H' and a['type'] == 'L' and b['type'] == 'H' and c['type'] == 'L' and d['type'] == 'H':
            xa = abs(x['price'] - a['price'])
            if xa == 0: continue
            b_retracement = abs(a['price'] - b['price']) / xa
            d_retracement = abs(c['price'] - d['price']) / xa
            if (0.618 - TOLERANCE < b_retracement < 0.618 + TOLERANCE and
                0.786 - TOLERANCE < d_retracement < 0.786 + TOLERANCE):
                is_success = check_pattern_success(df, d['index'])
                found_patterns.append({'name': 'Bullish Gartley', 'date': df['date'].iloc[d['index']], 'success': is_success})
            if (0.382 - TOLERANCE < b_retracement < 0.5 + TOLERANCE and
                0.886 - TOLERANCE < d_retracement < 0.886 + TOLERANCE):
                is_success = check_pattern_success(df, d['index'])
                found_patterns.append({'name': 'Bullish Bat', 'date': df['date'].iloc[d['index']], 'success': is_success})
    return found_patterns

# --- 메인 실행 부분 (<<<< 여기가 업그레이드되었습니다!) ---
if __name__ == "__main__":
    log(" Harmonic Pattern Scanner (전체 종목 + 자동 저장)를 시작합니다...")
    
    try:
        all_stock_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.csv')]
        log(f"✅ 총 {len(all_stock_files)}개 종목의 데이터를 스캔합니다.")
    except FileNotFoundError:
        log(f"❌ 데이터 폴더를 찾을 수 없습니다: {DATA_PATH}")
        exit()

    all_found_patterns = {}
    total_files = len(all_stock_files)

    for i, file_name in enumerate(all_stock_files):
        stock_code = file_name.split('.')[0]
        if (i+1) % 100 == 0:
            log(f"    ... {i+1}/{total_files} 종목 스캔 중 ...")
            
        try:
            df = pd.read_csv(os.path.join(DATA_PATH, file_name))
            if len(df) < 50: continue
            swing_points = find_swing_points(df)
            if not swing_points: continue
            
            patterns = scan_harmonic_patterns(swing_points, df)
            if patterns:
                log(f"🎯 패턴 발견! [{stock_code}] - {len(patterns)}개")
                for p in patterns:
                    pattern_name = p['name']
                    if pattern_name not in all_found_patterns:
                        all_found_patterns[pattern_name] = {'total': 0, 'success': 0}
                    all_found_patterns[pattern_name]['total'] += 1
                    if p['success']:
                        all_found_patterns[pattern_name]['success'] += 1
        except Exception as e:
            log(f"❌ {stock_code} 처리 중 오류 발생: {e}")

    # --- 최종 결과를 화면과 파일에 모두 기록 ---
    report_header = "\n--- [하모닉 패턴 스캐너 최종 확률 분석 결과] ---"
    log(report_header)

    if all_found_patterns:
        report_body_intro = "전체 시장에서 발견된 하모닉 패턴의 통계적 성공 확률:"
        log(report_body_intro)
        
        report = []
        for name, data in all_found_patterns.items():
            success_rate = (data['success'] / data['total']) * 100 if data['total'] > 0 else 0
            report.append({
                "패턴 이름": name,
                "총 발견 횟수": data['total'],
                "성공 횟수": data['success'],
                "성공 확률(%)": f"{success_rate:.2f}"
            })
        
        report_df = pd.DataFrame(report)
        print(report_df.to_string()) # 화면에 표 출력
        
        # 파일에 최종 보고서 저장
        with open(REPORT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(report_header + "\n")
            f.write(report_body_intro + "\n")
            f.write(report_df.to_string())
        log(f"\n✅ 최종 분석 결과가 '{REPORT_FILE_PATH}' 파일에 저장되었습니다.")

    else:
        log("분석 기간 동안 의미 있는 하모닉 패턴을 찾지 못했습니다.")