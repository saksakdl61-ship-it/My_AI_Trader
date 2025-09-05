import configparser
import logging
from pathlib import Path
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from datetime import timedelta

# data_manager 모듈이 있다고 가정합니다.
# 이 파일은 주식 목록과 개별 주식 데이터를 로드하는 역할을 합니다.
from data_manager import DataManager 

class AIBacktester:
    """
    설정 파일을 기반으로 다양한 전략 파라미터에 대한 백테스팅을 수행하고,
    그 결과를 관리 및 저장하는 핵심 클래스.
    """
    def __init__(self, config: configparser.ConfigParser):
        """
        AIBacktester를 초기화합니다.
        
        Args:
            config (configparser.ConfigParser): 프로젝트의 전체 설정이 담긴 객체.
        """
        self.config = config
        self.paths = {}
        self.params = {}
        self.strategy_combinations = []
        self._configure()
        
        # 데이터 관리를 위한 DataManager 인스턴스 생성
        self.data_manager = DataManager(config)
        
        # 피보나치 레벨 기록을 위한 딕셔너리 추가
        self.fib_log = {}

    def _configure(self):
        """설정 객체로부터 필요한 모든 값들을 불러와 클래스 내부 변수를 설정합니다."""
        logging.info("백테스터(AIBacktester) 설정 시작...")
        try:
            # PATHS 설정
            base_path = Path(self.config.get('PATHS', 'base_path'))
            self.paths['report_file'] = base_path / self.config.get('PATHS', 'report_file')
            self.paths['fib_analysis_file'] = base_path / "fib_analysis.txt" # 새로운 파일 경로 추가
            self.paths['report_file'].parent.mkdir(parents=True, exist_ok=True)
            
            # BACKTEST 파라미터 설정
            self.params['initial_capital'] = self.config.getfloat('BACKTEST', 'INITIAL_CAPITAL', fallback=10000000)
            self.params['fee_rate'] = self.config.getfloat('BACKTEST', 'FEE_RATE', fallback=0.00015)

            # STRATEGY_PARAMS 설정 (설정 파일에서 리스트를 읽어옴)
            profit_targets = [float(p.strip()) for p in self.config.get('STRATEGY_PARAMS', 'profit_targets').split(',')]
            stop_losses = [float(s.strip()) for s in self.config.get('STRATEGY_PARAMS', 'stop_losses').split(',')]
            dca_options_str = [d.strip().lower() for d in self.config.get('STRATEGY_PARAMS', 'dca_options').split(',')]
            dca_options = [None if d == 'none' else float(d) for d in dca_options_str]

            for pt in profit_targets:
                for sl in stop_losses:
                    for dca in dca_options:
                        name = f"전략: 피보나치, 수익률 {int(pt*100)}%, 손절율 {int(sl*100)}%, 물타기 {bool(dca)}"
                        self.strategy_combinations.append({'profit_target': pt, 'stop_loss': sl, 'buy_the_dip': dca, 'strategy_name': name})
            
            logging.info(f"✅ 백테스터 설정 완료. {len(self.strategy_combinations)}개의 전략 조합 생성.")

        except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            logging.error(f"설정 파일('.ini')을 읽는 중 오류가 발생했습니다: {e}")
            raise KeyError(f"설정 파일의 [PATHS], [BACKTEST], [STRATEGY_PARAMS] 섹션과 값들을 확인해주세요: {e}")

    def _get_completed_tasks(self) -> set:
        """기존 리포트 파일에서 이미 완료된 전략들의 이름을 읽어옵니다."""
        completed = set()
        report_file = self.paths['report_file']
        if not report_file.exists():
            return completed
        
        with open(report_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "전략:" in line and "->" in line:
                    completed.add(line.split('->')[0].strip())
        return completed

    def _calculate_fibonacci_levels(self, df_slice: pd.DataFrame) -> dict:
        """주어진 데이터 조각에 대한 피보나치 되돌림 레벨을 계산합니다."""
        high_price = df_slice['high'].max()
        low_price = df_slice['low'].min()
        price_range = high_price - low_price
        if price_range == 0: return {}
        return {
            'level_38.2%': high_price - price_range * 0.382,
            'level_61.8%': high_price - price_range * 0.618
        }

    def _run_single_strategy(self, df: pd.DataFrame, params: dict) -> tuple:
        """단일 전략에 대한 백테스팅 시뮬레이션을 실행합니다."""
        capital = self.params['initial_capital']
        fee_rate = self.params['fee_rate']
        position = None
        trade_log = []
        capital_history = [capital]
        
        # 필요한 기술적 지표 계산 (매매 조건에서 제거되므로 주석 처리하거나 제거 가능)
        df.ta.rsi(append=True)
        df.ta.macd(append=True)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        for i in range(60, len(df)):
            current_price = df['close'].iloc[i]
            
            # --- 매수 조건 탐색 (피보나치 되돌림만 사용) ---
            if position is None:
                sub_df_for_fib = df.iloc[i-60:i]
                fib_levels = self._calculate_fibonacci_levels(sub_df_for_fib)
                
                # 어떤 피보나치 레벨에서 신호가 감지되었는지 확인하고 기록
                detected_fib_level = None
                for level_name, level_price in fib_levels.items():
                    if abs(current_price - level_price) / level_price < 0.01:
                        detected_fib_level = level_name
                        break
                
                if detected_fib_level:
                    # 피보나치 레벨 탐지 기록
                    self.fib_log.setdefault(detected_fib_level, 0)
                    self.fib_log[detected_fib_level] += 1
                
                is_fib_support = detected_fib_level is not None
                
                # 피보나치 지지선 근처에서 매수
                if is_fib_support:
                    buy_ratio = 0.5 if params['buy_the_dip'] else 1.0
                    quantity = (capital * buy_ratio) // current_price
                    if quantity > 0:
                        cost = current_price * quantity * (1 + fee_rate)
                        capital -= cost
                        position = {'price': current_price, 'quantity': quantity, 'dca_done': False}
            
            # --- 매도 또는 물타기 조건 탐색 ---
            elif position is not None:
                profit_rate = (current_price - position['price']) / position['price']
                
                # 매도
                if profit_rate >= params['profit_target'] or profit_rate <= -params['stop_loss']:
                    sell_value = current_price * position['quantity'] * (1 - fee_rate)
                    capital += sell_value
                    trade_log.append({'result': 'Win' if profit_rate >= 0 else 'Loss'})
                    position = None
                
                # 물타기 (DCA)
                elif params['buy_the_dip'] and not position['dca_done'] and profit_rate <= -params['buy_the_dip']:
                    dca_quantity = capital // current_price
                    if dca_quantity > 0:
                        dca_cost = dca_quantity * current_price * (1 + fee_rate)
                        capital -= dca_cost
                        
                        total_cost = (position['price'] * position['quantity']) + (current_price * dca_quantity)
                        total_quantity = position['quantity'] + dca_quantity
                        
                        position['price'] = total_cost / total_quantity
                        position['quantity'] = total_quantity
                        position['dca_done'] = True
            
            current_value = capital + (current_price * position['quantity'] if position else 0)
            capital_history.append(current_value)

        if position is not None:
            capital += df['close'].iloc[-1] * position['quantity']
        
        # 최종 성과 계산
        peak = np.maximum.accumulate(capital_history)
        drawdown = (peak - capital_history) / peak if np.all(peak != 0) else np.zeros_like(peak)
        mdd = np.max(drawdown) * 100
        total_return = (capital / self.params['initial_capital'] - 1) * 100
        win_count = sum(1 for t in trade_log if t.get('result') == 'Win')
        win_rate = (win_count / len(trade_log) * 100) if trade_log else 0
        
        return total_return, win_rate, mdd, len(trade_log)

    def _write_fib_analysis(self):
        """피보나치 되돌림 레벨 탐지 결과를 파일에 기록합니다."""
        if not self.fib_log:
            logging.info("⭐ 피보나치 되돌림 탐지 기록이 없어 분석을 건너뜁니다.")
            return

        sorted_fib_log = sorted(self.fib_log.items(), key=lambda item: item[1], reverse=True)
        
        with open(self.paths['fib_analysis_file'], "w", encoding="utf-8") as f:
            f.write("--- 피보나치 되돌림 레벨 탐지 횟수 분석 ---\n")
            for level, count in sorted_fib_log:
                f.write(f"• {level}: {count}회 탐지\n")
            f.write("\n")
        
        logging.info(f"✅ 피보나치 분석 결과가 '{self.paths['fib_analysis_file']}'에 저장되었습니다.")

    def run_backtest(self):
        """설정된 모든 전략 조합에 대해 백테스팅을 실행하고 결과를 저장합니다."""
        logging.info("🚀 AI 비서 전략 자동 탐색기 (피보나치 강화 v1)를 시작합니다...")
        completed_tasks = self._get_completed_tasks()
        logging.info(f"✅ 총 {len(completed_tasks)}개의 기존 전략 결과를 확인했습니다. 중단된 지점부터 이어갑니다.")
        
        stock_codes = self.data_manager.load_stock_list()
        if not stock_codes:
            logging.error("❌ 종목 리스트를 불러오지 못했습니다. 프로그램을 종료합니다.")
            return
        logging.info(f"✅ 총 {len(stock_codes)}개 종목에 대해 백테스팅을 시작합니다.")

        total_strategies = len(self.strategy_combinations)
        start_time = time.time()

        with open(self.paths['report_file'], "a", encoding="utf-8") as report_file:
            for i, strategy_params in enumerate(self.strategy_combinations):
                strategy_name = strategy_params['strategy_name']
                if strategy_name in completed_tasks:
                    logging.info(f"이미 완료된 전략: '{strategy_name}' ... 건너뜁니다.")
                    continue

                logging.info(f"\n--- [{i+1}/{total_strategies}] 전략 '{strategy_name}' 백테스팅 시작 ---")
                all_stock_results = []
                for j, code in enumerate(stock_codes):
                    if (j+1) % 200 == 0:
                        logging.info(f"    ... {j+1}/{len(stock_codes)} 종목 처리 중 ...")
                    
                    df = self.data_manager.load_stock_data(code)
                    if df is None or len(df) < 100:
                        continue

                    try:
                        total_return, win_rate, mdd, num_trades = self._run_single_strategy(df.copy(), strategy_params)
                        if num_trades > 0:
                            all_stock_results.append({'return': total_return, 'win_rate': win_rate, 'mdd': mdd})
                    except Exception as e:
                        logging.warning(f" 종목 '{code}' 백테스팅 중 오류 발생: {e}")

                if all_stock_results:
                    result_df = pd.DataFrame(all_stock_results)
                    avg_return = result_df['return'].mean()
                    avg_win_rate = result_df['win_rate'].mean()
                    avg_mdd = result_df['mdd'].mean()
                    
                    result_line = (f"{strategy_name} -> "
                                   f"총 수익률: {avg_return:.2f}%, "
                                   f"승률: {avg_win_rate:.2f}%, "
                                   f"MDD: {avg_mdd:.2f}%\n")
                    report_file.write(result_line)
                    report_file.flush()
                else:
                    result_line = f"{strategy_name} -> 거래 없음 (No Trades Found)\n"
                    report_file.write(result_line)
                    report_file.flush()
                    
                elapsed_time = time.time() - start_time
                avg_time_per_strategy = elapsed_time / (i + 1)
                remaining_strategies = total_strategies - (i + 1)
                eta_seconds = avg_time_per_strategy * remaining_strategies
                eta_formatted = str(timedelta(seconds=int(eta_seconds)))
                logging.info(f"✅ 전략 백테스팅 완료. 남은 전략: {remaining_strategies}개, 예상 시간: {eta_formatted}")
        
        self._write_fib_analysis() # 백테스팅 완료 후 분석 결과를 기록합니다.
        logging.info(f"🎉 모든 백테스팅 완료! 최종 결과는 '{self.paths['report_file']}'에 저장되었습니다.")
