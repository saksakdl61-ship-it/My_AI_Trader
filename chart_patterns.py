import pandas as pd
import numpy as np

class ChartPatterns:
    def detect_cup_and_handle(self, df_slice):
        """
        컵앤핸들(Cup and Handle) 패턴을 감지하고 유사도 점수를 반환합니다.
        컵과 손잡이의 비율, 깊이, 그리고 돌파 강도를 기반으로 점수를 매깁니다.
        """
        if len(df_slice) < 50: return 0
        
        # 컵 모양 감지 (U자형)
        cup_slice = df_slice.iloc[-40:-10]
        cup_high = cup_slice['high'].max()
        cup_low = cup_slice['low'].min()
        cup_range = cup_high - cup_low
        
        # 컵의 바닥이 U자형인지 확인 (긴 기간의 횡보 후 상승)
        is_cup_shape = np.all(cup_slice['close'].diff().fillna(0).cumsum() > 0)
        
        # 손잡이 모양 감지 (작은 하락 횡보)
        handle_slice = df_slice.iloc[-10:]
        handle_high = handle_slice['high'].max()
        handle_low = handle_slice['low'].min()
        handle_range = handle_high - handle_low

        # 컵과 손잡이의 관계 확인
        is_handle_valid = (handle_high < cup_high and handle_range < cup_range * 0.3)
        
        if is_cup_shape and is_handle_valid:
            # 돌파 강도 계산 (현재 종가가 손잡이 고점보다 높을 때)
            if df_slice.iloc[-1]['close'] > handle_high:
                similarity = 1 - (handle_high - df_slice.iloc[-1]['close']) / handle_high
                return int(similarity * 100)
        
        return 0

    def detect_inverse_head_and_shoulders(self, df_slice):
        """
        역헤드앤숄더(Inverse Head and Shoulders) 패턴을 감지하고 유사도를 반환합니다.
        어깨, 머리, 넥라인의 비율과 대칭성을 기반으로 점수를 매깁니다.
        """
        if len(df_slice) < 60: return 0
        
        # 각 부분의 인덱스 설정 (대략적인 위치)
        left_shoulder_idx = df_slice.iloc[-50:-40]
        head_idx = df_slice.iloc[-35:-25]
        right_shoulder_idx = df_slice.iloc[-20:-10]
        
        # 각 부분의 저점
        left_shoulder_low = left_shoulder_idx['low'].min()
        head_low = head_idx['low'].min()
        right_shoulder_low = right_shoulder_idx['low'].min()
        
        # 머리가 양 어깨보다 낮은지 확인
        is_head_lower = head_low < left_shoulder_low and head_low < right_shoulder_low
        
        # 넥라인(neckline) 형성 확인
        neckline_high = df_slice.iloc[-25:-10]['high'].max()
        is_neckline_breakout = df_slice.iloc[-1]['close'] > neckline_high

        # 어깨의 대칭성 확인
        shoulder_diff = abs(left_shoulder_low - right_shoulder_low)
        shoulder_avg = (left_shoulder_low + right_shoulder_low) / 2
        
        if is_head_lower and is_neckline_breakout:
            # 유사도 점수 계산
            similarity = 1 - (shoulder_diff / shoulder_avg)
            return int(similarity * 100)
            
        return 0

    def detect_double_top(self, df_slice):
        """
        이중 천장(Double Top) 패턴을 감지하고 유사도를 반환합니다.
        두 개의 고점과 그 사이의 저점, 그리고 넥라인 돌파를 기반으로 점수를 매깁니다.
        """
        if len(df_slice) < 30: return 0

        # 첫 번째 고점 감지
        first_peak = df_slice.iloc[-30:-15]
        peak1_high = first_peak['high'].max()
        
        # 두 번째 고점 감지
        second_peak = df_slice.iloc[-15:-5]
        peak2_high = second_peak['high'].max()
        
        # 중간 저점 감지
        valley = df_slice.iloc[-20:-10]
        valley_low = valley['low'].min()

        # 두 개의 고점이 비슷한지 확인
        is_peaks_similar = abs(peak1_high - peak2_high) < (peak1_high * 0.03)

        # 고점이 중간 저점보다 높은지 확인
        is_highs_above_valley = peak1_high > valley_low and peak2_high > valley_low
        
        if is_peaks_similar and is_highs_above_valley:
            # 넥라인 돌파 확인 (종가가 저점보다 낮을 때)
            if df_slice.iloc[-1]['close'] < valley_low:
                return 100
        
        return 0

    def detect_double_bottom(self, df_slice):
        """
        이중 바닥(Double Bottom) 패턴을 감지하고 유사도를 반환합니다.
        """
        if len(df_slice) < 30: return 0

        first_trough = df_slice.iloc[-30:-15]
        trough1_low = first_trough['low'].min()
        
        second_trough = df_slice.iloc[-15:-5]
        trough2_low = second_trough['low'].min()
        
        middle_peak = df_slice.iloc[-20:-10]
        middle_peak_high = middle_peak['high'].max()

        is_troughs_similar = abs(trough1_low - trough2_low) < (trough1_low * 0.03)

        is_lows_below_peak = trough1_low < middle_peak_high and trough2_low < middle_peak_high
        
        if is_troughs_similar and is_lows_below_peak:
            if df_slice.iloc[-1]['close'] > middle_peak_high:
                return 100
        
        return 0
        
    def detect_triangle_ascending(self, df_slice):
        """
        상승 삼각형(Ascending Triangle) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현

    def detect_triangle_descending(self, df_slice):
        """
        하락 삼각형(Descending Triangle) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현

    def detect_triangle_symmetrical(self, df_slice):
        """
        대칭 삼각형(Symmetrical Triangle) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현

    def detect_wedge_bullish(self, df_slice):
        """
        불리시 웻지(Bullish Wedge) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현

    def detect_wedge_bearish(self, df_slice):
        """
        베어리시 웻지(Bearish Wedge) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현

    def detect_head_and_shoulders(self, df_slice):
        """
        헤드앤숄더(Head and Shoulders) 패턴을 감지하고 유사도를 반환합니다.
        """
        return 0 # 미구현
